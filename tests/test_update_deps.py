import tomlkit
from update_deps import apply_updates, bump_spec, latest_stable, package_names

PYPROJECT = """\
[project]
dependencies = [
    "Requests>=2.0",  # http
    "pydantic[email]>=2.1",
    "attrs",
]

[project.optional-dependencies]
docs = ["mkdocs==1.5.0"]

[dependency-groups]
dev = ["pytest>=8.0,<9", "ruff>=0.4"]
"""


def test_bump_spec_preserves_operator_extras_and_markers() -> None:
    assert bump_spec("foo>=1.0", "2.0") == "foo>=2.0"
    assert bump_spec("foo[bar] ~= 1.0", "1.5") == "foo[bar] ~= 1.5"
    assert bump_spec("foo==1.0; python_version<'3.13'", "2.0") == "foo==2.0; python_version<'3.13'"


def test_bump_spec_leaves_unbumpable_specs() -> None:
    assert bump_spec("foo", "2.0") == "foo"
    assert bump_spec("foo<2", "2.0") == "foo<2"
    assert bump_spec("foo>=1.0,<2", "2.5") == "foo>=1.0,<2"
    assert bump_spec("foo>=3.0", "2.0") == "foo>=3.0"
    assert bump_spec("foo>=1.0", None) == "foo>=1.0"


def test_latest_stable_skips_prereleases_and_yanked() -> None:
    data = {
        "releases": {
            "1.0": [{"yanked": False}],
            "1.2": [{"yanked": True}],
            "1.10": [{"yanked": False}],
            "2.0rc1": [{"yanked": False}],
            "1.11": [],
            "bogus": [{"yanked": False}],
        }
    }
    assert latest_stable(data) == "1.10"


def test_apply_updates_edits_all_tables_in_place() -> None:
    doc = tomlkit.parse(PYPROJECT)
    assert package_names(doc) == {"requests", "pydantic", "mkdocs", "pytest", "ruff"}

    changes = apply_updates(
        doc, {"requests": "2.32.3", "pydantic": "2.9.0", "mkdocs": "1.6.1", "pytest": "9.1"}
    )

    assert changes == [
        ("Requests>=2.0", "Requests>=2.32.3"),
        ("pydantic[email]>=2.1", "pydantic[email]>=2.9.0"),
        ("mkdocs==1.5.0", "mkdocs==1.6.1"),
    ]
    out = tomlkit.dumps(doc)
    assert '"Requests>=2.32.3",  # http' in out
    assert '"pytest>=8.0,<9"' in out
    assert '"ruff>=0.4"' in out
