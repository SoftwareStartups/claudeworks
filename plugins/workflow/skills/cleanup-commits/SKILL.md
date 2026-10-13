---
name: cleanup-commits
description: Group and squash the commits on the current branch into a few logical commits before opening a PR.
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

# Cleanup Commits

Rewrite the commits on the current branch into logical groups. The final tree must be
byte-identical to the starting tree; only the history changes.

## Step 1: Safety checks

Stop and tell the user if any check fails:

- Working tree is clean: `git status --porcelain` is empty
- Not on the default branch (`main`/`master`)
- No rebase or merge in progress

## Step 2: Choose the base

```bash
git fetch origin
git merge-base HEAD origin/main     # default base (use origin/master if that is the default)
git log --oneline <base>..HEAD
```

Use `AskUserQuestion` to confirm the base. Offer the merge-base (recommended) and a few recent
commits as `abc1234 - message` options. Every commit after the base will be rewritten.

## Step 3: Propose groups

For each commit in `<base>..HEAD`, inspect `git show --stat <commit>`. Group by feature area and
intent (feat, fix, refactor, docs, chore), and write a conventional commit message per group.

Show the plan with `AskUserQuestion` and let the user approve, adjust, or ask for alternatives:

```text
Group 1: "feat: add user authentication"
  - abc1234 add login form
  - def5678 add auth service

Group 2: "fix: resolve navigation bugs"
  - 1234abc fix back button
```

## Step 4: Back up

```bash
BACKUP="backup/$(git branch --show-current)-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP"
```

## Step 5: Rewrite

Use Phase A when each group's commits can be squashed after moving them together without
conflicts. Fall back to Phase B if the rebase conflicts or a single commit belongs to several groups.

### Phase A: scripted rebase (preferred)

Write the todo list to a temp file: groups in the desired order, oldest commit first within each
group, and an `exec` line after each group that sets its message.

```text
pick abc1234 add login form
fixup def5678 add auth service
exec git commit --amend -q -m "feat: add user authentication"
pick 1234abc fix back button
exec git commit --amend -q -m "fix: resolve navigation bugs"
```

Run the rebase with the file as the sequence editor, so no editor opens:

```bash
GIT_SEQUENCE_EDITOR="cp /path/to/todo" git rebase -i <base>
```

On conflicts run `git rebase --abort` and switch to Phase B.

### Phase B: reset and recommit

```bash
git reset <base>        # moves the branch to <base>, keeps all changes in the working tree
```

For each group, stage its files and commit:

```bash
git add <files-for-group>
git commit -m "<group message>"
```

If one file has changes for several groups, commit it with the group it fits best and tell the
user. Do not use interactive `git add -p`.

## Step 6: Verify

```bash
git diff "$BACKUP" HEAD --stat   # must print nothing
git status --porcelain           # must print nothing
git log --oneline <base>..HEAD
```

If either diff is non-empty, restore with `git reset --hard "$BACKUP"` and report the problem.

## Step 7: Finish

Show the new history and `git diff origin/main...HEAD --stat`. Do not push. Tell the user:

- To publish: `git push --force-with-lease`
- To undo: `git reset --hard <backup-branch>`
- To drop the backup when happy: `git branch -D <backup-branch>`
