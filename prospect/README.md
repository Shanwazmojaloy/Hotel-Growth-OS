# Prospect screener — who is worth a call, and who is not

A solo operator with nights and weekends has maybe **one sales conversation a week**. The screener's job is not to find prospects; it is to **protect the calendar** by killing the engagements that cannot work *before* a call is spent on them.

## Run it

```bash
cd hotel-growth-os

# Rank a list
python3 -m prospect.cli screen \
    --input prospect/data/prospects_sample.csv \
    --fee 19000 --media 50000 \
    --out prospect/reports

# One-page opportunity review for a named prospect (docx)
python3 -m prospect.cli review \
    --input prospect/data/prospects_sample.csv \
    --name "Gulshan" \
    --fee 19000 --media 50000 \
    --out prospect/reports
```

Output files: `prospect_scores.csv` (regenerated input, with verdicts), `prospect_scores.json`, and one `<slug>_opportunity.docx` per reviewed prospect.

## Why it reuses the feasibility engine

A prospect's viability is the **same arithmetic** as a design partner's: break-even room-nights per month, expressed as a required lift on the direct volume the hotel already has. There is one definition of "can this work", in `measurement/feasibility.py`, used by both. Two engines would eventually disagree, and the disagreement would be discovered in front of a customer.

`python3 -m prospect.cli screen` refuses to quote anything it cannot compute: a missing direct-share figure is estimated *and flagged as estimated*, and the estimate is never read back to the prospect as fact.

## Input format

One row per hotel. `name`, `city`, `segment` are text; everything else is numeric. `direct_share` is optional — leave it blank if unknown.

| Column | Meaning | Notes |
|---|---|---|
| `name` | Property name, used in reports and filenames | |
| `city`, `segment` | Human context for the table | business / resort / budget … |
| `rooms` | Room count | |
| `adr_bdt` | Average daily rate, ৳ | |
| `occupancy` | **Fraction, not percent** (0.51, not 51) | A percentage is rejected as a likely unit error |
| `ota_share` | Share of room-nights from OTAs | 0–1 |
| `effective_ota_commission` | Blended commission actually paid, all-in | Benchmarks 0.15 (Booking) / 0.18–0.22 (Expedia) before Genius/visibility boosts |
| `direct_share` | Share of room-nights booked direct | **Optional.** Blank → estimated at 55% of non-OTA volume and flagged |
| `season_ratio` | Peak-to-trough room-nights, if the hotel states one | **Optional.** ≥1.6 triggers the seasonal downgrade below — it can only ever worsen a verdict |

Free-text fields containing commas must be quoted (`"Beach resort — 72 rooms, seasonal"`). Unquoted commas shift columns; the loader detects the shift and refuses to run.

## The honest number: how `capturable` is computed

```
total room-nights    = rooms × 30.44 × occupancy
OTA room-nights      = total × ota_share
commission / month   = OTA room-nights × ADR × effective_ota_commission
saving per room-night= ADR × (effective_ota_commission − 0.045)   # 4.5% = cost of a direct booking
capturable / month   = OTA room-nights × 0.20 × saving per room-night
```

Three deliberate conservatisms, all of which reduce the pitch number:

1. **Only 20% of OTA volume is assumed shiftable** (`CONSERVATIVE_SHIFTABLE_SHARE`). Real behaviour is driven by guests who already know the hotel — repeat, corporate, branded search — not by the bulk of OTA discovery traffic.
2. **Every lift figure is quoted at the pessimistic end of a band** (`DIRECT_SHARE_BAND`, 0.65×–1.5× of the direct volume). The band exists even when the owner *states* their direct share, because owners consistently overstate it — a guest who saw the hotel on Booking.com and then telephoned is usually counted as direct. Treat a stated direct share as a claim to be verified, not a number to plan against.
3. **Saving is net of direct cost**, not gross commission: ~4.5% for payment processing, channel fees and the website's own costs, so the saving does not overstate by pretending direct is free.
4. **The figure quoted to the prospect is this number**, not the commission total. Commission totals are big and motivating, but quoting them as "what we'll get you" is the exact overclaim the pack exists to avoid.

## The decision rule

Four verdicts, assigned by one rule. It lives in `screener.py`, is restated in `honesty_gate.py`, and the two are asserted to agree on every run — a verdict that disagrees with the rule is a bug, not a judgement call.

| Verdict | Condition | Action |
|---|---|---|
| **NOT A FIT** | break-even needs **>60% lift even on the favourable reading** | Screen out. Say so if asked |
| **CALL LATER** | worst reading needs **>70% lift**, or capturable **< ৳25,000/month** | Do not spend a call this quarter |
| **CALL NOW** | worst reading needs **≤35% lift**, on a **confirmed** direct volume | Call this week |
| **CONFIRM DIRECT VOLUME FIRST** | worst reading ≤35% but the volume was **estimated**; or the band sits in the ambiguous middle (≤35% best, ≤70% worst) | One question decides it |
| **CALL LATER (seasonal)** | `season_ratio` ≥1.6 **and** the trough month cannot pay back | Revisit only with a season-weighted fee |

