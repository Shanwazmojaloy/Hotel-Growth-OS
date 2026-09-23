"""Validate a SKILL.md against the Agent Skills specification.

    python3 scripts/validate_skill.py [path/to/SKILL.md]      # check one skill
    python3 scripts/validate_skill.py --self-test             # prove the checks can fail

Checks (agentskills.io/specification):
  * only the documented frontmatter fields are present
  * `name` is 1-64 chars, lowercase alphanumeric + hyphens, no leading/trailing or doubled
    hyphen, and matches the parent directory name
  * `description` is present, 1-1024 chars
  * the activated body stays within the recommended size (<500 lines, <~5000 tokens)
  * every relative path referenced in the body exists

Exit code is non-zero if any check fails, so this can be a CI gate.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_BODY_LINES = 500
MAX_BODY_TOKENS = 5000
MAX_DESCRIPTION = 1024


def parse_frontmatter(text: str) -> tuple[dict, str, list[str]]:
    """Minimal YAML subset: top-level `key: value` plus one nested block under `metadata:`."""
    errors: list[str] = []
    if not text.startswith("---"):
        return {}, text, ["file does not start with a frontmatter block"]
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text, ["frontmatter block is not closed"]
    raw, body = parts[1], parts[2]

    data: dict = {}
    nested_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        indented = line.startswith(" ")
        if ":" not in line:
            errors.append(f"frontmatter line is not a key/value pair: {line!r}")
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if indented and nested_key:
            data.setdefault(nested_key, {})
            if isinstance(data[nested_key], dict):
                data[nested_key][key] = value
        else:
            nested_key = key if not value else None
            data[key] = {} if not value else value
    return data, body, errors


def check(skill_path: Path) -> list[str]:
    failures: list[str] = []
    text = skill_path.read_text(encoding="utf-8")
    data, body, errors = parse_frontmatter(text)
    failures.extend(errors)

    unknown = set(data) - ALLOWED_FIELDS
    if unknown:
        failures.append(
            f"unknown frontmatter field(s): {', '.join(sorted(unknown))} "
            f"— the spec defines only: {', '.join(sorted(ALLOWED_FIELDS))}"
        )

    name = data.get("name")
    if not isinstance(name, str) or not name:
        failures.append("`name` is required")
    else:
        if not NAME_RE.match(name):
            failures.append(f"`name` {name!r} must be lowercase alphanumeric with single hyphens")
        if len(name) > 64:
            failures.append("`name` exceeds 64 characters")
        parent = skill_path.parent.name
        if name != parent:
            failures.append(f"`name` {name!r} must match the parent directory {parent!r}")

    description = data.get("description")
    if not isinstance(description, str) or not description:
        failures.append("`description` is required")
    elif len(description) > MAX_DESCRIPTION:
        failures.append(f"`description` is {len(description)} chars (max {MAX_DESCRIPTION})")

    if isinstance(data.get("metadata"), str):
        failures.append("`metadata` must be a mapping, not a scalar")

    body_lines = body.strip().splitlines()
    if len(body_lines) > MAX_BODY_LINES:
        failures.append(
            f"body is {len(body_lines)} lines (recommended < {MAX_BODY_LINES}); move detail to references/"
        )
    approx_tokens = len(body) // 4
    if approx_tokens > MAX_BODY_TOKENS:
        failures.append(
            f"body is ~{approx_tokens} tokens (recommended < {MAX_BODY_TOKENS}); use progressive disclosure"
        )

    for rel in set(re.findall(r"`((?:references|scripts|assets)/[\w./-]+)`", body)):
        target = skill_path.parent / rel
        if not target.exists():
            failures.append(f"body references {rel}, which does not exist")

    return failures


def self_test() -> int:
    """Mutate a known-good skill and assert each mutation is caught. A check that cannot fail
    is decoration, so this proves each rule bites."""
    here = Path(__file__).resolve().parent.parent
    good = here / "SKILL.md"
    if not good.exists():
        print("no SKILL.md to self-test against")
        return 1
    original = good.read_text(encoding="utf-8")

    mutations = {
        "non-standard field": lambda t: t.replace("metadata:", "triggers:", 1),
        "name/directory mismatch": lambda t: t.replace("name: agency-master", "name: agency-master-v5", 1),
        "invalid name characters": lambda t: t.replace("name: agency-master", "name: Agency_Master", 1),
        "oversized description": lambda t: t.replace(
            "description: Chief", "description: " + "x" * 1100 + " Chief", 1),
        "missing reference file": lambda t: t.replace(
            "`references/frontend-stack.md`", "`references/does-not-exist.md`", 1),
    }

    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        # the validator checks name-vs-directory, so mirror the directory name
        for label, mutate in mutations.items():
            case = Path(tmp) / "agency-master"
            case.mkdir(exist_ok=True)
            target = case / "SKILL.md"
            target.write_text(mutate(original), encoding="utf-8")
            for resource in ("references", "scripts"):
                src = here / resource
                if src.exists():
                    shutil.copytree(src, case / resource, dirs_exist_ok=True)
            caught = check(target)
            if caught:
                print(f"  ✔ caught: {label} — {caught[0][:78]}")
            else:
                print(f"  ✘ MISSED: {label}")
                failures += 1

        clean = Path(tmp) / "agency-master" / "SKILL.md"
        clean.write_text(original, encoding="utf-8")
        if check(clean):
            print("  ✘ the unmutated skill does not pass:", check(clean))
            failures += 1
        else:
            print("  ✔ unmutated skill passes all checks")
    return failures


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        print("self-test — each mutation must be caught:")
        return 1 if self_test() else 0

    path = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent / "SKILL.md"
    failures = check(path)
    print(f"validating {path}")
    if failures:
        for f in failures:
            print(f"  ✘ {f}")
        return 1
    print("  ✔ frontmatter, name, description, size and references all conform")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
