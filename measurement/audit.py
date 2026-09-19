"""Pre-onboarding data audit — find the problems before they cost you a month.

Onboarding hours are the binding constraint on margin, and a large share of them
are not spent on the hotel: they are spent discovering, three weeks in, that
conversions were never firing, that a month of OTA statements is missing, or
that the attribution flag is being set on everything. This module finds those in
seconds, from the exports the hotel already has.

Verdicts:
  READY       nothing blocking; start the engagement
  NEEDS_WORK  proceed, but fix the listed items before trusting the primary metric
  BLOCKED     do not start; the data cannot support the measurement plan yet

Exit code is non-zero on BLOCKED, so this can gate a kickoff.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from .config import HotelConfig
from .counterfactual import window_months
from .feasibility import assess
from .seasonality import assess_payback, build_profile


SEVERITY_ORDER = {"BLOCKER": 0, "WARNING": 1, "NOTE": 2}


@dataclass
class Finding:
    check: str
    severity: str          # BLOCKER | WARNING | NOTE
    headline: str
    evidence: str
    fix: str

    def as_dict(self) -> dict:
        return {
            "check": self.check,
            "severity": self.severity,
            "headline": self.headline,
            "evidence": self.evidence,
            "fix": self.fix,
        }


@dataclass
class AuditResult:
    verdict: str
    findings: list[Finding] = field(default_factory=list)
    checks_run: int = 0
    summary: str = ""

    def blockers(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "BLOCKER"]

    def as_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "checks_run": self.checks_run,
            "summary": self.summary,
            "findings": [f.as_dict() for f in
                         sorted(self.findings, key=lambda f: SEVERITY_ORDER[f.severity])],
        }


# --------------------------------------------------------------------- helpers
def _pearson(xs: list[float], ys: list[float]) -> float:
    n = min(len(xs), len(ys))
    if n < 3:
        return 0.0
    xs, ys = xs[:n], ys[:n]
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = sum((a - mx) ** 2 for a in xs) ** 0.5
    dy = sum((b - my) ** 2 for b in ys) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def _longest_zero_run(daily: dict[str, float], start: date, end: date) -> tuple[int, str]:
    run = best = 0
    best_start = cur_start = start.isoformat()
    d = start
    while d <= end:
        key = d.isoformat()
        if daily.get(key, 0.0) == 0:
            if run == 0:
                cur_start = key
            run += 1
            if run > best:
                best, best_start = run, cur_start
        else:
            run = 0
        d += timedelta(days=1)
    return best, best_start


# ------------------------------------------------------------------- the audit
def audit(cfg: HotelConfig, loaded: dict) -> AuditResult:
    res = AuditResult(verdict="READY")
    bookings = loaded["bookings"]
    ga4 = loaded["ga4"]
    gsc = loaded["gsc"]
    pms = loaded["pms"]
    ota = loaded["ota"]
    spend = loaded["spend"]

    pilot_months = window_months(cfg.pilot_start, max(p["month"] for p in pms))
    spend_months = {s["month"] for s in spend if s["spend_bdt"] > 0}

    # ---------------------------------------------------------- 1. completeness
    res.checks_run += 1
    all_days = [b["date"] for b in bookings]
    span_start, span_end = min(all_days), max(all_days)
    daily_rn: dict[str, float] = {}
    for b in bookings:
        daily_rn[b["date"].isoformat()] = daily_rn.get(b["date"].isoformat(), 0.0) + b["room_nights"]
    gap, gap_start = _longest_zero_run(daily_rn, span_start, span_end)
    if gap >= 3:
        res.findings.append(Finding(
            "completeness",
            "BLOCKER",
            f"{gap} consecutive days with zero bookings",
            f"{gap_start} onwards. A run of zero days inside a period that otherwise has volume is an export "
            f"or tracking outage, not a business event.",
            "Confirm with the property whether those dates were genuinely closed. If not, re-export before "
            "doing anything else — every metric downstream inherits the hole.",
        ))
    elif gap == 2:
        res.findings.append(Finding(
            "completeness", "WARNING", "2 consecutive days with zero bookings",
            f"{gap_start}. Could be real (a closure) or a gap.",
            "Ask the property. If unexplained, re-export.",
        ))

    # ---------------------------------------------------------- 2. freshness
    res.checks_run += 1
    today = max([b["date"] for b in bookings] + [g["date"] for g in ga4])
    staleness = (today - span_end).days
    ga4_stale = (max(g["date"] for g in ga4) - span_end).days
    if ga4_stale > 3:
        res.findings.append(Finding(
            "freshness", "WARNING",
            f"GA4 export ends {ga4_stale} days before the booking export",
            f"Bookings end {span_end}, analytics end {max(g['date'] for g in ga4)}.",
            "Re-export both from the same date. Mismatched windows make every ratio misleading.",
        ))

    # ---------------------------------------------------------- 3. attribution coverage
    res.checks_run += 1
    for month in sorted(pilot_months):
        month_bookings = [b for b in bookings if f"{b['date']:%Y-%m}" == month]
        direct = [b for b in month_bookings if b["channel"] in {"direct", "phone"}]
        if not direct:
            continue
        covered = sum(b["room_nights"] for b in direct if b["campaign_attributed"])
        total = sum(b["room_nights"] for b in direct)
        share = covered / total if total else 0.0
        has_spend = month in spend_months
        if has_spend and share > 0.70:
            res.findings.append(Finding(
                "attribution", "BLOCKER",
                f"{share:.0%} of direct room-nights are flagged campaign-attributed in {month}",
                "Attribution coverage above ~70% means the flag is being set by something broader than "
                "campaign touchpoints — a site-wide UTM, a default, or a tagging rule.",
                "Audit how the flag is set. Over-attribution inflates the primary metric under the "
                "attribution design and destroys its credibility under cross-check.",
            ))
        elif has_spend and share < 0.10:
            res.findings.append(Finding(
                "attribution", "BLOCKER",
                f"only {share:.0%} of direct room-nights are campaign-attributed in {month}, while media "
                f"spend was recorded",
                "Spend with almost no attributable bookings usually means the booking engine is not passing "
                "campaign data, or the conversion is firing on the wrong step.",
                "Verify the campaign parameter survives to the booking confirmation and is stored on the "
                "booking record. This is the single highest-value hour in onboarding.",
            ))
        elif not has_spend and share > 0.25:
            res.findings.append(Finding(
                "attribution", "NOTE",
                f"{share:.0%} of direct room-nights are attributed in {month} with no media spend recorded",
                "Pre-pilot months should show near-zero attribution.",
                "Either spend exists outside this feed, or the flag is set too broadly. Both matter.",
            ))

    # ---------------------------------------------------------- 4. conversion fidelity
    # Measured over the PILOT WINDOW, not the whole history. A correlation across
    # fifteen months is dominated by seasonality and stays respectable even when
    # the conversion event has been broken since the campaign started — which is
    # exactly the failure this check exists to catch.
    res.checks_run += 1
    by_day_conv: dict[str, float] = {}
    for g in ga4:
        key = g["date"].isoformat()
        by_day_conv[key] = by_day_conv.get(key, 0.0) + g["conversions"]
    by_day_direct: dict[str, float] = {}
    for b in bookings:
        if b["channel"] in {"direct", "phone"}:
            key = b["date"].isoformat()
            by_day_direct[key] = by_day_direct.get(key, 0.0) + b["room_nights"]
    pilot_set = set(pilot_months)
    in_window = {d for d in set(by_day_conv) & set(by_day_direct) if d[:7] in pilot_set}
    all_shared = set(by_day_conv) & set(by_day_direct)
    days = sorted(in_window) if len(in_window) >= 14 else sorted(all_shared)
    corr = _pearson([by_day_conv[d] for d in days], [by_day_direct[d] for d in days])
    if days and corr < 0.15:
        res.findings.append(Finding(
            "conversion fidelity", "BLOCKER",
            f"analytics conversions barely track actual bookings (correlation {corr:.2f})",
            f"Across {len(days)} shared days in the pilot window, analytics conversions move almost "
            f"independently of booked direct room-nights.",
            "Find out what the conversion event actually fires on. Until conversions and bookings move "
            "together, no optimisation based on platform-reported conversions is meaningful.",
        ))
    elif days and corr < 0.35:
        res.findings.append(Finding(
            "conversion fidelity", "WARNING",
            f"conversions and bookings correlate only {corr:.2f}",
            "Weak but non-zero: the event is firing, imprecisely.",
            "Check for duplicate events, thank-you-page reloads, and offline/phone bookings that inflate or "
            "deflate the comparison.",
        ))
    else:
        res.findings.append(Finding(
            "conversion fidelity", "NOTE",
            f"conversions track bookings (correlation {corr:.2f})",
            f"Across {len(days)} shared days.",
            "No action. Keep it in the monthly report as a sanity check.",
        ))

    # ---------------------------------------------------------- 5. reconciliation pre-check
    res.checks_run += 1
    pms_rn = sum(p["total_room_nights"] for p in pms)
    ota_rn = sum(o["room_nights"] for o in ota)
    engine_direct = sum(b["room_nights"] for b in bookings if b["channel"] in {"direct", "phone"})
    ota_months = {o["month"] for o in ota}
    missing_ota = [m for m in pilot_months if m not in ota_months]
    if missing_ota:
        res.findings.append(Finding(
            "reconciliation", "BLOCKER",
            f"OTA statements missing for {len(missing_ota)} month(s) of the pilot window",
            f"Missing: {', '.join(missing_ota)}. The effective commission rate — the economic basis of the "
            f"engagement — is computed from these statements.",
            "Obtain the statements before kickoff. Without them the saving per room-night is a guess.",
        ))
    implied_ota = max(0.0, pms_rn - engine_direct - sum(b["room_nights"] for b in bookings if b["channel"] != "direct" and b["channel"] != "phone") * 0)
    engine_ota = sum(b["room_nights"] for b in bookings if b["channel"] not in {"direct", "phone"})
    if ota_rn and engine_ota:
        spread = abs(ota_rn - engine_ota) / max(ota_rn, engine_ota)
        if spread > 0.15:
            res.findings.append(Finding(
                "reconciliation", "WARNING",
                f"OTA room-nights differ {spread:.0%} between statements and the booking engine",
                f"Statements: {ota_rn:,.0f}. Booking engine: {engine_ota:,.0f}.",
                "Usually a dating difference (booking date vs stay date) or cancellations landing in one "
                "system first. Establish which the property treats as authoritative before reporting.",
            ))

    # ---------------------------------------------------------- 6. baseline sufficiency
    res.checks_run += 1
    pms_months = sorted({p["month"] for p in pms})
    if pilot_months and pms_months:
        pre_pilot = [m for m in pms_months if m < pilot_months[0]]
        if len(pre_pilot) < 12:
            res.findings.append(Finding(
                "baseline", "WARNING",
                f"only {len(pre_pilot)} month(s) of history before the pilot window",
                "The pre/post design compares against the same window last year. Sparse history weakens it and "
                "may push the plan to a weaker design.",
                "Ask for 12 months where records exist. If unavailable, agree a conservative attribution design "
                "in the plan rather than pretending to a baseline you do not have.",
            ))

    # ---------------------------------------------------------- 7. ADR outliers
    res.checks_run += 1
    outliers = []
    for b in bookings:
        if b["room_nights"] > 0 and cfg.adr_bdt > 0:
            implied = b["revenue_bdt"] / b["room_nights"]
            if implied > cfg.adr_bdt * 4 or (implied < cfg.adr_bdt * 0.25 and implied > 0):
                outliers.append((b["date"].isoformat(), implied))
    if outliers:
        res.findings.append(Finding(
            "data quality",
            "WARNING" if len(outliers) >= 3 else "NOTE",
            f"{len(outliers)} booking(s) imply a rate far from the stated ADR",
            f"Examples: " + "; ".join(f"{d} → ৳{v:,.0f}" for d, v in outliers[:4]),
            "Usually currency mix-ups, deposits recorded as revenue, or package rates. Clean before using ADR "
            "as a denominator anywhere.",
        ))

    # ---------------------------------------------------------- 8. spend coverage
    res.checks_run += 1
    missing_spend = [m for m in pilot_months if m not in spend_months]
    if missing_spend:
        res.findings.append(Finding(
            "spend coverage", "NOTE",
            f"no media spend recorded for {len(missing_spend)} pilot month(s)",
            f"Missing: {', '.join(missing_spend)}.",
            "Expected before the engagement starts. Confirm the spend feed will be populated from month one — "
            "cost per incremental booking cannot be computed without it.",
        ))

    # ---------------------------------------------------------- 9. economics pre-check
    res.checks_run += 1
    monthly_direct = engine_direct / max(1, len(pms_months))
    media_assumed = 50_000.0
    feas = assess(cfg, media_assumed, monthly_direct)
    if feas.verdict == "NOT_VIABLE":
        res.findings.append(Finding(
            "economics", "BLOCKER",
            f"the unit economics do not support this engagement: {feas.verdict}",
            f"Break-even needs {feas.break_even_room_nights:,.1f} incremental room-nights/month "
            f"({feas.required_lift_vs_current_direct:.0%} of current direct volume) at an assumed "
            f"৳{media_assumed:,.0f} media budget.",
            "Do not sign this property on this plan. Either reduce the fee/media to a level the property's "
            "volume can support, or decline — a NOT_VIABLE engagement produces a STOP report in three months.",
        ))
    elif feas.verdict == "MARGINAL":
        res.findings.append(Finding(
            "economics", "WARNING",
            f"economics are marginal: break-even is {feas.required_lift_vs_current_direct:.0%} of current "
            f"direct volume",
            f"{feas.reasons[0]}",
            "Sign only with an explicitly lower fee or media budget, and tell the property up front that the "
            "honest answer may take two or three windows.",
        ))

    # ------------------------------------------------------- 10. seasonality
    # The fee is charged in every month, so a hotel whose year has two different
    # businesses cannot be judged on its average month.
    res.checks_run += 1
    profile = build_profile({r["month"]: float(r["total_room_nights"]) for r in pms})
    direct_by_month: dict[str, float] = {}
    for b in bookings:
        if b["channel"] in {"direct", "phone"}:
            mk = f"{b['date']:%Y-%m}"
            direct_by_month[mk] = direct_by_month.get(mk, 0.0) + b["room_nights"]
    direct_mean = (sum(direct_by_month.values()) / len(direct_by_month)
                   if direct_by_month else monthly_direct)
    total_pms_rn = sum(float(r["total_room_nights"]) for r in pms)
    total_ota_rn = sum(float(r["room_nights"]) for r in ota)
    ota_share = (total_ota_rn / total_pms_rn) if total_pms_rn else 0.0

    if profile.reliability == "insufficient":
        res.findings.append(Finding(
            "seasonality", "WARNING",
            f"only {profile.months_observed} months of history — seasonality cannot be assessed",
            f"Peak-to-trough ratio {profile.ratio:.2f} over {profile.months_observed} months is not a seasonal "
            f"pattern; it may be a trend, or noise.",
            "Twelve months of history are needed before a pilot window can be compared against the same season "
            "a year earlier. Ask for the earlier exports, or state in the measurement plan that the first "
            "window's result is unadjusted for season.",
        ))
    elif profile.reliability == "partial":
        res.findings.append(Finding(
            "seasonality", "NOTE",
            "the history is missing calendar months",
            f"{profile.months_observed} months observed with at least one calendar month absent, so the seasonal "
            f"index ({profile.ratio:.2f} peak-to-trough) is built from an incomplete year.",
            "Fill the gaps before the first window closes, or accept a wider seasonal band in the report.",
        ))

    if profile.is_seasonal:
        payback = assess_payback(profile, break_even_room_nights=feas.break_even_room_nights,
                                 direct_rn_per_month=direct_mean, ota_share=ota_share)
        if payback.verdict == "SEASONAL_MISMATCH":
            res.findings.append(Finding(
                "seasonality", "WARNING",
                f"the engagement can only pay back in {payback.months_feasible} of {payback.months_total} months",
                f"Peak-to-trough ratio {profile.ratio:.2f}. Break-even needs "
                f"{feas.break_even_room_nights:,.0f} incremental room-nights a month; "
                f"{', '.join(payback.impossible_months[:6])} cannot produce them. "
                f"A flat monthly fee would be charged through months the property cannot earn in.",
                "Quote a season-weighted fee or an annual term rather than a flat monthly fee, and say so before "
                "signing. The annual average is the number that hides this.",
            ))
        elif payback.verdict == "SEASONAL":
            res.findings.append(Finding(
                "seasonality", "NOTE",
                f"seasonal business: break-even is producible in {payback.months_feasible} of "
                f"{payback.months_total} months",
                f"Peak-to-trough ratio {profile.ratio:.2f}. Weakest months: "
                f"{', '.join(payback.impossible_months[:4]) or 'none'}. A flat monthly fee is defensible only "
                f"because the fee is small relative to the seasonal swing.",
                "Report results by season, and consider front-loading activity into the months that can pay back.",
            ))

    # ---------------------------------------------------------------- verdict
    blockers = res.blockers()
    if blockers:
        res.verdict = "BLOCKED"
        res.summary = (
            f"{len(blockers)} blocker(s) found. Do not start the engagement until these are resolved — each "
            f"one would corrupt the primary metric."
        )
    elif any(f.severity == "WARNING" for f in res.findings):
        res.verdict = "NEEDS_WORK"
        res.summary = (
            f"{sum(1 for f in res.findings if f.severity == 'WARNING')} warning(s). Proceed, but fix these "
            f"before the first report is treated as evidence."
        )
    else:
        res.verdict = "READY"
        res.summary = "No blocking issues. The data can support the signed measurement plan."
    res.checks_run = res.checks_run
    return res
