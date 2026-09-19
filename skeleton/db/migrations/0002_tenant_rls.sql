-- ============================================================================
-- 0002_tenant_rls.sql — Row Level Security for every tenant-scoped table
--
-- Written explicitly, table by table, rather than generated in a loop. Reason:
-- security configuration should be greppable and reviewable line by line, and
-- the CI census (scripts/ci/policy_census.py) verifies it textually.
--
-- Every table with organization_id gets:
--   enable row level security + force row level security + explicit policies
-- ============================================================================

-- ----------------------------------------------------------------- helpers
-- security definer is required so the policy can read `membership` without
-- recursing into membership's own policy. search_path is always pinned.
create or replace function is_member(org uuid)
returns boolean
language sql
stable
security definer
set search_path = public, pg_temp
as $$
  select exists (
    select 1 from membership m
    where m.organization_id = org
      and m.user_id = auth.uid()
  );
$$;

create or replace function is_org_role(org uuid, roles text[])
returns boolean
language sql
stable
security definer
set search_path = public, pg_temp
as $$
  select exists (
    select 1 from membership m
    where m.organization_id = org
      and m.user_id = auth.uid()
      and m.role = any(roles)
  );
$$;

create or replace function is_platform_admin()
returns boolean
language sql
stable
security definer
set search_path = public, pg_temp
as $$
  select exists (select 1 from platform_admin p where p.user_id = auth.uid());
$$;

-- Worker context: set per tenant-iteration, never trusted from a client body.
create or replace function current_org_setting()
returns uuid
language sql
stable
as $$
  select nullif(current_setting('app.current_organization', true), '')::uuid;
$$;

grant execute on function is_member(uuid)              to authenticated, anon;
grant execute on function is_org_role(uuid, text[])    to authenticated, anon;
grant execute on function is_platform_admin()          to authenticated, anon;
grant execute on function current_org_setting()        to authenticated, anon;

-- ----------------------------------------------------------------- organization
alter table organization enable row level security;
alter table organization force  row level security;
create policy org_select on organization
  for select using ( is_member(id) );
create policy org_update on organization
  for update using ( is_org_role(id, array['owner']) )
  with check     ( is_org_role(id, array['owner']) );
-- No insert/delete policy: organisations are created by service-role provisioning.

-- ----------------------------------------------------------------- membership
alter table membership enable row level security;
alter table membership force  row level security;
create policy membership_select on membership
  for select using ( user_id = auth.uid() or is_member(organization_id) );
create policy membership_insert on membership
  for insert with check ( is_org_role(organization_id, array['owner']) );
create policy membership_update on membership
  for update using ( is_org_role(organization_id, array['owner']) )
  with check     ( is_org_role(organization_id, array['owner']) );
create policy membership_delete on membership
  for delete using ( is_org_role(organization_id, array['owner']) );

-- ----------------------------------------------------------------- platform_admin
alter table platform_admin enable row level security;
alter table platform_admin force  row level security;
create policy platform_admin_select on platform_admin
  for select using ( user_id = auth.uid() or is_platform_admin() );

-- ----------------------------------------------------------------- property
alter table property enable row level security;
alter table property force  row level security;
create policy property_select on property
  for select using ( is_member(organization_id) );
create policy property_insert on property
  for insert with check ( is_org_role(organization_id, array['owner','operator']) );
create policy property_update on property
  for update using ( is_org_role(organization_id, array['owner','operator']) )
  with check     ( is_org_role(organization_id, array['owner','operator']) );
create policy property_delete on property
  for delete using ( is_org_role(organization_id, array['owner']) );

-- ----------------------------------------------------------------- channel_account
-- Owner-only writes: these rows point at credentials and spend authority.
alter table channel_account enable row level security;
alter table channel_account force  row level security;
create policy channel_select on channel_account
  for select using ( is_org_role(organization_id, array['owner','operator']) );
create policy channel_insert on channel_account
  for insert with check ( is_org_role(organization_id, array['owner']) );
create policy channel_update on channel_account
  for update using ( is_org_role(organization_id, array['owner']) )
  with check     ( is_org_role(organization_id, array['owner']) );
create policy channel_delete on channel_account
  for delete using ( is_org_role(organization_id, array['owner']) );

-- ----------------------------------------------------------------- knowledge core
alter table knowledge_doc enable row level security;
alter table knowledge_doc force  row level security;
create policy kdoc_select on knowledge_doc
  for select using ( is_member(organization_id) );
create policy kdoc_insert on knowledge_doc
  for insert with check ( is_org_role(organization_id, array['owner','operator']) );
create policy kdoc_update on knowledge_doc
  for update using ( is_org_role(organization_id, array['owner','operator']) )
  with check     ( is_org_role(organization_id, array['owner','operator']) );
create policy kdoc_delete on knowledge_doc
  for delete using ( is_org_role(organization_id, array['owner']) );

alter table knowledge_chunk enable row level security;
alter table knowledge_chunk force  row level security;
create policy kchunk_select on knowledge_chunk
  for select using ( is_member(organization_id) );
create policy kchunk_insert on knowledge_chunk
  for insert with check ( is_org_role(organization_id, array['owner','operator']) );
create policy kchunk_update on knowledge_chunk
  for update using ( is_org_role(organization_id, array['owner','operator']) )
  with check     ( is_org_role(organization_id, array['owner','operator']) );
