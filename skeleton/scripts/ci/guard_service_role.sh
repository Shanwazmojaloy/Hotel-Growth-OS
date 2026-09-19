#!/usr/bin/env bash
# ============================================================================
# guard_service_role.sh — the service role may be reached from exactly one file.
#
# RLS does not apply to the service role, so its blast radius is "every tenant".
# Containment is a lint rule, not a convention: if this guard passes, no new
# module can quietly acquire cross-tenant reach.
#
#   ./scripts/ci/guard_service_role.sh
# ============================================================================
set -uo pipefail

ROOT="${1:-apps}"
WRAPPER="apps/worker/src/db/service.ts"
violations=0

echo "── service-role containment guard ─────────────────────────────────"

# 1. the credential and the elevated client may only be named inside the wrapper
mapfile -t key_users < <(grep -rlE 'SUPABASE_SERVICE_ROLE|service_role|SERVICE_ROLE_KEY' \
  "$ROOT" --include='*.ts' 2>/dev/null | grep -v "^${WRAPPER}$" || true)
if [ "${#key_users[@]}" -gt 0 ]; then
  echo "   ✘ service-role credential referenced outside the wrapper:"
  printf '      %s\n' "${key_users[@]}"
  violations=$((violations + 1))
else
  echo "   ✔ credential referenced only in $WRAPPER"
fi

# 2. no direct client construction outside the wrapper
mapfile -t client_users < <(grep -rlE 'createClient\s*\(' "$ROOT" --include='*.ts' 2>/dev/null \
  | grep -v "^${WRAPPER}$" || true)
if [ "${#client_users[@]}" -gt 0 ]; then
  echo "   ✘ direct client construction outside the wrapper:"
  printf '      %s\n' "${client_users[@]}"
  violations=$((violations + 1))
else
  echo "   ✔ no ad-hoc database clients outside the wrapper"
fi

# 3. every service-role query must pass an organisation id
if [ -f "$WRAPPER" ]; then
  if grep -qE 'assertOrg\(' "$WRAPPER"; then
    echo "   ✔ the wrapper enforces a mandatory organization_id"
  else
    echo "   ✘ the wrapper no longer asserts an organization_id — the core control is gone"
    violations=$((violations + 1))
  fi
  if grep -qE 'CrossTenantLeakError' "$WRAPPER"; then
    echo "   ✔ returned rows are verified against the requested organisation"
  else
    echo "   ✘ post-hoc cross-tenant row verification has been removed"
    violations=$((violations + 1))
  fi
fi

# 4. the capability matrix must still gate irreversible classes
MATRIX="apps/worker/src/executor/capabilityMatrix.ts"
if [ -f "$MATRIX" ]; then
  auto_financial=$(grep -cE 'financial_increasing"[^}]*autoEligible:\s*true' "$MATRIX" || true)
  if [ "$auto_financial" -gt 0 ]; then
    echo "   ✘ an action classed financial_increasing is marked autoEligible — asymmetry broken"
    violations=$((violations + 1))
  else
    echo "   ✔ irreversible and financial classes remain human-gated"
  fi
fi

echo ""
if [ "$violations" -eq 0 ]; then
  echo "✔ service-role containment intact"
  exit 0
else
  echo "✘ $violations containment violation(s)"
  exit 1
fi
