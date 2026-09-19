-- ============================================================================
-- 0004_app_roles_and_grants.sql — least privilege for workers, and the
-- service-role containment strategy.
--
-- The spec's rule: background jobs get their own role with explicit policies
-- instead of the service role. A worker that can only INSERT metrics for the
-- organisation named in its job payload is a far smaller blast radius.
--
-- The worker binds itself per tenant iteration:
--     set local role ingest;
--     set local app.current_organization = '<org uuid>';
-- ============================================================================

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'ingest') then
    create role ingest nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'scheduler') then
    create role scheduler nologin;
  end if;
end $$;

grant usage on schema public to ingest, scheduler;

-- ----------------------------------------------------------------- ingest role
-- Reads: the reference data it needs to normalise incoming platform metrics.
grant select on property, campaign, channel_account, knowledge_doc to ingest;

-- Writes: exactly two tables, exactly one orientation of change.
grant select          on metric_daily to ingest;
grant insert, update  on metric_daily to ingest;
grant select          on booking_fact to ingest;
grant insert, update  on booking_fact to ingest;
grant insert          on audit_event to ingest;

-- Tenant binding for the ingest role. Note these are the ONLY policies that
-- reference app.current_organization: nothing else may trust a session variable.
create policy ingest_metric_select on metric_daily
  for select to ingest using ( organization_id = current_org_setting() );
create policy ingest_metric_insert on metric_daily
  for insert to ingest with check ( organization_id = current_org_setting() );
create policy ingest_metric_update on metric_daily
  for update to ingest using ( organization_id = current_org_setting() )
  with check            ( organization_id = current_org_setting() );

create policy ingest_booking_select on booking_fact
  for select to ingest using ( organization_id = current_org_setting() );
create policy ingest_booking_insert on booking_fact
  for insert to ingest with check ( organization_id = current_org_setting() );
create policy ingest_booking_update on booking_fact
  for update to ingest using ( organization_id = current_org_setting() )
  with check            ( organization_id = current_org_setting() );

create policy ingest_ref_select on property
  for select to ingest using ( organization_id = current_org_setting() );
create policy ingest_campaign_select on campaign
  for select to ingest using ( organization_id = current_org_setting() );
create policy ingest_channel_select on channel_account
  for select to ingest using ( organization_id = current_org_setting() );

-- ----------------------------------------------------------------- scheduler role
-- Proposes actions; never writes results. Read-only otherwise.
grant select on campaign, metric_daily, booking_fact, measurement_plan,
                budget_envelope, knowledge_doc, action_log to scheduler;
grant insert on agent_run to scheduler;
grant insert on cost_ledger to scheduler;
grant execute on function fn_propose_action(uuid, uuid, text, text, text, jsonb, text) to scheduler;
grant execute on function fn_append_audit(uuid, text, uuid, uuid, text, text, uuid, jsonb, jsonb, inet) to scheduler;

create policy sched_campaign_select on campaign
  for select to scheduler using ( organization_id = current_org_setting() );
create policy sched_metric_select on metric_daily
  for select to scheduler using ( organization_id = current_org_setting() );
create policy sched_booking_select on booking_fact
  for select to scheduler using ( organization_id = current_org_setting() );
create policy sched_plan_select on measurement_plan
  for select to scheduler using ( organization_id = current_org_setting() );
create policy sched_budget_select on budget_envelope
  for select to scheduler using ( organization_id = current_org_setting() );
create policy sched_kdoc_select on knowledge_doc
  for select to scheduler using ( organization_id = current_org_setting() );
create policy sched_action_select on action_log
  for select to scheduler using ( organization_id = current_org_setting() );
create policy sched_agent_run_insert on agent_run
  for insert to scheduler with check ( organization_id = current_org_setting() );
create policy sched_cost_insert on cost_ledger
  for insert to scheduler with check ( organization_id = current_org_setting() );

-- ----------------------------------------------------------------- dashboard role
grant usage on schema public to authenticated, anon;
grant select, insert, update, delete on
  property, channel_account, knowledge_doc, knowledge_chunk, campaign, metric_daily,
  booking_fact, measurement_plan, budget_envelope, kill_switch, approval_request,
  membership, organization
  to authenticated;
grant select on agent_run, action_log, audit_event, cost_ledger to authenticated;
grant usage, select on all sequences in schema public to authenticated;

-- service_role carries BYPASSRLS in Supabase and all privileges on public.
-- Mirror that here so local behaviour matches production — and so the wrapper
-- (apps/worker/src/db/service.ts) is the only thing standing between a worker
-- and every tenant's rows, which is precisely why it exists.
grant usage on schema public to service_role;
grant all on all tables    in schema public to service_role;
grant all on all sequences in schema public to service_role;
grant all on all functions in schema public to service_role;

-- Anonymous users get nothing. If this ever needs to change, change it explicitly.
revoke all on all tables    in schema public from anon;
revoke all on all sequences in schema public from anon;
