-- ============================================================================
-- 01_fixtures_two_orgs.sql — the two-organisation fixture.
--
-- Deliberate design choice: the two organisations have near-identical names
-- ("Sea Breeze Resort" in two cities). If any layer ever filters by name, by
-- naive similarity search, or by a stale cache, this fixture is what catches
-- it. Both properties are literally called "Sea Breeze Resort".
--
-- Runs as the database owner (superuser locally), so RLS is bypassed here on
-- purpose: this is seeding, not application traffic.
-- ============================================================================

insert into auth.users (id, email) values
  ('aaaaaaaa-0000-0000-0000-000000000001', 'owner.a@seabreeze.test'),
  ('aaaaaaaa-0000-0000-0000-000000000002', 'viewer.a@seabreeze.test'),
  ('aaaaaaaa-0000-0000-0000-000000000003', 'operator.a@seabreeze.test'),
  ('bbbbbbbb-0000-0000-0000-000000000001', 'owner.b@seabreeze.test'),
  ('cccccccc-0000-0000-0000-000000000001', 'agency@partner.test'),
  ('dddddddd-0000-0000-0000-000000000001', 'ops@hotelgrowthos.test')
on conflict (id) do nothing;

insert into organization (id, name, slug, status) values
  ('11111111-1111-1111-1111-111111111111', 'Sea Breeze Resort Cox''s Bazar', 'seabreeze-cxb', 'pilot'),
  ('22222222-2222-2222-2222-222222222222', 'Sea Breeze Resort Sylhet',      'seabreeze-syl', 'pilot')
on conflict (id) do nothing;

insert into membership (organization_id, user_id, role) values
  ('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-0000-0000-0000-000000000001', 'owner'),
  ('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-0000-0000-0000-000000000002', 'viewer'),
  ('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-0000-0000-0000-000000000003', 'operator'),
  ('22222222-2222-2222-2222-222222222222', 'bbbbbbbb-0000-0000-0000-000000000001', 'owner'),
  -- multi-org membership: the agency/white-label case that must NOT become a god role
  ('11111111-1111-1111-1111-111111111111', 'cccccccc-0000-0000-0000-000000000001', 'operator'),
  ('22222222-2222-2222-2222-222222222222', 'cccccccc-0000-0000-0000-000000000001', 'operator')
on conflict do nothing;

insert into platform_admin (user_id, note) values
  ('dddddddd-0000-0000-0000-000000000001', 'founder/operator — separate audited path')
on conflict (user_id) do nothing;

