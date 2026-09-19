# Sales Playbook — the conversation that decides everything

**Why this document exists.** The 90-day plan's kill criterion is three signed LOIs by day 45. Everything else in this pack — the model, the security spec, the measurement spine, the skeleton — is worthless if that conversation doesn't land. So the conversation gets the same rigour as the code.

**The core problem to solve:** you are one person, part-time, with no track record, selling to an owner who has probably been disappointed by a marketing provider before. You cannot win on credentials. You win on **arithmetic and honesty** — the two things most providers cannot offer, because their numbers don't survive scrutiny.

---

## 1. The opening: lead with their number, not your product

Owners do not care what you built. They care what they're losing.

**The WhatsApp / first-message opener** (short, specific, no attachments):

> Assalamu alaikum [name]. I work with hotels in [city] on direct bookings — specifically getting more bookings through your own website rather than paying 15–20% commission to Booking.com.
>
> Two quick questions if I may: roughly what share of your bookings come through OTAs, and how many arrive by phone or at the desk?

**Why those two questions.** They are the entire feasibility calculation (§3). Asking them first does three things: it screens the prospect before you invest a call, it makes you sound like someone who knows the economics, and it forces the owner to say a number out loud — which is the beginning of the sale.

**Do not** open with: your company, AI, automation, "we help hotels grow", or a PDF. Every one of those signals "provider", and providers waste owners' time.

---

## 2. The 60-second structure of the first call

Owners give you about a minute to be interesting. Use this order every time.

| # | Beat | What you say | Why in this order |
|---|---|---|---|
| 1 | **Their number** | "On the figures you gave me, you're paying roughly ৳X a month in OTA commission — about ৳Y a year." | You have already done maths about *them*, which almost nobody does |
| 2 | **The mechanism** | "Most of the bookings you'd want direct come from guests who already know you — past guests, people who searched your name, repeat corporate. Those are already yours; the OTA is just charging you for them." | This is the insight. It reframes the problem from 'marketing' to 'leakage' |
| 3 | **The asymmetric ask** | "The first thing I do is set up measurement so we can both see whether it worked — before spending anything. If the numbers say it isn't working, I tell you and we stop." | Removes the risk that killed their last provider relationship |
| 4 | **The ceiling** | "Your ad account stays yours. You set the monthly ceiling. I can't exceed it." | Pre-empts the biggest unspoken fear: money disappearing |
| 5 | **The small ask** | "Can I see three months of your booking report and one month of Booking.com statements? I'll send you a one-page read on what's actually available before you pay anything." | Not "buy" — *share data*. Tiny yes, and it produces the leave-behind |

**Rule: never quote a number that you have not computed from their data.** The whole pitch is arithmetic; a made-up figure destroys it.

---

## 3. Discovery — the questions that qualify or disqualify

Ask these in the first call. They are the screener's inputs, and the answers decide whether you proceed.

| # | Question | What you're really learning | If the answer is bad |
|---|---|---|---|
| 1 | What share of bookings come through OTAs? | OTA dependency — the size of the problem | Below 35%: little to work with. Deprioritise |
| 2 | **How many bookings arrive by phone or at the desk?** | Direct volume — the single most verdict-changing input | Unknown → run the base screener with the estimate flagged, and confirm before quoting |
| 3 | What do you pay in commission, all-in? | Whether they know their real rate (usually 3–6 points above what they remember) | If they don't know: that's an opening, not a blocker — offer to compute it from their statements |
| 4 | Who approves marketing spend, and who approves a Facebook post? | The approval map, and whether the decision-maker is on this call | If neither is on the call, you are talking to the wrong person |
| 5 | What did you try before, and why did it stop? | The objection you will otherwise hit in month two | Listen carefully. This is usually the real brief |
| 6 | What's your ADR and occupancy? | Whether the economics can work at all | Occupancy under ~45%: an empty-rooms problem, not a channel problem |
| 7 | Which months do you always sell out? | Where the work is genuinely incremental | If they sell out year-round, marketing adds little |
| 8 | Have you ever collected a guest's phone or email at check-in? | Whether repeat-guest marketing is even possible | No: that's phase two, and worth telling them |

**Time-box: 20 minutes.** Owners respect brevity more than thoroughness.

