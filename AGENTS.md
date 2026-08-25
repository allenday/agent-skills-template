# Agent guidance

Before editing a skill, read its `SKILL.md` completely and inspect the local files it references.

- Keep runtime dependencies inside the target skill directory so the skill remains portable.
- Use `scripts/new-skill` to create new skills.
- Run `scripts/validate` and `python3 -m unittest discover -s tests -v` before completion.
- Preserve user work and third-party work; do not overwrite or remove it without explicit scope.
- Do not add MCP servers, hooks, UI, or external dependencies unless the task explicitly requests them.
