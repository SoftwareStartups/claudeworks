---
name: cleanup-commits
description: Interactive command to cleanup commits by grouping and squashing them using rebase
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
  - TodoWrite
---

# Cleanup Commits Command

This command guides you through cleaning up commits in the current branch by grouping them logically and using interactive rebase to squash/fixup.

## Workflow

### Step 1: Fetch and Show Recent Commits

First, fetch the latest from origin and show recent commits for selection:

```bash
git fetch origin
git log --oneline -20
```

### Step 2: Present Commit Selection

Use `AskUserQuestion` to let the user select a starting commit. Present the commits as options with their hash and message. The selected commit will be the starting point for the rebase (commits from this point forward will be cleaned up).

Example question format:

- Header: "Start from"
- Question: "Select the starting commit for cleanup (all commits after this will be grouped and squashed):"
- Options: List 4-5 recent commits with format "abc1234 - commit message"

### Step 3: Analyze and Group Commits

After user selects the starting commit:

1. Get all commits from the starting point to HEAD:

   ```bash
   git log --oneline <starting-commit>..HEAD
   ```

2. Analyze the commits and group them logically by:

   - Related file changes (use `git show --stat <commit>` to see files)
   - Feature area (frontend, backend, tests, docs, config)
   - Semantic meaning (feat, fix, refactor, chore)

3. Propose logical groupings with suggested final commit messages.

### Step 4: Present Grouping for Review

Use `AskUserQuestion` to show the proposed groupings and let the user:

- Approve the groupings
- Request modifications
- See alternative grouping suggestions

Format the groupings clearly:

```text
Group 1: "feat: add user authentication"
  - abc1234 - add login form
  - def5678 - add auth service
  - ghi9012 - add session handling

Group 2: "fix: resolve navigation bugs"
  - jkl3456 - fix back button
  - mno7890 - fix menu collapse
```

### Step 5: Execute Rebase

Once the user approves the grouping:

1. Create a backup branch:

   ```bash
   git branch backup-before-cleanup
   ```

2. For each group, use fixup commits. Reset to the starting commit and recommit in groups:

   ```bash
   # Option A: Use --autosquash with fixup commits already in place
   GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash <starting-commit>~

   # Option B: If restructuring is needed, use soft reset and recommit
   git reset --soft <starting-commit>~
   # Then stage and commit files in logical groups
   ```

3. After restructuring commits, rebase onto origin/main:

   ```bash
   git rebase origin/main
   ```

4. Show the result:

   ```bash
   git log --oneline origin/main..HEAD
   ```

### Step 6: Final Review

Present the cleaned up commit history and ask user to confirm before any push:

- Show `git log --oneline` of the new commits
- Show `git diff origin/main..HEAD --stat` for a summary of changes
- Remind user they can reset with: `git reset --hard backup-before-cleanup`

## Error Handling

- If rebase conflicts occur, guide the user through resolution
- Always create a backup branch before rebasing
- If anything goes wrong: `git rebase --abort` and `git checkout backup-before-cleanup`

## Safety Checks

Before starting:

- Verify working directory is clean: `git status --porcelain`
- Ensure we're not on main/master branch
- Check if there are unpushed commits to preserve
