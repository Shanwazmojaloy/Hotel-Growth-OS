-- ============================================================================
-- 0001_core_schema.sql — Hotel Growth OS core schema
-- Supabase-compatible. Assumes the `auth` schema and `auth.uid()` exist
-- (Supabase provides them; db/tests/00_shim.sql stubs them for local testing).
--
-- Design rules enforced here:
--   * Every tenant-scoped table carries organization_id. No exceptions.
--   * NO credential columns anywhere. channel_account stores a *reference* to a
--     secret held in Vault; tokens never enter a queryable table or a prompt.
--   * Guest PII is not modelled at all. booking_fact holds aggregates, not guests.
-- ============================================================================

create extension if not exists pgcrypto;

-- ----------------------------------------------------------------- tenant root
create table if not exists organization (
  id             uuid primary key default gen_random_uuid(),
  name           text not null,
  slug           text not null unique,
  country_code   text not null default 'BD',
  status         text not null default 'pilot'
                 check (status in ('pilot','active','paused','churned')),
  created_at     timestamptz not null default now()
);

create table if not exists membership (
  organization_id uuid not null references organization(id) on delete cascade,
  user_id         uuid not null,            -- references auth.users(id) in Supabase
  role            text not null check (role in ('owner','operator','viewer')),
  created_at      timestamptz not null default now(),
  primary key (organization_id, user_id)
);

-- Platform operator access is a separate, audited path — never a normal login.
create table if not exists platform_admin (
  user_id    uuid primary key,
  note       text,
  created_at timestamptz not null default now()
);

create table if not exists property (
  id              uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organization(id) on delete cascade,
  name            text not null,
  city            text,
  rooms           int check (rooms > 0),
  timezone        text not null default 'Asia/Dhaka',
  currency        text not null default 'BDT',
  created_at      timestamptz not null default now()
);

-- ----------------------------------------------------------------- integrations
-- Note what is absent: access_token, refresh_token, client_secret.
-- credential_ref points at Vault-managed secret material, readable only by the
-- worker role that needs it (see 0004 grants).
create table if not exists channel_account (
  id                  uuid primary key default gen_random_uuid(),
  organization_id     uuid not null references organization(id) on delete cascade,
  property_id         uuid not null references property(id) on delete cascade,
  platform            text not null check (platform in
                      ('google_ads','meta_ads','ga4','gsc','gbp','meta_page','whatsapp','booking_engine')),
  external_id         text,                 -- e.g. Google Ads CID, GA4 property id
  credential_ref      uuid,                 -- -> vault.secrets.id (never the token itself)
  scopes              text[] not null default '{}',
  status              text not null default 'pending'
                      check (status in ('pending','connected','expired','revoked','error')),
  expires_at          timestamptz,
  last_verified_at    timestamptz,
  created_at          timestamptz not null default now(),
  unique (organization_id, platform, external_id)
);

-- ----------------------------------------------------------------- knowledge core
create table if not exists knowledge_doc (
  id              uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organization(id) on delete cascade,
  property_id     uuid references property(id) on delete cascade,
  kind            text not null check (kind in
                  ('brand_voice','persona','fact_sheet','offer','pricing_rule','faq','property_note')),
  title           text not null,
  body            text not null,
  version         int  not null default 1,
  status          text not null default 'draft' check (status in ('draft','active','archived')),
  approved_by     uuid,                     -- must be set before status='active' (see policy)
  created_at      timestamptz not null default now(),
  check (status <> 'active' or approved_by is not null)
);

create table if not exists knowledge_chunk (
  id              uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organization(id) on delete cascade,
  property_id     uuid references property(id) on delete cascade,
  doc_id          uuid not null references knowledge_doc(id) on delete cascade,
  chunk_index     int  not null,
  content         text not null,
  created_at      timestamptz not null default now(),
  unique (doc_id, chunk_index)
  -- embedding column added by 0005_optional_pgvector.sql when available
);

