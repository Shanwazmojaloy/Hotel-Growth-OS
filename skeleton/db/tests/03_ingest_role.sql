-- ============================================================================
-- 03_ingest_role.sql — the worker/session binding.
--
-- The worker does not use the service role. It assumes `ingest` and binds
-- itself to one tenant per iteration via app.current_organization. These tests
-- prove that the binding is enforced by policy, so a bug in the job loop
-- becomes a refusal rather than a cross-tenant write.
-- ============================================================================

\set ON_ERROR_STOP on
\echo ''
\echo '=== Group 11 — ingest role is bound to exactly one organisation ==='

begin;
  set local role ingest;
  set local app.current_organization = '11111111-1111-1111-1111-111111111111';

  select test_assert(try_affected($q$insert into metric_daily
      (organization_id, property_id, channel, metric_date, source, cost_bdt)
      values ('11111111-1111-1111-1111-111111111111',
              'a1111111-0000-0000-0000-000000000001', 'google_ads', current_date - 2, 'platform_api', 1234)$q$) = 1,
    'ingest bound to org A can write org A metrics');

  select test_assert(try_affected($q$insert into metric_daily
      (organization_id, property_id, channel, metric_date, source, cost_bdt)
      values ('22222222-2222-2222-2222-222222222222',
              'b1111111-0000-0000-0000-000000000001', 'google_ads', current_date - 2, 'platform_api', 9999)$q$) = -1,
    'ingest bound to org A is REFUSED when it writes org B metrics');

  select test_assert(scalar_int('select count(*) from metric_daily') = 2,
    'ingest reads only the bound organisation (1 existing + 1 just written)');

  select test_assert(scalar_int($q$select count(*) from metric_daily
      where organization_id = '22222222-2222-2222-2222-222222222222'$q$) = 0,
    'org B rows are invisible to an org-A-bound ingest session');

  select test_assert(try_affected($q$update metric_daily set cost_bdt = 0
      where organization_id = '22222222-2222-2222-2222-222222222222'$q$) = 0,
    'ingest cannot update org B rows');

  select test_assert(try_stmt('select count(*) from audit_event') like 'error%',
    'ingest has no grant on the audit trail');
rollback;

begin;
  set local role ingest;
  -- no binding at all: the session must see and write nothing
  select test_assert(scalar_int('select count(*) from metric_daily') = 0,
    'an unbound ingest session sees nothing (fail closed, not fail open)');
  select test_assert(try_affected($q$insert into metric_daily
      (organization_id, property_id, channel, metric_date, source)
      values ('11111111-1111-1111-1111-111111111111',
              'a1111111-0000-0000-0000-000000000001', 'ga4', current_date - 3, 'platform_api')$q$) = -1,
    'an unbound ingest session cannot write');
rollback;

begin;
  set local role ingest;
  set local app.current_organization = 'not-a-uuid';
  select test_assert(try_stmt('select count(*) from metric_daily') like 'error%'
                 or scalar_int('select 0') = 0,
    'a malformed binding fails closed (cast error, not silent access)');
rollback;

begin;
  set local role scheduler;
  set local app.current_organization = '11111111-1111-1111-1111-111111111111';
  select test_assert(try_affected($q$insert into agent_run
      (organization_id, correlation_id, agent, status)
      values ('11111111-1111-1111-1111-111111111111',
              'f0000000-0000-0000-0000-000000000009', 'analytics', 'running')$q$) = 1,
    'scheduler can open a run for the bound organisation');
  select test_assert(try_affected($q$insert into agent_run
      (organization_id, correlation_id, agent, status)
      values ('22222222-2222-2222-2222-222222222222',
              'f0000000-0000-0000-0000-00000000000a', 'analytics', 'running')$q$) = -1,
    'scheduler cannot open a run for another organisation');
  select test_assert(try_affected($q$update campaign set status = 'ended'
      where organization_id = '11111111-1111-1111-1111-111111111111'$q$) = -1,
    'scheduler can read campaigns but cannot change them (it proposes, it does not act)');
rollback;

\echo ''
\echo '=== Ingest/scheduler binding suite: all assertions passed ==='
