"""The one-page opportunity review — what a prospect actually receives.

Two constraints shape this document:
  1. It must lead with a number the owner already knows is true (their OTA
     commission), not with a description of the provider.
  2. It must be safe to send to a sceptical owner, i.e. conservative, specific,
     and explicit about what is not being promised.

Sent after a first conversation, never before it — the numbers are only credible
once you have confirmed the inputs on a call.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Cm, Pt, RGBColor

from .screener import CONSERVATIVE_SHIFTABLE_SHARE, SEASONAL_RATIO, Prospect

NAVY = RGBColor(0x1F, 0x38, 0x64)


def money(v: float) -> str:
    return f"৳{v:,.0f}"


def slugify(name: str, *, max_words: int = 5) -> str:
    """Filenames that survive a file system and a human: 'Gulshan business hotel
    — 120 rooms (archetype B)' -> 'gulshan_business_hotel'."""
    cleaned = re.sub(r"[^A-Za-z0-9\s-]", " ", name)
    words = [w for w in cleaned.replace("-", " ").split() if w]
    return "_".join(words[:max_words]).lower() or "prospect"


def seasonality_note(p: Prospect) -> tuple[float, float] | None:
    """(trough share of room-nights, break-even lift in the weakest month).

    Mirrors screener.decide()'s seasonal arithmetic exactly, and returns None for a
    property that did not report a peak/trough ratio. The one-pager quotes a flat
    month; for a seasonal property that is an overstatement unless it is said out loud,
    so this drives a visible section rather than a footnote.
    """
    if p.season_ratio < SEASONAL_RATIO or p.feasibility is None or p.direct_room_nights <= 0:
        return None
    trough_share = 2.0 / (1.0 + p.season_ratio)
    trough_direct = p.direct_room_nights * trough_share
    if trough_direct <= 0:
        return None
    return trough_share, p.feasibility.break_even_room_nights / trough_direct


