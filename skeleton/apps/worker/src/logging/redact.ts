/**
 * Redaction that runs before anything reaches log storage.
 *
 * The rule from the security spec — "never log tokens" — is not a rule you can
 * keep by discipline at 23:00 on a Tuesday. So it is a filter, installed once,
 * that also strips credential-shaped values that arrive inside free text
 * (error messages from HTTP clients are the usual culprit).
 */

const SECRET_KEY_PATTERN =
  /(token|secret|password|passwd|authorization|auth|cookie|api[-_]?key|refresh|access[-_]?token|client[-_]?secret|credential|service[-_]?role)/i;

/** Prefixes and shapes that indicate a live credential, wherever they appear. */
const SECRET_VALUE_PATTERNS: RegExp[] = [
  /ya29\.[A-Za-z0-9_\-\.]+/g,          // Google OAuth access token
  /1\/\/[A-Za-z0-9_\-\.]+/g,           // Google refresh token
  /EAA[A-Za-z0-9]{20,}/g,              // Meta long-lived token
  /sk-[A-Za-z0-9]{16,}/g,              // generic API key (OpenAI-style)
  /AIza[A-Za-z0-9_\-]{20,}/g,          // Google API key
  /eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}/g, // JWT
  /Bearer\s+[A-Za-z0-9_\-\.=]+/gi,     // Authorization header echo
  /postgres(ql)?:\/\/[^\s"']+/gi,      // connection string with password
];

export const REDACTED = "[REDACTED]";

export function redactString(value: string): string {
  let out = value;
  for (const re of SECRET_VALUE_PATTERNS) out = out.replace(re, REDACTED);
  return out;
}

/**
 * Deep-redact a structured log object. Keys that look secret are replaced
 * wholesale; every string is additionally scrubbed for credential shapes.
 */
export function redact(value: unknown, depth = 0): unknown {
  if (depth > 6) return "[depth-limit]";
  if (value === null || value === undefined) return value;

  if (typeof value === "string") return redactString(value);
  if (typeof value !== "object") return value;
  if (Array.isArray(value)) return value.map((v) => redact(v, depth + 1));

  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
    out[k] = SECRET_KEY_PATTERN.test(k) ? REDACTED : redact(v, depth + 1);
  }
  return out;
}

/** Minimal logger shape — swap for pino/winston and keep redact() in the path. */
export interface Logger {
  info(obj: Record<string, unknown>, msg?: string): void;
  warn(obj: Record<string, unknown>, msg?: string): void;
  error(obj: Record<string, unknown>, msg?: string): void;
}

export function createLogger(sink: Logger, base: Record<string, unknown> = {}): Logger {
  const emit =
    (level: "info" | "warn" | "error") =>
    (obj: Record<string, unknown>, msg?: string) =>
      sink[level](redact({ ...base, ...obj }) as Record<string, unknown>, msg ? redactString(msg) : undefined);
  return { info: emit("info"), warn: emit("warn"), error: emit("error") };
}

/**
 * Canary: call this once per deploy with a known value, then assert that the
 * value never appears in your log store. That assertion belongs in CI
 * (db/tests/README → "log hygiene"), not in a reviewer's memory.
 */
export const CANARY = "HGOS_CANARY_DO_NOT_LOG_7f3c81";
