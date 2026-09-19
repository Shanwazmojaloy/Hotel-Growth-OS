# 90-Day Execution Plan — Hotel Growth OS

**Start date:** `[ stamp it ]` · **Owner:** one part-time person · **Budget:** ৳235,500 (see `02-financial-model.xlsx` → Capital & Launch)

**The plan in one sentence:** spend the first 10 days on paperwork that cannot be compressed, the next 35 days building only what has no gate, and the last 45 days delivering two measured monthly cycles — then decide, using numbers written down in advance.

---

## Why this plan looks like this

| Constraint | Value | Consequence for the plan |
|---|---|---|
| Your capacity | ~12 hrs/week | ~156 hrs total. Every hour is allocated below. Nothing is "as time permits" |
| Tenants you can carry part-time | **7** | Capacity is not the constraint in 90 days. Selling 3 is the constraint |
| Tenants needed to pay yourself ৳60k/mo | **9** | Not reachable part-time. Do not plan as if it is |
| Platform review queues | 2–6 weeks each, effort-independent | **Week one is paperwork, not code** |
| Economic gross margin at 2 support hrs | **60.9%** | Viable; onboarding labour is what must be watched |
| Cost of finding out you were wrong | ৳235,500 + 156 hrs | Hence the day-45 kill criterion |

**The uncomfortable arithmetic:** 156 hours is not enough to build the system in the blueprint *and* sell it *and* deliver it. So the plan builds roughly 40% of it, delivers a service that is honest about being partly manual, and spends the rest proving the measurement method works. Automation is what you buy with evidence, not with optimism.

---

## Hour budget (156 hrs over 13 weeks)

| Allocation | Hours | Why this much |
|---|---|---|
| Platform paperwork & access | 12 | Calendar-bound; front-loaded; cannot be rushed later |
| Build (no-gate components only) | 55 | GA4 + GSC ingestion, reporting, ledger, digest, deploy |
| Selling (outreach, conversations, pilots) | 35 | You need 3 LOIs by day 45. This is the actual bottleneck |
| Delivery & support (2 tenants × 2 cycles) | 40 | Onboarding is 10–20 hrs each — this is where the 78% margin myth lives |
| Buffer & slack (real life, illness, restarts) | 14 | Non-negotiable. Solo plans without buffer fail at the first bad week |
| **Total** | **156** | |

**Your week (proposed, adjust to your life):** Tue 2h · Thu 2h · Sat 5h · Sun 3h. The two weekday evenings are for build (uninterrupted, no calls). Saturday morning is for sales conversations. Sunday is for delivery, reporting and admin. **Protect the Saturday block** — it is the one that produces revenue.

---

## Phase 0 — Days 1–10: paperwork (12 hrs, zero code)

All seven items below cost nothing but time, and four of them are on someone else's clock. File them on **day one**, not as they come up.

| # | Action | Expected wait | Why it matters / what to say |
|---|---|---|---|
| 1 | **Email n8n licensing** with your exact topology | Days | Determines whether n8n can be in the customer-facing path at all. See draft below |
| 2 | **Register/confirm the business entity** | 1–2 weeks | Brand verification, Meta business verification, GBP access and gateways all require a verified business with a real domain |
| 3 | **Google Cloud project + Google Ads API access** under the new (post-10-Sept-2026) flow | 2 days – 2 weeks | Access levels now attach to the Cloud project; brand verification required; pending applications were closed on 10 Sept and must be refiled |
| 4 | **Meta Business Manager + business verification** (do *not* file App Review yet) | 3–5 days | App Review needs a screencast of the permission in a live product; you have no product yet. Verification first, review later |
| 5 | **Google Business Profile API access request** | ~14 days | Rejection reasons are documented: vague use-case, domain/email mismatch, no live policy pages. Draft below |
| 6 | **Foreign-currency payment route** | 1–3 weeks | You cannot run this on a personal card: ~$300/transaction caps and a ~$12k/year individual allowance. Business/dual-currency route with endorsement |
| 7 | **Send 10 design-partner messages** | Continuous | Outreach starts day one, in parallel. Waiting until the product exists costs you the quarter |

### Draft — n8n licensing inquiry

> Subject: Licensing question — multi-tenant hosting for hotel clients
>
> Hello,
>
> I'm building a small marketing-automation service for hotels in Bangladesh and want to confirm my intended use against the Sustainable Use License before I architect anything.
>
> Intended topology: a single self-hosted Community Edition instance operated by my company, holding per-tenant OAuth credentials for several hotel clients, with their workflows stored centrally. Clients would not log into n8n; they would see results in my own dashboard (separate Next.js app). I would charge a monthly service fee.
>
> Reading the license, I believe this counts as hosting customer workflows and credentials rather than internal use, and that it likely requires a commercial agreement — possibly an Embed or Enterprise license. Could you confirm (a) whether a commercial license is required for this topology, (b) which license, and (c) whether the alternative of one instance per client, hosted on the client's own infrastructure, would avoid the requirement?
>
> I'd rather ask now than build on the wrong foundation. Happy to describe the architecture in more detail.
>
> Thanks, `[ name ]`

