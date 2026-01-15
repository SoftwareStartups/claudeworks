# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ClaudeWorks - A Claude plugin marketplace for Python tools. Contains reusable skills and utilities for Claude Code workflows.

## Commands

```bash
make install     # Install python dependencies
make format      # Format code with ruff
make lint        # Lint code with ruff
make lint-fix    # Auto-fix linting issues
make typecheck   # Type check with pyright
make check       # Run lint + typecheck
make test        # Run tests
make test-cov    # Run tests with coverage
make clean       # Remove build artifacts and caches
make all         # Run all checks and tests
```

## Code Style

- Python 3.12+, strict pyright typing
- Ruff: line-length 100, rules E/F/I/N/W/UP
- Use `uv` for dependency management

## Structure

- `plugins/` - Claude Code plugins (skills, commands)
  - `python-tools/` - Python development tools (update-deps)
  - `workflow/` - Git workflow tools (git-rebase)
- `shared/` - Shared utilities across plugins

## Plugin Format

Skills live in `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` with YAML frontmatter:
```yaml
---
name: skill-name
description: When to use this skill
context: fork # optional for executing the skill in a sub agent
---
```
