import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_plugin_manifest_points_to_skills(self):
        manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], "agent-skills-template")
        self.assertEqual(manifest["skills"], "./skills/")

    def test_repo_marketplace_exposes_root_plugin(self):
        market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(market["name"], "agent-skills-template")
        self.assertEqual(market["plugins"][0]["name"], "agent-skills-template")
        self.assertEqual(market["plugins"][0]["source"]["path"], "./")

    def test_example_skill_has_local_reference_and_evals(self):
        skill = ROOT / "skills/example-skill/SKILL.md"
        reference = ROOT / "skills/example-skill/references/example-reference.md"
        fixture = json.loads((ROOT / "evals/example-skill.json").read_text())
        self.assertTrue(skill.is_file())
        self.assertTrue(reference.is_file())
        self.assertEqual(fixture["skill"], "example-skill")
        self.assertGreaterEqual(len(fixture["positive"]), 3)
        self.assertGreaterEqual(len(fixture["negative"]), 2)

    def test_repository_validator_passes(self):
        completed = subprocess.run(
            [str(ROOT / "scripts/validate"), "--root", str(ROOT), "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_readme_documents_the_actual_commands(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("scripts/new-skill", readme)
        self.assertIn("scripts/validate", readme)
        self.assertIn("Use this template", readme)
        for source in (
            "codex plugin marketplace add OWNER/REPOSITORY --ref main",
            "codex plugin marketplace add https://github.com/OWNER/REPOSITORY.git --ref main",
            "codex plugin marketplace add git@github.com:OWNER/REPOSITORY.git --ref main",
            "codex plugin marketplace add /absolute/path/to/REPOSITORY",
            "codex plugin marketplace list",
        ):
            with self.subTest(source=source):
                self.assertIn(source, readme)

    def test_governance_files_exist(self):
        for path in ("AGENTS.md", "CONTRIBUTING.md", "LICENSE", "THIRD_PARTY_NOTICES.md"):
            self.assertTrue((ROOT / path).is_file(), path)

    def test_ci_runs_unit_tests_and_validator(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text()
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn("scripts/validate --format json", workflow)


if __name__ == "__main__":
    unittest.main()
