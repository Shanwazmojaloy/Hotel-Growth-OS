# Security & Multi-Tenancy Spec — Hotel Growth OS

**Status:** pre-build design. Nothing here is implemented yet.
**Scope:** the controls that must exist *before* the first real tenant's ad account is connected.
**Posture:** this is a design for a **solo operator**. The critique's advice ("pentest before taking real ad spend customers", "per-tenant encryption keys", "SOC 2 path") is correct in spirit and, for you, unaffordable in sequence. This spec orders the controls by **risk reduced per hour spent** and says plainly which ones are Year-1, which are Year-2, and which are theatre at your size.

> Verify anything version-specific (Supabase Vault behaviour, Realtime RLS inheritance, pgcrypto availability) against current Supabase docs at implementation time. This document describes *patterns*, not a substitute for the vendor's docs.

---

## 0. The one-paragraph version

Row Level Security on every tenant-scoped table is not optional, but **RLS is not where multi-tenant systems actually leak.** They leak in the places RLS doesn't reach: background workers using the service role "and forgetting the tenant predicate", storage buckets, realtime channels, edge functions, analytics exports, and LLM prompts that carry one tenant's context into another's run. This spec therefore spends as much space on the **service-role boundary and the prompt boundary** as on policy syntax — because that is where a solo founder will actually ship a cross-tenant bug.

---

## 1. Threat model (ranked by realistic likelihood × damage)

