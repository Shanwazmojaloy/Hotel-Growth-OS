#!/usr/bin/env bash
# ============================================================================
# run_tests.sh — build a throwaway database, apply migrations, run the
# two-organisation adversarial RLS suite.
#
#   ./run_tests.sh                      # local Postgres (socket at /tmp/pgsock)
#   PGHOST=localhost PGPORT=5432 PGUSER=postgres ./run_tests.sh
#
# On Supabase you would instead use:  supabase db reset && supabase test db
# (the shim is local-only; Supabase provides the auth schema itself).
# ============================================================================
set -euo pipefail

SKIP_SHIM="${SKIP_SHIM:-0}"
TEST_DB="${TEST_DB:-hgos_test}"
PSQL_ARGS=(-h "${PGHOST:-/tmp/pgsock}" -p "${PGPORT:-5433}" -U "${PGUSER:-postgres}")
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATIONS="$HERE/../migrations"

psql_su() { psql "${PSQL_ARGS[@]}" -v ON_ERROR_STOP=1 "$@"; }

echo "── rebuilding $TEST_DB ─────────────────────────────────────────────"
psql "${PSQL_ARGS[@]}" -q -c "drop database if exists $TEST_DB" postgres
psql "${PSQL_ARGS[@]}" -q -c "create database $TEST_DB" postgres

if [ "$SKIP_SHIM" != "1" ]; then
  echo "── local auth shim ────────────────────────────────────────────────"
  psql_su -q -d "$TEST_DB" -f "$HERE/00_shim_local_auth.sql" >/dev/null
fi

echo "── migrations ─────────────────────────────────────────────────────"
for f in $(ls "$MIGRATIONS"/*.sql | sort); do
  printf '   %-34s' "$(basename "$f")"
  if psql_su -q -d "$TEST_DB" -f "$f" >/tmp/mig.log 2>&1; then
    echo "applied"
  else
    echo "FAILED"; tail -20 /tmp/mig.log; exit 1
  fi
done

echo "── fixtures (two orgs, near-identical names) ──────────────────────"
psql_su -q -d "$TEST_DB" -f "$HERE/01_fixtures_two_orgs.sql" >/dev/null

echo "── adversarial suite ──────────────────────────────────────────────"
set +e
psql "${PSQL_ARGS[@]}" -d "$TEST_DB" -f "$HERE/02_rls_adversarial.sql" >/tmp/rls.log 2>&1
rc1=$?
psql "${PSQL_ARGS[@]}" -d "$TEST_DB" -f "$HERE/03_ingest_role.sql" >/tmp/ingest.log 2>&1
rc2=$?
set -e

grep -c 'ok —' /tmp/rls.log /tmp/ingest.log | sed 's/^/   assertions passed: /' || true

if [ $rc1 -eq 0 ] && [ $rc2 -eq 0 ]; then
  echo ""
  echo "✔ RLS adversarial suite PASSED"
  echo "   isolation: two orgs, near-identical names, zero leakage"
  echo "   governance: approvals, immutability and the reversibility asymmetry hold"
  exit 0
else
  echo ""
  echo "✘ RLS adversarial suite FAILED"
  [ $rc1 -ne 0 ] && { echo "--- 02_rls_adversarial.log (tail) ---"; grep -E 'FAILED|ERROR|ASSERTION' -A3 /tmp/rls.log | tail -25; }
  [ $rc2 -ne 0 ] && { echo "--- 03_ingest_role.log (tail) ---";   grep -E 'FAILED|ERROR|ASSERTION' -A3 /tmp/ingest.log | tail -25; }
  exit 1
fi
