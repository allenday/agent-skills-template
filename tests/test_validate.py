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


if __name__ == "__main__":
    unittest.main()
