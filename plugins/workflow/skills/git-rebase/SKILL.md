---
name: git-rebase
description: Use when committing changes to code already committed in the current branch, or when preparing commits for PR review. Creates clean, reviewable commits using --fixup and autosquash rebase.
---

# Git Rebase for Clean Commits

Rebase commands below run without opening an editor, so they work from Claude Code.

## Commit Strategy

| Scenario | Action |
|----------|--------|
| New feature/logical change | `git commit -m "feat: add X"` |
| Editing code from a previous commit in this branch | `git commit --fixup=<commit-hash>` |

**Finding the right commit to fixup:**

```bash
git log --oneline origin/main..HEAD   # Commits in this branch
git log --oneline -- <file>           # Commits that touched a file
```

## Squash Workflow

**1. Squash fixups into their targets:**
```bash
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash $(git merge-base HEAD origin/main)
```

**2. Rebase onto the latest main:**
```bash
git fetch origin
git rebase origin/main
```

On conflicts: fix the files, `git add <files>`, then `GIT_EDITOR=true git rebase --continue`.
If stuck: `git rebase --abort`.

## Verify Before Push

Compare against the remote branch to confirm only intended changes differ:

```bash
git range-diff @{u}...HEAD   # Commit-by-commit comparison with the pushed branch
git diff @{u} HEAD --stat    # Tree differences (also shows changes from main after a rebase)
```

If wrong, restore the pushed state: `git reset --hard @{u}`.

If correct:
```bash
git push --force-with-lease
```

## Reordering or Regrouping Commits

To squash or reorder arbitrary commits, write the todo list to a file and use it as the sequence
editor:

```bash
cat > /tmp/rebase-todo << 'EOF'
pick abc1234 First commit message
fixup def5678 Squash into first, discard message
pick ghi9012 Third commit message
EOF
GIT_SEQUENCE_EDITOR="cp /tmp/rebase-todo" git rebase -i <base>
```

| Command | Effect |
|---------|--------|
| `pick` | Keep commit as-is |
| `fixup` | Squash into previous, discard message |
| `squash` | Squash into previous, combine messages (opens an editor; avoid) |
| `exec <cmd>` | Run a shell command, e.g. `git commit --amend -q -m "new message"` |
| `drop` | Remove commit |

Reordering conflicts when a moved commit depends on changes from a commit it now precedes. Use the
`/cleanup-commits` skill in that case; it falls back to resetting and recommitting by group.

## Merging the PR

After approval, rebase the branch onto `origin/main` (Squash Workflow step 2) and push, then merge
with a merge commit. Main keeps a semi-linear history: each branch's distinct commits sit in a
straight line, closed by a merge commit.

```bash
git checkout main
git pull --ff-only
git merge --no-ff <branch>
git push
```

The PR then shows as merged.
