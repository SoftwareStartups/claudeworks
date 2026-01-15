---
name: git-rebase
description: Use when committing changes to code already committed in the current branch, or when preparing commits for PR review. Creates clean, reviewable commits using --fixup and interactive rebase.
---

# Git Rebase for Clean Commits

## Commit Strategy

| Scenario | Action |
|----------|--------|
| New feature/logical change | `git commit -m "feat: add X"` |
| Editing code from previous commit in this branch | `git commit --fixup=<commit-hash>` |

**Finding the right commit to fixup:**

```bash
git log --oneline                    # List commits with hashes
git show -s --format=%s <commit>     # View commit message to confirm
```

## Squash Workflow

**1. Sync with remote:**
```bash
git fetch
git status
# If behind: git pull
```

**2. Squash fixups into clean commits:**
```bash
git rebase -i --autosquash <first-commit-in-branch>~
```

**3. Rebase onto main:**
```bash
git fetch
git rebase -i origin/main
```

Resolve conflicts: `git add <files>` then `git rebase --continue`.
If stuck: `git rebase --abort`.

## Verify Before Push

```bash
git diff @{u}..HEAD
```

Should show only your intended changes. If wrong:
```bash
git reset --hard @{u}  # Reset to remote, start over
```

If correct:
```bash
git push -f
```

## Merge to Main

After PR approval, merge with a merge commit to preserve branch history:

```bash
git checkout main
git pull
git merge --no-ff <your-branch-name>
git push
```

The PR should appear as merged. History in main must be linear (no branched paths) with all distinct commits plus the merge commit visible.
