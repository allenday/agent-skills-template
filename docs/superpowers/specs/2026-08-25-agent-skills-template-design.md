# Agent skills template design

## Objective

Create a public, native GitHub template repository that helps people maintain a collection of independently extractable Agent Skills as one installable Codex plugin.

GitHub's native template mechanism will create derived repositories with independent histories. The public repository will be marked as a template after its first validated commit is pushed.

## Template structure

```text
agent-skills-template/
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── .codex-plugin/
│   └── plugin.json
├── .github/
│   └── workflows/
│       └── validate.yml
├── skills/
│   └── example-skill/
│       ├── SKILL.md
│       └── references/
│           └── example-reference.md
├── evals/
│   └── example-skill.json
├── scripts/
│   ├── new-skill
│   └── validate
├── AGENTS.md
├── CONTRIBUTING.md
├── README.md
├── LICENSE
└── THIRD_PARTY_NOTICES.md
```

The example skill is intentionally small and removable. It demonstrates frontmatter, progressive disclosure, a local reference, and trigger fixtures without imposing a domain workflow on derived repositories.

## Portability rules

Every directory under `skills/` must remain independently installable:

- Runtime instructions, references, scripts, assets, and templates stay inside the owning skill.
- Skills must not depend on repository-root files or sibling skills to function.
- Cross-skill references may mention another skill by name but must degrade gracefully when that skill is absent.
- Root scripts and evals maintain the monorepo; extracted skills do not require them.
- Imported skills record their source, revision, license, and modifications in `THIRD_PARTY_NOTICES.md`.

## Validation and authoring experience

The repository will provide dependency-free commands:

- `scripts/new-skill <name>` scaffolds a skill and trigger-eval fixture.
- `scripts/validate` runs the same checks locally and in GitHub Actions.

Validation will check:

- Plugin manifest, repo marketplace structure, and skill discovery.
- Required `SKILL.md` frontmatter.
- Skill name and directory consistency.
- Nonempty, bounded, trigger-oriented descriptions.
- Broken relative references.
- References that escape the owning skill.
- Oversized `SKILL.md` files as warnings.
- Positive and negative trigger fixtures for every skill.
- Orphan evals and unintended skills.

The validator will report all findings in one run, use stable error codes, and exit nonzero on failures. It will not install dependencies or mutate repository content.

## Codex plugin packaging

The template is a skills-only plugin. `.codex-plugin/plugin.json` points to the root `skills/` directory, and `.agents/plugins/marketplace.json` exposes the root plugin as a native repository marketplace. Derived repositories can be installed as a complete plugin while retaining the option to copy or publish individual skill directories.

The initial version will not include an MCP server, hooks, UI, or external tool dependencies. Those capabilities can be added later without changing the skill layout.

## Licensing

Use Apache License 2.0 for the template.

- Derived repositories choose their own compatible license.
- Imported material must retain its required copyright, license, attribution, and modification notices.
- Record imported source URLs and revisions in `THIRD_PARTY_NOTICES.md`.
- Prefer paraphrase and attribution over copying external guidance wholesale.

## Verification

Before the template is marked ready:

1. Run the validator locally.
2. Exercise `scripts/new-skill` in a temporary directory.
3. Confirm GitHub Actions passes on the pushed default branch.
4. Confirm Codex recognizes the example skill through the plugin manifest.
5. Mark the GitHub repository as a native template.

## Out of scope

- Publishing to the universal public plugin directory.
- An MCP server or remote service.
- Synchronizing future upstream changes automatically.
