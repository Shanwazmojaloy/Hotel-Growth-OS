# First 45 days — the activity plan behind "three signed LOIs"

The 90-day plan sets the kill criterion. This file sets the weekly activity that produces it. Everything below is sized for **nights and weekends**: ~8–10 hours a week of sales work alongside the build.

**The number that matters: 3 signed LOIs by day 45.** Everything else here is a leading indicator.

---

## The funnel, worked backwards from three signatures

| Stage | Conversion used | Required by day 45 |
|---|---|---|
| Hotels identified | — | 60 |
| Screened (feasibility run) | — | 40 |
| Screened as NOT A FIT (and told so) | — | 15+ |
| First calls held | ~50% of qualified | 20 |
| Data shares received (rung 3) | ~40% of calls | 8 |
| One-page reads delivered | ~100% of shares | 8 |
| LOIs signed | ~35–40% of reads | **3** |

**Why 40% of qualified hotels get screened out:** the screener's job is to protect the calendar. A hotel needing a 124% lift is not a sales problem to be worked harder — it is a no that should be delivered in ninety seconds rather than after six weeks of hope.

### What the real Dhaka list proved (2026-09)

The table above is the plan. This is what happened when it was run against live public sources:

| Step | Plan | Measured |
|---|---|---|
| Names surfaced from public sources | 60 | **58** (18 screenable + 40 needing one lookup each) |
| Screenable without extra work | 40 | **18** — room counts are published for barely a third of independents |
| Reaching 40 screenable | — | **40 lookups × ~2 minutes ≈ 1.5 hours** — the gap is arithmetic, not luck |
| Calls earned by the first 18 | — | **7 CONFIRM-class, 0 CALL NOW** |
| Screened out | 15+ | **8 NOT A FIT, 3 CALL LATER** |

Two things follow. First, **week 1's "60 identified" is realistic and week 1's "20 screened" is not, unless the room-count lookups happen** — so the lookup is the deliverable, not the research. Second, **zero CALL NOW is the correct output on public data**: no public source states a hotel's direct volume, and the screener refuses to call on an assumption. The first message asks the one question that converts CONFIRM into CALL NOW, which is why rung 1 of the outreach ladder is a question rather than a pitch.

---

## Week by week

### Week 1 — 60 hotels identified, 20 screened (6–8 hrs)
- Build the list from sources that actually carry room counts, in this order: **star-rated hotel directories** (dhaka-hotel.com lists 69 four-star and 201 three-star properties, with room counts on many), **trade directories** (travelweekly, hotelchains.com) for the chain/independent split, **Booking.com city pages** for live "from" rates, and **Google Maps for the phone number** — one lookup per property, and never an invented one.
- Populate `prospect/data/prospects.csv` with what is publicly visible (rooms, ADR from listings, OTA presence). Leave `direct_share` blank — that is what the call is for. Mark anything you assumed in the `notes` column: `prospect/data/dhaka_2026-09.sources.md` is the pattern.
- Where a room count is missing, the property goes on the watchlist, not into the screen. `prospect/data/dhaka_watchlist.csv` shows the shape of that queue.
- **Deliverable: a ranked call list from `python3 -m prospect.cli screen`.**

### Week 2 — 5 first calls, 20 more screened (8 hrs)
- Two calls a week is the honest sustainable rate on nights/weekends; five is the stretch.
- Open every call with the two questions (OTA share, direct volume). Ten minutes in, you know whether to continue.
- **Deliverable: 5 calls held, 5 screened with real direct-share answers (not estimates).**

### Week 3 — first data shares, first reads (8 hrs)
- Convert the two best call outcomes into rung 3 (data share). Send the exact list from `outreach-templates.md` §4.
- Produce the first one-page read. Time it — this is a repeatable process that should take under an hour, not a day.
- **Deliverable: 2 data shares, 2 reads delivered.**

### Week 4 — first LOI request (8 hrs)
- Show the two best prospects the LOI and measurement plan. Ask directly.
- Anti-goal: do not add a fourth prospect to the "maybe later" pile before asking anyone for a signature.
- **Deliverable: 2 LOI conversations opened.**

### Week 5 — pipeline discipline (8 hrs)
- Ask both open LOIs for a decision, either way. A yes that takes three weeks to arrive is worse than a no today.
- Re-engage the week-2/3 noes with one useful observation (template §7).
- **Deliverable: 1 signed LOI. Pipeline of ≥6 live conversations.**

### Week 6 — full push to the deadline (9 hrs)
- Ask everyone who has received a read. Offer the choice in template §6 — terms in writing, or the measurement plan first.
- If sitting at 2 signed: the constraint is pipeline volume, not persuasion. Add 15 more screened hotels this week.
- **Deliverable by day 45 (≈ end of week 6): 3 signed LOIs, or the kill criterion speaks.**

---

## Weekly review — five numbers, five minutes

| # | Number | Target | If behind |
|---|---|---|---|
| 1 | Hotels screened | 6/week | The list is too small — go back to week 1 and build 20 more names |
| 2 | Calls held | 3/week | Conversion problem at rung 1–2; re-read the opener in the playbook §1 |
| 3 | Data shares | 1.3/week | The call is not producing enough curiosity — lead with their number earlier |
| 4 | Reads delivered | 1/week | Production bottleneck, not sales — time yourself, the target is under 60 minutes |
| 5 | LOIs signed | 3 by day 45 | **This is the plan. Everything else is a hypothesis about how to move it.** |

---

## What is deliberately not in this plan

| Omitted | Why |
|---|---|
| A pitch deck | The one-page read from their own data outperforms it, and takes less time to produce |
| Case studies | There are no clients yet. Claiming otherwise is the fastest way to lose the ones you might get |
| Paid advertising for your own service | It converts later and costs cash the runway does not have |
| LinkedIn/content marketing | Weeks-to-months payoff; the deadline is six weeks. (Revisit at day 60 if the pilot is live) |
| A CRM | 40 prospects and 20 calls fit in a spreadsheet. Buying software is a way to feel productive while not calling |
| Partnering with an agency | Your positioning is *against* what they sell. A confused referral is worse than no referral |

---

## Diagnostic: what a stall actually means

| Symptom | Most likely cause | Fix |
|---|---|---|
| Screened 20, called 0 | Fear of the ask, not a list problem | Call the two best NOT A FIT hotels and disqualify them out loud. Rejection you chose is easy to survive, and it starts the habit |
| Called 10, no data shares | Led with product instead of their number | Re-read playbook §1–2. The opener is the whole game |
| Data shared, no LOI conversations | The read was delivered without a next step | Template §4 ends with a question. Make sure it does |
| 4 LOIs "coming next week" | Talking to people who cannot sign | Playbook discovery question 4 — ask who approves the spend, and get that person on the call |
| Zero NOT A FIT verdicts | The honest answer is being suppressed to keep the pipeline looking full | Re-run the screener and read the output without flinching. A pipeline of unsuited prospects fails in month four, not now |
