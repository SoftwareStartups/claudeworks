---
name: update-deps
description: Update Python dependencies in pyproject.toml files (single project or uv workspace) to their latest stable versions, then sync and verify.
context: fork
---

# Update Dependencies

`${CLAUDE_SKILL_DIR}/update_deps.py` bumps version specs in `[project.dependencies]`,
`[project.optional-dependencies]` and `[dependency-groups]` to the latest stable PyPI release.
It edits in place and keeps formatting and comments.

## Workflow

1. **Check the tree is clean**: `git status --porcelain` must be empty, so the update is its own commit.
2. **Find pyproject.toml files**: Glob `**/pyproject.toml`, excluding `.venv/` and other virtualenvs.
3. **Dry run**: `uv run ${CLAUDE_SKILL_DIR}/update_deps.py <files...>` and review the listed changes.
4. **Apply**: rerun with `--update`.
5. **Sync**: `uv lock --upgrade && uv sync --all-groups`. On a resolution conflict, lower the
   offending spec to the newest version that resolves, and rerun.
6. **Verify**: run the project's checks and tests (e.g. `task check test`, `make check test`,
   or `uv run pytest`). Fix breakage caused by the upgrade, or revert that single package and report it.
7. **Commit**: `chore: update dependencies to latest stable versions`

## What the script leaves alone

- Unversioned deps (`attrs`) and specs with only an upper bound (`foo<2`)
- Specs with extra clauses such as an upper bound (`foo>=1,<2`); bumping the lower bound could
  make them unsatisfiable. Report these so the user can decide.
- Pre-releases and yanked releases

It keeps the operator (`>=`, `==`, `~=`), extras and environment markers.
