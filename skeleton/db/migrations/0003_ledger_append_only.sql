-- ============================================================================
-- 0003_ledger_append_only.sql — immutability + the only paths that may write
-- to the ledger. Defence in depth: the absence of a policy is not the only
-- thing standing between a dashboard user and the audit trail.
-- ============================================================================

-- ----------------------------------------------------------------- immutability
create or replace function forbid_mutation()
returns trigger
language plpgsql
as $$
begin
  raise exception 'append-only table %: % is not permitted', tg_table_name, tg_op
    using errcode = 'restrict_violation';
end;
$$;

create trigger audit_event_immutable
  before update or delete on audit_event
  for each row execute function forbid_mutation();

create trigger cost_ledger_immutable
  before update or delete on cost_ledger
  for each row execute function forbid_mutation();

-- action_log is append-only except for a single, one-way decision transition.
create or replace function action_log_guard()
returns trigger
language plpgsql
as $$
begin
  if tg_op = 'DELETE' then
    raise exception 'action_log is append-only: delete is not permitted'
      using errcode = 'restrict_violation';
  end if;

  -- The decision may change exactly once, out of 'pending'. Execution
  -- bookkeeping (executed_at, external_ref, dry_run) is allowed while the
  -- decision itself stays put — the first version of this trigger forbade ALL
  -- updates once a decision existed, which blocked the executor's own
  -- bookkeeping on auto-decided actions. The test suite caught it.
  if new.decision is distinct from old.decision then
    if old.decision <> 'pending' then
      raise exception 'action_log decision is final (already %)', old.decision
        using errcode = 'restrict_violation';
    end if;
    if new.decision not in ('auto','approved','rejected','expired') then
      raise exception 'illegal decision transition: % -> %', old.decision, new.decision
        using errcode = 'restrict_violation';
    end if;
  end if;
  if new.organization_id <> old.organization_id
     or new.proposed_action <> old.proposed_action
     or new.action_class <> old.action_class then
    raise exception 'action_log identity columns are immutable'
      using errcode = 'restrict_violation';
  end if;
  return new;
end;
$$;

create trigger action_log_guard
  before update or delete on action_log
  for each row execute function action_log_guard();

-- ----------------------------------------------------------------- audit append
-- The only supported way to write an audit row. A dashboard user may only write
-- an audit entry for their own membership and only as themselves; the worker
-- (no auth.uid()) may write system/agent entries for the tenant it is bound to.
create or replace function fn_append_audit(
  p_org            uuid,
  p_actor_type     text,
  p_actor_id       uuid default null,
  p_correlation_id uuid default null,
  p_action         text default 'unspecified',
  p_object_type    text default null,
  p_object_id      uuid default null,
  p_before         jsonb default null,
  p_after          jsonb default null,
  p_ip             inet default null
) returns bigint
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare v_id bigint;
begin
  if auth.uid() is not null then
    if not is_member(p_org) then
      raise exception 'not a member of organisation %', p_org using errcode = 'insufficient_privilege';
    end if;
    if p_actor_type = 'user' and p_actor_id is distinct from auth.uid() then
      raise exception 'cannot write audit rows on behalf of another user' using errcode = 'insufficient_privilege';
    end if;
  end if;

  insert into audit_event (organization_id, actor_type, actor_id, correlation_id,
                           action, object_type, object_id, before, after, ip)
  values (p_org, p_actor_type, p_actor_id, p_correlation_id,
          p_action, p_object_type, p_object_id, p_before, p_after, p_ip)
  returning id into v_id;
  return v_id;
end;
$$;

-- ----------------------------------------------------------------- propose action
-- Enforces the reversibility asymmetry at the database level: nothing may be
-- auto-executed unless it is reversible and non-financial, regardless of what
-- the reasoning layer or the worker believes.
create or replace function fn_propose_action(
  p_org           uuid,
  p_correlation_id uuid,
  p_agent         text,
  p_action        text,
  p_action_class  text,
  p_payload       jsonb default '{}'::jsonb,
  p_autonomy      text default 'gated'      -- 'auto' | 'gated'
) returns uuid
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare v_id uuid; v_decision text; v_run uuid;
begin
  if p_action_class not in ('reversible_reducing','reversible_neutral','irreversible_brand','financial_increasing') then
    raise exception 'unknown action class %', p_action_class using errcode = 'check_violation';
  end if;

  if p_autonomy = 'auto' and p_action_class not in ('reversible_reducing','reversible_neutral') then
    raise exception 'class % may never be auto-executed (reversibility asymmetry)', p_action_class
      using errcode = 'insufficient_privilege';
  end if;

  v_decision := case when p_autonomy = 'auto' then 'auto' else 'pending' end;

  select id into v_run from agent_run
   where organization_id = p_org and correlation_id = p_correlation_id
   order by started_at desc limit 1;

  insert into action_log (organization_id, correlation_id, agent_run_id, agent,
                          proposed_action, action_class, payload, decision, decided_at)
  values (p_org, p_correlation_id, v_run, p_agent, p_action, p_action_class, p_payload, v_decision,
          case when v_decision = 'auto' then now() else null end)
  returning id into v_id;

  if v_decision = 'pending' then
    insert into approval_request (organization_id, action_id, required_role)
    values (p_org, v_id, case when p_action_class = 'financial_increasing' then 'owner' else 'operator' end);
  end if;

  return v_id;
