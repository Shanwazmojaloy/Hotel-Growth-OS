# Skeleton — the executable core of the security spec

This is `03-security-multitenancy-spec.md` turned into something that runs: a schema with real policies, a worker that cannot be talked into leaking, and a test suite that proves it — plus a harness that proves the tests aren't decoration.

```bash
./scripts/verify_all.sh        # all five gates, one command
```

Current status on a local PostgreSQL 17.10 cluster:

```
✔ 1. policy census (static: RLS enabled + forced + policied, no permissive policies)
✔ 2. service-role containment (one file may hold the credential)
✔ 3. type-check worker (strict, noUncheckedIndexedAccess)
✔ 4. RLS adversarial suite (two orgs, near-identical names)   — 73 assertions
✔ 5. mutation harness (does the suite actually test anything?) — 7/7 mutations killed
```

---

## Layout

```
db/
  migrations/
    0001_core_schema.sql           18 tables · no credential columns · no guest PII
    0002_tenant_rls.sql            explicit policies per table (greppable, not generated)
    0003_ledger_append_only.sql    immutability + the only functions that may write
    0004_app_roles_and_grants.sql  least-privilege ingest/scheduler roles
    0005_optional_pgvector.sql     embeddings, skipped where pgvector is absent
  tests/
    00_shim_local_auth.sql         LOCAL ONLY: stubs the auth schema Supabase provides
    01_fixtures_two_orgs.sql       two orgs, near-identical names, overlapping ids
    02_rls_adversarial.sql         61 assertions: isolation, roles, ledgers, approvals
    03_ingest_role.sql             12 assertions: worker tenant binding
    run_tests.sh                   rebuild → migrate → seed → assert
    mutation_test.sh               sabotage a control; the suite must fail
apps/worker/src/
  db/service.ts                    the ONLY file allowed to hold service credentials
  executor/capabilityMatrix.ts     the reversibility asymmetry, as data
  executor/executor.ts             kill switches → matrix → budget → ledger → act
  logging/redact.ts                redaction before anything reaches log storage
scripts/
  ci/policy_census.py              static gate, runs without a database
  ci/guard_service_role.sh         containment lint
  verify_all.sh                    all gates
.github/workflows/security-gates.yml
```

## What the tests actually prove

**Isolation.** Organisation A sees exactly its own 2 properties, 1 campaign, 2 booking rows, 1 knowledge doc. Both orgs have properties literally named *"Sea Breeze Resort"* — so any layer that filters by name, by stale cache, or by naive similarity search fails the suite immediately. Cross-tenant inserts and updates are refused or touch zero rows, and a post-condition asserts no row named `HACKED` exists anywhere afterwards.

**FORCE RLS.** A purpose-built non-superuser role is made the *owner* of `campaign` mid-transaction and still sees zero rows without a tenant claim. That is the difference between `enable` (cosmetic for owners) and `force` (real).

**Immutability.** `audit_event` and `cost_ledger` refuse UPDATE and DELETE at two levels: the privilege is revoked for tenant roles, and a trigger raises `23001` even for the table owner. `action_log` allows its decision to change exactly once, out of `pending`, and never back.

**The reversibility asymmetry, in the database.** `fn_propose_action` refuses to auto-execute anything classed `financial_increasing` — regardless of what the reasoning layer or the worker believes. A gated action cannot execute while `pending`; a decided action cannot be re-decided; a live execution without an external reference is refused.

**Worker binding.** The `ingest` role writes metrics for the organisation it is bound to and is *refused* for any other. Unbound, it sees nothing and can write nothing — fail closed, not fail open. It has no grant on the audit trail at all.

**Multi-org membership.** The agency user with memberships in both orgs sees exactly 3 properties and still cannot see anything outside them. Multi-membership never becomes a god role.

## What the tests found (the honest version)

Two of the seven mutation runs initially reported **SURVIVED**, and both were real:

1. **A genuine bug in the schema.** `action_log_guard` forbade *all* updates once a decision existed, which silently blocked the executor's own bookkeeping on auto-decided actions (dry runs returned `error:23001`). Fixed by comparing decision *values* rather than forbidding updates wholesale — the decision may change once, out of `pending`, while execution metadata is updated in place.

2. **A blind spot in the suite.** The trigger was untested at the level it operates: the RPC refuses first, so removing the trigger broke nothing. Added Group 5b, which attacks the table directly with elevated privileges.

3. **A bug in the harness itself.** One mutation failed to apply (`CREATE OR REPLACE` cannot rename parameters), and an inapplicable mutation masquerades as a survivor — hiding a blind spot. The harness now fails loudly if a mutation does not apply.

Worth internalising: *all three were only visible because the mutation harness exists.* A green suite proves nothing about what it fails to look at.

## Design decisions worth knowing

| Decision | Why |
|---|---|
| Policies written explicitly per table, not generated in a loop | Security config should be greppable and reviewable line by line; the census verifies it textually |
| No credential columns in the schema at all | `channel_account.credential_ref` points at Vault. Tokens never enter a queryable table, a log, or a prompt |
| No guest PII modelled anywhere | The cheapest PDPO posture is not holding the data. `booking_fact` is aggregates |
| Worker uses `ingest` role, not the service role | Tenant binding enforced by policy, so a job-loop bug is a refusal rather than a leak |
| Every service-role result is verified against the requested org at runtime | A missing predicate becomes a loud `CrossTenantLeakError` instead of a silent leak |
| Dry-run does **not** relax the capability matrix | A simulation must produce the decision the live system would, or the ledger's evidence for raising autonomy is fiction |
| `service_role` has full table privileges in grants | Mirrors Supabase. That is precisely why the wrapper exists — the danger is real, so contain it structurally |

## Deliberately not here

This is a skeleton, and the gaps are on purpose — each one is a decision you should make with the spec open:

- **Storage and Realtime policies.** Buckets are a parallel authorisation system; RLS on tables does not protect them. Write bucket policies namespaced `organization_id/…` and test them.
- **Edge function caller validation.** Every function must validate membership before trusting a tenant id from the request body. Never trust a client-supplied org.
- **Vault wiring.** `credential_ref` is a placeholder column; the actual seal/unseal, single-refresher advisory lock and rotation job are not written yet.
- **Adapters.** `ChannelAdapter` is an interface. Google Ads / Meta / GBP clients, with circuit breakers and mocking, are the next real work — and the platform access gates in the adjudication come first.
- **Prompts, evals, retrieval.** The prompt-scope tests from the spec (context assembly refuses chunks from another org; monthly golden-set replay) belong with the reasoning layer.
- **Frontend.** Approvals, cost dashboards and Realtime subscriptions.

## Using this against Supabase

The migrations are Supabase-compatible as written. Locally the suite runs against plain PostgreSQL using `00_shim_local_auth.sql`, which stubs `auth.uid()`, `auth.jwt()` and the three roles — **never apply the shim to Supabase**, it already has all of it. Against a Supabase project:

```bash
supabase db reset          # applies db/migrations
supabase test db           # or: SKIP_SHIM=1 ./db/tests/run_tests.sh
```

The TypeScript type-checks under `strict` with `noUncheckedIndexedAccess`; it has not been executed against a live database in this environment, and the adapter layer is intentionally unwritten.
