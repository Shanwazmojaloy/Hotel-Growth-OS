#!/usr/bin/env bash
# ============================================================================
# mutation_test.sh — do the tests actually test anything?
#
# Each mutation breaks one control on purpose. A good suite FAILS on every one
# of them. If a mutation survives, the corresponding test is decoration.
#
#   if removing the safety check does not break a test, you do not have a test.
# ============================================================================
set -uo pipefail

PSQL_ARGS=(-h "${PGHOST:-/tmp/pgsock}" -p "${PGPORT:-5433}" -U "${PGUSER:-postgres}")
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATIONS="$HERE/../migrations"
MUT_DB="hgos_mutation"

psql_su() { psql "${PSQL_ARGS[@]}" -v ON_ERROR_STOP=1 "$@"; }

build_db() {
  psql "${PSQL_ARGS[@]}" -q -c "drop database if exists $MUT_DB" postgres
  psql "${PSQL_ARGS[@]}" -q -c "create database $MUT_DB" postgres
  psql_su -q -d "$MUT_DB" -f "$HERE/00_shim_local_auth.sql" >/dev/null
  for f in $(ls "$MIGRATIONS"/*.sql | sort); do
    psql_su -q -d "$MUT_DB" -f "$f" >/dev/null 2>&1 || { echo "migration failed: $f"; return 1; }
  done
  psql_su -q -d "$MUT_DB" -f "$HERE/01_fixtures_two_orgs.sql" >/dev/null
}

run_suite() {
  psql "${PSQL_ARGS[@]}" -d "$MUT_DB" -f "$HERE/02_rls_adversarial.sql" >/dev/null 2>&1
  local a=$?
  psql "${PSQL_ARGS[@]}" -d "$MUT_DB" -f "$HERE/03_ingest_role.sql" >/dev/null 2>&1
  local b=$?
  [ $a -eq 0 ] && [ $b -eq 0 ] && return 0 || return 1
}

# A mutation that fails to apply would masquerade as a "survivor" and hide a
# real blind spot — so applying it is itself checked.
mutate() {
  if ! psql_su -q -d "$MUT_DB" -c "$1" >/tmp/mut.log 2>&1; then
    echo "   !! MUTATION FAILED TO APPLY: $2"
    tail -3 /tmp/mut.log | sed 's/^/      /'
    return 1
  fi
}

# mutation name | SQL | which assertion should catch it
declare -a NAMES=(
  "no RLS on campaign"
  "no FORCE RLS on campaign"
  "cross-tenant read policy (using true)"
  "campaign insert policy dropped"
  "action_log guard trigger removed"
  "audit immutability trigger removed"
  "reversibility check removed from fn_propose_action"
)
declare -a MUTATIONS=(
  "alter table campaign disable row level security;"
  "alter table campaign no force row level security;"
  "drop policy campaign_select on campaign; create policy campaign_select on campaign for select using (true);"
  "drop policy campaign_insert on campaign;"
  "drop trigger action_log_guard on action_log;"
  "drop trigger audit_event_immutable on audit_event;"
  "drop function fn_propose_action(uuid, uuid, text, text, text, jsonb, text); create function fn_propose_action(p_org uuid, p_correlation_id uuid, p_agent text, p_action text, p_action_class text, p_payload jsonb, p_autonomy text) returns uuid language plpgsql security definer set search_path = public, pg_temp as \$f\$ declare v uuid; begin insert into action_log (organization_id, correlation_id, agent, proposed_action, action_class, payload, decision) values (p_org, p_correlation_id, p_agent, p_action, p_action_class, p_payload, case when p_autonomy = 'auto' then 'auto' else 'pending' end) returning id into v; return v; end \$f\$;"
)

echo "── mutation harness ───────────────────────────────────────────────"
echo "   a mutation SURVIVING means the suite has a blind spot"
echo ""
printf '   %-46s %s\n' "MUTATION" "RESULT"
printf '   %-46s %s\n' "----------------------------------------------" "------"

survivors=0
for i in "${!NAMES[@]}"; do
  build_db >/dev/null 2>&1 || { echo "   build failed"; exit 1; }
  mutate "${MUTATIONS[$i]}" "${NAMES[$i]}" || survivors=$((survivors + 1))
  if run_suite; then
    printf '   %-46s \033[31mSURVIVED (blind spot)\033[0m\n' "${NAMES[$i]}"
    survivors=$((survivors + 1))
  else
    printf '   %-46s \033[32mkilled (suite caught it)\033[0m\n' "${NAMES[$i]}"
  fi
done

# and confirm the unmutated suite passes — otherwise "killed" means nothing
build_db >/dev/null 2>&1
if run_suite; then
  printf '   %-46s \033[32mpasses (baseline)\033[0m\n' "no mutation"
else
  printf '   %-46s \033[31mFAILS (baseline broken)\033[0m\n' "no mutation"
  survivors=$((survivors + 1))
fi

psql "${PSQL_ARGS[@]}" -q -c "drop database if exists $MUT_DB" postgres

echo ""
if [ "$survivors" -eq 0 ]; then
  echo "✔ every control is covered by a failing-on-mutation assertion"
  exit 0
else
  echo "✘ $survivors mutation(s) survived — those controls are untested"
  exit 1
fi