end;
$$;

-- ----------------------------------------------------------------- decide action
create or replace function fn_decide_action(
  p_action_id uuid,
  p_decision  text,          -- 'approved' | 'rejected'
  p_note      text default null
) returns void
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  v_org uuid; v_class text; v_status text; v_required text; v_expires timestamptz;
begin
  select a.organization_id, a.action_class, a.decision,
         r.required_role, r.expires_at
    into v_org, v_class, v_status, v_required, v_expires
    from action_log a
    join approval_request r on r.action_id = a.id
   where a.id = p_action_id
   for update of a;

  if v_org is null then
    raise exception 'action % not found', p_action_id using errcode = 'no_data_found';
  end if;

  if auth.uid() is not null and not is_org_role(v_org, array[v_required]) then
    raise exception 'role % required to decide this action', v_required using errcode = 'insufficient_privilege';
  end if;

  if v_status <> 'pending' then
    raise exception 'action already decided (%)', v_status using errcode = 'restrict_violation';
  end if;
  if v_expires < now() then
    update action_log set decision = 'expired', decided_at = now() where id = p_action_id;
    update approval_request set status = 'expired', decided_at = now() where action_id = p_action_id;
    raise exception 'approval window expired' using errcode = 'restrict_violation';
  end if;
  if p_decision not in ('approved','rejected') then
    raise exception 'decision must be approved or rejected' using errcode = 'check_violation';
  end if;

  update action_log
     set decision = p_decision, decided_by = auth.uid(), decided_at = now()
   where id = p_action_id;

  update approval_request
     set status = p_decision, decided_by = auth.uid(), decided_at = now(), note = p_note
   where action_id = p_action_id;

  perform fn_append_audit(v_org, case when auth.uid() is null then 'system' else 'user' end,
                          auth.uid(), null, 'action.' || p_decision, 'action_log', p_action_id,
                          jsonb_build_object('class', v_class), jsonb_build_object('decision', p_decision), null);
end;
$$;

-- ----------------------------------------------------------------- execute guard
-- Nothing executes without a valid decision, and dry runs never touch the world.
create or replace function fn_mark_executed(
  p_action_id  uuid,
  p_external_ref text default null,
  p_dry_run    boolean default false
) returns void
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare v_status text; v_org uuid;
begin
  select decision, organization_id into v_status, v_org from action_log where id = p_action_id for update;

  if v_org is null then
    raise exception 'action % not found', p_action_id using errcode = 'no_data_found';
  end if;
  if auth.uid() is not null and not is_member(v_org) then
    raise exception 'not a member of organisation %', v_org using errcode = 'insufficient_privilege';
  end if;
  if v_status not in ('auto','approved') then
    raise exception 'refusing to execute action in state %', v_status using errcode = 'insufficient_privilege';
  end if;
  if not p_dry_run and p_external_ref is null then
    raise exception 'live execution requires an external reference' using errcode = 'check_violation';
  end if;

  update action_log
     set executed_at = now(), external_ref = p_external_ref, dry_run = p_dry_run
   where id = p_action_id;

  perform fn_append_audit(v_org, case when auth.uid() is null then 'system' else 'user' end, auth.uid(),
                          null, case when p_dry_run then 'action.dry_run' else 'action.executed' end,
                          'action_log', p_action_id, null,
                          jsonb_build_object('external_ref', p_external_ref), null);
end;
$$;

-- ----------------------------------------------------------------- grants
revoke all on function forbid_mutation() from public;
revoke all on function action_log_guard() from public;
grant execute on function fn_append_audit(uuid, text, uuid, uuid, text, text, uuid, jsonb, jsonb, inet) to authenticated;
grant execute on function fn_propose_action(uuid, uuid, text, text, text, jsonb, text) to authenticated;
grant execute on function fn_decide_action(uuid, text, text) to authenticated;
grant execute on function fn_mark_executed(uuid, text, boolean) to authenticated;
grant execute on function fn_append_audit(uuid, text, uuid, uuid, text, text, uuid, jsonb, jsonb, inet) to service_role;
grant execute on function fn_propose_action(uuid, uuid, text, text, text, jsonb, text) to service_role;
grant execute on function fn_decide_action(uuid, text, text) to service_role;
grant execute on function fn_mark_executed(uuid, text, boolean) to service_role;

-- Hard revocation: even if a policy is later added by mistake, these privileges
-- do not exist for tenant roles.
revoke update, delete on audit_event  from authenticated;
revoke update, delete on cost_ledger  from authenticated;
revoke delete         on action_log   from authenticated;
revoke update, delete on audit_event  from anon;
revoke update, delete on cost_ledger  from anon;
revoke delete         on action_log   from anon;