---

## 4. The reveal — the strongest moment available to you

After they share exports, you have something almost no competitor has: **findings from their own data, produced in under an hour.**

Run:

```bash
python3 -m measurement.cli audit    --hotel hotels/<their-slug>
python3 -m measurement.cli baseline --hotel hotels/<their-slug> --out reports
python3 -m measurement.cli feasibility --hotel hotels/<their-slug> --media <their budget>
```

Then lead the follow-up with **one finding they did not know**, in their language. From the sample data, real examples of what comes out:

- *"You paid ৳1.3 crore in OTA commission last year. Your effective rate is 19.4%, not the 15% on your contract — the gap is the Genius and visibility programs."*
- *"Your website's booking confirmation is firing the conversion on the wrong page, so anything you optimise against will be misled. That's fixable in about an hour."*
- *"Your branded search brings 68% of your search clicks. Those are guests who already knew you — the commission on them is the part worth attacking first."*

**The structure of the reveal:** their number → what we found → what it's worth → what it would take. Never "we found many issues"; always one specific finding with a number attached.

**This is the moment competence is demonstrated.** Not the pitch deck. Not the AI. A specific number from their own statements, three days after a 20-minute call.

---

## 5. The twelve objections, with answers

Answer with arithmetic, not enthusiasm. Where an honest answer loses the deal, lose it early — that is cheaper than losing it in month four.

| # | Objection | Your answer |
|---|---|---|
| 1 | **"We tried an agency before and got nothing."** | "What were you measuring? Most agencies report clicks and impressions, which can't tell you whether you gained a booking. I'd rather start by agreeing what success looks like, in writing, before spending anything — including the haircut for bookings that would have happened anyway. If that sounds like more paperwork than you want, I'm probably not your fit." |
| 2 | **"Booking.com brings us guests we'd never reach."** | "Agreed — keep them. The target isn't the guest who discovers you on Booking.com. It's the guest who found you there once, or searched your name directly, and paid 18% for the privilege of booking a room they'd already chosen. That portion is roughly a fifth to a half of OTA volume." |
| 3 | **"Our guests don't book online."** | "Then how did they find you? If they call, the question is whether the phone number was on a page they reached from a search. Phone bookings still count — the booking just needs to be attributable. Let me look at where your calls come from." |
| 4 | **"It's too expensive."** | "Compared to what? You're paying roughly ৳X/month in commission. The question is whether this costs less than the commission it removes. If it can't, I'll tell you — and I'd rather say that now than after three months of your money." |
| 5 | **"Why should I trust a one-person company?"** | "You shouldn't, on trust. So don't. You keep ownership of every account, you set the spend ceiling, nothing public goes out without your approval, and I sign a measurement plan that says what I'll be judged on. Judge me on the first month's report." |
| 6 | **"Can you guarantee bookings?"** | "No. Anyone who does is either lying or about to charge you for bookings you'd have received anyway. What I can guarantee is that you'll be able to verify whether any were produced." |
| 7 | **"My nephew handles our Facebook."** | "Keep him — organic social is worth doing and I'm not trying to replace it. The gap is usually the booking path: paid search for people already searching your name, and a website that doesn't lose them at checkout. Different job." |
| 8 | **"Come back after the season."** | "That's the right instinct, and here's the problem with it: [peak month] is when you're already full, so extra bookings there are worth least. The work pays most in [shoulder month]. But I'll structure the fee around your season rather than pretending a flat month is fair." |
| 9 | **"Send me a proposal."** | "I'll send a one-page read on your own numbers instead — it's more useful than a proposal. If it looks wrong, tell me and I'll fix it. If it looks right, we can talk about the 90 days." |
| 10 | **"What if you spend the budget badly?"** | "Your account, your card, your ceiling. I never hold your money. If I exceed the ceiling, I absorb it. And you can lower the ceiling by email at any time, effective immediately." |
| 11 | **"Do you do SEO / Facebook / influencers too?"** | "One channel for the first 90 days. Spreading across five channels is how a provider produces activity without producing a result — and it makes the measurement useless because you can't tell which channel did anything. Once we have a measured delta on one, we can talk about a second." |
| 12 | **"How long until results?"** | "Six to ten weeks before there's enough clean data to say anything honest. Anyone promising thirty days is reading you a platform dashboard, not your booking report." |

