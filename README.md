# Agent Skills Template

A forkable template for portable Agent Skills. The repository root is a skills-only plugin, and every directory in `skills/` is designed to be copied and installed independently.

## Create your repository

1. On GitHub, select **Use this template** to generate a new repository.
2. Update the names and display copy in `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`.
3. Remove `example-skill` and `evals/example-skill.json`, or use them as the pattern for your first skill.
4. Create a skill with `scripts/new-skill <name>`.
5. Replace the generated skill description and eval prompts with domain-specific triggers.
6. Validate locally:

   ```sh
   scripts/validate
   python3 -m unittest discover -s tests -v
   ```

7. Add the repository as a Codex plugin marketplace. Choose the source form that matches how Codex can read the repository:

   ```sh
   # GitHub shorthand (recommended for GitHub repositories)
   codex plugin marketplace add OWNER/REPOSITORY --ref main

   # Explicit HTTPS Git URL
   codex plugin marketplace add https://github.com/OWNER/REPOSITORY.git --ref main

   # Explicit SSH Git URL
   codex plugin marketplace add git@github.com:OWNER/REPOSITORY.git --ref main

   # A repository already available on this machine
   codex plugin marketplace add /absolute/path/to/REPOSITORY

   ```

   For a private repository, use a source form whose GitHub credentials are authorized to read it. The shorthand is GitHub-specific; use an HTTPS or SSH Git URL for another Git host.

8. Confirm that Codex can see the marketplace, then install its plugin from `/plugins` in a fresh Codex session:

   ```sh
   codex plugin marketplace list
   ```

Generated repositories have independent histories and do not receive template updates automatically. Bring over later improvements deliberately, after reviewing them for your repository.

## Portable skills

Each skill is independently extractable: copy one complete `skills/<name>/` directory to take that skill and every runtime dependency it needs. Keep references, scripts, and other runtime files inside the skill directory; root-level scripts are repository maintenance tools only.

## Repository commands

- `scripts/new-skill <name>` creates a portable skill directory and its eval fixture.
- `scripts/validate` checks the plugin, marketplace, skills, common local references, and eval contract without installing dependencies. It is not a full Markdown parser; keep every runtime file inside its owning skill directory.
- `python3 -m unittest discover -s tests -v` runs the repository test suite.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution contract and [AGENTS.md](AGENTS.md) for agent guidance.