-- ----------------------------------------------------------------- performance data
create table if not exists campaign (
  id                   uuid primary key default gen_random_uuid(),
  organization_id      uuid not null references organization(id) on delete cascade,
  property_id          uuid not null references property(id) on delete cascade,
  channel_account_id   uuid references channel_account(id) on delete set null,
  platform             text not null,
  external_campaign_id text,
  name                 text not null,
  status               text not null default 'draft'
                       check (status in ('draft','active','paused','ended')),
  daily_budget_bdt     numeric(12,2) check (daily_budget_bdt >= 0),
  state                jsonb not null default '{}'::jsonb,
  created_at           timestamptz not null default now(),
  unique (organization_id, platform, external_campaign_id)
);

create table if not exists metric_daily (
  id              uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organization(id) on delete cascade,
  property_id     uuid not null references property(id) on delete cascade,
  channel         text not null,            -- google_ads | meta_ads | ga4 | gsc | gbp | booking_engine | ota
  metric_date     date not null,
  impressions     bigint not null default 0,
  clicks          bigint not null default 0,
  cost_bdt        numeric(14,2) not null default 0,
  conversions     numeric(12,2) not null default 0,
  revenue_bdt     numeric(14,2) not null default 0,
  source          text not null,            -- platform_api | manual_upload | pms_export
  ingested_at     timestamptz not null default now(),
  unique (organization_id, property_id, channel, metric_date, source)
);

-- Aggregates only. This is what measurement reads; it never contains a guest record.
create table if not exists booking_fact (
  id              uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organization(id) on delete cascade,
  property_id     uuid not null references property(id) on delete cascade,
  booking_date    date not null,
  stay_date       date,
  channel         text not null,            -- direct | booking_com | expedia | agoda | walk_in | ota_other
  is_direct       boolean not null,
  room_nights     int not null default 0 check (room_nights >= 0),
  revenue_bdt     numeric(14,2) not null default 0,
  commission_bdt  numeric(14,2) not null default 0,
  source          text not null,
  ingested_at     timestamptz not null default now(),
  unique (organization_id, property_id, booking_date, channel, source)
);

-- ----------------------------------------------------------------- measurement
-- The .docx measurement plan, expressed as data so the system can enforce it.
create table if not exists measurement_plan (
  id                    uuid primary key default gen_random_uuid(),
  organization_id       uuid not null references organization(id) on delete cascade,
  property_id           uuid not null references property(id) on delete cascade,
  version               int  not null default 1,
  primary_metric        text not null default 'incremental_direct_room_nights',
  counterfactual_design text not null check (counterfactual_design in ('geo_holdout','time_holdout','pre_post','conservative_attribution')),
  haircut_factor        numeric(4,3) not null default 0.500 check (haircut_factor between 0 and 1),
  target_metric         numeric(12,2),
  stop_threshold        numeric(12,2),
  signed_at             timestamptz,
  created_at            timestamptz not null default now(),
  unique (property_id, version)
);

-- ----------------------------------------------------------------- governance
create table if not exists budget_envelope (
  id                uuid primary key default gen_random_uuid(),
  organization_id   uuid not null references organization(id) on delete cascade,
  period_start      date not null,
  period_end        date not null,
  ai_budget_usd     numeric(10,2) not null default 25.00,
  ai_used_usd       numeric(10,2) not null default 0,
  spend_ceiling_bdt numeric(14,2) not null default 0,   -- written ceiling from the plan
  spend_used_bdt    numeric(14,2) not null default 0,
  hard_stop         boolean not null default true,
  created_at        timestamptz not null default now(),
  unique (organization_id, period_start)
);

create table if not exists kill_switch (
  id              uuid primary key default gen_random_uuid(),
  scope           text not null check (scope in ('global','organization','property','channel')),
  organization_id uuid references organization(id) on delete cascade,  -- null only for scope='global'
  property_id     uuid references property(id) on delete cascade,
  channel         text,
  engaged         boolean not null default false,
  reason          text,
  engaged_by      uuid,
  engaged_at      timestamptz,
  created_at      timestamptz not null default now(),
  check ( (scope = 'global') = (organization_id is null) )
);

create table if not exists agent_run (
  id              uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organization(id) on delete cascade,
  correlation_id  uuid not null,
  agent           text not null,
  status          text not null default 'running' check (status in ('running','succeeded','failed','aborted')),
  model           text,
  input_manifest  jsonb not null default '{}'::jsonb,   -- what context was assembled (hash + sources)
  cost_usd        numeric(10,4) not null default 0,
  started_at      timestamptz not null default now(),
  finished_at     timestamptz
);

