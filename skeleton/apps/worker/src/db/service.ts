/**
 * The ONLY module permitted to hold service-role credentials.
 *
 * Why this file exists: RLS does not apply to the service role. Every
 * cross-tenant leak in a system like this starts with a background job that
 * forgot a tenant predicate. So the credential lives here, the raw client is
 * not exported, and every operation demands an organisation id.
 *
 * Enforced three ways:
 *   1. no other file may reference the service key (scripts/ci/guard_service_role.sh)
 *   2. every call requires `org` — there is no default and no overload without it
 *   3. every returned row is checked against the requested org at runtime, so a
 *      missing predicate becomes a loud failure instead of a silent leak
 *
 * Prefer the `ingest`/`scheduler` roles (see db/migrations/0004) for background
 * work: they are tenant-bound by policy and cannot see anything else. Reach for
 * this module only for provisioning and migrations.
 */

export interface Row {
  organization_id?: string;
  [key: string]: unknown;
}

export interface QueryResult {
  rows: Row[];
  rowCount: number;
  error?: string;
}

/** Thin port over whatever driver you use (pg pool, or a supabase-js adapter). */
export interface RawDb {
  query(sql: string, params: unknown[]): Promise<QueryResult>;
  rpc(fn: string, args: Record<string, unknown>): Promise<{ data: unknown; error?: string }>;
  /** Binds the session for role-based access: `set local app.current_organization = $1`. */
  setTenantContext?(org: string | null): Promise<void>;
}

export class TenantBoundaryError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TenantBoundaryError";
  }
}

export class CrossTenantLeakError extends Error {
  constructor(readonly requestedOrg: string, readonly rows: Row[]) {
    super(
      `cross-tenant leak: a query scoped to ${requestedOrg} returned ` +
        `${rows.length} row(s) belonging to other organisations`,
    );
    this.name = "CrossTenantLeakError";
  }
}

export class RowAnomalyError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RowAnomalyError";
  }
}

/** Provisioning tables this wrapper is allowed to touch. Fail closed. */
const ALLOWED_TABLES = new Set<string>([
  "organization",
  "membership",
  "property",
  "channel_account",
  "knowledge_doc",
  "knowledge_chunk",
  "campaign",
  "metric_daily",
  "booking_fact",
  "measurement_plan",
  "budget_envelope",
  "kill_switch",
  "agent_run",
  "action_log",
  "approval_request",
  "audit_event",
  "cost_ledger",
]);

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export interface ServiceOptions {
  /** Called when a leak is detected — wire this to your alerting, not a log line. */
  onCrossTenantLeak?: (err: CrossTenantLeakError) => void;
  /** Rows above this per call are treated as an anomaly (a normal job sees tens). */
  maxRowsPerCall?: number;
}

