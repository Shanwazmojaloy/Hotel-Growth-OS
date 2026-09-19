"""CLI.

  python3 -m measurement.cli report    --hotel data/hotel_seabreeze --through 2025-12 --out reports/
  python3 -m measurement.cli feasibility --hotel data/hotel_seabreeze --media 50000
  python3 -m measurement.cli check     --hotel data/hotel_seabreeze
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import audit
from .baseline import build_baseline, build_docx as build_baseline_docx
from .config import HotelConfig
from .counterfactual import direct_room_nights_by_month, window_months
from .feasibility import assess
from .seasonality import assess_payback, build_profile, combined_verdict
from .ingest import DataError, load_hotel
from .report import analyse, build_docx, to_json


def _load(data_dir: Path) -> tuple[HotelConfig, dict]:
    cfg = HotelConfig.load(data_dir / "hotel.json")
    problems = cfg.validate()
    if problems:
        print("configuration problems:", file=sys.stderr)
        for p in problems:
            print(f"  ✘ {p}", file=sys.stderr)
        raise SystemExit(2)
    return cfg, load_hotel(data_dir)


def cmd_check(args) -> int:
    cfg, loaded = _load(Path(args.hotel))
    print(f"{cfg.property_name} ({cfg.city}) — {cfg.rooms} rooms, ADR ৳{cfg.adr_bdt:,.0f}")
    print(f"counterfactual: {cfg.counterfactual_design}   commission: {cfg.effective_ota_commission:.1%}")
    print("inputs:")
    for s in loaded["sources"]:
        print(f"  · {s.describe()}")
    return 0


def cmd_feasibility(args) -> int:
    cfg, loaded = _load(Path(args.hotel))
    months = window_months(cfg.pilot_start, args.through or cfg.pilot_start)
    baseline = [f"{int(m[:4]) - 1:04d}-{m[5:]}" for m in months]
    direct = sum(b["room_nights"] for b in loaded["bookings"]
                 if f"{b['date']:%Y-%m}" in baseline and b["channel"] in {"direct", "phone"})
    direct /= max(1, len(months))
    f = assess(cfg, args.media, direct)

    # the annual average is not the question: the fee is charged in every month
    profile = build_profile({r["month"]: float(r["total_room_nights"]) for r in loaded["pms"]})
    total_pms_rn = sum(float(r["total_room_nights"]) for r in loaded["pms"])
    total_ota_rn = sum(float(r["room_nights"]) for r in loaded["ota"])
    direct_by_month = direct_room_nights_by_month(loaded["bookings"], attributed_only=False)
    direct_history_mean = (sum(direct_by_month.values()) / len(direct_by_month)
                           if direct_by_month else direct)
    payback = assess_payback(profile, break_even_room_nights=f.break_even_room_nights,
                             direct_rn_per_month=direct_history_mean,
                             ota_share=(total_ota_rn / total_pms_rn) if total_pms_rn else 0.0)
    verdict = combined_verdict(f.verdict, payback)

    print(f"Feasibility — {cfg.property_name}")
    print(f"  monthly cost (fee + media)   ৳{f.monthly_cost_bdt:,.0f}")
    print(f"  commission saved per room-night ৳{f.saving_per_room_night_bdt:,.0f}")
    print(f"  break-even incremental room-nights  {f.break_even_room_nights:,.1f} / month")
    print(f"  = {f.break_even_share_of_direct_volume:.0%} of current direct volume")
    print(f"  on the average month: {f.verdict}")
    print()
    print(f"  seasonality: peak/trough ratio {profile.ratio:.2f}"
          f"{' (seasonal)' if profile.is_seasonal else ' (not materially seasonal)'}"
          f" · {profile.reliability}")
    print(f"  months that can pay back: {payback.months_feasible} of {payback.months_total}")
    if payback.impossible_months:
        print(f"  cannot pay back: {', '.join(payback.impossible_months)}")
    print(f"  verdict on the fee as sold: {verdict}")
    for r in f.reasons + payback.reasons:
        print(f"    · {r}")
    return 0 if verdict not in {"NOT_VIABLE", "SEASONAL_MISMATCH"} else 1


def cmd_audit(args) -> int:
    cfg, loaded = _load(Path(args.hotel))
    res = audit(cfg, loaded)
    print(f"Data audit — {cfg.property_name}  [{res.verdict}]  ({res.checks_run} checks)")
    print(f"  {res.summary}")
    if res.findings:
        print()
        for f in sorted(res.findings, key=lambda f: {"BLOCKER": 0, "WARNING": 1, "NOTE": 2}[f.severity]):
            mark = {"BLOCKER": "✘", "WARNING": "!", "NOTE": "·"}[f.severity]
            print(f"  {mark} [{f.severity}] {f.check}: {f.headline}")
            print(f"      evidence: {f.evidence}")
            print(f"      fix:      {f.fix}")
    if args.json:
        Path(args.json).write_text(json.dumps(res.as_dict(), indent=2))
        print(f"\n  json written to {args.json}")
    return 0 if res.verdict != "BLOCKED" else 1


def cmd_baseline(args) -> int:
    cfg, loaded = _load(Path(args.hotel))
    b = build_baseline(cfg, loaded)
    out_dir = Path(args.out) / cfg.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    docx_path = build_baseline_docx(cfg, b, out_dir / "baseline.docx", loaded["pms"])
    (out_dir / "baseline.json").write_text(json.dumps(b.as_dict(), indent=2))
    print(f"Baseline — {cfg.property_name}  ({b.window}, {b.months_of_history} months)")
    print(f"  occupancy {b.occupancy:.1%} · ADR ৳{b.adr_bdt:,.0f} · RevPAR ৳{b.revpar_bdt:,.0f}")
    print(f"  OTA share {b.ota_share:.0%} · effective commission {b.effective_ota_commission:.1%} "
          f"(৳{b.ota_commission_bdt:,.0f} paid)")
    print(f"  direct {b.direct_room_nights_per_month:,.1f} room-nights/month "
          f"({b.direct_room_nights_per_room_per_month:.2f} per room)")
    print(f"  written to {docx_path}")
    return 0


def cmd_hours(args) -> int:
    """Summarise the onboarding hours log — the metric that decides the margin."""
    import csv as _csv
    path = Path(args.log)
    if not path.exists():
        print(f"no log at {path}. Start one — margin is decided by these hours.", file=sys.stderr)
        return 2
    with path.open(newline="", encoding="utf-8") as fh:
        rows = [r for r in _csv.DictReader(fh) if (r.get("minutes") or "").strip()]
    by_step: dict[str, float] = {}
    by_hotel: dict[str, float] = {}
    for r in rows:
        mins = float(r["minutes"])
        by_step[r["step"]] = by_step.get(r["step"], 0.0) + mins
        by_hotel[r["hotel"]] = by_hotel.get(r["hotel"], 0.0) + mins
    print("Onboarding hours")
    for hotel, mins in sorted(by_hotel.items()):
        flag = " ← at or under the 8-hour target" if mins / 60 <= 8 else ""
        print(f"  {hotel:24s} {mins / 60:6.1f} hrs{flag}")
    print("\nBy step (worst first — this is your automation backlog, in order):")
    for step, mins in sorted(by_step.items(), key=lambda kv: -kv[1]):
        print(f"  {mins / 60:6.1f} hrs  {step}")
    return 0


def cmd_report(args) -> int:
    cfg, loaded = _load(Path(args.hotel))
    through = args.through or cfg.pilot_start
    analysis = analyse(cfg, loaded, through)

    out_dir = Path(args.out) / cfg.slug
    docx_path = build_docx(analysis, loaded, out_dir / f"{through}_report.docx")
    json_path = out_dir / f"{through}_report.json"
    json_path.write_text(to_json(analysis))

    dec = analysis["decision"]
    inc = analysis["incremental"]
    spend = analysis["spend"]["total_bdt"]
    print(f"{cfg.property_name} — {analysis['months'][0]} → {through} ({len(analysis['months'])} months)")
    print(f"  incremental direct room-nights : {inc.incremental_room_nights:,.0f} "
          f"(target {analysis['target_room_nights']:,.0f}, break-even "
          f"{analysis['feasibility'].break_even_room_nights:,.0f})")
    print(f"  value / cost / net             : ৳{inc.value_bdt:,.0f} / ৳{spend:,.0f} / "
          f"৳{inc.value_bdt - spend:,.0f}")
    print(f"  data quality                   : {analysis['reconciliation'].data_quality}")
    print(f"  VERDICT                        : {dec.verdict} — {dec.headline}")
    print(f"  written to                     : {docx_path}")
    print(f"                                   {json_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="measurement", description="Hotel Growth OS measurement spine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("report", help="build the monthly report")
    p.add_argument("--hotel", required=True, help="directory containing hotel.json and the CSV inputs")
    p.add_argument("--through", help="last month of the window, YYYY-MM (default: pilot_start)")
    p.add_argument("--out", default="reports", help="output directory")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("feasibility", help="should this property be signed at all?")
    p.add_argument("--hotel", required=True)
    p.add_argument("--media", type=float, required=True, help="planned monthly media budget (BDT)")
    p.add_argument("--through")
    p.set_defaults(func=cmd_feasibility)

    p = sub.add_parser("check", help="validate inputs and show what was found")
    p.add_argument("--hotel", required=True)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("audit", help="pre-onboarding data audit (BLOCKED exits non-zero)")
    p.add_argument("--hotel", required=True)
    p.add_argument("--json", help="also write the findings as JSON here")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("baseline", help="build the measurement plan §2 baseline from the exports")
    p.add_argument("--hotel", required=True)
    p.add_argument("--out", default="reports")
    p.set_defaults(func=cmd_baseline)

    p = sub.add_parser("hours", help="summarise the onboarding hours log")
    p.add_argument("--log", default="onboarding/hours.csv")
    p.set_defaults(func=cmd_hours)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except DataError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