-- The agent action ledger. Append-only except for the one-way decision transition
-- enforced in 0003. This is the evidence base for raising autonomy.
create table if not exists action_log (
  id                 uuid primary key default gen_random_uuid(),
  organization_id    uuid not null references organization(id) on delete cascade,
  correlation_id     uuid not null,
  agent_run_id       uuid references agent_run(id) on delete set null,
  agent              text not null,
  proposed_action    text not null,
  action_class       text not null check (action_class in
                     ('reversible_reducing','reversible_neutral','irreversible_brand','financial_increasing')),
  payload            jsonb not null default '{}'::jsonb,
  decision           text not null default 'pending'
                     check (decision in ('pending','auto','approved','rejected','expired')),
  decided_by         uuid,
  decided_at         timestamptz,
  executed_at        timestamptz,
  dry_run            boolean not null default false,
  external_ref       text,
  rollback_available boolean not null default false,
  rollback_ref       text,
  created_at         timestamptz not null default now()
);

create table if not exists approval_request (
  id              uuid primary key default gen_random_uuid(),
  organization_id uuid not null references organization(id) on delete cascade,
  action_id       uuid not null references action_log(id) on delete cascade,
  required_role   text not null default 'owner' check (required_role in ('owner','operator')),
  status          text not null default 'pending' check (status in ('pending','approved','rejected','expired')),
  expires_at      timestamptz not null default (now() + interval '48 hours'),
  decided_by      uuid,
  decided_at      timestamptz,
  note            text,
  created_at      timestamptz not null default now()
);

-- Immutable event trail. Retention >= 5 years (PDPO processing records).
create table if not exists audit_event (
  id              bigserial primary key,
  organization_id uuid not null references organization(id) on delete cascade,
  actor_type      text not null check (actor_type in ('user','agent','system')),
  actor_id        uuid,
  correlation_id  uuid,
  action          text not null,
  object_type     text,
  object_id       uuid,
  before          jsonb,
  after           jsonb,
  ip              inet,
  created_at      timestamptz not null default now()
);

create table if not exists cost_ledger (
  id              bigserial primary key,
  organization_id uuid not null references organization(id) on delete cascade,
  correlation_id  uuid,
  provider        text not null,
  model           text,
  input_tokens    bigint not null default 0,
  cached_tokens   bigint not null default 0,
  output_tokens   bigint not null default 0,
  cost_usd        numeric(10,5) not null default 0,
  created_at      timestamptz not null default now()
);

-- ----------------------------------------------------------------- indexes
create index if not exists idx_membership_user              on membership (user_id);
create index if not exists idx_property_org                 on property (organization_id);
create index if not exists idx_channel_account_org          on channel_account (organization_id);
create index if not exists idx_knowledge_doc_org            on knowledge_doc (organization_id, status);
create index if not exists idx_knowledge_chunk_org          on knowledge_chunk (organization_id, doc_id);
create index if not exists idx_campaign_org                 on campaign (organization_id, property_id);
create index if not exists idx_metric_daily_org_date        on metric_daily (organization_id, metric_date desc);
create index if not exists idx_booking_fact_org_date        on booking_fact (organization_id, booking_date desc);
create index if not exists idx_measurement_plan_org         on measurement_plan (organization_id, property_id);
create index if not exists idx_budget_envelope_org          on budget_envelope (organization_id, period_start);
create index if not exists idx_kill_switch_org              on kill_switch (organization_id) where engaged;
create index if not exists idx_agent_run_org                on agent_run (organization_id, started_at desc);
create index if not exists idx_action_log_org               on action_log (organization_id, created_at desc);
create index if not exists idx_action_log_pending           on action_log (organization_id) where decision = 'pending';
create index if not exists idx_approval_request_pending     on approval_request (organization_id) where status = 'pending';
create index if not exists idx_audit_event_org              on audit_event (organization_id, created_at desc);
create index if not exists idx_cost_ledger_org              on cost_ledger (organization_id, created_at desc);
