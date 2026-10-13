---
name: adr-init
description: Set up a repository for architecture decision records, with the ADR folder, a checker in CI, a pull request checklist and a CLAUDE.md note.
disable-model-invocation: true
---

# Set up ADRs in this repository

Prepares the current repository for the `adr` skill. Check each step against what already exists,
and change only what is missing. Show the user the planned changes before writing them.

1. **Branch.** If on the default branch, create `chore/setup-adrs`.

2. **Folder.** Use the existing ADR folder if there is one (`docs/decisions/`, `docs/adr/`,
   `doc/adr/`, `adr/`, `decisions/`), otherwise create `docs/decisions/` with a one-line
   `README.md`, so Git tracks the folder and CI finds it before the first ADR. If it already holds
   ADRs in another format, stop and ask the user whether to keep that format. The checker only
   fits the `adr` skill's format.

3. **Checker.** Copy `${CLAUDE_SKILL_DIR}/../adr/check_adr.py` to `scripts/check_adr.py`, or to
   wherever the repo keeps scripts. It needs only Python 3.12, no packages. Run it on the folder
   to confirm it passes. If the repo has a task runner (Taskfile, Makefile, `package.json`
   scripts, justfile), add an `adr` target that runs it.

4. **CI.** For GitHub Actions, add `.github/workflows/adr.yml`, adjusting paths and branch:

   ```yaml
   name: ADRs

   on:
     pull_request:
     push:
       branches: [main]

   permissions:
     contents: read

   jobs:
     check:
       runs-on: ubuntu-24.04
       steps:
         - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
         - run: python3 scripts/check_adr.py docs/decisions
   ```

   The checker runs in well under a second, so the workflow has no path filter. A path filter
   would leave a required check pending forever on pull requests that touch no ADR. For another
   CI system, add the same command as a step in the existing pipeline.

5. **Pull request checklist.** Add this section to `.github/pull_request_template.md`, creating
   the file if needed:

   ```markdown
   ## ADR checks

   _Delete this section if the pull request adds or changes no ADR._

   - [ ] After one read, a reader can say what was chosen, and why.
   - [ ] The ADR says what happens next: the follow-up action, or when to revisit.
   - [ ] Each considered option has a Pros and Cons block with points a reader can weigh.
   - [ ] Validation gives invariants that someone can check later, not intentions.
   ```

6. **CLAUDE.md.** Add a short section to the project's CLAUDE.md, creating it if needed, with
   the folder and script paths from steps 2 and 3:

   ```markdown
   ## Architecture decisions

   ADRs live in `docs/decisions/`. Use the `adr` skill for any ADR work. An agent writes the
   ADR, but people make the decision, and a person approves each ADR before it is merged.
   `python3 scripts/check_adr.py docs/decisions` checks the format.
   ```

7. **First ADR.** Offer to write `0001-record-architecture-decisions.md` with the `adr` skill,
   recording the decision to keep ADRs in this repository. Write it only if the user agrees,
   and only with reasons the user gives.

8. **Report.** List the files created or changed. Note that the copied checker does not update
   with the plugin, so a newer version must be copied again.
