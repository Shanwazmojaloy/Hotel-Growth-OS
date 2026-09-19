/**
 * Executor — the only place an agent's proposal can become a real-world action.
 *
 * Order of checks is deliberate. Cheapest and most catastrophic first:
 *   1. kill switches        (global → organisation → property → channel)
 *   2. action known?        (fail closed on anything else)
 *   3. capability matrix    (class + delta ceiling — never the model's opinion)
 *   4. budget envelope      (AI spend and platform spend ceilings)
 *   5. propose to the ledger (auto or gated), then execute, then mark executed
 *
 * Every path writes to action_log and audit_event. There is no "just do it"
 * branch, and dry-run is a flag on this same code path — not a separate one.
 */

import { assertExecutable, specFor, UnknownActionError, type ActionSpec } from "./capabilityMatrix";

export interface Proposal {
  org: string;
  correlationId: string;
  agent: string;
  action: string;
  requestedAutonomy: "auto" | "gated";
  payload: Record<string, unknown>;
  /** Magnitude of change, when the action has a ceiling (e.g. budget +25). */
  deltaPct?: number;
}

export interface KillSwitches {
  global: boolean;
  organisations: string[];
  properties: string[];
  channels: Array<{ org: string; channel: string }>;
}

export interface Budget {
  aiBudgetUsd: number;
  aiUsedUsd: number;
  spendCeilingBdt: number;
  spendUsedBdt: number;
  /** Proposed additional spend, in BDT, if the action increases it. */
  proposedSpendBdt?: number;
}

export interface GovernanceDb {
  propose(org: string, p: Proposal, autonomy: "auto" | "gated"): Promise<string>; // -> action id
  markExecuted(org: string, actionId: string, externalRef: string | null, dryRun: boolean): Promise<void>;
  audit(org: string, event: {
    actorType: "agent" | "system";
    correlationId: string;
    action: string;
    objectType?: string;
    objectId?: string;
    after?: Record<string, unknown>;
  }): Promise<void>;
}

/** Adapters are the only things that talk to Google/Meta/GBP/etc. */
export interface ChannelAdapter {
  execute(action: string, payload: Record<string, unknown>): Promise<{ externalRef: string }>;
  rollback?(action: string, externalRef: string): Promise<void>;
}

export type ExecOutcome =
  | { kind: "executed"; actionId: string; externalRef: string; spec: ActionSpec }
  | { kind: "dry_run"; actionId: string; spec: ActionSpec; wouldHaveDone: Record<string, unknown> }
  | { kind: "queued_for_approval"; actionId: string; spec: ActionSpec; requiredRole: string }
  | { kind: "refused"; reason: string };

export interface ExecutorContext {
  db: GovernanceDb;
  adapter: ChannelAdapter;
  killSwitches: KillSwitches;
  budget: Budget;
  /** Dry-run is a first-class mode: same checks, no external calls. */
  dryRun: boolean;
  onRefusal?: (proposal: Proposal, reason: string) => void;
}

/** What would happen, with no writes at all. Use for onboarding demos and tests. */
export function previewProposal(
  p: Proposal,
  ctx: Pick<ExecutorContext, "killSwitches" | "budget">,
): { wouldDo: "execute" | "queue_for_approval" | "refuse"; reason?: string; requiredRole?: string } {
  if (ctx.killSwitches.global) return { wouldDo: "refuse", reason: "global kill switch engaged" };
  if (ctx.killSwitches.organisations.includes(p.org)) {
    return { wouldDo: "refuse", reason: "organisation kill switch engaged" };
  }
  let spec: ActionSpec;
  try {
    spec = assertExecutable(p.action, p.requestedAutonomy, p.deltaPct);
  } catch (e) {
    return { wouldDo: "refuse", reason: e instanceof Error ? e.message : "refused" };
  }
  if (ctx.budget.aiUsedUsd >= ctx.budget.aiBudgetUsd) {
    return { wouldDo: "refuse", reason: "AI budget exhausted" };
  }
  return spec.autoEligible
    ? { wouldDo: "execute" }
    : { wouldDo: "queue_for_approval", requiredRole: spec.approvalRole ?? "owner" };
}

