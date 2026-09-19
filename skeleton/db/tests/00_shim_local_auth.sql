-- ============================================================================
-- 00_shim_local_auth.sql — LOCAL TESTING ONLY. Do not apply to Supabase.
--
-- Supabase already provides the `auth` schema, auth.uid(), auth.jwt() and the
-- anon / authenticated / service_role roles. This shim recreates the minimum
-- surface so the RLS suite can run against a plain PostgreSQL instance
-- (CI, or `psql` on your laptop) and exercise the real policies.
--
-- Idempotent: safe to run repeatedly.
-- ============================================================================

create extension if not exists pgcrypto;

create schema if not exists auth;

create table if not exists auth.users (
  id         uuid primary key default gen_random_uuid(),
  email      text unique,
  created_at timestamptz not null default now()
);

-- Mirrors Supabase: the current user id comes from the JWT claims GUC.
create or replace function auth.uid()
returns uuid
language plpgsql
stable
as $$
declare v text;
begin
  v := nullif(current_setting('request.jwt.claims', true), '');
  if v is null then
    return null;
  end if;
  return nullif(v::jsonb ->> 'sub', '')::uuid;
exception when others then
  return null;
end;
$$;

create or replace function auth.jwt()
returns jsonb
language plpgsql
stable
as $$
declare v text;
begin
  v := nullif(current_setting('request.jwt.claims', true), '');
  return coalesce(v::jsonb, '{}'::jsonb);
exception when others then
  return '{}'::jsonb;
end;
$$;

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then
    create role anon nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then
    create role authenticated nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    -- Supabase's service_role carries BYPASSRLS. Reproduce that, and remember
    -- it is exactly why the worker wrapper exists (apps/worker/src/db/service.ts).
    create role service_role nologin bypassrls;
  end if;
end $$;

grant usage on schema auth to anon, authenticated, service_role;
grant select on auth.users to anon, authenticated, service_role;
grant execute on function auth.uid() to anon, authenticated, service_role;
grant execute on function auth.jwt() to anon, authenticated, service_role;

-- ----------------------------------------------------------------- test helpers
create or replace function test_assert(cond boolean, msg text)
returns void
language plpgsql
as $$
begin
  if cond is null or cond = false then
    raise exception 'ASSERTION FAILED: %', msg;
  end if;
  raise notice '  ok — %', msg;
end;
$$;

-- Runs a statement as the *current* role and reports the outcome instead of
-- aborting, so a test can assert that something is refused.
create or replace function try_stmt(stmt text)
returns text
language plpgsql
as $$
begin
  execute stmt;
  return 'ok';
exception when others then
  return 'error:' || sqlstate;
end;
$$;

-- Executes a single-value query as the current role.
create or replace function scalar_int(stmt text)
returns bigint
language plpgsql
as $$
declare v bigint;
begin
  execute stmt into v;
  return coalesce(v, 0);
end;
$$;

-- Number of rows a statement affected, or -1 if it was refused. Lets a test
-- assert the difference between "silently did nothing" and "errored".
create or replace function try_affected(stmt text)
returns int
language plpgsql
as $$
declare n int;
begin
  execute stmt;
  get diagnostics n = row_count;
  return n;
exception when others then
  return -1;
end;
$$;

grant execute on function try_affected(text) to authenticated, anon, service_role;

grant execute on function test_assert(boolean, text) to authenticated, anon, service_role;
grant execute on function try_stmt(text)            to authenticated, anon, service_role;
grant execute on function scalar_int(text)          to authenticated, anon, service_role;