| # | Threat | Likelihood | Damage | Primary control |
|---|---|---|---|---|
| T1 | Cross-tenant data leak via service-role query missing a tenant predicate (cron, worker, nightly job, analytics) | **High** | High | §3.4 service-role discipline + §6.3 adversarial tests |
| T2 | Cross-tenant context contamination in LLM prompts (retrieval returns another hotel's facts) | **High** | High | §7 retrieval scoping + §6.6 prompt-scope tests |
| T3 | Cross-tenant leak through dashboard SSR / cached responses / error messages | Medium | High | §3.6, no-cache on tenant data, error redaction |
| T4 | OAuth token theft from logs, error traces, or repo | Medium | High | §4 redaction layer, no-token-in-logs rule |
| T5 | Compromised tenant staff login (weak passwords, shared accounts) | Medium | Medium | §3.7 MFA, session revocation, per-user audit |
| T6 | Prompt injection via tenant content (a review or a webpage instructing the agent) | **High** | Medium–High | §7.3 injection posture |
| T7 | Over-broad agency/white-label access (client A sees client B) | Medium | High | §3.5 delegated access model |
| T8 | Supply chain (npm/pip, n8n community nodes, an LLM tool) | Medium | High | §8 minimum viable supply chain |
| T9 | Solo-founder operational error under fatigue (the honest #1 risk) | **High** | Medium | §9 defaults + §10 pre-launch gates |
| T10 | Regulatory: PDPO data-subject rights not honour-able | Medium | Medium–High | §11 PDPO duties |

**Deliberately out of scope for Year 1:** nation-state adversaries, per-tenant encryption keys with separate KMS, multi-region DR, formal SOC 2 attestation. Say so to a customer rather than implying otherwise.

---

## 2. Tenancy model

```
organization (the commercial entity: hotel, or hotel group, or your agency client)
  └── property (a physical hotel; one org may own several)
        └── channel_account (Google Ads CID, Meta ad account, GBP location, GA4 property)
  └── membership (user ↔ organization, with role)
```

- **Tenant boundary = `organization_id`.** Every tenant-scoped row carries it. `property_id` narrows further.
- A user may belong to **multiple organizations** (the agency case). Do not model this as "one org per user" — you will regret it, and it is the most common data-model mistake in this category.
- **Roles (minimum viable):** `owner` (billing, tokens, can approve spend), `operator` (approvals, content), `viewer` (read-only), plus `platform_admin` for you — which must be a *separate, audited, MFA-enforced* path, never a normal login.
- **Approval authority is a permission, not a UI state.** "Spend-increase approval" is a capability attached to a role, so it survives refactors.

### 2.1 Data classification (align with PDPO categories)

| Class | Examples in this system | Where it may live |
|---|---|---|
| Public | Hotel name, published content, GBP posts | Anywhere |
| Internal | Performance metrics, budgets, campaign structure | Tenant-scoped rows, RLS |
| Confidential | OAuth tokens, invoices, contract terms, contact lists | Encrypted, access-logged, never in prompts |
| Restricted | Guest PII (names, phone numbers, booking records, geolocation) | **Preferably never stored.** If unavoidable: encrypted column + explicit purpose + retention limit |

**Design rule: guest PII does not enter the LLM path.** Aggregate first, prompt with aggregates. This single rule removes most of your PDPO exposure and most prompt-injection payload surface at once.

---

## 3. Row Level Security

### 3.1 The canonical pattern

```sql
-- membership table is the source of truth for access
create table membership (
  organization_id uuid not null references organization(id) on delete cascade,
  user_id         uuid not null references auth.users(id) on delete cascade,
  role            text not null check (role in ('owner','operator','viewer')),
  primary key (organization_id, user_id)
);
alter table membership enable row level security;

-- helper: does the current user belong to this org?
create or replace function is_member(org uuid)
returns boolean
language sql
stable
security definer          -- must be definer to read membership without recursion
set search_path = public  -- ALWAYS set this on security definer functions
as $$
  select exists (
    select 1 from membership
    where membership.organization_id = org
      and membership.user_id = auth.uid()
  );
$$;
```

Then, on **every** tenant-scoped table:

```sql
alter table campaign enable row level security;
alter table campaign force row level security;   -- applies to table owner too

create policy tenant_read on campaign
  for select using ( is_member(organization_id) );

create policy tenant_write on campaign
  for update using ( is_member(organization_id) )
  with check     ( is_member(organization_id) );
```

Notes that matter:
- **`force row level security`** — without it, the table owner (and therefore some maintenance paths) can read across tenants. Turn it on.
- **Read policies and write policies are separate.** A missing `with check` is how a tenant writes rows into *another* tenant's id.
- **Never join across tables without re-checking membership** in the policy. "The policy on the parent table protects the child" is false.
- Put the tenant predicate in the policy, not in application code. Application-side filtering is a second line of defence, never the first.
- Deny by default: **no table ships without a policy.** A missing policy and a permissive policy look identical from the app; only one of them is safe. §6.1 makes this a CI gate.

### 3.2 Database roles

| Role | Used by | RLS | Notes |
|---|---|---|---|
| `anon` | Unauthenticated | restricted policies | Should be able to reach almost nothing. Test that this is true. |
| `authenticated` | Dashboard users | tenant policies | The normal path. |
| `service_role` | Workers, cron, ingest | **bypasses RLS** | The dangerous one. See §3.4. |
| dedicated app roles (e.g. `ingest`, `scheduler`) | background jobs | RLS applies, with explicit policies | Prefer this over service_role wherever possible. |

**Design decision: minimise service_role usage.** Give background jobs their own role with explicit policies, and reserve `service_role` for schema/admin operations. A worker that can only `insert` into `metrics_daily` for orgs listed in a job payload is a far smaller blast radius than one with the keys to every table.

### 3.3 Views and functions
- Prefer `security_invoker = true` views (they inherit the caller's RLS). A `security definer` view is an RLS bypass in disguise.
- Any `security definer` function: `set search_path`, take `organization_id` as an explicit parameter, and be reviewed by you as if it were public API. There will be few of these; enumerate them on a list you can count on one hand.

### 3.4 The service-role boundary (the most likely real-world leak)

Rules, in order of importance:

1. **Every service-role query takes `organization_id` as a mandatory argument.** No exceptions, no defaults, no "it's obvious from context".
2. **A wrapper, not direct clients.** All service-role data access goes through one module, e.g. `svc.orgQuery({ org, table, where })`, which *requires* `org` and injects the predicate. Direct `supabase.from(...)` calls with the service key are lint-blocked (a grep in CI is enough at this size).
3. **Row-count sanity checks on bulk operations.** A nightly job that expects ~30 rows per tenant and suddenly touches 3,000 has either a bug or a breach. Assert and alert.
4. **Job payloads carry the tenant list**, and the job iterates tenant-by-tenant, never in one cross-tenant statement. Slower, and that is the point: a cross-tenant bug becomes a partial failure instead of a total leak.
5. **One correlation id per agent run**, and every write from that run carries it. When something goes wrong you will need to reconstruct exactly which tenant's context produced which action.

### 3.5 Delegated / agency access
If you later let an agency user manage multiple hotels, model it as **separate memberships per organization**, never as a "sees everything" role. Test T7 explicitly: the agency user with memberships in org A and org B must get a **403**, not an empty result, when querying org C — and the API must not leak C's existence through timing or error text.

### 3.6 Interface layer
- **No shared cache for tenant data.** Per-tenant cache keys that include `organization_id`, or no cache at all in v1.
- Tenant-scoped responses: `Cache-Control: private, no-store`.
- **Error messages are a leak vector.** Return generic errors to the client; keep detail in the server log with the correlation id. A unique-constraint violation can reveal another tenant's identifiers.
- Supabase Realtime respects RLS for `postgres_changes`, but **verify per channel** and test it (T3) — do not assume, and never broadcast tenant data over a channel that isn't RLS-covered.
- Storage: buckets are a parallel authorisation system. Bucket policies must check membership, and object paths must be namespaced by `organization_id/…` so a misconfigured policy fails closed rather than open.

### 3.7 Identity hygiene
MFA required for any role that can approve spend or touch tokens; short session lifetimes for admin; ability to revoke all sessions for a user (hotel staff turnover is constant); no shared logins — if a hotel insists, log the shared-account risk in writing.

---

## 4. Credentials and tokens

- **Storage:** Supabase Vault (or envelope encryption with a key you keep out of the database) for OAuth refresh tokens. Column-level `pgcrypto` if you need encryption with your own key management. Never in n8n environment variables, never in the repo, never in a spreadsheet (I've seen it).
- **Access:** tokens are readable only by the worker role that must use them, never by the dashboard's `authenticated` role. A read of a token is an auditable event.
- **Refresh:** single refresher with a Postgres advisory lock per credential. Concurrent refreshes are how you get rate-limited or silently invalidated by the platform.
- **Rotation & revocation:** store `expires_at`, refresh proactively, and treat a 401 as "revoke and re-auth the tenant", not "retry". Surface it as a task in the daily digest with a one-click reconnect.
- **Least privilege at the source:** Google Ads via manager-account link (not password sharing); Meta via **system user tokens** (never a personal user token that dies when a human leaves); GBP via manager access, never ownership transfer.
- **Logging:** a redaction filter in the logger (keys matching `token|secret|authorization|refresh|cookie`, plus a regex for `ya29.`, `EAA`, `sk-`, `Bearer`) that runs **before** anything reaches log storage. Do not rely on remembering.
- **Agent-facing:** the reasoning layer never receives a token. It emits a **proposal**; an executor with the credential performs the action. This is the single most important structural control in the whole document, because it makes T4 (token theft) and T6 (prompt injection) non-catastrophic: a hijacked prompt can at most produce a proposal that the executor refuses.

---

## 5. Audit trail and the action ledger

Two tables, both append-only, both tenant-scoped with RLS:

**`audit_event`** — every state change, human or agent: `id, organization_id, actor_type (user|agent|system), actor_id, correlation_id, action, object_type, object_id, before, after, ip, created_at`.
Enforce append-only by revoking `UPDATE`/`DELETE` from application roles and granting only `INSERT`/`SELECT` (a trigger that raises on update/delete is belt-and-braces). Retention: **five years minimum** — PDPO requires processing records be maintained, so this is a compliance asset, not just an ops one.

**`action_log`** — the agent-specific ledger the critique correctly insisted on: `id, organization_id, correlation_id, agent, proposed_action, risk_class, reversibility, decision (auto|approved|rejected|expired), decided_by, decided_at, executed_at, external_ref, cost_usd, rollback_available, rollback_ref`.

This table is what makes the autonomy ladder auditable: to raise an agent to L3 you must show a run of auto-decisions with zero rollbacks of consequence. It is also your billing evidence and your dispute-resolution artefact ("we lowered the bid at 14:02, here is the log").

**Cost ledger** (can live in the same table or beside it): per-run input/output tokens, model, cache-hit flag, cost, correlation to the action. Per-tenant and global budget envelopes check *this* table before every call, with a hard stop — not a warning email.

---

## 6. Adversarial test plan

This is the part the critique was right about and under-specified. Write these as real tests, not a checklist you read once.

### 6.1 Structural gates (CI, every commit)
1. **Policy census:** every table with an `organization_id` column has RLS enabled, `force row level security`, and at least one policy per operation used. Fail the build if any table has zero policies (a table without a policy is not "open" — it is *unreviewed*).
2. **Service-role lint:** grep the codebase for service-key usage outside the wrapper module; fail the build.
3. **Migration review gate:** any migration that creates a table must add its policies in the same migration. No "I'll add policies later."

### 6.2 The two-org fixture
Seed org A and org B with overlapping-but-distinguishable data (same property names, different ids — this catches "filter by name" bugs). For every API route and every server action, run an authenticated-as-A request targeting B's identifiers and assert **404/403, empty body, no timing tell**. Keep this as a parameterised suite so new endpoints inherit it automatically.

### 6.3 Service-role path tests (T1)
A test that calls each background job and worker entry point with a payload containing **only org A**, seeds rows in org B, and asserts B's rows are untouched. Then a mutation test: remove the tenant predicate from the wrapper and confirm **the test fails**. If deleting the safety check does not break a test, you do not have a test.

### 6.4 Storage, realtime, edge
- Object from A's namespace is not readable with B's credentials (and not readable anonymously).
- Realtime channel for A receives no events from B's rows.
- Each edge/worker function validates its caller's membership before doing anything with a tenant id from the request body. **Never trust a tenant id supplied by the client.**

### 6.5 Token and log hygiene
- Assert that a full request cycle produces zero occurrences of any credential in log output (seed a canary token, grep the logs).
- Assert token columns are unreadable to the dashboard role (`select` as `authenticated` must fail or return null).

### 6.6 Prompt-scope tests (T2)
- Retrieval test: with only org A's knowledge base populated, a query for B's property name returns nothing from B. Include near-duplicate names and shared brand words — this is where naive similarity search fails.
- **Context-assembly assertion:** every prompt-rendering function is called with an `organization_id` and refuses to render if any retrieved chunk's org does not match. Fail loudly, do not silently drop.
- Golden-set replay per tenant monthly: the same prompt set run for org A must not mention org B's facts (an LLM-as-judge check that costs cents and catches the worst possible bug).

### 6.7 Approval and rollback integrity
- Attempt to execute a `financial_increase` action without an approval record → must fail.
- Attempt to execute with an expired or self-approved approval → must fail.
- For every action class marked reversible, assert a rollback path exists and works (pause → resume, budget change → revert). Untested rollback is not a rollback.

**Time cost, honest estimate (solo):** the structural gates and two-org fixture are ~12–18 hours to build and then nearly free to maintain — the highest security ROI available to you. The full suite is ~40–60 hours spread over the build. Do it once, incrementally, never as a "hardening sprint" (that sprint never happens).

---

## 7. Agent-specific controls

### 7.1 Capability matrix, enforced in code
Encode the reversibility asymmetry from the adjudication as data, not as prose:

```yaml
# enforcement lives in the executor, not in the prompt
pause_campaign:        { class: reversible_reducing, autonomy: L4 }
lower_bid:             { class: reversible_reducing, autonomy: L4 }
raise_budget:          { class: financial_increasing, autonomy: L1 }
create_campaign:       { class: financial_increasing, autonomy: L1 }
publish_gbp_post:      { class: irreversible_brand, autonomy: L2 }
reply_to_review:       { class: irreversible_brand, autonomy: L2 }
send_outbound_message: { class: irreversible_brand, autonomy: L2 }
draft_content:         { class: reversible_neutral, autonomy: L3 }
```
The executor checks the class before acting and refuses regardless of what the model proposed. **The model's confidence never overrides the matrix.**

### 7.2 Hard stops
Global, per-tenant, and per-channel kill switches; per-tenant daily/monthly AI budget and per-platform action quotas; a per-tenant spend ceiling *and* a maximum single-action delta (e.g. no single budget change above +15%); automatic freeze on anomalous platform errors or a burst of reversals. All of these live in the executor and are tested (§6.7).

### 7.3 Prompt-injection posture (T6)
Assume every external string is hostile: reviews, hotel websites, competitor pages, PDFs, even your own knowledge base after a hotel uploads a document. Posture: (a) tokens never reach the reasoner (§4); (b) retrieved content is data, never instructions — delimit and label it, and never concatenate it into the system message; (c) the executor validates the *shape* of every proposed action against the matrix and the ceilings; (d) any action derived from externally-sourced content is downgraded one autonomy level;
(e) log the source chunks that produced each proposal so a bad action is traceable to a bad input.

### 7.4 Dry-run mode
One code path, one flag: every executor action can run against a sandbox/log-only backend. This is your testing substrate, your demo mode, your onboarding tool ("here's what the agent would do this week"), and your safest way to raise autonomy — run new capabilities in dry-run against a live tenant for two weeks before granting execution rights.

---

## 8. Supply chain and platform posture (minimum viable)

- Pin dependencies; commit lockfiles; no new npm/pip package without you reading its purpose. At your size this is 10 minutes a week and it is the difference between a bug and a breach.
- n8n community nodes: install only from vendors you can name, and never on an instance holding customer credentials (see the licensing section of the adjudication — this is also a security argument for keeping n8n out of the multi-tenant credential path).
- **Get the licensing question answered in writing before you build the backbone** (n8n Sustainable Use License). A licensing problem discovered after onboarding 10 hotels is far more expensive than an email.
- VPS hygiene: no public admin UI, Cloudflare Tunnel or WireGuard, unattended security updates, daily encrypted backups, and a **restore drill you have actually performed** (an untested backup is a rumour).

---

## 9. Choose the risky defaults once, in code

Under fatigue, you will take the shortest path. So make the safe path the short path:

| Default | Why |
|---|---|
| New table template **already contains** RLS + policies + force RLS | Nobody remembers to add them later |
| Service-role client is **not importable** outside the wrapper | Removes T1 by construction |
| Tokens are **not retrievable** by the reasoner or the dashboard | Removes T4/T6 escalation |
| Logger redacts by default, not opt-in | Fatigue-proof |
| **Fail closed** on platform 5xx, ambiguous state, or missing approval | An agent that stops is boring; an agent that guesses is a lawsuit |
| Every agent action writes `audit_event` + `action_log` in the same transaction | Retro-fitting audit trails never works |

---

## 10. Pre-launch security gates (no real ad spend until all true)

1. RLS + policies + `force` on every tenant table, with the CI census passing.
2. Two-org adversarial suite green, including one mutation test per control.
3. Zero credentials reachable in logs (canary test).
4. Tokens encrypted at rest, unreadable to the dashboard role, single-refresher lock in place.
5. Capability matrix enforced in the executor; approval integrity and rollback tests passing.
6. Kill switches tested *live* (not just written) at global, tenant, and channel scope.
7. Backup restored into a scratch environment at least once.
8. DPA template + PDPO duties mapped to a real process (consent, retention, deletion, breach runbook).
9. Dry-run mode demonstrated to the first design partner as a feature, not a caveat.
10. A written, one-page incident runbook you have read *after* being woken up at night — a tabletop is enough.

**What you may defer to Year 2, in writing, to the customer:** per-tenant encryption keys with separate KMS, SOC 2 / ISO 27001 attestation (Supabase Team at $599/mo carries SOC 2 if a customer demands it), multi-region DR, and a third-party penetration test (book it when the first hotel with a brand-compliance department signs, and budget for a real cost — it is not a $500 exercise).

---

## 11. PDPO-specific duties (Bangladesh)

Statute: Personal Data Protection Ordinance, gazetted November 2025, amended by Ordinance No. 23 of 2026 (5 February 2026) — the amendment narrowed localisation to restricted/CII data. **Your role as platform: processor. The hotel: controller.** Practical mapping:

| Duty | What it means here |
|---|---|
| Consent & purpose limitation | Hotels collect guest consent; you must not repurpose guest data (e.g. no training on guest records, no enrichment resale) |
| Records of processing | `audit_event` retention ≥5 years doubles as this |
| Breach notification | Written runbook + a contact list for every tenant; design for notification within the authority's prescribed window (do not assume a 72-hour number — confirm the current rule) |
| Data-subject rights | Ability to export, correct, and delete a data subject's records on request; documented in the DPA and tested once |
| Security measures | Pseudonymisation/encryption where appropriate; the controls in §3–§4 are the substance of this |
| Retention limits | Aggregated metrics: keep. Raw guest-identifying rows: delete on a schedule you can state out loud |
| Localisation | Only restricted data and CII require a synchronised in-country copy — **do not build for worst-case localisation until a customer or counsel says you must**, but do not store restricted-class data offshore either |

The cheapest compliance posture that survives scrutiny: **don't hold guest PII at all.** Aggregate at ingestion, prompt with aggregates, delete what you don't need. That is a design decision, not a legal one — and it is free if you make it now.