export async function executeProposal(p: Proposal, ctx: ExecutorContext): Promise<ExecOutcome> {
  const refuse = (reason: string): ExecOutcome => {
    ctx.onRefusal?.(p, reason);
    return { kind: "refused", reason };
  };

  // 1 — kill switches ------------------------------------------------------
  if (ctx.killSwitches.global) return refuse("global kill switch engaged");
  if (ctx.killSwitches.organisations.includes(p.org)) return refuse("organisation kill switch engaged");
  const propertyId = typeof p.payload["property_id"] === "string" ? p.payload["property_id"] : undefined;
  if (propertyId && ctx.killSwitches.properties.includes(propertyId)) {
    return refuse("property kill switch engaged");
  }
  const channel = typeof p.payload["channel"] === "string" ? p.payload["channel"] : undefined;
  if (channel && ctx.killSwitches.channels.some((c) => c.org === p.org && c.channel === channel)) {
    return refuse("channel kill switch engaged");
  }

  // 2 — is this an action we know? ----------------------------------------
  let spec: ActionSpec;
  try {
    spec = specFor(p.action);
  } catch (e) {
    return refuse(e instanceof UnknownActionError ? e.message : "unknown action");
  }

  // 3 — capability matrix (class + single-step ceiling) -------------------
  // Note: dry-run does NOT relax this. A simulation must produce the same
  // decision the live system would, otherwise the ledger's evidence base for
  // raising autonomy is fiction. Dry-run only skips the adapter call.
  try {
    assertExecutable(p.action, p.requestedAutonomy, p.deltaPct);
  } catch (e) {
    return refuse(e instanceof Error ? e.message : "capability matrix refusal");
  }

  // 4 — budget envelopes --------------------------------------------------
  if (ctx.budget.aiUsedUsd >= ctx.budget.aiBudgetUsd) {
    return refuse("organisation AI budget exhausted (hard stop)");
  }
  const proposed = ctx.budget.proposedSpendBdt ?? 0;
  if (proposed > 0 && ctx.budget.spendUsedBdt + proposed > ctx.budget.spendCeilingBdt) {
    return refuse(
      `proposed spend would exceed the written ceiling ` +
        `(${ctx.budget.spendUsedBdt} + ${proposed} > ${ctx.budget.spendCeilingBdt} BDT)`,
    );
  }

  // 5 — ledger, then act --------------------------------------------------
  const autonomy: "auto" | "gated" = spec.autoEligible ? "auto" : "gated";
  const actionId = await ctx.db.propose(p.org, p, autonomy);

  if (autonomy === "gated") {
    await ctx.db.audit(p.org, {
      actorType: "agent",
      correlationId: p.correlationId,
      action: "action.queued_for_approval",
      objectType: "action_log",
      objectId: actionId,
      after: { action: p.action, class: spec.class, requiredRole: spec.approvalRole },
    });
    return {
      kind: "queued_for_approval",
      actionId,
      spec,
      requiredRole: spec.approvalRole ?? "owner",
    };
  }

  if (ctx.dryRun) {
    await ctx.db.markExecuted(p.org, actionId, null, true);
    return { kind: "dry_run", actionId, spec, wouldHaveDone: p.payload };
  }

  try {
    const { externalRef } = await ctx.adapter.execute(p.action, p.payload);
    await ctx.db.markExecuted(p.org, actionId, externalRef, false);
    await ctx.db.audit(p.org, {
      actorType: "agent",
      correlationId: p.correlationId,
      action: "action.executed",
      objectType: "action_log",
      objectId: actionId,
      after: { action: p.action, externalRef },
    });
    return { kind: "executed", actionId, externalRef, spec };
  } catch (e) {
    // A failed adapter call must never look like a success in the ledger.
    await ctx.db.audit(p.org, {
      actorType: "agent",
      correlationId: p.correlationId,
      action: "action.failed",
      objectType: "action_log",
      objectId: actionId,
      after: { action: p.action, error: e instanceof Error ? e.message : String(e) },
    });
    await ctx.db.markExecuted(p.org, actionId, null, true); // recorded as dry/no-op state
    return refuse(`adapter failed: ${e instanceof Error ? e.message : String(e)}`);
  }
}