**The threshold that matters is the *worst* reading, not the best.** A verdict is a promise, and the promise has to survive the pessimistic end of the range. Quoting the favourable end is how providers end up explaining, in month three, why the numbers didn't happen.

**Three bright lines worth stating plainly:**

1. **A CALL NOW requires an empty `assumed_fields` and a stated direct volume.** If the volume came from our own estimate, the best outcome is CONFIRM — because the first outreach message already asks the question ("how many bookings arrive by phone or at the desk?"), so a CONFIRM verdict costs one WhatsApp reply, not a wasted call.
2. **A seasonal hotel is downgraded by the season, never approved by the average.** A public `season_ratio` of 1.6 or more runs the break-even against the *weakest* months, approximated as 2/(1+ratio). The test is one-way — it can only ever move a verdict down — so an approximation here can make us too cautious but never too flattering. The honest fix for a seasonal resort is a season-weighted fee, which is a sales conversation, not a screening one.
3. **CALL LATER is not a soft no.** It says: no plausible version of these numbers works well enough to justify a call. Revisit only if something changes — a season, an ADR, a room count.

### Why the sensitivity band exists (a real bug, kept as evidence)

The first version estimated direct share as a fixed fraction of non-OTA volume. On the Sea Breeze archetype (72 rooms, 51% occupancy, ADR ৳11,000) that estimate produced a **10.8%** direct share, versus a true **20.3%** — which flipped the verdict from viable to **CALL LATER**. One unconfirmed assumption was deciding the outcome of a real prospect.

The fix was not a better single estimate. It was to admit the range: the same arithmetic is run at 0.65×, 1.0× and 1.5× the estimated direct volume, producing `lift_optimistic` and `lift_pessimistic`. **Any prospect whose verdict differs across the band is never reported as a confident yes or no** — it becomes CONFIRM DIRECT VOLUME FIRST.

**Standing rule: never quote a derived direct volume back to a prospect as fact.** Ask the question.

### Why the band does not just make everything "maybe"

Adding the CONFIRM category created a new failure mode: almost every mid-size hotel landed in it, and five of nine prospects marked "confirm first" is honest but useless as a call list — it tells you nothing about where to start.

The fix is that the band is read against **fixed thresholds**, not against itself:

- The favourable end above **60% lift** is a no, however uncertain the middle looks. Band extremes that require a 100%+ lift are not "uncertain" — they are a no, and treating them as uncertainty wastes the scarcest resource in the plan: a call.
- The pessimistic end above **70% lift** means the downside case is implausible enough that no question on the call fixes it. Defer.
- CONFIRM is reserved for the genuinely narrow middle: workable if the direct channel is healthy, not workable if it is weak, both within plausible range.

The honest verdict is therefore the one that survives **both** ends of the range — and the sample list now resolves to 1 call now, 3 confirm, 3 later, 2 not a fit rather than a uniform wall of "maybe".

## Real data: the Dhaka list (2026-09)

The sample CSV is synthetic. The working list is not:

| File | What it is |
|---|---|
| `data/dhaka_2026-09.csv` | **18 screenable properties** — independent Dhaka hotels whose room count is published by a source |
| `data/dhaka_2026-09.sources.md` | Provenance: every source, every assumption, every conflict, and the coverage gap — read this before the CSV |
| `data/dhaka_watchlist.csv` | **40 more** properties with a live rate but no published room count — the verification queue |
| `out/dhaka_2026-09_call_sheet.md` | The worklist: ranked, with the number to lead with and what to confirm |

```bash
### Two inputs worth knowing about

- **`season_ratio` is an optional column.** Absent, every property reads as flat (1.0) and the
  seasonal downgrade never fires. That is a stated assumption, not a finding — Dhaka business
  hotels are treated as year-round because nothing public says otherwise. For a coastal or
  leisure market the column is the whole question: the owner's stated peak/trough ratio is the
  only honest source, and a row that lacks it cannot be downgraded for seasonality.
- **The honesty gate is a restatement of the decision rule, not a second opinion.** Every clause
  of `screener.decide()` must appear in `honesty_gate.expected_verdict()` in the same order,
  and `tests/test_screener.py::TestGateMirrorsTheRule` fails if they drift. They drifted once:
  the gate began rejecting correct output, and the cheap way to satisfy it would have been to
  weaken the screener. A checker that fails correct work pushes in the unsafe direction.

python3 -m prospect.cli screen --input prospect/data/dhaka_2026-09.csv --fee 19000 --media 50000 --out prospect/reports
python3 -m prospect.cli callsheet --input prospect/data/dhaka_2026-09.csv --fee 19000 --media 50000 --city Dhaka --out prospect/reports
```

