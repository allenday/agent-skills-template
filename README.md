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

   Continue with [Verify and use the installed plugin](#verify-and-use-the-installed-plugin) before relying on the skills in a new session.

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

## Verify and use the installed plugin

Verify the plugin's state on the same host where you installed it:

```sh
codex plugin list --marketplace YOUR-PLUGIN
```

`YOUR-PLUGIN@YOUR-PLUGIN` must show `installed, enabled`. If it is disabled, enable it from the interactive plugin browser:

```text
codex
/plugins
```

Select the plugin and press Space, then exit and start a new `codex` session. A newly installed or enabled plugin is available only to new sessions.

Ask for a matching task and Codex can select the relevant skill automatically. To select a skill deliberately, use `/skills` or type its `$` invocation in a Codex session:

```text
$YOUR-SKILL
```

If the plugin is enabled but a skill is not in the initial list, use `/skills` or its `$` invocation. Codex limits the initial skill list when many skills are installed; that is a discovery limit, not proof that installation failed.

## Make a plugin available in ChatGPT

Git marketplace installation is local to the Codex host where you ran the commands. Installing the plugin on one remote host does not sync the plugin into ChatGPT on your desktop, web, or another host.

To use a plugin natively in ChatGPT, open **Plugins** in the intended ChatGPT account or workspace and install it from the **Plugins Directory**. To make your own plugin available there, follow the official plugin packaging, testing, and publishing flow; a local Git marketplace is useful for host-local development and testing, but does not itself create a Plugins Directory listing.

Availability depends on the account, workspace, role, supported surface, and rollout. After installation in ChatGPT, start a new chat and invoke the plugin or bundled skill from the prompt controls.

See [using plugins](https://learn.chatgpt.com/docs/plugins), [building skills](https://learn.chatgpt.com/docs/build-skills), and [testing/publishing plugins](https://developers.openai.com/plugins/deploy/connect-chatgpt) for the current product flow.

Generated repositories have independent histories and do not receive template updates automatically. Bring over later improvements deliberately, after reviewing them for your repository.

## Portable skills

Each skill is independently extractable: copy one complete `skills/<name>/` directory to take that skill and every runtime dependency it needs. Keep references, scripts, and other runtime files inside the skill directory; root-level scripts are repository maintenance tools only.

## Repository commands

- `scripts/new-skill <name>` creates a portable skill directory and its eval fixture.
- `scripts/validate` checks the plugin, marketplace, skills, common local references, and eval contract without installing dependencies. It is not a full Markdown parser; keep every runtime file inside its owning skill directory.
- `python3 -m unittest discover -s tests -v` runs the repository test suite.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution contract and [AGENTS.md](AGENTS.md) for agent guidance.
