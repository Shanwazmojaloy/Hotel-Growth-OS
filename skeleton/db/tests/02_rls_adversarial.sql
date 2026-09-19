-- ============================================================================
-- 02_rls_adversarial.sql — the two-organisation adversarial suite.
--
-- Every assertion either passes or raises, so `psql -v ON_ERROR_STOP=1` returns
-- non-zero on the first violation. That property is what makes the mutation
-- harness (mutation_test.sh) meaningful: sabotage the schema, and this file
-- must fail.
--
-- Fixture ids (db/tests/01_fixtures_two_orgs.sql):
--   org A  = 11111111-...  Sea Breeze Cox's Bazar  (2 properties, 1 campaign)
--   org B  = 22222222-...  Sea Breeze Sylhet       (1 property,  1 campaign)
--   owner A / viewer A / operator A / owner B / agency (both orgs) / platform admin
-- ============================================================================

\set ON_ERROR_STOP on
\echo ''
\echo '=== Group 1 — catalog invariants (structural, run as database owner) ==='

select test_assert(
  (select count(*) from pg_class c
     join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relkind = 'r'
      and exists (select 1 from information_schema.columns col
                   where col.table_schema = 'public' and col.table_name = c.relname
                     and col.column_name = 'organization_id')
      and not c.relrowsecurity) = 0,
  'every table carrying organization_id has RLS enabled');

select test_assert(
  (select count(*) from pg_class c
     join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relkind = 'r'
      and exists (select 1 from information_schema.columns col
                   where col.table_schema = 'public' and col.table_name = c.relname
                     and col.column_name = 'organization_id')
      and not c.relforcerowsecurity) = 0,
  'every table carrying organization_id has FORCE RLS (no owner bypass)');

select test_assert(
  (select count(*) from pg_class c
     join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relkind = 'r'
      and exists (select 1 from information_schema.columns col
                   where col.table_schema = 'public' and col.table_name = c.relname
                     and col.column_name = 'organization_id')
      and not exists (select 1 from pg_policies pol
                       where pol.schemaname = 'public' and pol.tablename = c.relname)) = 0,
  'no tenant table is left without at least one policy (unreviewed is not "open")');

\echo ''
\echo '=== Group 2 — org A owner: own data visible, org B data invisible ==='

begin;
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000001"}';
  set local role authenticated;

  select test_assert(scalar_int('select count(*) from property') = 2,
    'owner A sees exactly its own 2 properties');
  select test_assert(scalar_int('select count(*) from campaign') = 1,
    'owner A sees exactly 1 campaign');
  select test_assert(scalar_int('select count(*) from booking_fact') = 2,
    'owner A sees exactly its 2 booking rows');
  select test_assert(scalar_int('select count(*) from knowledge_doc') = 1,
    'identical titles across orgs do not leak (name-based filtering would fail here)');
  select test_assert(scalar_int('select count(*) from knowledge_chunk') = 1,
    'retrieval corpus is org-scoped');
  select test_assert(scalar_int('select count(*) from metric_daily') = 1,
    'metric_daily is org-scoped');
  select test_assert(scalar_int('select count(*) from measurement_plan') = 1,
    'measurement plan is org-scoped');
  select test_assert(scalar_int($q$select count(*) from property
      where organization_id = '22222222-2222-2222-2222-222222222222'$q$) = 0,
    'a direct predicate on org B returns nothing, not an error and not rows');
  select test_assert(scalar_int($q$select count(*) from audit_event
      where organization_id = '22222222-2222-2222-2222-222222222222'$q$) = 0,
    'audit trail is org-scoped too');
rollback;

\echo ''
\echo '=== Group 3 — cross-tenant writes must fail ==='

