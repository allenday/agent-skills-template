# Agent Skills Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public native GitHub template for independently extractable Agent Skills that can also be installed together as a skills-only Codex plugin.

**Architecture:** The repository root is one skills-only plugin and one repo marketplace. Each directory under `skills/` is a self-contained runtime unit. Dependency-free Python 3 scripts scaffold and validate skills, while `unittest` and GitHub Actions enforce the same repository contract.

**Tech Stack:** Agent Skills (`SKILL.md`), Codex plugin manifest JSON, GitHub marketplace JSON, Python 3 standard library, `unittest`, GitHub Actions, Markdown

**Spec:** `docs/superpowers/specs/2026-08-25-agent-skills-template-design.md`

## Global Constraints

- Every directory under `skills/` must be independently installable.
- Runtime files must not depend on repository-root files or sibling skills.
- Root scripts and evals may maintain the monorepo but must not be runtime dependencies of extracted skills.
- Validation must install no dependencies and mutate no repository content.
- The initial plugin contains no MCP server, hooks, UI, or external tool dependencies.
- The repository uses Apache License 2.0.

---

### Task 1: Installable plugin skeleton and example skill

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `skills/example-skill/SKILL.md`
- Create: `skills/example-skill/references/example-reference.md`
- Create: `evals/example-skill.json`
- Create: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: The Codex plugin manifest and marketplace formats described in the approved spec.
- Produces: A root plugin named `agent-skills-template`, a discoverable `example-skill`, and the eval fixture shape consumed by Task 2.

- [ ] **Step 1: Write repository contract tests**

Create `tests/test_repository_contract.py`:

```python
import json
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify the missing skeleton fails**

Run: `python3 -m unittest tests.test_repository_contract -v`

Expected: three errors containing `FileNotFoundError`.

- [ ] **Step 3: Create the minimal plugin and marketplace manifests**

Create `.codex-plugin/plugin.json`:

```json
{
  "name": "agent-skills-template",
  "version": "0.1.0",
  "description": "A forkable monorepo template for portable Agent Skills",
  "skills": "./skills/"
}
```

Create `.agents/plugins/marketplace.json`:

```json
{
  "name": "agent-skills-template",
  "interface": {
    "displayName": "Agent Skills Template"
  },
  "plugins": [
    {
      "name": "agent-skills-template",
      "source": {
        "source": "local",
        "path": "./"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

- [ ] **Step 4: Create the self-contained example skill**

Create `skills/example-skill/SKILL.md`:

```markdown
---
name: example-skill
description: Demonstrate the repository's portable skill structure. Use when testing a repository generated from this template or learning how its skills and references fit together.
---

# Example skill

Use this skill only as a working example. Replace or remove it when adapting the template.

1. Read [references/example-reference.md](references/example-reference.md).
2. State that the example skill loaded successfully.
3. Name the local reference you read.

Do not claim to perform a domain workflow.
```

Create `skills/example-skill/references/example-reference.md`:

```markdown
# Example reference

This file demonstrates progressive disclosure. Runtime references belong inside the skill that uses them so the skill remains portable when copied out of the monorepo.
```

Create `evals/example-skill.json`:

```json
{
  "skill": "example-skill",
  "positive": [
    "Test the example skill in this template.",
    "Show me how this repository's sample skill loads a reference.",
    "Verify that the example Agent Skill is discoverable."
  ],
  "negative": [
    "Write documentation for my API.",
    "Design a command-line interface."
  ]
}
```

- [ ] **Step 5: Run the repository contract tests**

Run: `python3 -m unittest tests.test_repository_contract -v`

Expected: `Ran 3 tests` and `OK`.

- [ ] **Step 6: Commit the skeleton**

```bash
git add .codex-plugin/plugin.json .agents/plugins/marketplace.json skills/example-skill evals/example-skill.json tests/test_repository_contract.py
git commit -m "feat: add installable skill plugin skeleton"
```

---

### Task 2: Dependency-free repository validator

**Files:**
- Create: `scripts/validate`
- Create: `tests/test_validate.py`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `skills/*/SKILL.md`, relative Markdown references, and `evals/*.json`.
- Produces: `validate(root: Path) -> list[Finding]`, stable finding codes, human output by default, JSON with `--format json`, and exit status 0 only when there are no error findings.

- [ ] **Step 1: Write validator behavior tests**

Create `tests/test_validate.py` with temporary repository fixtures and these tests:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the validator tests and verify the loader fails**

Run: `python3 -m unittest tests.test_validate -v`

Expected: error loading the absent `scripts/validate`.

- [ ] **Step 3: Implement the validator data model and parsers**

Create executable `scripts/validate` using only the standard library. Define:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)\n---(?:\n|\Z)", re.DOTALL)
LINK = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.search(text)
    if not match:
        return {}
    fields = {}
    for line in match.group("body").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def add(findings, severity, code, path, message):
    findings.append(Finding(severity, code, path.as_posix(), message))
```

- [ ] **Step 4: Implement repository checks**

Implement `validate(root: Path) -> list[Finding]` with explicit checks for:

- `MANIFEST_MISSING`, `MANIFEST_INVALID`, and `MANIFEST_SKILLS_PATH`.
- `MARKETPLACE_MISSING`, `MARKETPLACE_INVALID`, `MARKETPLACE_PLUGIN_MISMATCH`, and `MARKETPLACE_SOURCE_PATH`; the root plugin source must be `./` and match the manifest name.
- `SKILL_FRONTMATTER_MISSING`, `SKILL_NAME_INVALID`, `SKILL_NAME_MISMATCH`, `SKILL_DESCRIPTION_MISSING`, and `SKILL_DESCRIPTION_TOO_LONG` at 1024 characters.
- `SKILL_DESCRIPTION_TRIGGER` when the description lacks `use when`.
- `SKILL_TOO_LARGE` as a warning above 500 lines.
- `REFERENCE_MISSING` and `REFERENCE_ESCAPES_SKILL`, ignoring `http:`, `https:`, `mailto:`, anchors, and images.
- `EVAL_MISSING`, `EVAL_INVALID`, `EVAL_SKILL_MISMATCH`, `EVAL_POSITIVE_MIN` below 3, and `EVAL_NEGATIVE_MIN` below 2.
- `EVAL_ORPHAN` for eval files without a corresponding skill.

Sort findings by `(severity, path, code, message)` before returning them.

- [ ] **Step 5: Implement CLI rendering**

Add:

```python
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate an Agent Skills monorepo")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)
    findings = validate(args.root.resolve())
    errors = sum(f.severity == "error" for f in findings)
    warnings = sum(f.severity == "warning" for f in findings)
    if args.format == "json":
        print(json.dumps({
            "ok": errors == 0,
            "summary": {"errors": errors, "warnings": warnings},
            "findings": [asdict(f) for f in findings],
        }, indent=2, sort_keys=True))
    else:
        for finding in findings:
            print(f"{finding.severity.upper()} {finding.code} {finding.path}: {finding.message}")
        print(f"Validation complete: {errors} error(s), {warnings} warning(s)")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

Run: `chmod +x scripts/validate`

- [ ] **Step 6: Run validator tests and the real repository validation**

Run: `python3 -m unittest tests.test_validate -v`

Expected: `Ran 4 tests` and `OK`.

Run: `scripts/validate --format json`

Expected: JSON containing `"ok": true` and zero errors.

- [ ] **Step 7: Add the real validator to the repository contract test**

Add this test to `tests/test_repository_contract.py`:

```python
    def test_repository_validator_passes(self):
        import subprocess
        completed = subprocess.run(
            [str(ROOT / "scripts/validate"), "--root", str(ROOT), "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
```

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 8: Commit the validator**

```bash
git add scripts/validate tests/test_validate.py tests/test_repository_contract.py
git commit -m "feat: validate portable skill repositories"
```

---

### Task 3: Safe skill scaffolder

**Files:**
- Create: `scripts/new-skill`
- Create: `tests/test_new_skill.py`

**Interfaces:**
- Consumes: A kebab-case skill name and optional `--root PATH`.
- Produces: `skills/<name>/SKILL.md`, `skills/<name>/references/.gitkeep`, and `evals/<name>.json`; exits nonzero without changing files for invalid names or collisions.

- [ ] **Step 1: Write scaffolder tests**

Create `tests/test_new_skill.py`:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify the absent script fails**

Run: `python3 -m unittest tests.test_new_skill -v`

Expected: errors containing `FileNotFoundError`.

- [ ] **Step 3: Implement `scripts/new-skill`**

Use Python 3 standard library, validate `^[a-z0-9]+(?:-[a-z0-9]+)*$`, check all target paths before creating directories, and write this exact initial skill body:

```markdown
---
name: {name}
description: Describe what this skill does. Use when the user asks for its specific workflow.
---

# {title}

## Workflow

1. Confirm the workflow input and desired output.
2. Follow the project-specific source of truth.
3. Produce the requested result.
4. Verify the result before reporting completion.
```

Write an eval fixture with three clearly marked positive prompt strings and two negative prompt strings that the author must replace. Print the three created paths on success. Return exit code 2 for an invalid name and 3 for an existing target.

Run: `chmod +x scripts/new-skill`.

- [ ] **Step 4: Run scaffolder and full test suites**

Run: `python3 -m unittest tests.test_new_skill -v`

Expected: `Ran 3 tests` and `OK`.

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 5: Exercise the scaffolder in a temporary repository**

Run:

```bash
tmp_dir=$(mktemp -d)
scripts/new-skill smoke-test --root "$tmp_dir"
test -f "$tmp_dir/skills/smoke-test/SKILL.md"
test -f "$tmp_dir/evals/smoke-test.json"
```

Expected: three created paths and exit status 0.

- [ ] **Step 6: Commit the scaffolder**

```bash
git add scripts/new-skill tests/test_new_skill.py
git commit -m "feat: scaffold portable agent skills"
```

---

### Task 4: Fork-friendly documentation and policies

**Files:**
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `AGENTS.md`
- Create: `LICENSE`
- Create: `THIRD_PARTY_NOTICES.md`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: The commands and file layout from Tasks 1–3.
- Produces: A human quickstart, agent instructions, contribution contract, Apache-2.0 license, and import provenance template.

- [ ] **Step 1: Add documentation contract tests**

Add to `tests/test_repository_contract.py`:

```python
    def test_readme_documents_the_actual_commands(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("scripts/new-skill", readme)
        self.assertIn("scripts/validate", readme)
        self.assertIn("codex plugin marketplace add", readme)
        self.assertIn("Use this template", readme)

    def test_governance_files_exist(self):
        for path in ("AGENTS.md", "CONTRIBUTING.md", "LICENSE", "THIRD_PARTY_NOTICES.md"):
            self.assertTrue((ROOT / path).is_file(), path)
```

- [ ] **Step 2: Run the new tests and verify missing docs fail**

Run: `python3 -m unittest tests.test_repository_contract -v`

Expected: failures for absent `README.md` and governance files.

- [ ] **Step 3: Write `README.md`**

Document these exact workflows:

1. Generate a repository with **Use this template**.
2. Update `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` names and display copy.
3. Remove `example-skill` and its eval, or use it as a pattern.
4. Run `scripts/new-skill <name>`.
5. Replace scaffold descriptions and eval prompts.
6. Run `scripts/validate` and `python3 -m unittest discover -s tests -v`.
7. Add the GitHub repository with `codex plugin marketplace add owner/repo --ref main`.
8. Start a fresh Codex session and install from `/plugins`.
9. Explain independent extraction by copying one complete `skills/<name>/` directory.

State explicitly that generated repositories have independent histories and do not receive template updates automatically.

- [ ] **Step 4: Write contributor and agent guidance**

`CONTRIBUTING.md` must define:

- Kebab-case names and matching directory/frontmatter names.
- At least three positive and two negative trigger prompts.
- Runtime self-containment.
- Required local validation commands.
- Provenance recording for imported material.

`AGENTS.md` must tell agents to:

- Read the target skill completely before editing.
- Keep runtime dependencies inside the skill.
- Use `scripts/new-skill` for new skills.
- Run validator and unit tests before completion.
- Preserve user and third-party work.
- Avoid adding MCP, hooks, UI, or dependencies without explicit scope.

- [ ] **Step 5: Add licensing files**

Create `LICENSE` with the unmodified Apache License 2.0 text.

Create `THIRD_PARTY_NOTICES.md` with a reusable entry format containing:

```markdown
## Imported work name

- Source: URL and immutable revision
- Imported files: repository-relative paths
- Copyright: original notice
- License: SPDX identifier and bundled license location
- Modifications: concise description and date
```

State that the empty template has no bundled third-party work at publication time.

- [ ] **Step 6: Run documentation and full validation**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

Run: `scripts/validate --format json`

Expected: zero errors.

- [ ] **Step 7: Commit documentation and policy**

```bash
git add README.md CONTRIBUTING.md AGENTS.md LICENSE THIRD_PARTY_NOTICES.md tests/test_repository_contract.py
git commit -m "docs: explain skill template workflow"
```

---

### Task 5: Continuous validation and native GitHub template activation

**Files:**
- Create: `.github/workflows/validate.yml`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: `scripts/validate` and the complete `unittest` suite.
- Produces: Required CI evidence on pushes and pull requests, followed by GitHub repository template activation.

- [ ] **Step 1: Test the CI workflow contract**

Add to `tests/test_repository_contract.py`:

```python
    def test_ci_runs_unit_tests_and_validator(self):
        workflow = (ROOT / ".github/workflows/validate.yml").read_text()
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn("scripts/validate --format json", workflow)
```

- [ ] **Step 2: Run the contract test and verify it fails**

Run: `python3 -m unittest tests.test_repository_contract -v`

Expected: failure because `.github/workflows/validate.yml` is absent.

- [ ] **Step 3: Add the GitHub Actions workflow**

Create `.github/workflows/validate.yml`:

```yaml
name: Validate

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python3 -m unittest discover -s tests -v
      - run: scripts/validate --format json
```

- [ ] **Step 4: Run complete local verification**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

Run: `scripts/validate --format json`

Expected: `"ok": true`, zero errors, and zero unreviewed warnings.

Run: `git diff --check`.

Expected: no output and exit status 0.

- [ ] **Step 5: Commit and push CI**

```bash
git add .github/workflows/validate.yml tests/test_repository_contract.py
git commit -m "ci: validate skill template"
git push origin main
```

- [ ] **Step 6: Confirm remote checks pass**

Run: `gh run list --repo allenday/agent-skills-template --limit 1 --json databaseId,status,conclusion,headSha`.

If the run is still active, wait with `gh run watch <databaseId> --repo allenday/agent-skills-template --exit-status`.

Expected: conclusion `success` for the pushed commit.

- [ ] **Step 7: Mark the repository as a native GitHub template**

Run:

```bash
gh api --method PATCH repos/allenday/agent-skills-template -f is_template=true
```

Then verify:

```bash
gh repo view allenday/agent-skills-template --json isTemplate,defaultBranchRef,url
```

Expected: `"isTemplate": true` and default branch `main`.

- [ ] **Step 8: Perform final clean-state verification**

Run:

```bash
git status --short
python3 -m unittest discover -s tests -v
scripts/validate --format json
```

Expected: empty git status, all tests pass, and validator reports zero errors.
