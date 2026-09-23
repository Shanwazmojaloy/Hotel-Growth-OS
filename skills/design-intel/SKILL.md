---
name: design-intel
description: Evidence-first Figma design intelligence workflow. Use when researching Figma surfaces, auditing design resources, extracting design systems, comparing patterns, or producing traceable recommendations with source coverage, anchored scores, and explicit access limits.
metadata:
  version: "2.0"
  source: "Figma Design Intelligence BRIEF v2"
---
# Figma Design Intelligence â€” BRIEF v2

**Replaces:** "Figma Design Intelligence â€” Deep-Dive Research, Audit & System Extraction Prompt" (v1).
**Why:** v1 was internally contradictory â€” it forbade invention (Â§30), forbade shallowness (Â§31) and forbade
brevity (Â§33), then asked for ~2,880 field answers plus ~150 top-N items from 24 pages that contain a few
hundred extractable facts. Under that load the honesty rule loses. Full scoring:
`reviews/05-figma-brief-adjudication.md`.

**What changed:** sources are tiered; the field list is gated by source type; every source must declare its
coverage; scores have anchors and require cited evidence; lists are capped at 5; the output ends in â‰¤5
recommendations with hours attached. Everything v1 got right â€” the evidence taxonomy, traceability, the
anti-praise rule â€” is kept verbatim.

---

## Â§0 â€” Rules of evidence (unchanged from v1 Â§30, plus one level)

Tag **every** claim with exactly one:

| Tag | Meaning |
|---|---|
| `Observed` | Directly present in the source you fetched. |
| `Inferred` | A conclusion drawn from Observed facts. State the facts it rests on. |
| `Recommendation` | Your professional judgement. Never presented as observation. |
| `Requires-access` | Knowable only by opening the file / signing in. Say what access, and what it would change. |

**Never invent.** No colours, typefaces, tokens, breakpoints, timing values, easing curves, item counts or
licence terms that you did not see. If a field is unknowable from a source, it does not appear in that
source's output at all â€” it is counted in the coverage ledger instead.

**Never mix the four.** A sentence containing two tags is two sentences.

**Traceability:** every finding carries `Source â†’ page â†’ finding â†’ evidence â†’ implication`. A finding without
a URL is deleted, not softened.

**Banned phrasing** (auto-checked): "modern and intuitive", "clean and modern", "best-in-class",
"seamless experience", "looks professional". Explain the mechanism instead: what makes it legible, what makes
it trustworthy, what it costs the user.

---

## Â§1 â€” Sources, tiered

Do not treat 24 sources equally. Uniform treatment is what produced v1's impossible arithmetic.

| Tier | Count | Treatment |
|---|---|---|
| **T1 â€” deep** | 6 | Full field set, all six score dimensions, evidence per claim, coverage ledger |
| **T2 â€” standard** | 10 | Identity + commercial + structure + patterns + up to 3 scores |
| **T3 â€” index** | remainder | One paragraph: what it holds, what it's for, whether to revisit. No scores. |

**T1 (choose these first â€” they change decisions):**
1. `https://www.figma.com/community` â€” the current surface index (it defines what exists)
2. `https://help.figma.com/hc/en-us/categories/360002042553` â€” **Figma Design** docs
3. `https://help.figma.com/hc/en-us/categories/41274596092695` â€” **Figma Motion** docs (v1 listed this URL
   as an anonymous ID and then declared motion unobservable; it is the motion source)
4. `https://www.figma.com/community/ai-workflows?resource_type=files&editor_type=weave` â€” Weave workflows
   (the only listing class observed returning per-resource engagement data)
5. `https://www.figma.com/templates/` â€” Figma's own template framing
6. One vertical that matches the next client: restaurant, SaaS, business, fashion or portfolio

**T2:** `/design/`, `/wireframe-tool/`, `/ui-design-tool/`, `/ux-design-tool/`, `/figjam/brainstorming-tool/`,
`/community/ui-kits`, `/community/wireframes`, `/community/design-templates`, `/community/mobile-apps`,
`/community/icons`