begin;
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000001"}';
  set local role authenticated;

  select test_assert(try_affected($q$insert into campaign
      (organization_id, property_id, platform, name, status)
      values ('11111111-1111-1111-1111-111111111111',
              'a1111111-0000-0000-0000-000000000001', 'google_ads', 'Own-org insert', 'draft')$q$) = 1,
    'owner A can insert a campaign into its OWN org');

  select test_assert(try_affected($q$insert into campaign
      (organization_id, property_id, platform, name, status)
      values ('22222222-2222-2222-2222-222222222222',
              'b1111111-0000-0000-0000-000000000001', 'google_ads', 'Cross-tenant insert', 'draft')$q$) = -1,
    'owner A inserting into org B is REFUSED');

  select test_assert(try_affected($q$update campaign set name = 'HACKED'
      where organization_id = '22222222-2222-2222-2222-222222222222'$q$) = 0,
    'owner A updating org B touches zero rows');

  select test_assert(try_affected($q$delete from campaign
      where organization_id = '22222222-2222-2222-2222-222222222222'$q$) = 0,
    'owner A deleting org B touches zero rows');

  select test_assert(try_affected($q$update property set name = 'HACKED'
      where id = 'b1111111-0000-0000-0000-000000000001'$q$) = 0,
    'owner A cannot rewrite org B property by primary key');

  select test_assert(try_affected($q$insert into metric_daily
      (organization_id, property_id, channel, metric_date, source)
      values ('22222222-2222-2222-2222-222222222222',
              'b1111111-0000-0000-0000-000000000001', 'google_ads', current_date, 'manual_upload')$q$) = -1,
    'owner A cannot inject metrics into org B');
rollback;

select test_assert(scalar_int($q$select count(*) from campaign where name = 'HACKED'$q$) = 0,
  'no write leaked: no row named HACKED exists anywhere');

\echo ''
\echo '=== Group 4 — role granularity inside a tenant ==='

begin;
  -- viewer: read only
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000002"}';
  set local role authenticated;
  select test_assert(scalar_int('select count(*) from property') = 2,
    'viewer can read its org data');
  select test_assert(try_affected($q$insert into property
      (organization_id, name, city, rooms)
      values ('11111111-1111-1111-1111-111111111111', 'Viewer insert', 'Dhaka', 10)$q$) = -1,
    'viewer cannot insert a property');
  select test_assert(try_affected($q$update budget_envelope set ai_budget_usd = 999$q$) = 0,
    'viewer cannot raise the AI budget');
rollback;

begin;
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000003"}';
  set local role authenticated;
  select test_assert(try_affected($q$update channel_account set external_id = 'TAMPERED'$q$) = 0,
    'operator cannot modify channel accounts (owner-only: these point at credentials)');
  select test_assert(try_affected($q$delete from booking_fact$q$) = 0,
    'operator cannot delete booking facts');
  select test_assert(try_affected($q$insert into measurement_plan
      (organization_id, property_id, version, counterfactual_design)
      values ('11111111-1111-1111-1111-111111111111',
              'a1111111-0000-0000-0000-000000000001', 2, 'geo_holdout')$q$) = -1,
    'operator cannot sign a new measurement plan (owner-only)');
  select test_assert(try_affected($q$update campaign set daily_budget_bdt = 3000
      where organization_id = '11111111-1111-1111-1111-111111111111'$q$) = 1,
    'operator CAN adjust campaign state within its own org');
rollback;

begin;
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000001"}';
  set local role authenticated;
  select test_assert(try_affected('update channel_account set external_id = ''CID-A-100''') = 1,
    'owner can maintain channel accounts');
rollback;

\echo ''
\echo '=== Group 5 — immutable trails ==='

begin;
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000001"}';
  set local role authenticated;
  select test_assert(try_affected('update audit_event set action = ''tampered''') = -1,
    'authenticated role cannot UPDATE the audit trail (privilege revoked, not just unpolicied)');
  select test_assert(try_affected('delete from audit_event') = -1,
    'authenticated role cannot DELETE the audit trail');
  select test_assert(try_affected('update cost_ledger set cost_usd = 0') = -1,
    'authenticated role cannot rewrite the cost ledger');
  select test_assert(try_affected('delete from action_log') = -1,
    'action_log cannot be pruned by a user');
  select test_assert(try_affected('update action_log set decision = ''auto''') = -1,
    'action_log decisions cannot be forged directly');
rollback;

-- Even with the privileges of the database owner, the trigger blocks mutation.
select test_assert(try_stmt('update audit_event set action = ''trigger test''') = 'error:23001',
  'audit_event is append-only even for the table owner (trigger raises)');
select test_assert(try_stmt('delete from cost_ledger') = 'error:23001',
  'cost_ledger is append-only even for the table owner');

\echo ''
\echo '=== Group 5b — direct table mutation: the trigger is the last line ==='

