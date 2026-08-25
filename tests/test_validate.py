import importlib.machinery
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate"


def load_validator():
    loader = importlib.machinery.SourceFileLoader("skill_validator", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


def write_repo(root: Path, *, name="sample-skill", description=None):
    description = description or "Demonstrate validation. Use when testing this fixture."
    (root / ".codex-plugin").mkdir(parents=True)
    (root / ".agents/plugins").mkdir(parents=True)
    (root / "skills" / name / "references").mkdir(parents=True)
    (root / "evals").mkdir()
    (root / ".codex-plugin/plugin.json").write_text(json.dumps({
        "name": "fixture", "version": "0.1.0", "description": "fixture", "skills": "./skills/"
    }))
    (root / ".agents/plugins/marketplace.json").write_text(json.dumps({
        "name": "fixture",
        "plugins": [{
            "name": "fixture",
            "source": {"source": "local", "path": "./"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    }))
    (root / "skills" / name / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# Sample\n"
        "Read [the reference](references/example.md).\n"
    )
    (root / "skills" / name / "references/example.md").write_text("# Reference\n")
    (root / "evals" / f"{name}.json").write_text(json.dumps({
        "skill": name,
        "positive": ["one", "two", "three"],
        "negative": ["four", "five"],
    }))


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def test_valid_repository_has_no_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            findings = self.validator.validate(root)
            self.assertEqual([f for f in findings if f.severity == "error"], [])

    def test_name_mismatch_and_weak_evals_have_stable_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            skill = root / "skills/sample-skill/SKILL.md"
            skill.write_text(skill.read_text().replace("name: sample-skill", "name: wrong-name"))
            fixture = root / "evals/sample-skill.json"
            fixture.write_text(json.dumps({"skill": "sample-skill", "positive": [], "negative": []}))
            codes = {finding.code for finding in self.validator.validate(root)}
            self.assertIn("SKILL_NAME_MISMATCH", codes)
            self.assertIn("EVAL_POSITIVE_MIN", codes)
            self.assertIn("EVAL_NEGATIVE_MIN", codes)

    def test_missing_and_escaping_references_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            skill = root / "skills/sample-skill/SKILL.md"
            skill.write_text(skill.read_text() + "\n[Missing](references/nope.md)\n[Escape](../../README.md)\n")
            codes = {finding.code for finding in self.validator.validate(root)}
            self.assertIn("REFERENCE_MISSING", codes)
            self.assertIn("REFERENCE_ESCAPES_SKILL", codes)

    def test_invalid_marketplace_source_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            market = root / ".agents/plugins/marketplace.json"
            data = json.loads(market.read_text())
            data["plugins"][0]["source"]["path"] = "../outside"
            market.write_text(json.dumps(data))
            codes = {finding.code for finding in self.validator.validate(root)}
            self.assertIn("MARKETPLACE_SOURCE_PATH", codes)

    def test_nonlocal_marketplace_source_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            market = root / ".agents/plugins/marketplace.json"
            data = json.loads(market.read_text())
            data["plugins"][0]["source"]["source"] = "github"
            market.write_text(json.dumps(data))
            codes = {finding.code for finding in self.validator.validate(root)}
            self.assertIn("MARKETPLACE_SOURCE_PATH", codes)

    def test_symlinked_skill_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            skill_dir = root / "skills/sample-skill"
            relocated = root / "relocated-skill"
            skill_dir.rename(relocated)
            skill_dir.symlink_to(relocated, target_is_directory=True)

            codes = {finding.code for finding in self.validator.validate(root)}

            self.assertIn("SKILL_DIRECTORY_SYMLINK", codes)

    def test_symlinked_skill_file_and_asset_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            skill_dir = root / "skills/sample-skill"
            skill_path = skill_dir / "SKILL.md"
            original = skill_dir / "original-skill.md"
            skill_path.rename(original)
            skill_path.symlink_to(original.name)
            asset = skill_dir / "references/example.md"
            asset.unlink()
            asset.symlink_to(root / "outside.md")
            (root / "outside.md").write_text("outside\n")

            codes = {finding.code for finding in self.validator.validate(root)}

            self.assertIn("SKILL_FILE_SYMLINK", codes)
            self.assertIn("SKILL_ASSET_SYMLINK", codes)
            self.assertIn("SKILL_ASSET_ESCAPES", codes)

    def test_manifest_and_marketplace_required_metadata_fail_with_stable_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            manifest_path = root / ".codex-plugin/plugin.json"
            manifest_path.write_text(json.dumps({
                "name": "Bad_Name", "version": " ", "description": "\t", "skills": "skills",
            }))
            marketplace_path = root / ".agents/plugins/marketplace.json"
            marketplace_path.write_text(json.dumps({
                "name": " ",
                "plugins": [{
                    "name": "Bad_Name",
                    "source": {"source": "github", "path": "not-local"},
                    "policy": {"installation": " ", "authentication": ""},
                    "category": "\n",
                }],
            }))

            codes = {finding.code for finding in self.validator.validate(root)}

            self.assertTrue({
                "MANIFEST_NAME_INVALID", "MANIFEST_VERSION_MISSING",
                "MANIFEST_DESCRIPTION_MISSING", "MANIFEST_SKILLS_PATH",
                "MARKETPLACE_NAME_MISSING", "MARKETPLACE_PLUGIN_NAME_INVALID",
                "MARKETPLACE_SOURCE_PATH",
                "MARKETPLACE_POLICY_INSTALLATION_MISSING",
                "MARKETPLACE_POLICY_AUTHENTICATION_MISSING", "MARKETPLACE_CATEGORY_MISSING",
            }.issubset(codes))

            data = json.loads(marketplace_path.read_text())
            data["plugins"][0]["policy"] = []
            marketplace_path.write_text(json.dumps(data))
            codes = {finding.code for finding in self.validator.validate(root)}
            self.assertIn("MARKETPLACE_POLICY_INVALID", codes)

    def test_eval_prompt_entries_must_be_nonblank_and_not_placeholders(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_repo(root)
            fixture = root / "evals/sample-skill.json"
            fixture.write_text(json.dumps({
                "skill": "sample-skill",
                "positive": ["valid", " ", "REPLACE: positive"],
                "negative": ["REPLACE: negative", 5],
            }))

            codes = {finding.code for finding in self.validator.validate(root)}

            self.assertIn("EVAL_PROMPT_INVALID", codes)
            self.assertIn("EVAL_PROMPT_PLACEHOLDER", codes)


if __name__ == "__main__":
    unittest.main()
