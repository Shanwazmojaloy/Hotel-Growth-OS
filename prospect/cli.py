"""CLI.

  python3 -m prospect.cli screen --input prospect/data/prospects_sample.csv --fee 19000 --media 50000
  python3 -m prospect.cli review --input prospect/data/prospects_sample.csv --name "..." --out prospect/reports
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .review import build_review, slugify
from .callsheet import write_callsheet
from .screener import ProspectError, format_table, load_prospects, screen_all, to_csv


def cmd_screen(args) -> int:
    prospects = load_prospects(Path(args.input))
    scored = screen_all(prospects, fee_bdt=args.fee, media_bdt=args.media)

    print(format_table(scored))
    print()
    counts: dict[str, int] = {}
    for p in scored:
        counts[p.recommendation] = counts.get(p.recommendation, 0) + 1
    print(f"  {counts.get('CALL NOW', 0)} to call now · "
          f"{counts.get('CONFIRM DIRECT VOLUME FIRST', 0)} need one question answered first · "
          f"{counts.get('CALL LATER', 0)} later · {counts.get('NOT A FIT', 0)} not a fit")
    print(f"  assumed: fee {args.fee:,.0f} + media {args.media:,.0f}/month, "
          f"20% conservative shift rate")

    ready = [p for p in scored if p.recommendation == "CALL NOW"]
    if ready:
        print("\nWhy each call-now prospect makes the list:")
    else:
        ready = [p for p in scored if p.recommendation == "CONFIRM DIRECT VOLUME FIRST"]
        print("\nNothing earned a confident call on public data alone.")
        print(("These lead the list once one question is answered "
               "(how many bookings arrive by phone or at the desk?):"))
    for p in scored:
        if p.recommendation != "CALL NOW":
            continue
        print(f"\n  {p.name}  ({p.city}, {p.rooms} rooms)")
        for r in p.reasons:
            print(f"    · {r}")

    if args.out:
        out = Path(args.out)
        csv_path = to_csv(scored, out / "prospect_scores.csv")
        (out / "prospect_scores.json").write_text(
            json.dumps([p.as_dict() for p in scored], indent=2))
        print(f"\n  written to {csv_path}")
        print(f"             {out / 'prospect_scores.json'}")
    return 0


def cmd_review(args) -> int:
    prospects = load_prospects(Path(args.input))
    scored = screen_all(prospects, fee_bdt=args.fee, media_bdt=args.media)
    match = [p for p in scored if args.name.lower() in p.name.lower()]
    if not match:
        print(f"no prospect matching '{args.name}'", file=sys.stderr)
        return 2
    p = match[0]
    out = build_review(p, Path(args.out) / f"{slugify(p.name)}_opportunity.docx",
                       fee_bdt=args.fee, media_bdt=args.media)
    print(f"{p.name}: {p.recommendation}")
    print(f"  commission/month  ৳{p.commission_bdt:,.0f}")
    print(f"  capturable/month  ৳{p.capturable_bdt:,.0f} (conservative 20% shift)")
    print(f"  lift needed       {p.lift_optimistic:.0%}–{p.lift_pessimistic:.0%} "
          f"(planning against the {p.lift_pessimistic:.0%} end)")
    print(f"  written to        {out}")
    return 0


def cmd_callsheet(args) -> int:
    prospects = load_prospects(Path(args.input))
    scored = screen_all(prospects, fee_bdt=args.fee, media_bdt=args.media)
    stem = Path(args.input).stem
    out = write_callsheet(
        scored,
        Path(args.out) / f"{stem}_call_sheet.md",
        fee_bdt=args.fee, media_bdt=args.media,
        city=args.city, source_file=args.input,
    )
    actionable = [p for p in scored if p.recommendation in
                  ("CALL NOW", "CONFIRM DIRECT VOLUME FIRST")]
    print(f"{len(actionable)} to work · "
          f"{sum(1 for p in scored if p.recommendation == 'CALL LATER')} parked · "
          f"{sum(1 for p in scored if p.recommendation == 'NOT A FIT')} screened out")
    print(f"  written to        {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="prospect", description="prospecting screener and leave-behind")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name, fn, helptext in (("screen", cmd_screen, "rank a prospect list"),
                               ("review", cmd_review, "build the one-page opportunity review"),
                               ("callsheet", cmd_callsheet, "write the markdown worklist for a screened list")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--input", required=True, help="prospect CSV")
        p.add_argument("--fee", type=float, default=19_000, help="monthly engagement fee (BDT)")
        p.add_argument("--media", type=float, default=50_000, help="monthly media budget (BDT)")
        p.add_argument("--out", default="prospect/reports")
        if name == "review":
            p.add_argument("--name", required=True, help="prospect name (partial match)")
        if name == "callsheet":
            p.add_argument("--city", default="Dhaka", help="city label used in the call sheet")
        p.set_defaults(func=fn)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except ProspectError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
