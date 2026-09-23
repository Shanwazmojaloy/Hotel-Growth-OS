#!/usr/bin/env python3
"""check_output.py — validate a Figma design-intel audit against BRIEF-v2 rules.

The brief forbids invention, forbids shallowness, and forbids brevity. Those three
cannot all hold (see reviews/05-figma-brief-adjudication.md). This validator enforces
the parts that are actually checkable, so the integrity rules survive a real run
instead of degrading into decoration.

Usage:
    python3 check_output.py audit.md [--required-fields 12] [--strict]
    python3 check_output.py --self-test

Exit codes: 0 = pass (warnings allowed), 1 = errors found, 2 = bad usage.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field

TAGS = ("Observed", "Inferred", "Recommendation", "Requires-access")
DIMENSIONS = ("ux", "interface", "visual-system", "layout", "accessibility", "production-readiness")
BANNED = (
    "modern and intuitive",
    "clean and modern",
    "best-in-class",
    "seamless experience",
    "looks professional",
)
SCORE_RE = re.compile(r"score\(([a-z\-]+)\):\s*(\d{1,2})\s*/\s*10\s*(?:—|-)\s*evidence:\s*(.+)$")
COVERAGE_RE = re.compile(
    r"coverage:\s*(\d+)\s*/\s*(\d+)\s*fields answered\s*\|\s*(\d+)\s*not-observable\s*\|\s*(\d+)\s*requires-access"
)
TOP_RE = re.compile(r"^#{2,4}\s*Top-(\d+)\b", re.I)
SECTION_TOP_RE = re.compile(r"^Top-(\d+)\b", re.I)
REC_ITEM_RE = re.compile(r"^\d+\.\s+\S")


@dataclass
class Block:
    name: str
    lines: list[str] = field(default_factory=list)
    # (h3 section heading, line) — section is "" for content before any h3
    sections: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _split_sources(text: str) -> tuple[list[Block], list[Block]]:
    """Return (source blocks, other heading blocks)."""
    lines = text.splitlines()
    blocks: list[Block] = []
    current: Block | None = None
    others: list[Block] = []
    for ln in lines:
        m = re.match(r"^##\s+SOURCE\s+#(\d+)\s*[—-]\s*(.+)$", ln)
        if m:
            current = Block(name=f"SOURCE #{m.group(1)} {m.group(2).strip()}")
            blocks.append(current)
            continue
        h = re.match(r"^##\s+(.+)$", ln)
        if h:
            current = Block(name=h.group(1).strip())
            others.append(current)
            continue
        if current is None:
            continue
        h3 = re.match(r"^###\s+(.+)$", ln)
        if h3:
            current.lines.append(f"\x00H3\x00{h3.group(1).strip()}")
            continue
        current.lines.append(ln)
        section = ""
        for prev in reversed(current.lines):
            if prev.startswith("\x00H3\x00"):
                section = prev[4:]
                break
        current.sections.append((section, ln))
    return blocks, others


def _field(block: Block, key: str) -> str | None:
    pat = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.I)
    for ln in block.lines:
        if ln.startswith("\x00H3\x00"):
            continue
        m = pat.match(ln.strip())
        if m:
            return m.group(1).strip()
    return None


def check(text: str, required_fields: int = 12, strict: bool = False) -> Report:
    rep = Report()
    sources, others = _split_sources(text)

    if not sources:
        rep.err("no '## SOURCE #n — title' blocks found")

    for b in sources:
        tier = (_field(b, "tier") or "").upper()
        if tier not in ("T1", "T2", "T3"):
            rep.err(f"{b.name}: missing/invalid 'tier:' (T1|T2|T3)")
        url = _field(b, "url")
        if not url or not url.startswith("http"):
            rep.err(f"{b.name}: missing/invalid 'url:' line")
        rtype = _field(b, "type")
        if not rtype:
            rep.err(f"{b.name}: missing 'type:' line (marketing-page|category-listing|help-doc|resource-page)")

        cov = _field(b, "coverage")
        if not cov:
            rep.err(f"{b.name}: missing 'coverage:' line — thin sources must be visible, not padded")
        else:
            m = COVERAGE_RE.search("coverage: " + cov)
            if not m:
                rep.err(f"{b.name}: coverage line unparseable: {cov!r}")
            else:
                answered, total, notobs, needs = (int(g) for g in m.groups())
                if answered + notobs + needs != total:
                    rep.err(
                        f"{b.name}: coverage does not sum "
                        f"({answered}+{notobs}+{needs} != {total})"
                    )
                if total != required_fields:
                    rep.warn(
                        f"{b.name}: coverage denominator {total} != required {required_fields}"
                    )
                if total and notobs / total > 0.5:
                    msg = f"{b.name}: {notobs}/{total} fields unobservable — source is thin for this tier"
                    (rep.err if (strict or tier in ("T1", "T2")) else rep.warn)(msg)

        if tier in ("T1", "T2"):
            lic = _field(b, "license")
            if not lic:
                rep.err(f"{b.name}: missing 'license:' — commercial reuse is the point (Finding 6)")
            plan = _field(b, "plan")
            if not plan:
                rep.err(f"{b.name}: missing 'plan:' — paid-seat gating is decisive for a solo studio")

        bullets = [
            ln.strip()
            for section, ln in b.sections
            if ln.strip().startswith("- ") and not SECTION_TOP_RE.match(section)
        ]
        if not bullets:
            rep.err(f"{b.name}: no tagged evidence bullets")
        for ln in bullets:
            body = ln[2:].strip()
            if not body.startswith(tuple(f"{t}:" for t in TAGS)):
                rep.err(f"{b.name}: untagged claim — every bullet needs one of {TAGS}: {body[:60]!r}")

        for ln in b.lines:
            if ln.startswith("\x00H3\x00"):
                continue
            s = ln.strip()
            m = SCORE_RE.search(s)
            if not m:
                if re.match(r"^score\(", s):
                    rep.err(f"{b.name}: score missing anchor or evidence: {s[:70]!r}")
                continue
            dim, val, ev = m.group(1), int(m.group(2)), m.group(3).strip()
            if dim not in DIMENSIONS:
                rep.err(f"{b.name}: unknown score dimension {dim!r}")
            if not 1 <= val <= 10:
                rep.err(f"{b.name}: score out of range for {dim}: {val}")
            if len(ev) < 20:
                rep.err(f"{b.name}: evidence too short for {dim} — must cite what was seen")

    # Top-N lists: cap at 5, count the items
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        m = TOP_RE.match(ln)
        if not m:
            continue
        cap = int(m.group(1))
        if cap > 5:
            rep.err(f"'{ln.strip()}': top-N lists are capped at 5 by BRIEF-v2")
        n = 0
        for nxt in lines[i + 1:]:
            if re.match(r"^#{1,4}\s", nxt) and not nxt.strip().startswith("-"):
                break
            if nxt.strip().startswith("- "):
                n += 1
        if n > cap:
            rep.err(f"'{ln.strip()}': {n} items exceeds its own cap of {cap}")
        for j in range(i + 1, i + 1 + n):
            if "used for:" not in lines[j]:
                rep.err(f"'{ln.strip()}': list items need a 'used for:' column: {lines[j].strip()[:50]!r}")

    recs = [b for b in others if b.name.lower().startswith("recommendation")]
    if not recs:
        rep.err("missing '## RECOMMENDATIONS' section — research must end in a decision")
    else:
        items = [ln.strip() for ln in recs[0].lines if REC_ITEM_RE.match(ln.strip())]
        if not items:
            rep.err("RECOMMENDATIONS contains no numbered items")
        if len(items) > 5:
            rep.err(f"RECOMMENDATIONS has {len(items)} items; BRIEF-v2 caps this at 5")
        for it in items:
            for need in ("cost:", "hours:", "decision:"):
                if need not in it:
                    rep.err(f"recommendation missing '{need}' — {it[:60]!r}")

    low = text.lower()
    for phrase in BANNED:
        if phrase in low:
            rep.err(f"banned slop phrasing present: {phrase!r}")

    return rep


FIXTURE = """# Design audit — fixture

