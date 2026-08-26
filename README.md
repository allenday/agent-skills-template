# Agent Skills Template

A forkable template for portable Agent Skills. The repository root is a skills-only plugin, and every directory in `skills/` is designed to be copied and installed independently.

## Create your repository

1. On GitHub, select **Use this template** to generate a new repository.
2. Before you publish or install a generated repository, replace the template identity with your plugin name. Use lower-case hyphen-case, such as `acme-agent-skills`, and set the same value in all three places:

   - `.codex-plugin/plugin.json` → `name`
   - `.agents/plugins/marketplace.json` → top-level `name`
   - `.agents/plugins/marketplace.json` → `plugins[0].name`

   Also replace the display names and descriptions in those files. Do not install a generated repository while any of these identifiers remains `agent-skills-template`; otherwise Codex will install it under the template name.
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

8. Confirm that Codex can see the marketplace, then install the plugin. This example assumes you used the same identifier for the marketplace and plugin in step 2:

   ```sh
   codex plugin marketplace list
   codex plugin list --marketplace YOUR-PLUGIN
   codex plugin add YOUR-PLUGIN@YOUR-PLUGIN
   ```

   Start a fresh Codex session after installing the plugin so it can discover the skills.

   The GitHub marketplace installs the plugin only into the Codex environment where you ran the commands. It does not upload the plugin to ChatGPT or the ChatGPT Plugin Directory. In a new Codex session, ask for a task that matches a skill; Codex selects and applies matching skills automatically.

9. To remove the plugin later, remove the installed plugin first, then the marketplace source:

   ```sh
   codex plugin remove YOUR-PLUGIN@YOUR-PLUGIN
   codex plugin marketplace remove YOUR-PLUGIN
   ```

## Update a plugin in Codex

After a new version is available in the Git repository, refresh the configured marketplace, then reinstall the plugin from its refreshed snapshot:

```sh
codex plugin marketplace upgrade YOUR-PLUGIN
codex plugin add YOUR-PLUGIN@YOUR-PLUGIN
```

Start a new Codex session after the reinstall.

## Make a plugin available in ChatGPT

A private workspace plugin is enough; a public Plugin Directory listing is optional. To make a plugin available in ChatGPT web or desktop:

1. Confirm that the target workspace grants your role permission to use, share, or publish plugins.
2. Create or import the plugin into that ChatGPT workspace using its available provisioning flow. The current ChatGPT documentation does not describe a GitHub repository import path, so a repository marketplace alone cannot perform this step.
3. After the plugin exists as an owned workspace plugin, open `Plugins -> select the owned plugin -> ... -> Share plugin`.
4. Choose invite-only access, a workspace link, or workspace-directory visibility. Workspace-directory visibility stays within the workspace and is not a global public listing.

See [OpenAI's plugin sharing guide](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt-and-codex) for workspace permissions and sharing controls.

Generated repositories have independent histories and do not receive template updates automatically. Bring over later improvements deliberately, after reviewing them for your repository.

## Portable skills

Each skill is independently extractable: copy one complete `skills/<name>/` directory to take that skill and every runtime dependency it needs. Keep references, scripts, and other runtime files inside the skill directory; root-level scripts are repository maintenance tools only.

## Repository commands

- `scripts/new-skill <name>` creates a portable skill directory and its eval fixture.
- `scripts/validate` checks the plugin, marketplace, skills, common local references, and eval contract without installing dependencies. It is not a full Markdown parser; keep every runtime file inside its owning skill directory.
- `python3 -m unittest discover -s tests -v` runs the repository test suite.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution contract and [AGENTS.md](AGENTS.md) for agent guidance.
