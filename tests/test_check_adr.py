from pathlib import Path

import pytest
from check_adr import check_dir, main

VALID = """\
# Use PostgreSQL for the event store

* Status: accepted
* Date: 2026-10-11
* Decision-makers: Alex

## TL;DR

We store events in PostgreSQL, because the team runs it already.

## Context and Problem Statement

The service must keep each event. Where do we store the events?

## Considered Options

* Option 1 - PostgreSQL
* Option 2 - Kafka

## Decision Outcome

Chosen option: "Option 1 - PostgreSQL", because the team runs it already.

### Consequences

#### Good

* One database to operate.

#### Bad

* Replay is slower than with a log.

### Validation

Each event write is one row in the events table.

## Pros and Cons of the Options

### Option 1 - PostgreSQL

#### Good

* The team knows it.

### Option 2 - Kafka

#### Bad

* A new system to operate.

```markdown
### Not an option heading
```

## Additional context for AI agents

The load test gave 2,000 writes per second.
"""


def write(folder: Path, name: str, text: str) -> None:
    (folder / name).write_text(text, encoding="utf-8")


def messages(folder: Path) -> list[str]:
    return [f"{p.path.name}:{p.line}: {p.message}" for p in check_dir(folder) if not p.warning]


def test_valid_adr_passes(tmp_path: Path) -> None:
    write(tmp_path, "0001-use-postgresql.md", VALID)
    write(tmp_path, "README.md", "# Decisions\n")
    assert check_dir(tmp_path) == []


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        ("* Status: accepted", "* Status: approved", "Status must be"),
        ("* Status: accepted\n", "", "one `* Status:` line"),
        ("2026-10-11", "2026-02-31", "real date"),
        ("2026-10-11", "11-10-2026", "real date"),
        ("### Validation", "### Confirmation", "`### Validation`"),
        ("## Considered Options\n", "", "`## Considered Options`"),
        ("### Option 2 - Kafka", "### Option: Kafka", "`Option N - Name`"),
        ("#### Bad\n\n* Replay", "#### Cons\n\n* Replay", "Good, Bad or Neutral"),
        ("* One database", "* Good, one database", "`#### Good`"),
        ("## TL;DR", "## TLDR", "`## TL;DR`"),
        ("## Additional context for AI agents", "## Notes for agents", "`## Additional context"),
        ("# Use PostgreSQL for the event store\n", "", "level-1 heading"),
        ("## Considered Options", "# Second title\n\n## Considered Options", "one level-1 heading"),
        ("## Context and", "## TL;DR\n\nAgain.\n\n## Context and", "one `## TL;DR`"),
        ("## TL;DR\n\nWe store", "## Notes\n\nText.\n\n## TL;DR\n\nWe store", "first section"),
        ("The load test", "Text.\n\n## Notes\n\nThe load test", "last section"),
        ("* Status: accepted", "* Status: accepted\n* Status: proposed", "one `* Status:` line"),
        ("* Status: accepted", "- Status: accepted", "use `*` bullets"),
        ("* Status: accepted", "* Status: superseded by ADR-0002", "Status must be"),
        ("* Date: 2026-10-11\n", "", "one `* Date:` line"),
        ("* Date: 2026-10-11", "* Date: 2026-10-11\n* Date: 2026-10-12", "one `* Date:` line"),
        ("2026-10-11", "20261011", "real date"),
        ("* Option 2 - Kafka", "* Option 2 - Kafka Streams", "same options, in the same order"),
        (
            "* Option 1 - PostgreSQL\n* Option 2 - Kafka",
            "* Option 2 - Kafka\n* Option 1 - PostgreSQL",
            "same order",
        ),
        ('Chosen option: "Option 1', 'We chose "Option 1', "start with `Chosen option:"),
        (
            '"Option 1 - PostgreSQL", because',
            '"Option 3 - MySQL", because',
            "not one of the options",
        ),
        ("Alex", "<Names>", "placeholder `<Names>`"),
        ("### Validation", "<!-- ### Validation -->", "`### Validation`"),
    ],
)
def test_rule_violations(tmp_path: Path, old: str, new: str, expected: str) -> None:
    assert old in VALID
    write(tmp_path, "0001-use-postgresql.md", VALID.replace(old, new, 1))
    assert any(expected in m for m in messages(tmp_path)), messages(tmp_path)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("* Status: accepted", "* Status: accepted  "),
        ("* Date: 2026-10-11", "* Date: 2026-10-11 "),
        ("```markdown\n### Not", "````markdown\n```\n### Not"),
        ("```\n\n## Additional", "```\n````\n\n## Additional"),
        ("The load test", "Quoted:\n\n* Status: rejected\n\nThe load test"),
        ("The load test", "<!--\n## Context and Problem Statement\nold draft\n-->\nThe load test"),
        ("The load test", "Use `<Name>` in code. The load test"),
        ("Alex", "Alex <alex@example.com>, https://example.com/" + "a/" * 30),
    ],
)
def test_realistic_variations_pass(tmp_path: Path, old: str, new: str) -> None:
    assert old in VALID
    write(tmp_path, "0001-use-postgresql.md", VALID.replace(old, new, 1))
    assert check_dir(tmp_path) == []