## SOURCE #1 — Figma Community landing
url: https://www.figma.com/community
tier: T1
type: category-index
coverage: 9/12 fields answered | 2 not-observable | 1 requires-access
license: not stated on page
plan: free to browse
- Observed: Navigation exposes Skills, Weave tools, Shaders and Apps/MCP clients as first-class sections.
- Inferred: The Community surface is drifting toward agent-facing assets rather than static UI kits.
- Requires-access: Per-file licence terms, shown only inside a file page after sign-in.

### Scores
score(ux): 8/10 — evidence: each section label carries a one-line description of what it holds.
score(interface): 7/10 — evidence: filter chips and a sort control appear on every listing page.
score(visual-system): 6/10 — evidence: one accent colour, dense card grid, consistent card anatomy.
score(layout): 7/10 — evidence: three-column card grid at desktop width, single column when narrow.
score(accessibility): 6/10 — evidence: focus rings visible on nav links; no skip link observed.
score(production-readiness): 7/10 — evidence: item counts and engagement figures are exposed for triage.

### Top-5 resources, used for
- Skills: reusable agent instructions — used for: briefing the agency skill.
- Make: prompt-to-app prototypes — used for: fast client-side demos.
- Weave tools: on-canvas AI edits — used for: creative iteration.
- Apps and MCP clients: agent connection surface — used for: pipeline wiring.
- Shaders: canvas effects — used for: visual differentiation.

