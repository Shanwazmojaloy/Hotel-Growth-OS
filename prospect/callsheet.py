"""Turn a scored prospect list into the document you actually work from.

The screener decides *who* is worth a call. This writes the sheet you hold while
making it: the ranked order, the number to lead with (computed, never guessed),
exactly which inputs are assumptions to confirm on the call, and the rows that
were screened out so the discipline is visible rather than implied.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from .screener import Prospect, screen

ACTIONABLE = ("CALL NOW", "CONFIRM DIRECT VOLUME FIRST")


def _money(v: float) -> str:
    return f"৳{v:,.0f}"


def _basis_label(p: Prospect) -> str:
    parts = []
    if p.adr_basis == "listed":
        parts.append("rate from a live listing")
    elif p.adr_basis == "class_avg":
        parts.append("rate from a star-class average, not this hotel")
    else:
        parts.append("rate source unrecorded")
    if p.rooms_status == "disputed":
        parts.append("**room count disputed between sources**")
    return " · ".join(parts)


def _confirm_lines(p: Prospect) -> list[str]:
    lines: list[str] = []
    if p.derived_direct_share:
        lines.append("direct volume — ask how many bookings arrive by phone or at the desk")
    for f in p.assumed_fields:
        if f == "direct_share":
            lines.append("direct volume — ask how many bookings arrive by phone or at the desk")
        elif f == "occupancy":
            lines.append("occupancy — assumed at 52%, the national average (ask for theirs)")
        elif f == "ota_share":
            lines.append(f"OTA share — assumed at {p.ota_share:.0%} (ask what share of bookings arrive via platforms)")
        elif f == "commission":
            lines.append(f"effective commission — assumed at {p.effective_ota_commission:.1%} "
                         f"(ask what they pay all-in, including visibility programmes)")
        elif f == "adr":
            lines.append("average daily rate — ask for their ADR rather than the website's lowest room")
        else:
            lines.append(f)
    # de-duplicate, keep order
    seen, out = set(), []
    for line in lines:
        if line not in seen:
            seen.add(line)
            out.append(line)
    return out


def build_callsheet(scored: list[Prospect], *, fee_bdt: float, media_bdt: float,
                    city: str = "Dhaka", source_file: str = "") -> str:
    today = date.today().isoformat()
    actionable = [p for p in scored if p.recommendation in ACTIONABLE]
    parked = [p for p in scored if p.recommendation == "CALL LATER"]
    rejected = [p for p in scored if p.recommendation == "NOT A FIT"]

    L: list[str] = []
    L.append(f"# Call sheet — {city} independent hotels")
    L.append("")
    L.append(f"Generated {today} from `{source_file or 'the prospect file'}`, screened at a fee of "
             f"{_money(fee_bdt)}/month plus {_money(media_bdt)}/month of media.")
    L.append("")
    L.append(f"**{len(actionable)} to work · {len(parked)} parked · {len(rejected)} screened out** of {len(scored)} properties.")
    L.append("")

    if not any(p.recommendation == "CALL NOW" for p in scored):
        L.append("> **Nothing in this list earned a confident call.** Every row rests on at least one input that "
                 "public data could not supply — occupancy, OTA share, effective commission, or the hotel's direct "
                 "volume. That is not a defect in the list; it is the reason the first message asks a question "
                 "instead of making a pitch. The names below are ordered by how much money is plausibly in play. "
                 "Each becomes a call the moment those inputs are confirmed.")
        L.append("")

    # ---------------------------------------------------------------- the worklist
    L.append("## Work these, in order")
    L.append("")
    L.append("| # | Property | Area | Rooms | Commission/mo (est.) | Capturable/mo | Lift needed |")
    L.append("|---|---|---|---|---|---|---|")
    for i, p in enumerate(actionable, 1):
        flag = " ⚠" if (p.rooms_status == "disputed" or p.adr_basis != "listed") else ""
        L.append(f"| {i} | **{p.name}**{flag} | {p.city} | {p.rooms} | {_money(p.commission_bdt)} | "
                 f"{_money(p.capturable_bdt)} | {p.lift_optimistic:.0%}–{p.lift_pessimistic:.0%} |")
    L.append("")
    L.append("⚠ = room count disputed between sources, or the rate is a class average rather than this hotel's own "
             "listing. Verify before quoting anything from that row.")
    L.append("")

    for i, p in enumerate(actionable, 1):
        L.append(f"### {i}. {p.name} — {p.city}")
        L.append("")
        L.append(f"{p.rooms} rooms · {p.segment} · ADR {_money(p.adr_bdt)} ({_basis_label(p)})")
        L.append("")
        L.append(f"- **Commission estimate:** {_money(p.commission_bdt)}/month — about "
                 f"{_money(p.commission_bdt * 12)}/year")
        L.append(f"- **Conservatively capturable:** {_money(p.capturable_bdt)}/month "
                 f"({_money(p.capturable_bdt * 12)}/year) at a 20% shift of OTA volume")
        L.append(f"- **Break-even:** {p.feasibility.break_even_room_nights:,.0f} room-nights/month, a "
                 f"**{p.lift_optimistic:.0%}–{p.lift_pessimistic:.0%}** increase on their direct volume")
        L.append(f"- **Lead with:** \"On the figures I have, this property pays roughly "
                 f"{_money(p.commission_bdt)} a month in OTA commission — about {_money(p.commission_bdt * 12)} a "
                 f"year. The conservative prize is about {_money(p.capturable_bdt)} a month.\"")
        confirms = _confirm_lines(p)
        if confirms:
            L.append("- **Confirm on the call before quoting anything:**")
            for line in confirms:
                L.append(f"  - {line}")
        if p.notes:
            L.append(f"- **What is known:** {p.notes}")
        if p.source_id:
            L.append(f"- **Sources:** {p.source_id}")
        L.append("")
        L.append(f"- *Ask:* {_ask(p)}")
        L.append("")

    # ------------------------------------------------------------------ parked
    if parked:
        L.append("## Parked (CALL LATER)")
        L.append("")
        L.append("Revisit only if something changes — a rate, a room count, or a cheaper structure. Do not spend a "
                 "call this quarter.")
        L.append("")
        L.append("| Property | Rooms | Commission/mo | Lift needed | Why parked |")
        L.append("|---|---|---|---|---|")
        for p in parked:
            reason = next((r for r in p.reasons if "implausible" in r or "below the point" in r), "")
            L.append(f"| {p.name} | {p.rooms} | {_money(p.commission_bdt)} | "
                     f"{p.lift_optimistic:.0%}–{p.lift_pessimistic:.0%} | {reason or 'see screener output'} |")
        L.append("")

    # --------------------------------------------------------------- screened out
    if rejected:
        L.append("## Screened out (NOT A FIT)")
        L.append("")
        L.append("The arithmetic does not clear even on the most favourable reading. If asked, say so plainly — "
                 "this is the list that makes the offer credible.")
        L.append("")
        L.append("| Property | Rooms | ADR | Lift needed | Capturable/mo |")
        L.append("|---|---|---|---|---|")
        for p in rejected:
            L.append(f"| {p.name} | {p.rooms} | {_money(p.adr_bdt)} | "
                     f"{p.lift_optimistic:.0%}–{p.lift_pessimistic:.0%} | {_money(p.capturable_bdt)} |")
        L.append("")

    # ------------------------------------------------------- structure sensitivity
    L.append("## What the structure costs you")
    L.append("")
    L.append("The same list re-screened at three media budgets. The fee is rarely the constraint; the media budget is.")
    L.append("")
    L.append("| Media/month | Actionable | Parked | Screened out |")
    L.append("|---|---|---|---|")
    for media in (0.0, media_bdt * 0.5, media_bdt):
        alt = [screen(p, fee_bdt=fee_bdt, media_bdt=media) for p in scored]
        n_act = sum(1 for p in alt if p.recommendation in ACTIONABLE)
        n_park = sum(1 for p in alt if p.recommendation == "CALL LATER")
        n_rej = sum(1 for p in alt if p.recommendation == "NOT A FIT")
        label = f"{_money(media)}" + (" (fee only)" if media == 0 else "")
        L.append(f"| {label} | {n_act} | {n_park} | {n_rej} |")
    L.append("")
    L.append("Read this before defending the media budget: it decides how much of the mid-tier is addressable at all.")
    L.append("")

    # ------------------------------------------------------------------- caveats
    L.append("## Before you quote anything from this sheet")
    L.append("")
    L.append("1. **Every rate is a floor.** Rates come from publicly listed prices — usually the cheapest bookable "
             "room, not ADR. A hotel clearing break-even on its floor rate clears it on its real ADR too.")
    L.append("2. **Occupancy, OTA share and commission are assumptions** by segment, not measurements. They are "
             "stated per row so they can be replaced as answers arrive.")
    L.append("3. **Nothing here has been confirmed by a hotel.** No property has stated its direct volume, which is "
             "the input the verdict is most sensitive to.")
    L.append("4. **Seasonality is not modelled.** These verdicts are annual averages; a heavily seasonal property "
             "will look worse in its low months than this sheet implies.")
    L.append("5. **Room counts and rates go stale in about a month.** Re-run the screen before a fresh round of calls.")
    L.append("")
    L.append("### Verify first (before the first call)")
    L.append("")
    L.append("- Phone number and current trading name — one Google Maps lookup per property.")
    L.append("- Any row flagged ⚠: resolve the disputed room count or the class-average rate.")
    L.append("")
    return "\n".join(L)


def _ask(p: Prospect) -> str:
    """The one question that decides this prospect, given what is missing."""
    if p.derived_direct_share or "direct_share" in p.assumed_fields:
        return "how many bookings arrive by phone or at the desk each month?"
    if "ota_share" in p.assumed_fields:
        return "what share of your bookings come through the platforms?"
    return "who decides on marketing spend here?"


def write_callsheet(scored: list[Prospect], path: Path, *, fee_bdt: float, media_bdt: float,
                    city: str = "Dhaka", source_file: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_callsheet(scored, fee_bdt=fee_bdt, media_bdt=media_bdt,
                                    city=city, source_file=source_file), encoding="utf-8")
    return path