-- The RPC refuses most of this already, so these assertions exist to test the
-- LAYER ITSELF: what happens when a future migration, a service-role script or
-- a grant mistake tries to write the ledger directly.
begin;
  select fn_propose_action('11111111-1111-1111-1111-111111111111',
    'f0000000-0000-0000-0000-0000000000b1', 'content', 'publish_gbp_post',
    'irreversible_brand', '{"post":"direct-mutation test"}'::jsonb, 'gated');
  select fn_decide_action(
    (select id from action_log where correlation_id = 'f0000000-0000-0000-0000-0000000000b1'),
    'approved', 'approved for the mutation test');

  select test_assert(try_stmt($q$update action_log set decision = 'rejected'
      where correlation_id = 'f0000000-0000-0000-0000-0000000000b1'$q$) = 'error:23001',
    'a final decision cannot be changed by a direct privileged UPDATE');

  select test_assert(try_stmt($q$update action_log set decision = 'pending'
      where correlation_id = 'f0000000-0000-0000-0000-0000000000b1'$q$) = 'error:23001',
    'a decided action can never be returned to pending');

  select test_assert(try_stmt($q$delete from action_log
      where correlation_id = 'f0000000-0000-0000-0000-0000000000b1'$q$) = 'error:23001',
    'action_log rows cannot be deleted even with privileges');

  select test_assert(try_stmt($q$update action_log set executed_at = now()
      where correlation_id = 'f0000000-0000-0000-0000-0000000000b1'$q$) = 'ok',
    'execution bookkeeping on a decided action is still permitted (regression guard)');
rollback;

\echo ''
\echo '=== Group 6 — reversibility asymmetry enforced in the database ==='

begin;
  select test_assert(try_stmt($q$select fn_propose_action(
      '11111111-1111-1111-1111-111111111111',
      'f0000000-0000-0000-0000-000000000001',
      'media_buying', 'raise_budget', 'financial_increasing',
      '{"delta_pct": 25}'::jsonb, 'auto')$q$) like 'error%',
    'a financial_increasing action can NEVER be auto-executed');

  select test_assert(scalar_int($q$select count(*) from (
      select fn_propose_action(
        '11111111-1111-1111-1111-111111111111',
        'f0000000-0000-0000-0000-000000000002',
        'media_buying', 'pause_campaign', 'reversible_reducing',
        '{"campaign_external_id": "C-A-1"}'::jsonb, 'auto') as id) s$q$) = 1,
    'a reversible_reducing action may be auto-executed');

  select test_assert(scalar_int($q$select count(*) from action_log
      where correlation_id = 'f0000000-0000-0000-0000-000000000002' and decision = 'auto'$q$) = 1,
    'the auto action is recorded with decision = auto');
rollback;

\echo ''
\echo '=== Group 7 — approval flow: no decision, no execution ==='

begin;
  set local role service_role;   -- the worker proposes; this is a system path
  set local request.jwt.claims = '';

  select test_assert(scalar_int($q$select count(*) from (
      select fn_propose_action(
        '11111111-1111-1111-1111-111111111111',
        'f0000000-0000-0000-0000-000000000003',
        'content', 'publish_gbp_post', 'irreversible_brand',
        '{"post": "Monsoon offer"}'::jsonb, 'gated') as id) s$q$) = 1,
    'a gated brand-facing action can be proposed');

  select test_assert(scalar_int($q$select count(*) from action_log
      where correlation_id = 'f0000000-0000-0000-0000-000000000003' and decision = 'pending'$q$) = 1,
    'gated action lands in pending, never in auto');

  select test_assert(scalar_int($q$select count(*) from approval_request r
      join action_log a on a.id = r.action_id
      where a.correlation_id = 'f0000000-0000-0000-0000-000000000003' and r.status = 'pending'$q$) = 1,
    'an approval request was created automatically');
rollback;

begin;
  set local request.jwt.claims = '';
  set local role service_role;
  select fn_propose_action(
    '11111111-1111-1111-1111-111111111111',
    'f0000000-0000-0000-0000-000000000004',
    'content', 'publish_gbp_post', 'irreversible_brand',
    '{"post": "second"}'::jsonb, 'gated');

  select test_assert(try_stmt($q$select fn_mark_executed(
      (select id from action_log where correlation_id = 'f0000000-0000-0000-0000-000000000004'),
      'gbp://post/123', false)$q$) like 'error%',
    'an action in pending state REFUSES to execute');

  -- operator cannot decide an irreversible_brand action? (required_role = operator for brand)
  reset role;
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000002"}';  -- viewer A
  set local role authenticated;
  select test_assert(try_stmt($q$select fn_decide_action(
      (select id from action_log where correlation_id = 'f0000000-0000-0000-0000-000000000004'),
      'approved', 'viewer approving')$q$) like 'error%',
    'a viewer cannot approve anything');

  reset role;
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000003"}';  -- operator A
  set local role authenticated;
  select test_assert(try_stmt($q$select fn_decide_action(
      (select id from action_log where correlation_id = 'f0000000-0000-0000-0000-000000000004'),
      'approved', 'operator approving brand post')$q$) = 'ok',
    'the operator (required role for brand-facing actions) can approve');

  select test_assert(try_stmt($q$select fn_decide_action(
      (select id from action_log where correlation_id = 'f0000000-0000-0000-0000-000000000004'),
      'approved', 'approving twice')$q$) like 'error%',
    'a decided action cannot be re-decided (decision is final)');

  select test_assert(try_stmt($q$select fn_decide_action(
      (select id from action_log where correlation_id = 'f0000000-0000-0000-0000-000000000004'),
      'rejected', 'flip it')$q$) like 'error%',
    'a decided action cannot be flipped');
