# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check the architecture decision records (ADRs) in a folder.

Each ADR is a MADR file named NNNN-title-with-dashes.md, with a metadata list, the mandatory
sections in order, Good/Bad/Neutral subsections and `Option N - Name` headings. The script also
checks what one file cannot show: duplicate numbers and the target of each `superseded by` link.
Prints one line per problem and exits 1 if any problem is an error. Warnings do not fail.
"""

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

SKIP_NAMES = {"README.md", "index.md"}
NUMBER_RE = re.compile(r"^(\d{4})-")
NAME_RE = re.compile(r"^\d{4}-[a-z0-9]+(-[a-z0-9]+)*\.md$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
STATUS_RE = re.compile(r"^\* Status: (.*?)\s*$")
DATE_RE = re.compile(r"^\* Date: (.*?)\s*$")
STATUS_VALUES = ("proposed", "accepted", "rejected", "deprecated")
SUPERSEDED_RE = re.compile(
    r"^superseded by \[ADR-(?P<id>\d{4})\]\((?P<target>(?P<number>\d{4})-[a-z0-9-]+\.md)\)$"
)
OPTION_RE = re.compile(r"^Option \d+ - \S")
PREFIX_RE = re.compile(r"^\s*[-*]\s+\**(Good|Bad|Neutral|Pros|Cons)\**[,:]")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
PLACEHOLDER_RE = re.compile(r"<[A-Z][^<>\n]*>")
BULLET_RE = re.compile(r"^[*+-]\s+(.*?)\s*$")
CHOSEN_RE = re.compile(r'^Chosen option: "([^"]+)", because \S')
DASH_METADATA_RE = re.compile(r"^[-+] (Status|Date):")
TLDR_RE = re.compile(r"^[^a-z]*t[^a-z]*l[^a-z]*d[^a-z]*r[^a-z]*$")
AGENT_RE = re.compile(r"^(additional )?(context|notes|information) for (an |the )?(ai )?agents?$")

MANDATORY = [
    (2, "Context and Problem Statement"),
    (2, "Considered Options"),
    (2, "Decision Outcome"),
    (3, "Consequences"),
    (3, "Validation"),
    (2, "Pros and Cons of the Options"),
]
CONSEQUENCES = "Consequences"
OPTIONS = "Pros and Cons of the Options"
POINT_NAMES = {"Good", "Bad", "Neutral"}
TLDR = "TL;DR"
AGENT_CONTEXT = "Additional context for AI agents"
# Optional sections with a fixed position: name, pattern for near misses, index in the sections.
FIXED_SECTIONS = ((TLDR, TLDR_RE, 0), (AGENT_CONTEXT, AGENT_RE, -1))
MAX_WORDS = 25


@dataclass
class Heading:
    line: int
    level: int
    text: str


@dataclass
class Problem:
    path: Path
    line: int
    message: str
    warning: bool = False

    def __str__(self) -> str:
        kind = "warning" if self.warning else "error"
        return f"{self.path}:{self.line}: {kind}: {self.message}"


def unfenced(lines: list[str]) -> list[tuple[int, str]]:
    """Return (line number, line) for each line outside a fenced code block."""
    result: list[tuple[int, str]] = []
    fence = ""
    for number, line in enumerate(lines, 1):
        if fence:
            # A closing fence uses the same character, at least as many times, and nothing else.
            if line.strip().startswith(fence) and not line.strip().strip(fence[0]):
                fence = ""
        elif m := FENCE_RE.match(line):
            fence = m[1]
        else:
            result.append((number, line))
    return result


def headings(lines: list[tuple[int, str]]) -> list[Heading]:
    found: list[Heading] = []
    for number, line in lines:
        if m := HEADING_RE.match(line):
            found.append(Heading(number, len(m[1]), re.sub(r"[*`]", "", m[2]).strip()))
    return found


def check_structure(hs: list[Heading]) -> list[tuple[int, str]]:
    errors: list[tuple[int, str]] = []

    titles = [h for h in hs if h.level == 1]
    if not hs or hs[0].level != 1:
        errors.append((hs[0].line if hs else 1, "start the ADR with a level-1 heading, the title"))
    for h in titles[1:]:
        errors.append((h.line, "an ADR has one level-1 heading, the title"))

    found = 0
    for h in hs:
        if found < len(MANDATORY) and (h.level, h.text) == MANDATORY[found]:
            found += 1
    if found < len(MANDATORY):
        level, text = MANDATORY[found]
        errors.append((1, f"missing or out of order: `{'#' * level} {text}`"))

    section: str | None = None
    for h in hs:
        if h.level <= 2:
            section = OPTIONS if h.text == OPTIONS else None
        elif h.level == 3:
            if h.text == CONSEQUENCES:
                section = CONSEQUENCES
            elif section == CONSEQUENCES:
                section = None
            elif section == OPTIONS and not OPTION_RE.match(h.text):
                errors.append((h.line, "write the option heading as `Option N - Name`"))
        elif h.level == 4 and section and h.text not in POINT_NAMES:
            errors.append((h.line, "name the subsection Good, Bad or Neutral"))

    sections = [h for h in hs if h.level == 2]
    for name, pattern, position in FIXED_SECTIONS:
        matches = [h for h in hs if pattern.match(h.text.lower())]
        for h in matches:
            if h.text != name or h.level != 2:
                errors.append((h.line, f"write the heading as `## {name}`"))
        for h in matches[1:]:
            errors.append((h.line, f"an ADR has one `## {name}` section"))
        if matches and sections and matches[0] is not sections[position]:
            where = "first" if position == 0 else "last"
            errors.append((matches[0].line, f"make `## {name}` the {where} section"))
    return errors


def section_body(
    lines: list[tuple[int, str]], hs: list[Heading], title: str
) -> tuple[Heading | None, list[tuple[int, str]]]:
    """Return the level-2 heading `title` and the lines up to the next heading."""
    for i, h in enumerate(hs):
        if h.level == 2 and h.text == title:
            end = hs[i + 1].line if i + 1 < len(hs) else sys.maxsize
            return h, [(n, line) for n, line in lines if h.line < n < end]
    return None, []


def check_options(lines: list[tuple[int, str]], hs: list[Heading]) -> list[tuple[int, str]]:
    errors: list[tuple[int, str]] = []
    options: list[str] = []
    in_options = False
    for h in hs:
        if h.level <= 2:
            in_options = h.text == OPTIONS
        elif h.level == 3 and in_options:
            options.append(h.text)

    heading, body = section_body(lines, hs, "Considered Options")
    listed = [re.sub(r"[*`]", "", m[1]).strip() for _, line in body if (m := BULLET_RE.match(line))]
    if heading and listed != options:
        errors.append(
            (
                heading.line,
                "list the same options, in the same order, as the `### Option N - Name` "
                "headings in Pros and Cons of the Options",
            )
        )

    heading, body = section_body(lines, hs, "Decision Outcome")
    if heading:
        first = next(((n, line) for n, line in body if line.strip()), (heading.line, ""))
        if not (m := CHOSEN_RE.match(first[1])):
            errors.append((first[0], 'start with `Chosen option: "Option N - Name", because ...`'))
        elif m[1] not in options:
            errors.append((first[0], f'"{m[1]}" is not one of the options in Pros and Cons'))
    return errors


def check_metadata(
    lines: list[tuple[int, str]], hs: list[Heading], name: str, names: set[str]
) -> list[tuple[int, str]]:
    errors: list[tuple[int, str]] = []
    # The metadata list sits between the title and the first section.
    end = next((h.line for h in hs if h.level == 2), sys.maxsize)
    lines = [(n, line) for n, line in lines if n < end]
    for n, line in lines:
        if DASH_METADATA_RE.match(line):
            errors.append((n, "use `*` bullets for the metadata"))

    statuses = [(n, m[1]) for n, line in lines if (m := STATUS_RE.match(line))]
    if len(statuses) != 1:
        errors.append((statuses[1][0] if statuses else 1, "an ADR has one `* Status:` line"))
    else:
        number, value = statuses[0]
        if superseded := SUPERSEDED_RE.match(value):
            adr_id, target = superseded["id"], superseded["target"]
            if target == name:
                errors.append((number, "an ADR cannot supersede itself"))
            elif superseded["number"] != adr_id:
                errors.append((number, f"ADR-{adr_id} links to {target}, which has another number"))
            elif target not in names:
                errors.append((number, f"ADR-{adr_id} links to {target}, which does not exist"))
        elif value not in STATUS_VALUES:
            errors.append(
                (
                    number,
                    f"Status must be {', '.join(STATUS_VALUES)}, "
                    "or superseded by [ADR-NNNN](NNNN-title.md)",
                )
            )

    dates = [(n, m[1]) for n, line in lines if (m := DATE_RE.match(line))]
    if len(dates) != 1:
        errors.append((dates[1][0] if dates else 1, "an ADR has one `* Date:` line"))
    else:
        number, value = dates[0]
        try:
            date.fromisoformat(value)
            valid = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
        except ValueError:
            valid = False
        if not valid:
            errors.append((number, "Date must be a real date of the form YYYY-MM-DD"))
    return errors


def check_prose(
    lines: list[tuple[int, str]],
) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    errors: list[tuple[int, str]] = []
    warnings: list[tuple[int, str]] = []
    for number, line in lines:
        if PREFIX_RE.match(line):
            errors.append(
                (number, "put the point under `#### Good`, `#### Bad` or `#### Neutral` instead")
            )
        if m := PLACEHOLDER_RE.search(re.sub(r"`[^`]*`", "", line)):
            errors.append((number, f"replace the template placeholder `{m[0]}`"))
        if line.startswith(("#", "|", "* Status:", "* Date:")):
            continue
        text = re.sub(r"`[^`]*`|\]\([^)]*\)|https?://\S+", " ", line)
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if len(re.findall(r"\b\w+\b", sentence)) > MAX_WORDS:
                warnings.append((number, f"sentence has more than {MAX_WORDS} words, split it"))
    return errors, warnings


def check_file(path: Path, names: set[str]) -> list[Problem]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return [Problem(path, 1, "the file is not UTF-8")]
    # Drop HTML comments but keep their newlines, so line numbers stay correct.
    text = COMMENT_RE.sub(lambda m: "\n" * m[0].count("\n"), text)
    lines = unfenced(text.splitlines())
    hs = headings(lines)
    errors = (
        check_structure(hs) + check_options(lines, hs) + check_metadata(lines, hs, path.name, names)
    )
    prose_errors, warnings = check_prose(lines)
    problems = [Problem(path, n, msg) for n, msg in errors + prose_errors]
    problems += [Problem(path, n, msg, warning=True) for n, msg in warnings]
    return sorted(problems, key=lambda p: p.line)


def check_dir(folder: Path) -> list[Problem]:
    paths = sorted(p for p in folder.glob("*.md") if p.is_file() and p.name not in SKIP_NAMES)
    names = {p.name for p in paths}
    seen: dict[str, str] = {}
    problems: list[Problem] = []
    for path in paths:
        if not NAME_RE.match(path.name):
            problems.append(Problem(path, 1, "name the file NNNN-title-with-dashes.md, lowercase"))
        if (m := NUMBER_RE.match(path.name)) and (
            first := seen.setdefault(m[1], path.name)
        ) != path.name:
            problems.append(Problem(path, 1, f"ADR-{m[1]} is also used by {first}"))
        problems += check_file(path, names)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("folder", nargs="?", default="docs/decisions", type=Path)
    args = parser.parse_args()
    folder: Path = args.folder
    if not folder.is_dir():
        print(f"check_adr: {folder} is not a folder", file=sys.stderr)
        return 2

    problems = check_dir(folder)
    for problem in problems:
        print(problem)
    errors = sum(not p.warning for p in problems)
    warnings = len(problems) - errors
    print(f"check_adr: {errors} errors, {warnings} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