export function createOrgScopedService(raw: RawDb, opts: ServiceOptions = {}) {
  const maxRows = opts.maxRowsPerCall ?? 5_000;

  function assertOrg(org: string | undefined | null): string {
    if (!org || !UUID_RE.test(org)) {
      // The single most important line in this file: no org, no query.
      throw new TenantBoundaryError(
        "every service-role operation requires a valid organization_id (no defaults, no wildcards)",
      );
    }
    return org;
  }

  function assertTable(table: string): string {
    if (!ALLOWED_TABLES.has(table)) {
      throw new TenantBoundaryError(`table '${table}' is not reachable through the service wrapper`);
    }
    return table;
  }

  /** Post-hoc verification: refuses to hand back rows from another tenant. */
  function verify(org: string, rows: Row[]): Row[] {
    const foreign = rows.filter((r) => r.organization_id !== undefined && r.organization_id !== org);
    if (foreign.length > 0) {
      const err = new CrossTenantLeakError(org, foreign);
      opts.onCrossTenantLeak?.(err);
      throw err;
    }
    if (rows.length > maxRows) {
      throw new RowAnomalyError(
        `query scoped to ${org} returned ${rows.length} rows (limit ${maxRows}) — investigate before trusting it`,
      );
    }
    return rows;
  }

  function whereClause(where: Record<string, unknown> | undefined, startIndex: number) {
    const keys = Object.keys(where ?? {});
    const clauses = keys.map((k, i) => `${k} = $${startIndex + i}`);
    const params = keys.map((k) => (where as Record<string, unknown>)[k]);
    return { sql: clauses.length ? ` and ${clauses.join(" and ")}` : "", params };
  }

  return {
    /** SELECT, always with the tenant predicate injected first. */
    async select<T extends Row = Row>(
      org: string,
      table: string,
      where?: Record<string, unknown>,
    ): Promise<T[]> {
      const o = assertOrg(org);
      assertTable(table);
      const w = whereClause(where, 2);
      const res = await raw.query(
        `select * from ${table} where organization_id = $1${w.sql}`,
        [o, ...w.params],
      );
      if (res.error) throw new Error(`select ${table} failed: ${res.error}`);
      return verify(o, res.rows) as T[];
    },

    /** INSERT with the org forced onto every row, overriding anything passed in. */
    async insert(org: string, table: string, rows: Row[]): Promise<number> {
      const o = assertOrg(org);
      assertTable(table);
      if (rows.length === 0) return 0;
      const columns = Object.keys({ organization_id: null, ...rows[0] });
      const values = rows
        .map((r) => {
          const bound: Record<string, unknown> = { ...r, organization_id: o }; // never trust a caller-supplied org
          return `(${columns.map((c) => `'${String(bound[c] ?? "").replace(/'/g, "''")}'`).join(", ")})`;
        })
        .join(", ");
      const res = await raw.query(
        `insert into ${table} (${columns.join(", ")}) values ${values} on conflict do nothing`,
        [],
      );
      if (res.error) throw new Error(`insert ${table} failed: ${res.error}`);
      return res.rowCount;
    },

    /** UPDATE, tenant-scoped, returning the affected count so no-ops are visible. */
    async update(
      org: string,
      table: string,
      patch: Record<string, unknown>,
      where?: Record<string, unknown>,
    ): Promise<number> {
      const o = assertOrg(org);
      assertTable(table);
      delete (patch as Row)["organization_id"]; // the tenant is immutable
      const setKeys = Object.keys(patch);
      if (setKeys.length === 0) throw new TenantBoundaryError("empty patch");
      const sets = setKeys.map((k, i) => `${k} = $${i + 2}`).join(", ");
      const w = whereClause(where, setKeys.length + 2);
      const res = await raw.query(
        `update ${table} set ${sets} where organization_id = $1${w.sql}`,
        [o, ...setKeys.map((k) => patch[k]), ...w.params],
      );
      if (res.error) throw new Error(`update ${table} failed: ${res.error}`);
      return res.rowCount;
    },

    /** Governance RPCs (propose/decide/execute/audit). Org is required here too. */
    async rpc<T = unknown>(org: string, fn: string, args: Record<string, unknown>): Promise<T> {
      const o = assertOrg(org);
      const { data, error } = await raw.rpc(fn, { ...args, p_org: o });
      if (error) throw new Error(`rpc ${fn} failed: ${error}`);
      return data as T;
    },

    /**
     * Iterate tenants one at a time. The job payload carries the list; the body
     * runs once per tenant with the session bound, so a bug becomes a partial
     * failure rather than a full cross-tenant read.
     */
    async forEachTenant<T>(orgs: string[], fn: (org: string) => Promise<T>): Promise<T[]> {
      const out: T[] = [];
      for (const org of orgs) {
        const o = assertOrg(org);
        await raw.setTenantContext?.(o);
        try {
          out.push(await fn(o));
        } finally {
          await raw.setTenantContext?.(null);
        }
      }
      return out;
    },
  };
}

export type OrgScopedService = ReturnType<typeof createOrgScopedService>;