def test_bom_and_crlf_pass(tmp_path: Path) -> None:
    (tmp_path / "0001-use-postgresql.md").write_bytes(
        b"\xef\xbb\xbf" + VALID.replace("\n", "\r\n").encode()
    )
    assert check_dir(tmp_path) == []


def test_unreadable_entries_are_reported_not_raised(tmp_path: Path) -> None:
    (tmp_path / "0001-latin.md").write_bytes(b"# Caf\xe9\n")
    (tmp_path / "0002-folder.md").mkdir()
    assert messages(tmp_path) == ["0001-latin.md:1: the file is not UTF-8"]


def test_file_names_and_duplicate_numbers(tmp_path: Path) -> None:
    write(tmp_path, "0001-use-postgresql.md", VALID)
    write(tmp_path, "0001-other.md", VALID)
    write(tmp_path, "0002-Use-Kafka.md", VALID)
    write(tmp_path, "0002-other.md", VALID)
    result = messages(tmp_path)
    assert any("0001-use-postgresql.md" in m and "also used by 0001-other.md" in m for m in result)
    assert any(m.startswith("0002-Use-Kafka.md") and "NNNN-title" in m for m in result)
    assert any(
        m.startswith("0002-other.md") and "also used by 0002-Use-Kafka.md" in m for m in result
    )


@pytest.mark.parametrize(
    ("link", "expected"),
    [
        ("[ADR-0002](0002-use-kafka.md)", None),
        ("[ADR-0003](0003-use-kafka.md)", "does not exist"),
        ("[ADR-0003](0002-use-kafka.md)", "has another number"),
        ("[ADR-0001](0001-use-postgresql.md)", "cannot supersede itself"),
    ],
)
def test_superseded_link_target(tmp_path: Path, link: str, expected: str | None) -> None:
    write(tmp_path, "0002-use-kafka.md", VALID)
    status = f"* Status: superseded by {link}"
    write(tmp_path, "0001-use-postgresql.md", VALID.replace("* Status: accepted", status))
    result = messages(tmp_path)
    if expected:
        assert any(expected in m for m in result), result
    else:
        assert result == []


def test_long_sentence_is_a_warning(tmp_path: Path) -> None:
    long = " ".join(["word"] * 30) + "."
    write(tmp_path, "0001-use-postgresql.md", VALID.replace("Each event write", long + " Each"))
    problems = check_dir(tmp_path)
    assert [p.warning for p in problems] == [True]


def test_main_exit_codes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def run(folder: Path) -> int:
        monkeypatch.setattr("sys.argv", ["check_adr.py", str(folder)])
        return main()

    assert run(tmp_path / "missing") == 2

    long = " ".join(["word"] * 30) + "."
    write(tmp_path, "0001-use-postgresql.md", VALID.replace("Each event write", long + " Each"))
    assert run(tmp_path) == 0
    assert "check_adr: 0 errors, 1 warnings" in capsys.readouterr().out

    write(tmp_path, "0001-use-postgresql.md", VALID.replace("accepted", "approved"))
    assert run(tmp_path) == 1