**T3:** `/community/fonts-typography`, `/community/shapes-colors`, `/community/portfolio-templates`, and the
remaining verticals.

**Add these â€” v1 omitted the entire 2026 product surface:**

| Surface | URL | Why it belongs |
|---|---|---|
| Skills | `figma.com/community/ai-skills` | Reusable instructions for the Figma agent â€” the analogue of an agency skill |
| Apps & MCP clients | `figma.com/community/apps` | The MCP surface; Dev Mode MCP server needs a paid seat |
| Weave tools | `figma.com/community/tools` | On-canvas AI tools |
| Make | `figma.com/community/make` + `figma.com/make/` | Prompt-to-app; competes with hand-built landing pages |
| Motion | `figma.com/motion/` | New product surface |
| Draw / Sites / Buzz / Slides / Shaders | `figma.com/draw/`, `/sites/`, `/buzz/`, `/community/shaders` | Publishing, illustration, effects |
| Accessibility tools | `figma.com/community/accessibility` | v1 asked for an accessibility checklist and skipped the category built for it |
| Pricing & plans | `figma.com/pricing/` | Plan gating decides what a solo studio can even use |

**Per-source rules:**
- **Non-zero check.** If a filtered URL returns no items, report it as a **failed source**, not as an empty
  category. (Observed: `/community/ui-kits?resource_type=files&editor_type=figma` returned no listing items
  while `/community/ai-workflows?...editor_type=weave` returned entries with counts.)
- **Deduplicate** URLs and say which were dropped.
- **Follow internal links** only when the linked page materially changes a finding; record the hop.

---

## Â§2 â€” Field gating by source type

Ask only what the source type can answer. `O` = observable Â· `B` = needs a browser session Â·
`R` = requires opening the file Â· `â€”` = not observable, do not request it.

