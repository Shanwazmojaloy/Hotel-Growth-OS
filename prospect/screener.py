"""Rank prospects by whether the engagement can work, before spending a call.

Why this exists: the day-45 kill criterion is three signed LOIs, which makes
prospecting the binding constraint on the whole plan. Cold-calling every hotel
in Cox's Bazar is a slow way to find the two that cannot work arithmetically.

Two outputs per prospect:
  * CAN IT WORK   — the feasibility verdict, reused from the measurement engine
                    so the pre-sale view and the post-hoc report cannot disagree
  * WHAT IS AT STAKE — commission paid per month, and the portion plausibly
                    capturable at a conservative shift rate

The "capturable" figure is deliberately conservative. Industry analysis puts the
shiftable share of OTA volume at roughly a fifth to a half; this uses a fifth.
Under-claiming in the pitch is what makes the first report believable.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from measurement.config import HotelConfig
from measurement.feasibility import Feasibility, assess

# Conservative default share of OTA volume that could plausibly shift to direct.
# Source: hotel-distribution analysis puts the shiftable share at 20-50% of OTA
# volume. We pitch the bottom of that range.
CONSERVATIVE_SHIFTABLE_SHARE = 0.20
SEASONAL_RATIO = 1.60   # same threshold the measurement spine uses

# Of the non-OTA volume, how much is direct vs walk-in/comps/contract. Used only
# when the prospect cannot state their direct volume.
#
# This single assumption does more to change the verdict than any other input —
# in testing it moved a real prospect from NOT_VIABLE to VIABLE. So it is never
# used as a point estimate: the screener recomputes the verdict across a band
# and, where the band straddles the threshold, refuses to give a confident
# answer until the direct volume is confirmed on the call.
ASSUMED_DIRECT_SHARE_OF_NON_OTA = 0.55
DIRECT_SHARE_BAND = (0.65, 1.0, 1.5)   # pessimistic, base, optimistic multipliers
DAYS_PER_MONTH = 30.44


class ProspectError(Exception):
    """Raised when a prospect row cannot be trusted."""


@dataclass
class Prospect:
    name: str
    city: str
    segment: str
    rooms: int
    adr_bdt: float
    occupancy: float
    ota_share: float
    effective_ota_commission: float
    direct_share: float | None = None          # None → derived, and flagged
    season_ratio: float = 1.0                  # peak/trough room-nights, if the prospect states one
    adr_basis: str = ""                        # "listed" (a live rate) | "class_avg" | ""
    rooms_status: str = "published"            # "published" | "disputed"
    assumed_fields: list[str] = field(default_factory=list)   # inputs we assumed, not measured
    source_id: str = ""
    contact: str = ""
    notes: str = ""

    # ---- derived
    total_room_nights: float = 0.0
    ota_room_nights: float = 0.0
    direct_room_nights: float = 0.0
    commission_bdt: float = 0.0
    saving_per_room_night: float = 0.0
    capturable_bdt: float = 0.0
    derived_direct_share: bool = False
    lift_pessimistic: float = 0.0
    lift_optimistic: float = 0.0
    recommendation: str = ""
    reasons: list[str] = field(default_factory=list)
    feasibility: Feasibility | None = None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "city": self.city,
            "segment": self.segment,
            "rooms": self.rooms,
            "adr_bdt": round(self.adr_bdt),
            "occupancy": round(self.occupancy, 3),
            "ota_share": round(self.ota_share, 3),
            "effective_ota_commission": round(self.effective_ota_commission, 4),
            "total_room_nights": round(self.total_room_nights),
            "ota_room_nights": round(self.ota_room_nights),
            "direct_room_nights": round(self.direct_room_nights),
            "commission_bdt": round(self.commission_bdt),
            "saving_per_room_night_bdt": round(self.saving_per_room_night),
            "capturable_bdt": round(self.capturable_bdt),
            "derived_direct_share": self.derived_direct_share,
            "season_ratio": round(self.season_ratio, 2),
            "adr_basis": self.adr_basis or "",
            "rooms_status": self.rooms_status,
            "assumed_fields": ";".join(self.assumed_fields),
            "source_id": self.source_id,
            "recommendation": self.recommendation,
            "reasons": self.reasons,
            "break_even_room_nights": round(self.feasibility.break_even_room_nights, 1)
            if self.feasibility else None,
            "required_lift": round(self.feasibility.required_lift_vs_current_direct, 3)
            if self.feasibility else None,
            "lift_pessimistic": round(self.lift_pessimistic, 3),
            "lift_optimistic": round(self.lift_optimistic, 3),
        }


REQUIRED_COLUMNS = ["name", "city", "segment", "rooms", "adr_bdt", "occupancy",
                    "ota_share", "effective_ota_commission"]


def _f(row: dict, key: str, path: Path) -> float:
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ProspectError(f"{path}: column '{key}' must be numeric (got {row.get(key)!r})") from exc


def load_prospects(path: Path) -> list[Prospect]:
    path = Path(path)
    if not path.exists():
        raise ProspectError(f"missing prospect file: {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = set(reader.fieldnames or [])
        missing = [c for c in REQUIRED_COLUMNS if c not in cols]
        if missing:
            raise ProspectError(f"{path}: missing columns {missing}")
        rows = [r for r in reader if (r.get("name") or "").strip()]
    if not rows:
        raise ProspectError(f"{path}: no prospect rows")

    out: list[Prospect] = []
    for r in rows:
        ds_raw = (r.get("direct_share") or "").strip()
        out.append(Prospect(
            name=r["name"].strip(),
            city=r["city"].strip(),
            segment=(r.get("segment") or "").strip(),
            rooms=int(_f(r, "rooms", path)),
            adr_bdt=_f(r, "adr_bdt", path),
            occupancy=_f(r, "occupancy", path),
            ota_share=_f(r, "ota_share", path),
            effective_ota_commission=_f(r, "effective_ota_commission", path),
            direct_share=float(ds_raw) if ds_raw else None,
            season_ratio=float((r.get("season_ratio") or "1").strip() or 1.0),
            adr_basis=(r.get("adr_basis") or "").strip(),
            rooms_status=(r.get("rooms_status") or "published").strip(),
            assumed_fields=[f.strip() for f in (r.get("assumed_fields") or "").split(";") if f.strip()],
            source_id=(r.get("source_id") or "").strip(),
            contact=(r.get("contact") or "").strip(),
            notes=(r.get("notes") or "").strip(),
        ))
    return out


def screen(prospect: Prospect, *, fee_bdt: float, media_bdt: float) -> Prospect:
    p = prospect

    if not 0 < p.occupancy <= 1:
        raise ProspectError(f"{p.name}: occupancy must be a fraction between 0 and 1 (got {p.occupancy})")
    if not 0 <= p.ota_share <= 1:
        raise ProspectError(f"{p.name}: ota_share must be between 0 and 1 (got {p.ota_share})")

    p.total_room_nights = p.rooms * DAYS_PER_MONTH * p.occupancy
    p.ota_room_nights = p.total_room_nights * p.ota_share

    if p.direct_share is None:
        p.direct_share = (1 - p.ota_share) * ASSUMED_DIRECT_SHARE_OF_NON_OTA
        p.derived_direct_share = True
    p.direct_room_nights = p.total_room_nights * p.direct_share

    p.commission_bdt = p.ota_room_nights * p.adr_bdt * p.effective_ota_commission
    p.saving_per_room_night = p.adr_bdt * (p.effective_ota_commission - 0.045)
    p.capturable_bdt = (
        p.ota_room_nights * CONSERVATIVE_SHIFTABLE_SHARE * p.saving_per_room_night
    )

    cfg = HotelConfig(
        slug="prospect", organization=p.name, property_name=p.name, city=p.city,
        rooms=p.rooms, adr_bdt=p.adr_bdt,
        effective_ota_commission=p.effective_ota_commission,
        direct_variable_cost=0.045, engagement_fee_bdt=fee_bdt,
        pilot_start=f"{date.today():%Y-%m}",
        target_incremental_room_nights=1,
    )
    p.feasibility = assess(cfg, media_bdt, p.direct_room_nights)

    # ---- sensitivity: how much does the answer depend on the assumption?
    def lift_under(multiplier: float) -> float:
        direct = max(1.0, p.direct_room_nights * multiplier)
        return p.feasibility.break_even_room_nights / direct

    p.lift_pessimistic = lift_under(DIRECT_SHARE_BAND[0])
    p.lift_optimistic = lift_under(DIRECT_SHARE_BAND[2])

    def verdict_for(lift: float) -> str:
        if lift > 0.60:
            return "NOT_VIABLE"
        if lift > 0.35:
            return "MARGINAL"
        return "VIABLE"

    # ---- recommendation, with the reasoning shown so it can be audited
    if verdict_for(p.lift_optimistic) == "NOT_VIABLE":
        p.recommendation = "NOT A FIT"
        p.reasons.append(
            f"break-even needs a {p.lift_optimistic:.0%} lift even on the most favourable reading of their "
            f"direct volume; above 60% is not a promise worth making"
        )
    elif p.capturable_bdt < 25_000:
        p.recommendation = "CALL LATER"
        p.reasons.append(
            f"only ৳{p.capturable_bdt:,.0f}/month plausibly capturable at a conservative "
            f"{CONSERVATIVE_SHIFTABLE_SHARE:.0%} shift — below the point where the fee is easy to justify"
        )
    elif (verdict_for(p.lift_pessimistic) == "VIABLE" and not p.derived_direct_share
          and not p.assumed_fields):
        p.recommendation = "CALL NOW"
        p.reasons.append(
            f"viable on confirmed numbers: break-even is {p.lift_pessimistic:.0%} of their stated direct "
            f"volume, with ৳{p.capturable_bdt:,.0f}/month capturable"
        )
    elif verdict_for(p.lift_pessimistic) == "VIABLE":
        # The economics work, but against inputs we assumed rather than were told. A confident
        # yes is a promise to the prospect, and a promise cannot rest on our own guess.
        blockers: list[str] = []
        if p.derived_direct_share:
            blockers.append("their direct volume was estimated, not confirmed")
        if p.assumed_fields:
            blockers.append("these inputs are assumptions: " + ", ".join(p.assumed_fields))
        p.recommendation = "CONFIRM DIRECT VOLUME FIRST"
        p.reasons.append(
            f"would be a call on the pessimistic reading ({p.lift_pessimistic:.0%} lift, "
            f"৳{p.capturable_bdt:,.0f}/month capturable) but " + "; ".join(blockers)
            + " — confirm them and this becomes a call"
        )
    elif p.lift_pessimistic > 0.70:
        # even a favourable reading needs an implausible lift — do not spend a call
        p.recommendation = "CALL LATER"
        p.reasons.append(
            f"needs a {p.lift_optimistic:.0%} lift on the best reading and {p.lift_pessimistic:.0%} on the "
            f"worst — too dependent on a favourable assumption to be worth a call this quarter"
        )
    else:
        p.recommendation = "CONFIRM DIRECT VOLUME FIRST"
        p.reasons.append(
            f"verdict depends on the assumption: break-even needs {p.lift_optimistic:.0%} of direct volume if "
            f"their direct channel is healthy, {p.lift_pessimistic:.0%} if it is weak. One question on the call "
            f"decides it — ask how many bookings arrive by phone or at the desk"
        )

    # ---- seasonal downgrade: a peak/trough ratio can only ever weaken a verdict.
    # The trough share is approximated as 2/(1+ratio); it is used to warn, never to
    # approve, so an approximation here cannot flatter a prospect.
    if p.season_ratio >= SEASONAL_RATIO and p.feasibility is not None:
        trough_share = 2.0 / (1.0 + p.season_ratio)
        trough_direct = p.direct_room_nights * trough_share
        trough_lift = (p.feasibility.break_even_room_nights / trough_direct
                       if trough_direct > 0 else 999.0)
        p.reasons.append(
            f"seasonal (peak/trough ratio {p.season_ratio:.1f}): in the weakest months the break-even needs "
            f"about a {trough_lift:.0%} lift — quote a season-weighted fee or an annual term, not a flat month"
        )
        if trough_lift > 0.60 and p.recommendation in ("CALL NOW", "CONFIRM DIRECT VOLUME FIRST"):
            p.recommendation = "CALL LATER"
            p.reasons.append(
                "on the seasonal arithmetic the weakest months cannot pay back at all — revisit only with a "
                "season-weighted structure"
            )

    # tells worth leading with on the call, independent of the verdict
    if p.effective_ota_commission >= 0.17:
        p.reasons.append(
            f"effective commission is {p.effective_ota_commission:.0%} — at the higher end, so the gap is worth "
            f"৳{p.saving_per_room_night:,.0f} per shifted room-night"
        )
    if p.ota_share >= 0.70:
        p.reasons.append(
            f"{p.ota_share:.0%} of room-nights come through OTAs — the dependency is the pain, and it is visible "
            "in their own statements"
        )
    if p.derived_direct_share:
        p.reasons.append(
            f"direct volume was estimated at {(1 - p.ota_share) * ASSUMED_DIRECT_SHARE_OF_NON_OTA:.0%} of "
            f"room-nights (never stated); ask how many bookings arrive by phone and at the desk"
        )
    if p.occupancy and p.occupancy < 0.45:
        p.reasons.append(
            f"occupancy {p.occupancy:.0%} is low — an empty-room problem, which is a different (and harder) "
            "conversation than a channel-mix problem"
        )
    return p


def screen_all(prospects: list[Prospect], *, fee_bdt: float, media_bdt: float) -> list[Prospect]:
    scored = [screen(p, fee_bdt=fee_bdt, media_bdt=media_bdt) for p in prospects]
    order = {"CALL NOW": 0, "CONFIRM DIRECT VOLUME FIRST": 1, "CALL LATER": 2, "NOT A FIT": 3}
    return sorted(scored, key=lambda p: (order[p.recommendation], -p.capturable_bdt))


def to_csv(prospects: list[Prospect], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(prospects[0].as_dict().keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for p in prospects:
            row = p.as_dict()
            row["reasons"] = " | ".join(p.reasons)
            w.writerow(row)
    return path


def format_table(prospects: list[Prospect]) -> str:
    lines = []
    lines.append(f"{'RECOMMENDATION':<29} {'ROOMS':>5} {'COMMISSION/MO':>14} {'CAPTURABLE':>11} "
                 f"{'LIFT NEEDED':>13}  PROSPECT")
    lines.append("─" * 118)
    for p in prospects:
        rng = f"{p.lift_optimistic:.0%}–{p.lift_pessimistic:.0%}" if p.feasibility else "—"
        lines.append(
            f"{p.recommendation:<29} {p.rooms:>5} "
            f"{'৳' + format(round(p.commission_bdt), ','):>14} "
            f"{'৳' + format(round(p.capturable_bdt), ','):>11} {rng:>12}  {p.name[:44]}"
        )
    lines.append("─" * 118)
    assumed = [p for p in prospects if p.assumed_fields or p.derived_direct_share]
    if assumed:
        fields = sorted({f for p in assumed for f in p.assumed_fields})
        lines.append(
            f"  {len(assumed)} of {len(prospects)} rows rest on assumed or unconfirmed inputs"
            + (f" ({', '.join(fields)})" if fields else "")
            + " — none of them can be CALL NOW by rule"
        )
    return "\n".join(lines)
