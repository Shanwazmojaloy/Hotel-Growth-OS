"""Incremental direct room-nights — the primary metric, computed conservatively.

Two designs are implemented. Both are deliberately pessimistic, because a
number the hotel can verify is worth more than a number that flatters us.

  pre_post                    observed vs the same window last year, adjusted by
                              a market trend factor. No haircut: the previous
                              year IS the counterfactual. Weakest defensible
                              design; used when nothing better is available.
  conservative_attribution    campaign-attributed direct room-nights, reduced by
                              the agreed haircut (the share assumed to have
                              happened anyway).

  geo_holdout                 NOT implemented. It is the strongest design, and
                              silently approximating it would be worse than
                              refusing: it raises rather than guessing.

Every result carries its inputs so the report can state its own assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .config import HotelConfig


class DesignNotImplemented(Exception):
    """Raised instead of silently approximating a design we cannot compute."""


@dataclass
class IncrementalResult:
    design: str
    attributed_room_nights: float
    observed_direct_room_nights: float
    expected_direct_room_nights: float
    incremental_room_nights: float
    haircut_applied: float
    value_bdt: float
    method_statement: str
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "design": self.design,
            "attributed_room_nights": round(self.attributed_room_nights, 1),
            "observed_direct_room_nights": round(self.observed_direct_room_nights, 1),
            "expected_direct_room_nights": round(self.expected_direct_room_nights, 1),
            "incremental_room_nights": round(self.incremental_room_nights, 1),
            "haircut_applied": self.haircut_applied,
            "value_bdt": round(self.value_bdt),
            "method_statement": self.method_statement,
            "notes": self.notes,
        }


def _month_of(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def _shift_year(month: str, years: int) -> str:
    year, mon = month.split("-")
    return f"{int(year) + years:04d}-{mon}"


def window_months(start: str, through: str) -> list[str]:
    """Inclusive list of YYYY-MM from start to through."""
    sy, sm = (int(x) for x in start.split("-"))
    ty, tm = (int(x) for x in through.split("-"))
    out, y, m = [], sy, sm
    while (y, m) <= (ty, tm):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def direct_room_nights_by_month(bookings: list[dict], *, attributed_only: bool) -> dict[str, float]:
    totals: dict[str, float] = {}
    for b in bookings:
        is_direct = b["channel"] in {"direct", "phone"}
        if not is_direct:
            continue
        if attributed_only and not b["campaign_attributed"]:
            continue
        key = _month_of(b["date"])
        totals[key] = totals.get(key, 0.0) + b["room_nights"]
    return totals


def compute(
    bookings: list[dict],
    cfg: HotelConfig,
    months: list[str],
) -> IncrementalResult:
    design = cfg.counterfactual_design

    if design == "geo_holdout":
        raise DesignNotImplemented(
            "geo_holdout requires matched control locations which this CSV schema does not carry. "
            "Either supply region-level data and implement the comparison, or change the signed plan "
            "to pre_post. Refusing rather than approximating."
        )

    all_direct = direct_room_nights_by_month(bookings, attributed_only=False)
    attributed = direct_room_nights_by_month(bookings, attributed_only=True)

    observed = sum(all_direct.get(m, 0.0) for m in months)
    attributed_rn = sum(attributed.get(m, 0.0) for m in months)

    if design == "pre_post":
        baseline_month_set = [_shift_year(m, -1) for m in months]
        baseline = sum(all_direct.get(m, 0.0) for m in baseline_month_set)
        expected = baseline * cfg.market_trend_factor
        incremental = max(0.0, observed - expected)
        statement = (
            f"Observed direct room-nights ({observed:,.0f}) less the same window last year "
            f"({baseline:,.0f}) adjusted by a market trend factor of {cfg.market_trend_factor:.3f} "
            f"= {expected:,.0f} expected. Difference counted as incremental."
        )
        notes = [
            "No haircut is applied to this design: last year's performance is itself the counterfactual.",
            f"Trend factor {cfg.market_trend_factor:.3f} is an agreed input from the signed measurement plan, "
            "not a fitted value.",
        ]
        haircut = 0.0
    elif design == "conservative_attribution":
        incremental = attributed_rn * (1 - cfg.haircut_factor)
        expected = observed - incremental
        statement = (
            f"Campaign-attributed direct room-nights ({attributed_rn:,.0f}) reduced by the agreed haircut "
            f"of {cfg.haircut_factor:.0%}, on the assumption that the remainder would have booked anyway."
        )
        notes = ["Attribution design: the haircut is doing the work of a counterfactual, so it must be "
                 "conservative. It is set in the signed plan, not chosen after the result."]
        haircut = cfg.haircut_factor
    else:
        raise DesignNotImplemented(f"unknown counterfactual design '{design}'")

    return IncrementalResult(
        design=design,
        attributed_room_nights=attributed_rn,
        observed_direct_room_nights=observed,
        expected_direct_room_nights=expected,
        incremental_room_nights=incremental,
        haircut_applied=haircut,
        value_bdt=incremental * cfg.saving_per_room_night(),
        method_statement=statement,
        notes=notes,
    )


def cross_check(bookings: list[dict], cfg: HotelConfig, months: list[str]) -> IncrementalResult | None:
    """Always compute the *other* design as a disclosed cross-check.

    A result that only survives under one method should be seen to only survive
    under one method — by the hotel, before they ask.
    """
    other = "conservative_attribution" if cfg.counterfactual_design != "conservative_attribution" else "pre_post"
    shadow = HotelConfig(**{**cfg.__dict__, "counterfactual_design": other})
    try:
        return compute(bookings, shadow, months)
    except DesignNotImplemented:
        return None
