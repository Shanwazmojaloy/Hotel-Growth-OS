#!/usr/bin/env bash
# ============================================================================
# verify_all.sh — run every gate in one command.
#
#   ./scripts/verify_all.sh
#
# Requires either a local Postgres (socket default /tmp/pgsock, port 5433) or
# connection env vars: PGHOST / PGPORT / PGUSER.
# ============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"

pass=0; fail=0
declare -a RESULTS=()

pass=0; fail=0; skip=0
declare -a RESULTS=()

# A gate that fails because a binary is missing reads exactly like a security
# regression. Reported the same way, it trains you to ignore red — so prerequisites
# are detected first and reported as SKIPPED, and the summary says plainly whether
# the run verified anything or merely tried to.
need() {  # need <description> <test-command...>
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then return 0; fi
  printf '  ⚠ skipped: %s\n' "$desc"
  return 1
}

run_gate() {
  local name="$1"; shift
  printf '\n\033[1m── %s\033[0m\n' "$name"
  if "$@"; then
    RESULTS+=("✔ $name"); pass=$((pass + 1))
  else
    RESULTS+=("✘ $name"); fail=$((fail + 1))
  fi
}

skip_gate() {  # skip_gate <name> <reason>
  printf '\n\033[1m── %s\033[0m\n  ⚠ SKIPPED — %s\n' "$1" "$2"
  RESULTS+=("○ $1 (skipped: $2)"); skip=$((skip + 1))
}

have_postgres() {
  command -v psql >/dev/null 2>&1 || return 1
  PGCONNECT_TIMEOUT=3 psql -h "${PGHOST:-/tmp/pgsock}" -p "${PGPORT:-5433}" \
    -U "${PGUSER:-postgres}" -d postgres -c 'select 1' >/dev/null 2>&1
}

run_gate "1. policy census (static: RLS enabled + forced + policied, no permissive policies)" \
  python3 scripts/ci/policy_census.py db/migrations/*.sql

run_gate "2. service-role containment (one file may hold the credential)" \
  bash scripts/ci/guard_service_role.sh

G3="3. type-check worker (strict, noUncheckedIndexedAccess)"
if [ -x ./node_modules/.bin/tsc ]; then
  run_gate "$G3" bash -c './node_modules/.bin/tsc -p tsconfig.json'
else
  skip_gate "$G3" "node_modules absent — run 'npm install' in skeleton/ first"
fi

G4="4. RLS adversarial suite (two orgs, near-identical names)"
G5="5. mutation harness (does the suite actually test anything?)"
if have_postgres; then
  run_gate "$G4" bash db/tests/run_tests.sh
  run_gate "$G5" bash db/tests/mutation_test.sh
else
  skip_gate "$G4" "no Postgres at ${PGHOST:-/tmp/pgsock}:${PGPORT:-5433} — start it or set PGHOST/PGPORT"
  skip_gate "$G5" "same prerequisite as gate 4"
fi

printf '\n\033[1m═══ summary ═══\033[0m\n'
for r in "${RESULTS[@]}"; do printf '  %s\n' "$r"; done
printf '\n  %d passed, %d failed, %d skipped\n' "$pass" "$fail" "$skip"
if [ "$skip" -gt 0 ]; then
  printf '  \033[33m⚠ NOT FULLY VERIFIED — %d gate(s) never ran. A skip is not a pass.\033[0m\n' "$skip"
fi
printf '\n'

[ "$fail" -eq 0 ] || exit 1
# STRICT=1 makes a missing prerequisite a failure, for CI where a skip must not pass.
[ "${STRICT:-0}" = "1" ] && [ "$skip" -gt 0 ] && exit 1
exit 0
