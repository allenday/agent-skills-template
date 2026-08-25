import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/new-skill"


class NewSkillTests(unittest.TestCase):
    def run_script(self, root, name):
        return subprocess.run(
            [str(SCRIPT), name, "--root", str(root)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_scaffolds_portable_skill_and_eval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            completed = self.run_script(root, "release-notes")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            skill = root / "skills/release-notes/SKILL.md"
            fixture = json.loads((root / "evals/release-notes.json").read_text())
            self.assertIn("name: release-notes", skill.read_text())
            self.assertEqual(fixture["skill"], "release-notes")

    def test_rejects_invalid_name_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            completed = self.run_script(root, "Not Valid")
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse((root / "skills").exists())

    def test_refuses_to_overwrite_existing_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(self.run_script(root, "release-notes").returncode, 0)
            skill = root / "skills/release-notes/SKILL.md"
            original = skill.read_text()
            completed = self.run_script(root, "release-notes")
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(skill.read_text(), original)

    def test_existing_evals_file_creates_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evals").write_text("not a directory\n")

            completed = self.run_script(root, "release-notes")

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse((root / "skills").exists())
            self.assertEqual((root / "evals").read_text(), "not a directory\n")

    def test_dangling_eval_symlink_creates_nothing_or_writes_outside_root(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repository"
            evals = root / "evals"
            outside = base / "outside.json"
            evals.mkdir(parents=True)
            (evals / "release-notes.json").symlink_to(outside)

            completed = self.run_script(root, "release-notes")

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse((root / "skills").exists())
            self.assertTrue((evals / "release-notes.json").is_symlink())
            self.assertFalse(outside.exists())


if __name__ == "__main__":
    unittest.main()