## RECOMMENDATIONS
1. Add licence and plan columns to the resource ledger. cost: 0 BDT | hours: 1 | decision: whether Community files may ship on client work.
"""


MUTATIONS = {
    "drop tier line": lambda t: t.replace("tier: T1\n", ""),
    "untag a bullet": lambda t: t.replace("- Inferred:", "- "),
    "score without evidence": lambda t: re.sub(r"score\(ux\): 8/10 — evidence:.*", "score(ux): 8/10", t),
    "top-5 with 6 items": lambda t: t.replace(
        "### Top-5 resources, used for", "### Top-5 resources, used for\n- Extra: filler — used for: nothing."
    ),
    "sixth recommendation": lambda t: t + "2. One. cost: 0 | hours: 0 | decision: x\n3. Two. cost: 0 | hours: 0 | decision: x\n4. Three. cost: 0 | hours: 0 | decision: x\n5. Four. cost: 0 | hours: 0 | decision: x\n6. Five. cost: 0 | hours: 0 | decision: x\n",
    "coverage does not sum": lambda t: t.replace(
        "coverage: 9/12 fields answered | 2 not-observable | 1 requires-access",
        "coverage: 9/12 fields answered | 2 not-observable | 3 requires-access",
    ),
    "banned phrasing": lambda t: t.replace(
        "- Inferred: The Community surface is drifting",
        "- Inferred: The Community surface is a modern and intuitive design, drifting",
    ),
}


def self_test() -> int:
    base = check(FIXTURE)
    if base.errors:
        print("FIXTURE INVALID — self-test is meaningless:")
        for e in base.errors:
            print("  x", e)
        return 1
    print("fixture: valid (0 errors, {} warnings)".format(len(base.warnings)))

    caught = 0
    for name, mutate in MUTATIONS.items():
        reps = check(mutate(FIXTURE))
        ok = bool(reps.errors)
        caught += ok
        print(f"  [{'KILLED' if ok else 'SURVIVED'}] {name}"
              + (f" -> {reps.errors[0][:70]}" if ok else ""))
    total = len(MUTATIONS)
    print(f"\nmutations killed: {caught}/{total}")
    return 0 if caught == total else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a BRIEF-v2 design-intel audit.")
    ap.add_argument("path", nargs="?", help="audit markdown file")
    ap.add_argument("--required-fields", type=int, default=12)
    ap.add_argument("--strict", action="store_true", help="treat thin-source warnings as errors")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.path:
        ap.print_help()
        return 2

    text = open(args.path, encoding="utf-8").read()
    rep = check(text, required_fields=args.required_fields, strict=args.strict)
    for e in rep.errors:
        print("ERROR  ", e)
    for w in rep.warnings:
        print("WARN   ", w)
    status = "FAIL" if rep.errors else "PASS"
    print(f"\n{status}: {len(rep.errors)} errors, {len(rep.warnings)} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