### Provenance columns, and the rule they enforce

Real data arrives with a history, so each row declares it:

| Column | Values | Meaning |
|---|---|---|
| `adr_basis` | `listed` \| `class_avg` | Was the rate taken from a live listing, or from the star-class average? |
| `rooms_status` | `published` \| `disputed` | Do the sources agree on the room count? |
| `assumed_fields` | `occupancy;ota_share;commission;direct_share` … | Which inputs are **ours**, not the hotel's |
| `source_id` | `S5;S6` | Pointers into the sources file |

**The rule: a CALL NOW requires an empty `assumed_fields` and a stated direct volume.** If any number in the chain is ours rather than theirs, the best verdict available is CONFIRM. That is why the Dhaka list produces **zero confident calls** — and why that is the correct answer rather than a bug. Public data cannot know a hotel's occupancy, its OTA share, its real commission, or its direct volume. The first message asks for them.

### What the real list showed

1. **Dhaka yields 18 screenable hotels from public data, not 40.** Room counts are published for barely a third of the properties found. The funnel in `sales-kit/first-45-days-activity.md` assumes 40 screened; closing that gap needs ~2 minutes per property on the watchlist (phone or Google Maps), not a bigger scrape.
2. **The fee is rarely the constraint; the media budget is.** The same list at ৳50k media screens out 8 of 18; at ৳25k, 6; with no media budget, only 2. If the mid-tier matters, the media assumption is the lever — and it is the one the hotel pays directly.
3. **The upscale independents dominate.** Hotels with ADR ≥ ৳6,000 and ≥ 50 rooms carry the entire workable tier. That is worth knowing before spending weekends on 25-room budget properties that cannot clear the arithmetic at any price.
4. **Rates are floors.** Every rate is a "from" price — the cheapest bookable room, not ADR — which makes both the required lift and the quoted prize conservative. The screen understates; it cannot overstate.

### What the list does not contain

No phone numbers (one Google Maps lookup each — and inventing a plausible-looking number is worse than omitting it), no owner names, no `season_ratio` (nothing public states a hotel's monthly occupancy, so it can only come from the hotel), and no per-hotel OTA measurement. Review counts are used only as a ranking proxy for OTA dependence. Dhaka's business hotels are also the least seasonal segment available, which is part of why this city was the right first list.

## Reading the output

```
RECOMMENDATION                ROOMS  COMMISSION/MO  CAPTURABLE  BEST–WORST  PROSPECT
CALL NOW                        120     ৳2,761,517   ৳386,612        3%–8%  Gulshan business hotel
CALL NOW                         85     ৳1,307,574   ৳185,591      10%–23%  Airport hotel
CONFIRM DIRECT VOLUME FIRST      72     ৳1,615,606   ৳242,341      19%–43%  Beach resort
CALL LATER                       45     ৳653,189      ৳96,057     37%–85%  Mid-range beach hotel
NOT A FIT                        30     ৳322,752      ৳45,185    124%–286%  Boutique hotel
```

`BEST–WORST` is the required lift on direct volume at the favourable and pessimistic ends of the band. **Lower is better.** A 3%–8% prospect is an easy sell on arithmetic alone; a 124%–286% prospect cannot be sold honestly at any price.

## Tests

```bash
python3 -m unittest discover -s prospect/tests -t .   # 31 tests
```

They cover the derivations, the verdict thresholds, the CONFIRM state, the seasonal downgrade (including the one-way property), ranking order, input validation (including the occupancy-as-percentage unit error), and the slug used for filenames.

## What the screener does not do

- **It does not know the prospect's real commission rate.** `effective_ota_commission` is often 3–6 points above the contracted rate. If it is unconfirmed, the true economics may be better than shown — a reason to ask, not to assume.
- **It does not model the whole seasonal year.** When a hotel declares a `season_ratio`, the trough is tested and can downgrade the verdict — but never upgrade it. It still cannot say which month, what the shoulder seasons look like, or what a season-weighted fee should be; that is the measurement spine's `seasonality.py`, which needs the hotel's own monthly history. Ask which months sell out, and treat a beach or hill property's annual average as a peak number until proven otherwise.
- **It does not price the work to the property.** The same fee is applied to 30-room and 120-room hotels. Per-room economics matter: the same 3% lift is a different business at 30 rooms than at 120.
- **It does not replace the call.** It decides *whether* there is a conversation worth having. Everything else is in `08-sales-playbook.md`.
