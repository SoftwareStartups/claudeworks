# ClaudeWorks

A Claude Code plugin marketplace for Python tools. Contains reusable skills and utilities for Claude Code workflows.

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

# Or in-session
/plugin install python-tools@claudeworks
/plugin install workflow@claudeworks
```

Or browse available plugins interactively with `/plugin > Discover`.

See [Claude Code plugin docs](https://code.claude.com/docs/en/plugins) for more details.

## Plugins

### python-tools

Python development tools for Claude Code workflows.

- **update-deps** - Update Python dependencies to latest stable versions in uv workspaces

### workflow

Git workflow tools for clean commits and rebasing.

- **git-rebase** - Create clean, reviewable commits using --fixup and interactive rebase
  - `/cleanup-commits` - Interactive command to group and squash commits before PR

## Development

For contributing to this repository:

```bash
make install    # Install dependencies
make check      # Run lint + typecheck
make test       # Run tests
make all        # Run all checks and tests
```

## License

MIT