def build_review(p: Prospect, out_path: Path, *, fee_bdt: float, media_bdt: float) -> Path:
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(1.6)
        s.left_margin = s.right_margin = Cm(1.8)
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10)
    st.paragraph_format.space_after = Pt(5)

    def H(text, level=1):
        h = doc.add_heading(text, level=level)
        for r in h.runs:
            r.font.color.rgb = NAVY

    def P(text="", bold=False, italic=False, size=None):
        para = doc.add_paragraph()
        r = para.add_run(text)
        r.bold = bold
        r.italic = italic
        if size:
            r.font.size = Pt(size)
        return para

    def T(rows, widths=None):
        t = doc.add_table(rows=0, cols=len(rows[0]))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate(rows):
            cells = t.add_row().cells
            for j, val in enumerate(row):
                cells[j].text = ""
                run = cells[j].paragraphs[0].add_run(str(val))
                run.font.size = Pt(9)
                if i == 0:
                    run.bold = True
        if widths:
            for j, w in enumerate(widths):
                for row in t.rows:
                    row.cells[j].width = Cm(w)
        doc.add_paragraph()

    h = doc.add_heading(f"Direct Booking Opportunity — {p.name}", level=0)
    for r in h.runs:
        r.font.color.rgb = NAVY
    P(f"{p.city} · {p.rooms} rooms · prepared {date.today():%d %B %Y}", italic=True, size=9)
    season = seasonality_note(p)

    # ---------------------------------------------------------------- the number
    H("The number that matters", 1)
    P(f"On the figures you gave me, this property pays an estimated "
      f"{money(p.commission_bdt)} per month in OTA commission — about "
      f"{money(p.commission_bdt * 12)} a year. That is roughly "
      f"{p.effective_ota_commission:.0%} of the room revenue that arrives through those channels, and it is "
      f"the largest single marketing cost most independent hotels carry.")
    P(f"Every room-night that moves from an OTA to a direct booking saves "
      f"{money(p.saving_per_room_night)} — the difference between the commission and what direct actually "
      f"costs to process (payment fees and booking engine, around 4.5%).", bold=True)

    # ------------------------------------------------------------- what is possible
    H("What is realistically available", 1)
    shift = p.ota_room_nights * CONSERVATIVE_SHIFTABLE_SHARE
    T([
        ["Measure", "Value", "Basis"],
        ["OTA room-nights per month", f"{p.ota_room_nights:,.0f}", "your occupancy and channel mix"],
        ["Shiftable to direct (20%)", f"{shift:,.0f}", "the conservative end of the range; industry analysis "
                                                       "puts it at 20–50%"],
        ["Value of that shift", f"{money(p.capturable_bdt)}/month",
         f"{shift:,.0f} room-nights × {money(p.saving_per_room_night)} saved each"],
        ["Over a year", f"{money(p.capturable_bdt * 12)}",
         "if the shift is achieved and held" + (
             " — this is the peak-window reading; see the seasonality note"
             if season else "")],
    ], widths=[5.0, 3.2, 8.3])
    P("I am quoting the bottom of the range on purpose. A provider who leads with the largest plausible number "
      "is telling you how they will report the results.", italic=True, size=9)

    if season:
        trough_share, trough_lift = season
        H("One thing the numbers above do not yet account for: seasonality", 1)
        P(f"You have told me your peak months run about {p.season_ratio:.1f}× your weakest. The table above "
          f"quotes a flat month, and a flat month is not what you will experience: in the trough, roughly "
          f"{trough_share:.0%} of those room-nights exist, and the same fee would need about a "
          f"{trough_lift:.0%} lift to pay for itself — "
          + ("which is not achievable on these numbers, whatever the method."
             if trough_lift > 0.60 else "a materially harder ask than the headline figure suggests."))
        P("That is why I would quote a season-weighted fee or an annual term rather than a flat monthly "
          "number, and why this pilot should be judged over twelve months rather than over its best month.",
          bold=True)

    # ------------------------------------------------------------ what it requires
    H("What it would take to get there", 1)
    annual = (fee_bdt + media_bdt) * 12
    P(f"An engagement at {money(fee_bdt)}/month plus {money(media_bdt)}/month of media — "
      f"{money(annual)} over a year, spent directly by you, never through me — needs to shift "
      f"{p.feasibility.break_even_room_nights:,.0f} additional direct room-nights a month to pay for itself. "
      f"Against your current direct volume of about {p.direct_room_nights:,.0f} room-nights, that is a "
      f"{p.lift_optimistic:.0%}–{p.lift_pessimistic:.0%} increase depending on how much of that direct "
      f"business is genuinely direct. I plan against the {p.lift_pessimistic:.0%} figure.")
    if season and season[1] > 0.60:
        # The feasibility verdict above is computed on the annual average. On a flat fee
        # the weakest months do not clear it, and saying otherwise in the same document
        # as the seasonality note would be a contradiction the owner can see.
        P("On the annual average that is within what is normally achievable — but on a flat monthly fee the "
          "weakest months are not, which is the whole argument for a season-weighted structure. I would "
          "rather quote that than quote a flat number and explain it later.", bold=True)
    elif p.feasibility.verdict == "VIABLE":
        P("That is within what is normally achievable, which is why I am suggesting we talk.", bold=True)
    elif p.feasibility.verdict == "MARGINAL":
        P("That is achievable but thin — it may take two or three measurement windows before a clear answer. "
          "I would rather tell you that now than in month four.", bold=True)
    else:
        P("That is above what I would be willing to promise. On these numbers I would not take the engagement "
          "on the standard structure — if we proceed, it should be at a materially lower fee or with a smaller "
          "media budget, and I will say so plainly.", bold=True)

    # ------------------------------------------------------------- the proposal
    H("How I would work, and what protects you", 1)
    T([
        ["What", "Detail"],
        ["Measurement agreed first", "We agree how success will be measured — the counterfactual, the metric, the "
                                     "haircut for bookings that would have happened anyway — before any money is spent"],
        ["Your accounts stay yours", "Ad accounts and payment instruments remain in your name. I operate through "
                                     "manager access. No money of yours passes through me"],
        ["A written spend ceiling", "You set the monthly ceiling. I cannot exceed it. If I do, I absorb it"],
        ["Nothing published without approval", "Every public post, review reply or outbound message goes to you "
                                                "for approval first"],
        ["A monthly report with the bad news in it", "One document: what was produced, what it was worth, what "
                                                      "disagrees between systems, and what I am changing"],
        ["90 days, then an honest answer", "If the data says this is not working, I will say so before you have "
                                           "to ask, and the work stops"],
    ], widths=[4.6, 11.9])

    # --------------------------------------------------------------- the ask
    H("What I am asking for", 1)
    P("A 90-day pilot at a design-partner rate: three months, a written measurement plan, and an honest verdict "
      "at the end. Before that, one conversation where I show you what your own numbers would need to look like.")

    P("Two things I will never claim, so that you can judge everything else I say:", bold=True)
    P("· Platform-reported ROAS. It counts bookings that would have happened anyway and cannot see the "
      "commission you saved.", size=9)
    P("· A guarantee of bookings. Nobody can promise those honestly. What I can promise is that you will be "
      "able to verify whether any were produced.", size=9)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return out_path