| Field group | Marketing page | Category listing | Help doc | Resource page | Template gallery |
|---|---|---|---|---|---|
| Identity (url, publisher, type, last updated) | O | O | O | O | O |
| Commercial (licence, cost, plan requirement) | â€” | â€” | O | R | B |
| Positioning (what it is, who it's for, what it solves) | O | O (Figma-authored prose + FAQ) | O | O | O |
| Structure & patterns (sections, nav taxonomy, page architecture) | O | B | O | B | B |
| Visual tokens (colour, type ramp, spacing, radius, elevation) | â€” | R | â€” | R | R |
| Interaction & motion (states, timing, easing) | â€” | R | O | R | R |
| Accessibility | â€” | B | O | R | B |
| Adoption evidence (item counts, likes, duplicates) | â€” | O when shown | â€” | O | O |

Two consequences worth stating plainly:
- **A listing page's highest-value content is Figma's own editorial prose.** Observed examples: the restaurant
  gallery states menu/location/hours/contact above the fold, sub-3-second load targets, NAP accuracy and
  schema markup for local search; the SaaS gallery states homepageâ†’featuresâ†’pricingâ†’signup as the core set and
  value-proposition-before-plan-details. Harvest this verbatim with the URL. It is the closest thing to
  methodology the free sources contain.
- **Visual tokens, easings and breakpoints are never observable from a page.** They exist only inside files.
  Count them as `Requires-access` and stop.

---

## Â§3 â€” Per-source output format (machine-checked)

```md
## SOURCE #4 â€” Weave AI workflows
url: https://www.figma.com/community/ai-workflows?resource_type=files&editor_type=weave
tier: T1
type: category-listing
coverage: 9/12 fields answered | 2 not-observable | 1 requires-access
license: not stated on listing page
plan: free to browse; running tools depends on seat AI credits

- Observed: six workflow entries returned with engagement counts (Automated Ads 277 likes / 8k views).
- Observed: Figma-authored intro names use cases â€” image generation, video creation, branding, storytelling.
- Inferred: the Weave surface is positioned as generative asset production, not interface design.
- Requires-access: per-workflow inputs and model choice, visible only inside the workflow.

### Scores
score(ux): 7/10 â€” evidence: entries expose publisher, count and preview without opening the file.
score(interface): 7/10 â€” evidence: consistent card anatomy across entries, single accent colour.
score(production-readiness): 6/10 â€” evidence: outputs are image/video assets, not reusable components.

### Top-5 resources, used for
- Automated Ads: campaign asset generation â€” used for: paid-social creative drafts.
```

Rules: every bullet tagged; coverage line required; `license:` and `plan:` required for T1/T2; scores cite
what was seen.

---

## Â§4 â€” Scorecard

Six dimensions, anchored, scored against **named resources** â€” never against a whole category (a category
mixes Figma's platform with thousands of independent contributors).

| Dimension | 1 | 5 | 10 |
|---|---|---|---|
| `ux` | Blocks the goal | Works with friction | Goal reached without instruction |
| `interface` | Inconsistent anatomy between items | Recognisable conventions | Every state considered, including empty and error |
| `visual-system` | Ad-hoc values per view | One palette and type ramp, loosely applied | Tokens, spacing scale and elevation applied throughout |
| `layout` | Breaks at common widths | Adapts, with manual repair | Fluid across desktop, tablet and mobile |
| `accessibility` | Contrast or focus failures | Passes the obvious checks | Keyboard-complete, announced correctly, motion-reduced |
| `production-readiness` | A mockup | Usable with rework | Ships: components, states, licence clear |

`score(dimension): N/10 â€” evidence: <what you saw>`. A score without evidence is deleted, not adjusted.
Report the distribution; six identical 7s means you weren't looking.

---

## Â§5 â€” Cross-source synthesis

Answer four questions, one page each, evidence-linked:

1. **Recurring** structural patterns across the collections.
2. **Contradictions** â€” where sources disagree (naming, hierarchy, section order).
3. **Emerging** â€” present now, absent from older resources.
4. **Declining** â€” appearing in old files, not in new ones.

**Every list is capped at 5 items and every item carries a `used for:` column.** Top-20 lists are banned;
they are the failure mode v1 Â§31 was written to prevent.

## Â§6 â€” Industry frameworks

One page each, only for a vertical you will actually build: hospitality, SaaS, portfolio, fashion, mobile.
Each ends with the same thing: the section order you will reuse, and the two decisions the source cannot make
for you (copy, and the booking/contact path).

## Â§7 â€” Recommendations (the point of the exercise)

**Cap: 5.** Each one line, with three required fields:

```
1. <action> | cost: <BDT or USD> | hours: <estimate> | decision: <which choice it unlocks>
```

Research that does not end in a decision is a bibliography. If a source produced no recommendation, say so.

## Â§8 â€” Output budget and self-check

| Tier | Budget |
|---|---|
| T1 source | â‰¤ 1 page each |
| T2 source | â‰¤ Â½ page each |
| T3 source | â‰¤ 4 lines each |
| Synthesis | â‰¤ 4 pages |
| Total | **â‰¤ 15 pages**, or say what was cut and why |

Run before delivering:

```bash
python3 check_output.py audit.md --required-fields 12
```

It verifies required fields, coverage arithmetic, tag coverage, score anchors and evidence, list caps, the
recommendation cap and banned phrasing. `--self-test` proves the checker itself works (7/7 mutations caught).

---

## Appendix â€” what v2 deleted from v1, and why

| v1 | Why it went |
|---|---|
| Aâ€“J template for all 24 sources (~2,880 answers) | Impossible at the stated quality bar; the cause of the contradiction |
| 16 unanchored score dimensions | Unreproducible; replaced by 6 anchored ones scored on named resources |
| Â§33's ~150 top-N items | Restates itself and contradicts Â§31's anti-shallow rule |
| Â§24 Design Evolution Map | Narrative taxonomy with no source behind it â€” would be written from priors, which Â§30 forbids |
| Â§29's 18-part structure | Parts 04â€“08, 11â€“14 and 28 substantially overlap |
| "Do not optimize for brevity" | Replaced with a page budget. Scoping is the honesty lever |
| Motion declared unobservable | The brief's own URL #7 documents keyframes, easing, motion paths and path trim |
| "Do not fabricate Community statistics" | Reworded: don't invent them â€” read the ones that are there (4,770+ kits; per-resource counts) |

