---
name: adr
description: Write, review, number or supersede an architecture decision record (ADR) in MADR format. Use when creating or editing an ADR, recording an architecture decision, reviewing an ADR, changing its status, or when asked what an ADR must contain.
---

# Architecture Decision Records

An ADR is one Markdown file that records one decision, its context and its consequences.
The format is MADR (Markdown Any Decision Records) with a few stricter conventions, listed below.
`${CLAUDE_SKILL_DIR}/check_adr.py` enforces them.

## The human makes the decision

Write the words, the format and the file. Do not choose between the options, and do not invent
a reason, a driver or a consequence the user did not give you. If the decision, the options or
the reasons are missing, ask. Before opening a pull request, tell the user that a person must
read and approve the ADR, and wait for their answer.

## Where ADRs live

Use the repo's existing ADR folder. Look for `docs/decisions/`, `docs/adr/`, `doc/adr/`,
`adr/` or `decisions/`, and check the project's CLAUDE.md. If there is none, use `docs/decisions/`.

If the folder already holds ADRs in another format (Nygard, adr-tools, MADR with YAML front
matter), follow that format and skip the checker. Do not convert existing ADRs unless asked.

## File name and number

`NNNN-title-with-dashes.md`: a four-digit number, then the lowercase title with dashes.

- The number is the identity. Text refers to it as `ADR-NNNN`. It does not change when the
  title changes, and a removed ADR's number is never reused.
- Next number: one more than the largest in the folder, or `0001` in an empty folder.
  `ls <folder> | grep -oE '^[0-9]{4}' | sort -n | tail -1`. If `git log` shows that a
  higher-numbered ADR was removed, continue after that one.
- Two branches can take the same number. The checker reports the duplicate, and the later
  branch renumbers before merging.

## Format

Start from `${CLAUDE_SKILL_DIR}/template.md`. The file has one level-1 heading (the title), then
the metadata list, then the sections. Write every heading in `#` style, starting at column 0.
The checker does not recognise underlined (setext) headings.

Metadata is a bullet list in the body, not YAML front matter. Use `*` bullets, one `Key: value`
per line, in this order: `Status`, `Date`, `Decision-makers`, `Consulted`, `Informed`. Only
`Status` and `Date` are required. `Date` is `YYYY-MM-DD`, the date of the last change to the
decision, not of the first draft.

Sections, in this order. Do not add sections between the mandatory ones.

| Section | Required | Contents |
| --- | --- | --- |
| `## TL;DR` | No | 3 or 4 sentences: the decision, the reason, what changes. Must be first. |
| `## Context and Problem Statement` | Yes | 2 or 3 sentences on the situation, ending with the question the ADR answers. |
| `## Decision Drivers` | No | The forces that control the choice, as a list. |
| `## Considered Options` | Yes | `Option N - Name` per bullet, in the same order as Pros and Cons. |
| `## Decision Outcome` | Yes | Starts with `Chosen option: "Option N - Name", because <reason>`. |
| `### Consequences` | Yes | What becomes true afterwards, under `#### Good`, `#### Bad`, `#### Neutral`. |
| `### Validation` | Yes | Invariants that stay true while the implementation follows the decision. |
| `## Pros and Cons of the Options` | Yes | One `### Option N - Name` per option, with Good/Bad/Neutral subsections. |
| `## More Information` | No | Links to related ADRs, issues and pull requests. |
| `## Additional context for AI agents` | No | Long-form detail for agents. Must be last. |

Where this differs from stock MADR:

- **Good/Bad/Neutral are level-4 headings**, not a word on each bullet. Write
  `#### Good` then `* One review process for code and decisions.`, never `* Good, because ...`.
  No other level-4 heading names are allowed under Consequences or an option.
- **Option headings** are exactly `Option N - Name`, with a plain hyphen.
- **Validation replaces Confirmation.** Give the invariant ("CI rejects an ADR without a
  Status line"), not the method that checks it. Methods change more often than decisions.
- **TL;DR** is a shorter form of the record, not a second record. It states nothing the other
  sections do not.
- **Additional context for AI agents** holds the detail that slows a human reader down:
  measurements, full lists, the data behind each driver, history. It adds detail only. It never
  holds a decision or contradicts another section, and a reader who skips it still gets the
  decision and the reason.

Keep the Decision Outcome short. Detail belongs in Pros and Cons. It may end with the
conditions for revisiting the decision, as a list after `Revisit this decision if any of these
becomes true:`.

## Status and superseding

`Status` is one of `proposed`, `accepted`, `rejected`, `deprecated`, or
`superseded by [ADR-NNNN](NNNN-title.md)`.

Never delete an accepted ADR or rewrite its decision. Write a new ADR, and set the old one's
status to `superseded by` with a link to the new one. Link other ADRs with relative links, the
number as the link text: `[ADR-0007](0007-use-postgres.md)`.

## Keep implementation out

An ADR chooses between options and records why. It is not a manual or a setup guide.

The test: would this sentence change if a different option were chosen? If not, it is
implementation and belongs in the code, the README or a skill.

Leave out setup and migration steps, CLI flags, file paths, environment variables,
configuration blocks, version pins, install commands, and how internal helpers work. Leave out
an implementation plan unless its phases are part of the agreement.

Keep the shape of the outcome when that shape is the decision, constraints that include or
exclude an option, costs, limits and risks the reader must weigh (a pre-1.0 dependency, a
per-seat price, an unstable API), and at most one short example where the subject is otherwise
hard to see. In place of mechanics, add a short Implementation paragraph at the end of the
Decision Outcome that names where they live: the skill, README or package (a link or path to it
is fine there).

## Writing

Plain, direct English. One sentence per line, at most 25 words each (the checker warns above
that). Use the same term for the same thing throughout. State conditions in words, never through
formatting or color. Keep code, identifiers, product names and quoted text exactly as they are.
If the project's CLAUDE.md sets a stricter register, follow it.

## Workflow

1. Work on a branch, one ADR per branch and pull request.
2. Get the next free number and create the file from the template with `Status: proposed`.
3. Fill each section from what the user gave you. Ask for anything missing. Delete unused
   optional sections and the template comments.
4. Run `uv run ${CLAUDE_SKILL_DIR}/check_adr.py <folder>` (or `python3`), and fix every error.
   Shorten sentences it warns about. If the repo has its own copy of the checker (see
   `/adr-init`), run that one.
5. Reread the ADR as a reviewer. The checker cannot see a wrong but well-formed claim.
6. Ask the user to read the ADR before you open the pull request. The team decides in the
   pull request review.
7. When the reviewers approve, set `Status: accepted` (or `rejected`) and `Date` to the approval
   date, then merge. A rejected ADR is merged too, so the record shows what was considered.

## Reviewing an ADR

Run the checker, then check what it cannot:

- After one read, can a reader say what was chosen and why?
- Does it say what happens next: the follow-up action, or when to revisit?
- Does every considered option have a Pros and Cons block, with points a reader can weigh?
- Does Validation give invariants that someone can check later, not intentions?
- Is any of it implementation detail that fails the test above?
- Is every date real, and does every claim match the sources?