-- Same property name in both organisations. If a filter ever uses the name,
-- these rows leak and the suite fails. That is the point.
insert into property (id, organization_id, name, city, rooms) values
  ('a1111111-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'Sea Breeze Resort', 'Cox''s Bazar', 48),
  ('a1111111-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', 'Sea Breeze Resort', 'Cox''s Bazar', 12),
  ('b1111111-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'Sea Breeze Resort', 'Sylhet', 30)
on conflict (id) do nothing;

insert into channel_account (id, organization_id, property_id, platform, external_id, status, scopes) values
  ('a2222222-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001', 'google_ads', 'CID-A-100', 'connected', array['campaigns.read','campaigns.write']),
  ('b2222222-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'b1111111-0000-0000-0000-000000000001', 'google_ads', 'CID-B-200', 'connected', array['campaigns.read'])
on conflict (id) do nothing;

insert into campaign (id, organization_id, property_id, platform, external_campaign_id, name, status, daily_budget_bdt) values
  ('a3333333-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001', 'google_ads', 'C-A-1', 'Brand search — Cox''s Bazar', 'active', 2500),
  ('b3333333-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'b1111111-0000-0000-0000-000000000001', 'google_ads', 'C-B-1', 'Brand search — Sylhet',      'active', 1800)
on conflict (id) do nothing;

insert into metric_daily (organization_id, property_id, channel, metric_date, impressions, clicks, cost_bdt, conversions, revenue_bdt, source) values
  ('11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001', 'google_ads', current_date - 1, 1200, 85, 3100, 4, 42000, 'platform_api'),
  ('22222222-2222-2222-2222-222222222222', 'b1111111-0000-0000-0000-000000000001', 'google_ads', current_date - 1,  600, 40, 1500, 2, 18000, 'platform_api')
on conflict do nothing;

insert into booking_fact (organization_id, property_id, booking_date, channel, is_direct, room_nights, revenue_bdt, commission_bdt, source) values
  ('11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001', current_date - 1, 'direct',       true,  3, 24000,     0, 'booking_engine'),
  ('11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001', current_date - 1, 'booking_com',  false, 5, 40000,  6000, 'pms_export'),
  ('22222222-2222-2222-2222-222222222222', 'b1111111-0000-0000-0000-000000000001', current_date - 1, 'direct',       true,  2, 15000,     0, 'booking_engine')
on conflict do nothing;

insert into knowledge_doc (id, organization_id, property_id, kind, title, body, status, approved_by) values
  ('a4444444-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001', 'brand_voice', 'Brand voice', 'Warm, specific, never pushy.', 'active', 'aaaaaaaa-0000-0000-0000-000000000001'),
  ('b4444444-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'b1111111-0000-0000-0000-000000000001', 'brand_voice', 'Brand voice', 'Formal, heritage-led.',        'active', 'bbbbbbbb-0000-0000-0000-000000000001')
on conflict (id) do nothing;

insert into knowledge_chunk (organization_id, property_id, doc_id, chunk_index, content) values
  ('11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001', 'a4444444-0000-0000-0000-000000000001', 0, 'Sea Breeze Cox''s Bazar: monsoon packages, 48 rooms.'),
  ('22222222-2222-2222-2222-222222222222', 'b1111111-0000-0000-0000-000000000001', 'b4444444-0000-0000-0000-000000000001', 0, 'Sea Breeze Sylhet: tea-estate heritage, 30 rooms.')
on conflict do nothing;

insert into measurement_plan (organization_id, property_id, version, counterfactual_design, haircut_factor, target_metric, signed_at) values
  ('11111111-1111-1111-1111-111111111111', 'a1111111-0000-0000-0000-000000000001', 1, 'geo_holdout', 0.500, 40, now() - interval '10 days'),
  ('22222222-2222-2222-2222-222222222222', 'b1111111-0000-0000-0000-000000000001', 1, 'pre_post',     0.550, 20, now() - interval '5 days')
on conflict do nothing;

insert into budget_envelope (organization_id, period_start, period_end, ai_budget_usd, ai_used_usd, spend_ceiling_bdt, spend_used_bdt) values
  ('11111111-1111-1111-1111-111111111111', date_trunc('month', current_date)::date, (date_trunc('month', current_date) + interval '1 month - 1 day')::date, 25, 3.10, 75000, 12400),
  ('22222222-2222-2222-2222-222222222222', date_trunc('month', current_date)::date, (date_trunc('month', current_date) + interval '1 month - 1 day')::date, 15, 1.20, 45000,  6000)
on conflict do nothing;

insert into kill_switch (scope, organization_id, property_id, channel, engaged, reason, engaged_by, engaged_at) values
  ('global',       null,                                   null, null,          false, 'master switch',           null, null),
  ('organization', '11111111-1111-1111-1111-111111111111', null, null,          true,  'monsoon — maintain mode', 'aaaaaaaa-0000-0000-0000-000000000001', now() - interval '2 days'),
  ('channel',      '22222222-2222-2222-2222-222222222222', null, 'google_ads',  false, null, null, null);

-- Seeded by the platform, so it goes through the service path.
insert into audit_event (organization_id, actor_type, action, object_type) values
  ('11111111-1111-1111-1111-111111111111', 'system', 'fixture.seeded', 'organization'),
  ('22222222-2222-2222-2222-222222222222', 'system', 'fixture.seeded', 'organization');

insert into cost_ledger (organization_id, provider, model, input_tokens, output_tokens, cost_usd) values
  ('11111111-1111-1111-1111-111111111111', 'anthropic', 'claude-sonnet-5', 18000, 3200, 0.0680),
  ('22222222-2222-2222-2222-222222222222', 'anthropic', 'claude-sonnet-5',  9000, 1600, 0.0340);
