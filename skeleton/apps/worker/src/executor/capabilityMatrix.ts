/**
 * The reversibility asymmetry, as data.
 *
 * The model proposes; this table decides. Confidence scores and eval results
 * can widen what runs automatically over time, but they can never promote an
 * action out of its class. Mirrored in db/migrations/0003 (fn_propose_action
 * refuses to auto-execute anything outside the reversible classes), so a bug in
 * this file cannot produce an irreversible action either.
 *
 *   reversible_reducing     pause, lower bid, add negatives, cap budget
 *   reversible_neutral      draft, report, build audience, propose
 *   irreversible_brand      publish, send, reply — public and permanent
 *   financial_increasing    raise budget, create campaign, change billing
 */

export type ActionClass =
  | "reversible_reducing"
  | "reversible_neutral"
  | "irreversible_brand"
  | "financial_increasing";

export interface ActionSpec {
  readonly class: ActionClass;
  /** Can this run without a human when evals are green? */
  readonly autoEligible: boolean;
  /** Role required to approve when not auto-eligible (mirrors approval_request.required_role). */
  readonly approvalRole?: "owner" | "operator";
  /** Largest single-step change permitted, regardless of approvals. */
  readonly maxDeltaPct?: number;
  /** Is there a real, tested rollback for this action? */
  readonly rollback: "automatic" | "manual" | "none";
}

export const ACTIONS: Readonly<Record<string, ActionSpec>> = {
  // ---- reversible_reducing: may run unattended, errors are cheap and correctable
  pause_campaign:        { class: "reversible_reducing", autoEligible: true, rollback: "automatic" },
  resume_campaign:       { class: "reversible_reducing", autoEligible: true, rollback: "automatic" },
  lower_bid:             { class: "reversible_reducing", autoEligible: true, maxDeltaPct: 20, rollback: "automatic" },
  add_negative_keywords: { class: "reversible_reducing", autoEligible: true, rollback: "automatic" },
  cap_budget:            { class: "reversible_reducing", autoEligible: true, rollback: "automatic" },
  hide_listing_post:     { class: "reversible_reducing", autoEligible: true, rollback: "manual" },

  // ---- reversible_neutral: produces artefacts, touches nothing public
  draft_content:         { class: "reversible_neutral", autoEligible: true, rollback: "automatic" },
  build_report:          { class: "reversible_neutral", autoEligible: true, rollback: "none" },
  recompute_baseline:    { class: "reversible_neutral", autoEligible: true, rollback: "automatic" },
  propose_reallocation:  { class: "reversible_neutral", autoEligible: true, rollback: "none" },

  // ---- irreversible_brand: human gate, always, until evals say otherwise (documented)
  publish_gbp_post:      { class: "irreversible_brand", autoEligible: false, approvalRole: "operator", rollback: "manual" },
  reply_to_review:       { class: "irreversible_brand", autoEligible: false, approvalRole: "operator", rollback: "none" },
  send_outbound_message: { class: "irreversible_brand", autoEligible: false, approvalRole: "operator", rollback: "none" },
  publish_site_update:   { class: "irreversible_brand", autoEligible: false, approvalRole: "operator", rollback: "manual" },

  // ---- financial_increasing: owner gate, and never with the provider's money
  raise_budget:          { class: "financial_increasing", autoEligible: false, approvalRole: "owner", maxDeltaPct: 15, rollback: "automatic" },
  create_campaign:       { class: "financial_increasing", autoEligible: false, approvalRole: "owner", rollback: "automatic" },
  change_billing:        { class: "financial_increasing", autoEligible: false, approvalRole: "owner", rollback: "none" },
  assign_user_role:      { class: "financial_increasing", autoEligible: false, approvalRole: "owner", rollback: "automatic" },
};

export class UnknownActionError extends Error {
  constructor(action: string) {
    super(`unknown action '${action}' — refusing (fail closed)`);
    this.name = "UnknownActionError";
  }
}

export class AutonomyViolationError extends Error {
  constructor(action: string, spec: ActionSpec) {
    super(
      `action '${action}' is class ${spec.class} and may not be auto-executed` +
        (spec.approvalRole ? ` (requires ${spec.approvalRole} approval)` : ""),
    );
    this.name = "AutonomyViolationError";
  }
}

export class DeltaCeilingError extends Error {
  constructor(action: string, requested: number, max: number) {
    super(`action '${action}' requests a ${requested}% change; the ceiling is ${max}% in a single step`);
    this.name = "DeltaCeilingError";
  }
}

/** Fail closed: an action missing from the table is refused, not defaulted. */
export function specFor(action: string): ActionSpec {
  const spec = ACTIONS[action];
  if (!spec) throw new UnknownActionError(action);
  return spec;
}

export function canAutoExecute(action: string): boolean {
  try {
    return specFor(action).autoEligible;
  } catch {
    return false;
  }
}

/**
 * Called by the executor immediately before doing anything. `deltaPct` is the
 * magnitude of the change being requested, when the action has a ceiling.
 */
export function assertExecutable(
  action: string,
  requestedAutonomy: "auto" | "gated",
  deltaPct?: number,
): ActionSpec {
  const spec = specFor(action);

  if (requestedAutonomy === "auto" && !spec.autoEligible) {
    throw new AutonomyViolationError(action, spec);
  }
  if (deltaPct !== undefined && spec.maxDeltaPct !== undefined && Math.abs(deltaPct) > spec.maxDeltaPct) {
    throw new DeltaCeilingError(action, deltaPct, spec.maxDeltaPct);
  }
  return spec;
}

/**
 * What the dashboard can tell a hotel owner, generated from the same source of
 * truth the executor uses — so the promise and the behaviour cannot drift.
 */
export function describeAutonomy(): { action: string; class: ActionClass; runs: string }[] {
  return Object.entries(ACTIONS).map(([action, spec]) => ({
    action,
    class: spec.class,
    runs: spec.autoEligible
      ? "automatically, logged"
      : `after ${spec.approvalRole ?? "owner"} approval`,
  }));
}
