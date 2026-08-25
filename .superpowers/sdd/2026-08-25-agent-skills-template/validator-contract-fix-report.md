# Validator contract fix report

Base SHA: `665b8caec826b250f6fa869026a5222858676c03`

## RED evidence

Before implementation, this focused command failed with four expected regressions:

```sh
python3 -m unittest \
  tests.test_validate.ValidatorTests.test_escaping_local_image_reference_fails \
  tests.test_validate.ValidatorTests.test_symlinked_skills_root_is_rejected_before_walking \
  tests.test_validate.ValidatorTests.test_symlinked_nested_asset_named_skill_md_is_rejected \
  tests.test_validate.ValidatorTests.test_manifest_and_marketplace_required_metadata_fail_with_stable_codes -v
```

The failures showed that image links were skipped, `skills/` was walked through a
symlink, nested `SKILL.md` symlinks were exempt, and the stricter metadata and
policy diagnostics were absent.

## GREEN evidence

The same focused command passed after the implementation. The following full
verification also passed:

```sh
python3 -m unittest discover -s tests -v
scripts/validate --format json
git diff --check
```

Results: `24` tests passed; `scripts/validate --format json` returned
`{"ok": true, "summary": {"errors": 0, "warnings": 0}}`; and the diff
check returned no output.

## Native validator

Attempted exactly as requested:

```sh
python3 /Users/allenday/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

It did not reach validation because the installed `python3` has no `yaml`
module (`ModuleNotFoundError: No module named 'yaml'`). Installing PyYAML even
into a temporary directory was rejected because it would download a new
third-party package; no repository dependency was added.
