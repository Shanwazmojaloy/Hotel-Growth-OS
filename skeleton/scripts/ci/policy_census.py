#!/usr/bin/env python3
"""
policy_census.py — static structural gate for tenant isolation.

Runs WITHOUT a database, so CI catches a missing control in the pull request
rather than at runtime. Checks:

  1. every table carrying organization_id enables RLS
  2. ... and FORCEs it (no owner bypass)
  3. ... and has at least one CREATE POLICY
  4. no policy uses `using (true)` / `with check (true)` on a tenant table
     (a permissive policy is the most common way isolation quietly dies)
  5. no SECURITY DEFINER function is missing `set search_path`

Usage:  python3 scripts/ci/policy_census.py db/migrations/*.sql
Exit:   0 = clean, 1 = violations
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TENANT_COLUMN = "organization_id"


def strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def extract_tables(sql: str) -> dict[str, str]:
    """Map table name -> full CREATE TABLE body (paren-aware)."""
    tables: dict[str, str] = {}
    for m in re.finditer(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([\w\.\"]+)\s*\(", sql, re.I):
        name = m.group(1).strip('"').split(".")[-1]
        depth, start = 0, m.end() - 1
        for i in range(start, len(sql)):
            if sql[i] == "(":
                depth += 1
            elif sql[i] == ")":
                depth -= 1
                if depth == 0:
                    tables[name] = sql[start : i + 1]
                    break
    return tables


def main(paths: list[str]) -> int:
    files = [Path(p) for p in paths]
    if not files:
        print("usage: policy_census.py <migration.sql> [...]", file=sys.stderr)
        return 2

    raw = "\n".join(f.read_text() for f in files)
    sql = strip_comments(raw)
    tables = extract_tables(sql)

    tenant_tables = sorted(
        t for t, body in tables.items()
        if re.search(rf"\b{TENANT_COLUMN}\b", body, re.I)
    )

    violations: list[str] = []

    for t in tenant_tables:
        if not re.search(rf"alter\s+table\s+{t}\s+enable\s+row\s+level\s+security", sql, re.I):
            violations.append(f"{t}: RLS not ENABLED")
        if not re.search(rf"alter\s+table\s+{t}\s+force\s+row\s+level\s+security", sql, re.I):
            violations.append(f"{t}: RLS not FORCED (a table owner would bypass policy)")
        if not re.search(rf"create\s+policy\s+\w+\s+on\s+{t}\b", sql, re.I):
            violations.append(f"{t}: no CREATE POLICY (unreviewed is not the same as safe)")

    # permissive policies on tenant tables
    for m in re.finditer(r"create\s+policy\s+(\w+)\s+on\s+(\w+)([^;]*);", sql, re.I):
        policy, table, body = m.group(1), m.group(2), m.group(3)
        if table not in tenant_tables:
            continue
        if re.search(r"(using|with\s+check)\s*\(\s*true\s*\)", body, re.I):
            violations.append(
                f"{table}: policy '{policy}' is unconditionally permissive "
                f"(using/with check true) — isolation bypass"
            )

    # security definer without a pinned search_path
    for m in re.finditer(
        r"create\s+(?:or\s+replace\s+)?function\s+([\w\.]+)\s*\((.*?)\)(.*?)\$\$(.*?)\$\$",
        sql, re.I | re.S,
    ):
        name, _, header, _ = m.groups()
        if "security definer" in header.lower() and "set search_path" not in header.lower():
            violations.append(f"function {name}: SECURITY DEFINER without `set search_path`")

    print(f"policy census — {len(files)} migration file(s), {len(tables)} tables, "
          f"{len(tenant_tables)} tenant-scoped")
    print(f"  tenant tables: {', '.join(tenant_tables)}")
    if violations:
        print("\nVIOLATIONS:")
        for v in violations:
            print(f"  ✘ {v}")
        return 1
    print("\n✔ every tenant table is ENABLED, FORCED and policied; no permissive policies; "
          "no unpinned SECURITY DEFINER functions")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