### Draft — GBP API use-case (what Google actually reads)

> We operate a marketing service for independent hotels in Bangladesh. The hotel owner (or a manager they authorise) signs in with Google OAuth and grants the `business.manage` scope for their own Business Profile location. Using the granted access, our application, on the owner's behalf: (1) reads and displays their profile performance metrics alongside their booking data in a reporting dashboard; (2) drafts and, only after the owner approves it in our interface, publishes updates to their profile; (3) surfaces unreplied reviews to the owner and submits their approved reply.
>
> We are the manager of the profiles we operate on, never the owner. We do not scrape, do not aggregate competitor data, do not share our project with other agencies or third parties, and do not allow clients to route their own API calls through our project. Each client authorises access to their own location through OAuth. Our website is `[ domain ]`, our privacy policy is at `[ url ]`, and the use case exists to help small hotels manage their own public presence.

*(Fill in the domain and policy URL before sending — a domain/email mismatch is a documented rejection reason, and you should have policy pages live first.)*

### Draft — design-partner outreach (WhatsApp/LinkedIn, short on purpose)

> Assalamu alaikum `[ name ]`. I work with hotels in `[ city ]` on direct bookings — specifically getting more bookings through your own website instead of paying 15–20% to Booking.com.
>
> I'm taking on three hotels in a paid 90-day pilot at a reduced rate. The deal: I set up proper measurement first so we can both see whether it worked, and I'll tell you honestly at the end if it didn't. Nothing is routed through me — your ad account stays yours.
>
> Can I send you a one-page summary? If it's not relevant I'll leave you alone.

---

## Phase 1 — Weeks 2–6: build only what has no gate (55 hrs)

**Rule: no code that depends on an unapproved platform.** GA4 and Search Console are open APIs — that is why they are first.

| Week | Build | Hours | Done when |
|---|---|---|---|
| 2 | Supabase project; apply the skeleton migrations (they already exist); seed the first hotel's baseline | 8 | RLS suite green against the real project |
| 2–3 | GA4 ingestion (daily metrics, direct vs OTA channel split) | 10 | Yesterday's numbers appear without you touching anything |
| 3 | Search Console ingestion (queries, impressions, brand vs non-brand) | 5 | A hotel's branded search volume is visible next to ad spend |
| 4 | **Reporting generator** — one monthly document per hotel, built to the measurement plan's structure | 12 | A real report for hotel #1, produced from data, not memory |
| 4–5 | Cost ledger + per-tenant budget envelope with a hard stop | 6 | A runaway loop stops itself and you get a message, not a bill |
| 5 | Daily digest (email or WhatsApp): pending approvals, anomalies, yesterday's numbers, one action each | 8 | You can run approvals in 15 minutes a day from your phone |
| 6 | Deploy, backup, restore drill, one tracer | 6 | You have restored from backup once and it worked |

**Not in this list, on purpose:** dashboards, the content agent, the PR agent, video anything, the experiment engine, multi-region anything. Every one of those is a post-evidence purchase.

**Reuse note:** the skeleton in `skeleton/` already covers weeks-2 work — schema, RLS, adversarial tests, the worker guards. That is roughly 30–40 hours you do not have to spend, which is precisely why it exists.

---

## Phase 2 — Weeks 7–13: deliver twice, then decide (40 hrs delivery + 35 hrs sales, running throughout)

| Week | Focus | Hours |
|---|---|---|
| 7–9 | Onboard hotel #1 by hand where automation is missing. Complete the baseline, tracking, and the signed measurement plan. Launch one channel. ~14 hrs of onboarding, spent deliberately, noting every step you repeat | 18 |
| 9–10 | First monthly report. Deliver it in person or on a call — watch which pages get read and which get skipped. That observation is the most valuable output of the quarter | 6 |
| 10–12 | Second monthly cycle. Second hotel onboarded (target 8 hrs, not 14 — the runbook is the asset) | 8 |
| 12–13 | Day-90 read: measure, write the honest conclusion, decide scale / hold / stop | 4 |
| All | Selling runs continuously. Target: 3 signed LOIs by day 45, 5 conversations per week | 35 total |