create policy kchunk_delete on knowledge_chunk
  for delete using ( is_org_role(organization_id, array['owner','operator']) );

-- ----------------------------------------------------------------- performance
alter table campaign enable row level security;
alter table campaign force  row level security;
create policy campaign_select on campaign
  for select using ( is_member(organization_id) );
create policy campaign_insert on campaign
  for insert with check ( is_org_role(organization_id, array['owner','operator']) );
create policy campaign_update on campaign
  for update using ( is_org_role(organization_id, array['owner','operator']) )
  with check     ( is_org_role(organization_id, array['owner','operator']) );
create policy campaign_delete on campaign
  for delete using ( is_org_role(organization_id, array['owner']) );

alter table metric_daily enable row level security;
alter table metric_daily force  row level security;
create policy metric_select on metric_daily
  for select using ( is_member(organization_id) );
create policy metric_insert on metric_daily
  for insert with check ( is_org_role(organization_id, array['owner','operator']) );
create policy metric_update on metric_daily
  for update using ( is_org_role(organization_id, array['owner','operator']) )
  with check     ( is_org_role(organization_id, array['owner','operator']) );
create policy metric_delete on metric_daily
  for delete using ( is_org_role(organization_id, array['owner']) );

-- booking_fact is financial evidence: operators may append, only owners may amend.
alter table booking_fact enable row level security;
alter table booking_fact force  row level security;
create policy booking_select on booking_fact
  for select using ( is_member(organization_id) );
create policy booking_insert on booking_fact
  for insert with check ( is_org_role(organization_id, array['owner','operator']) );
create policy booking_update on booking_fact
  for update using ( is_org_role(organization_id, array['owner']) )
  with check     ( is_org_role(organization_id, array['owner']) );
create policy booking_delete on booking_fact
  for delete using ( is_org_role(organization_id, array['owner']) );

-- ----------------------------------------------------------------- measurement plan
alter table measurement_plan enable row level security;
alter table measurement_plan force  row level security;
create policy mplan_select on measurement_plan
  for select using ( is_member(organization_id) );
create policy mplan_insert on measurement_plan
  for insert with check ( is_org_role(organization_id, array['owner']) );
create policy mplan_update on measurement_plan
  for update using ( is_org_role(organization_id, array['owner']) )
  with check     ( is_org_role(organization_id, array['owner']) );
-- No delete policy: signed measurement plans are versioned, never removed.

-- ----------------------------------------------------------------- budgets
alter table budget_envelope enable row level security;
alter table budget_envelope force  row level security;
create policy budget_select on budget_envelope
  for select using ( is_member(organization_id) );
create policy budget_insert on budget_envelope
  for insert with check ( is_org_role(organization_id, array['owner']) );
create policy budget_update on budget_envelope
  for update using ( is_org_role(organization_id, array['owner']) )
  with check     ( is_org_role(organization_id, array['owner']) );

-- ----------------------------------------------------------------- kill switch
-- Global rows (organization_id is null) are visible only to platform admins.
alter table kill_switch enable row level security;
alter table kill_switch force  row level security;
create policy kill_select on kill_switch
  for select using (
    (organization_id is null and is_platform_admin())
    or (organization_id is not null and is_member(organization_id))
  );
create policy kill_insert on kill_switch
  for insert with check (
    (organization_id is null and is_platform_admin())
    or (organization_id is not null and is_org_role(organization_id, array['owner']))
  );
create policy kill_update on kill_switch
  for update using (
    (organization_id is null and is_platform_admin())
    or (organization_id is not null and is_org_role(organization_id, array['owner']))
  )
  with check (
    (organization_id is null and is_platform_admin())
    or (organization_id is not null and is_org_role(organization_id, array['owner']))
  );

-- ----------------------------------------------------------------- agent run
alter table agent_run enable row level security;
alter table agent_run force  row level security;
create policy agent_run_select on agent_run
  for select using ( is_member(organization_id) );
-- Writes come from the worker (service role / ingest role), not the dashboard.

-- ----------------------------------------------------------------- action ledger
alter table action_log enable row level security;
alter table action_log force  row level security;
create policy action_select on action_log
  for select using ( is_member(organization_id) );
-- No insert/update policies here on purpose: the executor writes through a
-- security-definer function (see 0003), so the decision transition cannot be
-- forged by a dashboard user.

alter table approval_request enable row level security;
alter table approval_request force  row level security;
create policy approval_select on approval_request
  for select using ( is_member(organization_id) );
create policy approval_insert on approval_request
  for insert with check ( is_org_role(organization_id, array['owner','operator']) );
create policy approval_update on approval_request
  for update using ( is_org_role(organization_id, array['owner']) )
  with check     ( is_org_role(organization_id, array['owner']) );

-- ----------------------------------------------------------------- immutable trails
alter table audit_event enable row level security;
alter table audit_event force  row level security;
create policy audit_select on audit_event
  for select using ( is_member(organization_id) );
-- Append-only: no update or delete policy for any tenant role, and 0003 revokes
-- the privileges entirely so the absence of a policy is not the only defence.

alter table cost_ledger enable row level security;
alter table cost_ledger force  row level security;
create policy cost_select on cost_ledger
  for select using ( is_member(organization_id) );
