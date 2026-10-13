# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ClaudeWorks - A Claude Code plugin marketplace with skills for Python development and git workflows.

## Commands

```bash
task install     # Install python dependencies
task format      # Format code with ruff
task lint        # Lint code with ruff
task lint-fix    # Auto-fix linting issues
task typecheck   # Type check with pyright
task validate    # Validate marketplace and plugin manifests
task check       # Run lint + typecheck + validate
task test        # Run tests
task test-cov    # Run tests with coverage
task clean       # Remove build artifacts and caches
task all         # Run all checks and tests
```

## Code Style

- Python 3.12+, strict pyright typing
- Ruff: line-length 100, rules E/F/I/N/W/UP
- Use `uv` for dependency management

## Structure

- `plugins/` - Claude Code plugins (skills)
  - `python-tools/` - Python development tools (update-deps, with bundled `update_deps.py`)
  - `workflow/` - Git workflow tools (git-rebase, cleanup-commits)
- `tests/` - Tests for bundled scripts (script dirs are on the pytest/pyright path)

## Plugin Format

Skills live in `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` with YAML frontmatter:
```yaml
---
name: skill-name
description: When to use this skill
context: fork # optional for executing the skill in a sub agent
disable-model-invocation: true # optional, only runs via /skill-name
---
```

- Prefer `skills/` over `commands/` for new user-invocable entries.
- Bundled scripts sit next to SKILL.md and are referenced as `${CLAUDE_SKILL_DIR}/script.py`.
  Make them self-contained with PEP 723 inline dependencies so `uv run` works anywhere.
- Plugins are copied into a cache on install, so they cannot import code from outside their own directory.
- Bump `version` in the plugin's `plugin.json` on every change, or users keep the old copy.
