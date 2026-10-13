# /// script
# requires-python = ">=3.12"
# dependencies = ["packaging>=24", "tomlkit>=0.13"]
# ///
"""Bump lower-bound and pinned dependency versions in pyproject.toml files to latest stable.

Covers [project.dependencies], [project.optional-dependencies] and [dependency-groups].
Edits in place and preserves formatting. Dry run unless --update is given.
"""

import argparse
import json
import re
import sys
import urllib.request
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, cast

import tomlkit
from packaging.version import InvalidVersion, Version
from tomlkit.items import Array
from tomlkit.toml_document import TOMLDocument

SPEC_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9_.\-]*)(?P<extras>\s*\[[^\]]*\])?"
    r"(?P<op>\s*(?:>=|==|~=)\s*)(?P<version>[0-9][^,;\s]*)(?P<rest>.*)$",
    re.DOTALL,
)


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def bump_spec(dep: str, latest: str | None) -> str:
    """Return dep with its version replaced by latest, or unchanged if not bumpable.

    Specs with an upper bound or extra clauses (e.g. ">=1,<2") are left alone, since
    bumping the lower bound could make them unsatisfiable.
    """
    m = SPEC_RE.match(dep)
    if not m or not latest or m["rest"].lstrip().startswith(","):
        return dep
    try:
        if Version(latest) <= Version(m["version"]):
            return dep
    except InvalidVersion:
        return dep
    return f"{m['name']}{m['extras'] or ''}{m['op']}{latest}{m['rest']}"


def latest_stable(data: dict[str, Any]) -> str | None:
    """Pick the highest non-prerelease version that has at least one non-yanked file."""
    best: Version | None = None
    for raw, files in cast(dict[str, list[dict[str, Any]]], data.get("releases", {})).items():
        try:
            version = Version(raw)
        except InvalidVersion:
            continue
        if version.is_prerelease or not any(not f.get("yanked") for f in files):
            continue
        if best is None or version > best:
            best = version
    return str(best) if best else None


def fetch_latest(name: str) -> str | None:
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=15) as resp:
            return latest_stable(json.load(resp))
    except OSError as e:
        print(f"warning: could not fetch {name}: {e}", file=sys.stderr)
        return None


def dependency_arrays(doc: TOMLDocument) -> Iterator[Array]:
    root = cast(dict[str, Any], doc)
    project: dict[str, Any] = root.get("project", {})
    candidates: list[Any] = [project.get("dependencies")]
    candidates += cast(dict[str, Any], project.get("optional-dependencies", {})).values()
    candidates += cast(dict[str, Any], root.get("dependency-groups", {})).values()
    for arr in candidates:
        if isinstance(arr, Array):
            yield arr


def package_names(doc: TOMLDocument) -> set[str]:
    return {
        normalize(m["name"])
        for arr in dependency_arrays(doc)
        for dep in cast(list[Any], arr)
        if isinstance(dep, str) and (m := SPEC_RE.match(dep))
    }


def apply_updates(doc: TOMLDocument, latest: dict[str, str | None]) -> list[tuple[str, str]]:
    """Bump deps in doc in place. Returns (old, new) spec pairs."""
    changes: list[tuple[str, str]] = []
    for arr in dependency_arrays(doc):
        for i, dep in enumerate(cast(list[Any], list(arr))):
            if not isinstance(dep, str) or not (m := SPEC_RE.match(dep)):
                continue
            new = bump_spec(dep, latest.get(normalize(m["name"])))
            if new != dep:
                arr[i] = new
                changes.append((str(dep), new))
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path, default=[Path("pyproject.toml")])
    parser.add_argument("--update", action="store_true", help="write changes to the files")
    args = parser.parse_args()
    files = cast(list[Path], args.files)

    docs = {path: tomlkit.parse(path.read_text()) for path in files}
    names = sorted(set[str]().union(*(package_names(doc) for doc in docs.values())))
    with ThreadPoolExecutor(max_workers=10) as pool:
        latest = dict(zip(names, pool.map(fetch_latest, names), strict=True))

    for path, doc in docs.items():
        changes = apply_updates(doc, latest)
        if not changes:
            continue
        print(path)
        for old, new in changes:
            print(f"  {old} -> {new}")
        if args.update:
            path.write_text(tomlkit.dumps(doc))

    if not args.update:
        print("(dry run, pass --update to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