**The day-45 checkpoint is the important one.** At that point you will have: 3 LOIs (or not), platform access granted (or refused), and one hotel's data flowing. If fewer than 3 LOIs are signed, the problem is demand, not software — and the correct response is to stop building and spend the remaining six weeks selling or repositioning, not to add features.

---

## The access gate tracker

Print this. It is the critical path, and it is the only part of the plan that other people control.

| Gate | Filed | Contact / ref | Status | If refused |
|---|---|---|---|---|
| n8n licensing answer | | `license@n8n.io` | ☐ | Move orchestration out of n8n entirely; per-client instances on client infrastructure as fallback |
| Business entity verified | | | ☐ | Everything downstream blocks. This is the true item zero |
| Google Ads API (Cloud-project flow) | | | ☐ | Run the first pilot on manual reporting from the Ads UI; the measurement method does not require the API |
| Meta business verification | | | ☐ | Skip Meta entirely in the first 90 days. Google search intent is the better first channel for hotels anyway |
| Meta Marketing API access tier | | | ☐ | Same as above; revisit when a client's ad account exists to point at |
| GBP API access | | | ☐ | GBP posts and review replies can be done manually via the owner's login for two hotels. Not a blocker for the pilot |
| Payment gateway (recurring) | | | ☐ | Invoice manually for the first three pilots; ugly, works |
| FX payment route | | | ☐ | Cap variable spend hard; keep COGS under the personal allowance until the business route exists |

**The pattern worth noticing:** none of these gates blocks the *measurement* work. GA4, Search Console, booking engine exports and PMS reports are all available on day one. That is the deliberate design of this plan — measurement is the deliverable, and measurement has no gatekeeper.

---

## Kill criteria (write them now, while you are unbiased)

| Day | Trigger | Decision |
|---|---|---|
| 45 | Fewer than 3 signed LOIs | Stop building. The constraint is demand, not capability. Spend the remaining weeks selling or reposition or stop entirely |
| 45 | Platform access refused at 3+ gates | Switch to the services-with-software-margin model: per-client instances on the client's infrastructure. A legitimate business, just not a SaaS multiple |
| 90 | No hotel shows a defensible booking or cost-per-acquisition delta | Reposition or stop. Do not renew on hope |
| 90 | Two hotels renew at the standard rate | Continue; begin automation of the steps you repeated most, in that order |
| Any | Support hours exceed 4/tenant/month | Freeze sales. Fix delivery before adding tenants — capacity, not demand, becomes the constraint |
| Any | You are avoiding the Saturday sales block | The business is not the priority it needs to be. Be honest and either recommit or stop |

---

## Anti-goals (the list that protects the plan)

- **Do not build a dashboard** before two hotels have renewed. A monthly document is the product; dashboards are for tenants 10+.
- **Do not add a second channel** until the first one shows a measured delta.
- **Do not touch video generation.** At ~$0.10/second it is the single fastest way to convert a 60.9% margin into a loss on a ৳19k contract.
- **Do not sign a fourth LOI** in the first 90 days. Three is capacity. A fourth is a support failure and a churn risk at exactly the moment your reputation is forming.
- **Do not accept a tenant who refuses measurement.** You cannot prove value where you cannot measure it, and unprovable value is how this business dies later.
- **Do not spend on paid acquisition** for your own service. At ৳19k ARPA the payback math is brutal, and your three design partners should come from direct relationships anyway.
- **Do not rebuild what the skeleton already does.** Apply it, then go sell.

---

## Weekly review — five questions, fifteen minutes, every Sunday

1. Did I spend my hours where the budget said? If not, why — and is the budget wrong or was I?
2. How many sales conversations happened this week? (Target: 5. Zero is the only unacceptable number.)
3. What did a tenant ask for that I have not built? Is it on the critical path or is it scope creep?
4. What broke, and did I find out from a customer or from a monitor? The second answer is the acceptable one.
5. Am I closer to answering the only question that matters — are we producing bookings that would not have happened otherwise, below the commission saved?

---

## What "day 90 success" actually looks like

Not "we built five agents." Success at day 90 is narrow and specific:

- **3 hotels paying**, at ৳15–25k/month, none of them free
- **2 complete monthly cycles delivered** on time, with reconciliation, to at least one hotel
- **One hotel showing a defensible delta** — incremental direct room-nights, above the agreed haircut, at a cost below the OTA commission saved
- **Support under 3 hrs/tenant/month** in the final month, with a runbook that made the second onboarding faster than the first
- **A written answer** to whether this is a business, from numbers agreed before you were emotionally invested in the answer

Anything beyond that is a bonus. Anything less, and the honest move is the one written in the kill criteria — which is exactly why they were written on day one.
