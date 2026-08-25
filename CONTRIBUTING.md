# Contributing

## Skill contract

- Use kebab-case names. A skill directory, its `SKILL.md` frontmatter `name`, and its eval filename must all use the same name.
- Provide at least three positive trigger prompts and two negative trigger prompts in `evals/<name>.json`.
- Keep runtime dependencies self-contained within `skills/<name>/`; an extracted skill must not require repository-root files or sibling skills.
- Record any imported material in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), including its immutable source revision, license, and modifications.

## Validation

Before submitting a change, run:

```sh
scripts/validate
python3 -m unittest discover -s tests -v
```

Keep contributions focused, preserve existing user and third-party work, and include tests whenever a repository contract changes.