**Three things never to say:** "AI-powered", "guaranteed", "we'll get you to the top of Google". Each marks you as the last provider they fired.

---

## 6. Disqualify fast — the discipline that protects the whole plan

Walk away (politely, permanently) when:

| Signal | Why |
|---|---|
| Occupancy below ~45% and falling | An empty-rooms problem. Marketing spend is the wrong instrument, and you'll be blamed for it |
| Fewer than ~30 rooms at a low ADR | The arithmetic cannot clear break-even, whatever you do (this is the NOT A FIT case in the screener) |
| They won't grant access to booking or OTA data | Without it you cannot measure, and unmeasurable means unprovable means churn |
| No single decision-maker | Every approval takes a week and the engagement dies of latency |
| They want a guarantee of bookings | They will churn no matter what you produce |
| They want you to hold the ad budget | A payments, licensing and legal problem for a one-person company. Never |
| They refuse to write down a spend ceiling | The black-swan failure, invited in |

**Say this out loud on the call:** *"There are hotels I'd turn down because the numbers can't work. If yours is one, I'll say so."* Nothing you can say builds credibility faster — and it is true.

---

## 7. The ask ladder

Never jump rungs. Each is a smaller yes than the next.

| Rung | The ask | What it costs them |
|---|---|---|
| 1 | "Answer two questions about your bookings." | 2 minutes |
| 2 | "Give me 20 minutes on a call." | 20 minutes |
| 3 | "Share three months of reports and one month of OTA statements." | An hour of someone's time |
| 4 | "Here's a one-page read on your own numbers — is it right?" | Reading one page |
| 5 | "Sign a 90-day pilot at the design-partner rate." | ৳15–25k/month for three months, cancellable on 14 days' notice |
| 6 | "Grant access and let me set up measurement." | Their team's cooperation |
| 7 | "Approve the first budget increase." | Trust, earned from a report |

**The single most important rung is 3.** Getting their data turns you from a vendor into the person who already did something for them.

---

## 8. Follow-up cadence (most deals die of silence, not refusal)

| When | What | Channel |
|---|---|---|
| Same day | One line: "Thanks — I'll look at your reports and come back with a one-page read by [day]." | WhatsApp |
| Within 3 business days | **The one-page read.** Lead with the finding they didn't know | WhatsApp + email |
| +3 days | "Did the number look right to you? Happy to walk through it in ten minutes." | WhatsApp |
| +10 days | One useful thing, no ask: "Your branded search share went up 4 points — worth knowing, no action needed." | WhatsApp |
| +21 days | Close the loop honestly: "I'll stop chasing. If the season changes how this looks, message me." | WhatsApp |

Then stop. A provider who keeps pushing after a clear no is the provider they remember badly.

**Never more than four touches without a reply.** Never a template that reads like a template.

---

## 9. What to send, and in what order

1. **Nothing** in the first message except two questions.
2. **The one-page opportunity review** (`prospect review` generates it) after they share data.
3. **The LOI and measurement plan** only when they say "how do we start".
4. **Never** a deck, a case study of another hotel (confidentiality, and you have none yet), or a price list before value.

---

## 10. Self-audit — the five questions after every call

1. Did I lead with **their** number, or with my product?
2. Did I name a specific figure from their own data, or speak generally?
3. Did I ask for something small enough to be an easy yes?
4. Did I disqualify honestly — or chase a hotel I know cannot work?
5. Did I promise anything I would be embarrassed to put in the monthly report?

A conversation that scores badly on 1 or 2 was a pitch, not a diagnosis. Owners can tell the difference even if they can't articulate it.

---

## 11. The honest positioning, in one paragraph

Use this wherever you need to describe what you do:

> I help independent hotels keep more of what they earn. Most hotels pay 15–20% of room revenue to booking platforms for guests who already knew the hotel's name. I find that leakage, fix the booking path, and measure whether it worked — with the measurement agreed before any money is spent. I don't hold your budget, I don't publish without your approval, and if the numbers say it isn't working, I tell you before you have to ask. That last part is the whole difference.