rollback;

begin;
  set local role service_role;
  set local request.jwt.claims = '';
  select fn_propose_action('11111111-1111-1111-1111-111111111111',
    'f0000000-0000-0000-0000-000000000005', 'analytics', 'add_negative_keywords',
    'reversible_reducing', '{"keywords": ["cheap","free"]}'::jsonb, 'auto');

  select test_assert(try_stmt($q$select fn_mark_executed(
      (select id from action_log where correlation_id = 'f0000000-0000-0000-0000-000000000005'),
      null, true)$q$) = 'ok',
    'a dry run may execute without an external reference');

  select test_assert(try_stmt($q$select fn_mark_executed(
      (select id from action_log where correlation_id = 'f0000000-0000-0000-0000-000000000005'),
      null, false)$q$) like 'error%',
    'a LIVE execution without an external reference is refused');
rollback;

\echo ''
\echo '=== Group 8 — kill switches and the platform-admin path ==='

begin;
  set local request.jwt.claims = '{"sub":"aaaaaaaa-0000-0000-0000-000000000001"}';
  set local role authenticated;
  select test_assert(scalar_int('select count(*) from kill_switch') = 1,
    'org A sees its own switch only');
  select test_assert(scalar_int('select count(*) from kill_switch where organization_id is null') = 0,
    'org A cannot see the global kill switch');
  select test_assert(try_affected($q$insert into kill_switch (scope, engaged, reason)
      values ('global', true, 'tenant tries to hit the master switch')$q$) = -1,
    'a tenant cannot create a GLOBAL kill switch');
  select test_assert(try_affected($q$insert into kill_switch
      (scope, organization_id, channel, engaged, reason)
      values ('channel', '11111111-1111-1111-1111-111111111111', 'google_ads', true, 'monsoon')$q$) = 1,
    'a tenant can pull its own channel switch');
rollback;

begin;
  set local request.jwt.claims = '{"sub":"dddddddd-0000-0000-0000-000000000001"}';
  set local role authenticated;
  select test_assert(scalar_int('select count(*) from kill_switch where organization_id is null') = 1,
    'the platform admin can see the global switch');
  select test_assert(try_affected($q$update kill_switch set engaged = true
      where organization_id is null$q$) = 1,
    'the platform admin can pull the global switch');
rollback;

\echo ''
\echo '=== Group 9 — multi-org membership (the agency case) ==='

begin;
  set local request.jwt.claims = '{"sub":"cccccccc-0000-0000-0000-000000000001"}';
  set local role authenticated;
  select test_assert(scalar_int('select count(*) from property') = 3,
    'the agency user with memberships in both orgs sees exactly 3 properties');
  select test_assert(scalar_int($q$select count(*) from property
      where organization_id = '11111111-1111-1111-1111-111111111111'$q$) = 2,
    'and it can still be scoped per organisation');
  select test_assert(scalar_int('select count(*) from campaign where organization_id is null') = 0,
    'multi-membership never becomes a god role (no null-org rows visible)');
rollback;

\echo ''
\echo '=== Group 10 — FORCE RLS: the table owner is not above the policy ==='

begin;
  create role tmp_table_owner nologin;
  grant usage on schema public to tmp_table_owner;
  grant execute on function scalar_int(text) to tmp_table_owner;
  alter table campaign owner to tmp_table_owner;

  set local request.jwt.claims = '';
  set local role tmp_table_owner;
  select test_assert(scalar_int('select count(*) from campaign') = 0,
    'a non-superuser table OWNER sees zero rows without a tenant claim (FORCE RLS works)');
rollback;

\echo ''
\echo '=== RLS adversarial suite: all assertions passed ==='
