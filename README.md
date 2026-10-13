# ClaudeWorks

A Claude Code plugin marketplace with skills for Python development, git workflows and architecture decision records.

## Installation

First, add the marketplace (from terminal or within a Claude Code session):

```bash
claude plugin marketplace add SoftwareStartups/claudeworks   # CLI
/plugin marketplace add SoftwareStartups/claudeworks         # in-session
```

This creates the `claudeworks` plugin group. Then install plugins from it:

```bash
# CLI
claude plugin install "python-tools@claudeworks"
claude plugin install "workflow@claudeworks"
claude plugin install "adr@claudeworks"

# Or in-session
/plugin install python-tools@claudeworks
/plugin install workflow@claudeworks
/plugin install adr@claudeworks
```

Or browse available plugins interactively with `/plugin > Discover`.

See [Claude Code plugin docs](https://code.claude.com/docs/en/plugins) for more details.

## Plugins

### python-tools

Python development tools for Claude Code workflows.

- **update-deps** - Bump pyproject.toml dependencies to the latest stable PyPI releases (uv projects and workspaces), then sync and run the tests

### workflow

Git workflow tools for clean commits and rebasing.

- **git-rebase** - Create clean, reviewable commits using `--fixup` and autosquash rebase
- **cleanup-commits** - `/cleanup-commits`, groups and squashes the branch's commits before a PR (manual invocation only)

### adr

Architecture decision records in MADR format, with a few stricter conventions.

- **adr** - Write, review, number and supersede ADRs. Claude writes the record, but the decision and its reasons come from people. Bundles a template and a stdlib-only `check_adr.py` that checks sections, metadata, file names, duplicate numbers and `superseded by` links
- **adr-init** - `/adr-init`, sets up a repo for ADRs: folder, checker in CI, PR checklist and a CLAUDE.md note (manual invocation only)

## Development

For contributing to this repository:

```bash
task install    # Install dependencies
task check      # Run lint, typecheck and plugin manifest validation
task test       # Run tests
task all        # Run all checks and tests
```

Bump `version` in a plugin's `.claude-plugin/plugin.json` when changing it. Installed copies only update when the version changes.

## License

MIT
