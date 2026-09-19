"""Honesty gate for the prospect screener.

A screener that says "call them" to everything is worse than no screener, because
it spends the scarcest resource in the plan — a sales call — on engagements that
cannot work. This gate asserts the properties that keep the verdicts honest, on
the screener's own output rather than on its docstrings.

Run directly (`python3 -m prospect.honesty_gate --scores prospect/reports/prospect_scores.json`)
or via `measurement/verify.sh` §9. Exit code 0 = every property holds.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Thresholds mirror screener.py. If those change, this gate must change with them —
# which is the point: the decision rule a prospect's verdict comes from is pinned here.
VARIABLE_MAX = 0.35      # lift at or below this = viable
HOPELESS_ABOVE = 0.60    # lift above this even on the best reading = not a fit
IMPLAUSIBLE_ABOVE = 0.70  # lift above this on the worst reading = not worth a call
CAPTURABLE_FLOOR = 25_000  # ৳/month below which the fee is hard to justify
QUOTE_CEILING = 0.5      # the quoted number must stay a minority of commission paid
SEASONAL_RATIO = 1.60    # mirrors screener.SEASONAL_RATIO
SEASONAL_TROUGH_LIFT_ABOVE = 0.60  # mirrors the trough guard in screener.decide()


class GateFailure(Exception):
    pass


def expected_verdict(p: dict) -> str:
    """The decision rule, restated. A verdict that disagrees with this is a bug in
    screener.py, not a matter of taste.

    Every clause of screener.decide() must appear here, in the same order — including
    the two that were missing when this last drifted:

      * a confident yes may not rest on an input we assumed, and
      * a seasonal trough can only ever weaken a verdict.

    The drift was not harmless. It made the gate reject *correct* screener output
    ("reported CONFIRM, rule gives CALL NOW" for a row whose assumptions also forbid
    CALL NOW), and the obvious way to satisfy a gate like that is to weaken the
    screener — i.e. to delete the discipline. A checker that fails correct work pushes
    in the unsafe direction, so the mirror is pinned by
    tests/test_screener.py::TestGateMirrorsTheRule.
    """
    best, worst = p["lift_optimistic"], p["lift_pessimistic"]
    if best > HOPELESS_ABOVE:
        return "NOT A FIT"
    if worst > IMPLAUSIBLE_ABOVE or p["capturable_bdt"] < CAPTURABLE_FLOOR:
        return "CALL LATER"

    if (worst <= VARIABLE_MAX and not p["derived_direct_share"]
            and not p.get("assumed_fields")):
        # economics hold, the volume was confirmed, and nothing in the row is our guess
        rec = "CALL NOW"
    else:
        rec = "CONFIRM DIRECT VOLUME FIRST"

    # seasonal downgrade — same arithmetic as screener.decide(), one-way only
    ratio = p.get("season_ratio") or 1.0
    if ratio >= SEASONAL_RATIO and rec in ("CALL NOW", "CONFIRM DIRECT VOLUME FIRST"):
        break_even = p.get("break_even_room_nights") or 0.0
        direct = p.get("direct_room_nights") or 0.0
        trough_direct = direct * (2.0 / (1.0 + ratio))
        if trough_direct > 0 and break_even / trough_direct > SEASONAL_TROUGH_LIFT_ABOVE:
            return "CALL LATER"
    return rec


def check(scores: list[dict]) -> list[str]:
    """Return human-readable lines; raise GateFailure on the first violation."""
    if not scores:
        raise GateFailure("no prospects scored")

    lines: list[str] = []
    verdicts = [p["recommendation"] for p in scores]
    counts = {v: verdicts.count(v) for v in sorted(set(verdicts))}

    # 1. a usable call list: not a yes to everything, not a blanket no, and not
    #    uniformly "maybe" — which is honest but useless as a worklist
    if len(counts) < 2:
        raise GateFailure(f"every prospect got the same verdict ({list(counts)}) — the screen is not discriminating")
    actionable = counts.get("CALL NOW", 0) + counts.get("CONFIRM DIRECT VOLUME FIRST", 0)
    if actionable < 1:
        raise GateFailure("nothing is actionable — the screen rejects the whole list")
    if counts.get("NOT A FIT", 0) < 1:
        raise GateFailure("nothing was screened out — the screen accepts everything")
    lines.append(f"verdicts differentiate: {counts}")

    for p in scores:
        name, v = p["name"], p["recommendation"]

        # 2. the reported verdict must be the one the rule dictates
        want = expected_verdict(p)
        if v != want:
            raise GateFailure(f"{name} reported {v} but the rule gives {want} "
                              f"(best {p['lift_optimistic']:.0%}, worst {p['lift_pessimistic']:.0%}, "
                              f"capturable ৳{p['capturable_bdt']:,.0f}, "
                              f"{'estimated' if p['derived_direct_share'] else 'confirmed'} direct volume)")

        # 3. never oversell: nothing hopeless may be put in front of a prospect
        if v in ("CALL NOW", "CONFIRM DIRECT VOLUME FIRST") and p["lift_optimistic"] > HOPELESS_ABOVE:
            raise GateFailure(f"{name} presented as workable at a {p['lift_optimistic']:.0%} required lift")

        # 4. a confident yes requires no assumed inputs at all: confirmed volume,
        #    sourced rate, and a pessimistic case that works
        if v == "CALL NOW":
            if p["derived_direct_share"]:
                raise GateFailure(f"{name} called now on an unconfirmed direct volume")
            if p.get("assumed_fields"):
                raise GateFailure(f"{name} called now on assumed inputs ({p['assumed_fields']})")
            if p["lift_pessimistic"] > VARIABLE_MAX:
                raise GateFailure(f"{name} called now but needs {p['lift_pessimistic']:.0%} lift "
                                  f"on the pessimistic reading")

        # 5. band ordering, positive opportunity, conservative quote
        if p["lift_optimistic"] > p["lift_pessimistic"]:
            raise GateFailure(f"{name} has an inverted band ({p['lift_optimistic']:.0%} best vs "
                              f"{p['lift_pessimistic']:.0%} worst)")
        if p["capturable_bdt"] <= 0:
            raise GateFailure(f"{name} has a non-positive opportunity")
        share = p["capturable_bdt"] / p["commission_bdt"] if p["commission_bdt"] else 1.0
        if share >= QUOTE_CEILING:
            raise GateFailure(f"{name} quotes {share:.0%} of commission paid as capturable")

    lines += [
        "every verdict matches the documented decision rule",
        "nothing hopeless is presented as workable",
        "no CALL NOW rests on an unconfirmed direct volume",
        "no CALL NOW rests on an assumed input",
        "CALL NOW survives the pessimistic end of the band",
        "capturable quote stays a minority of commission paid",
    ]
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="assert the screener's verdicts are honest")
    ap.add_argument("--scores", required=True, help="prospect_scores.json")
    args = ap.parse_args(argv)

    path = Path(args.scores)
    if not path.exists():
        print(f"   ✘ no scores file at {path}")
        return 1
    try:
        lines = check(json.loads(path.read_text()))
    except GateFailure as exc:
        print(f"   ✘ {exc}")
        return 1
    for line in lines:
        print(f"   ✔ {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
