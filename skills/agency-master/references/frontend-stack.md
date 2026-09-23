# Frontend stack profile

Loaded by `SKILL.md` when the project is a web frontend. Replace this file — not `SKILL.md` —
when the stack changes. That separation is the point: the orchestration rules are portable, the
toolchain is not.

## Mandated toolchain (2026-09)

| Component | Mandated | Notes |
|---|---|---|
| **Runtime** | **Bun** + Next.js | `bun run dev` (script = `next dev`). **Turbopack is the default bundler in Next.js 16** for both `dev` and `build` — no flag. Next.js 15 users: `next dev --turbopack`; `--turbo` is the deprecated alias. Escape hatch: `next dev --webpack`. `bun dev` only forwards flags to the package.json script, and silently does nothing useful if that script is not `next dev` |
| **Testing** | **Vitest** | Vite-powered. It is the test runner, not the app dev server — that distinction is deliberate |
| **Mock layer** | **MSW** | One handler set serves browser and node, so tests and the dev server share one mock contract. Use json-server (v0.17.4 stable; v1 still beta) only for throwaway prototypes with no test contract — running both creates two mock truths that drift |
| **UI components** | shadcn/ui **or** ant-design **or** daisyUI | Pick one per project. shadcn is copy-in source you own, not a dependency — mixing it with a component library is how design systems drift |
| **Icons** | lucide-react or Font Awesome | Zero emoji as icons |
| **Component docs** | Storybook | Isolated rendering for review and visual regression |
| **CSS** | Tailwind CSS v4 | Relative units (`rem`, `clamp()`) over `px` |
| **AST grounding** | tree-sitter (server or direct) | **Name the server and its tools before depending on it.** No unnamed MCP is a build target |
| **Audit** | `mcp.frontendchecklist.io` | 385 rules, 11 categories, 11 tools incl. `review_code`, `audit_url` |

## Design system hierarchy

Base tokens live in `design-system/MASTER.md`; a page or feature may override them in its own
`design-system/<route>.md`. **Page-level overrides beat global** — and every override states the
reason, or it is drift with extra steps.

Tokens are testable, so they are tested:

- text/background pairs ≥ 4.5:1 (AA), ≥ 7:1 for body copy where the design allows;
- the spacing scale is monotonic and derived from one base unit;
- no raw hex in components — tokens only.

## Taste dials

| Dial | Default | Meaning |
|---|---|---|
| `DESIGN_VARIANCE` | 3/10 | Clean, standard, usable. Asymmetry only for brutalist/portfolio work |
| `MOTION_INTENSITY` | 4/10 | 150–300 ms; animate `transform` and `opacity` only (compositor-friendly) |
| `VISUAL_DENSITY` | 5/10 | Balanced spaciousness with high information density |

**Banned patterns, not banned techniques.** No decorative multi-hue gradients (`from-purple-500
to-pink-500` and friends), no neon, no emoji icons. Ambient single-hue gradients used for depth are
fine. Banning the pattern is the rule; banning the technique was v5's over-rotation.

## Accessibility (checkable)

- Visible focus indicators on every interactive element; never `outline: none` without a replacement.
- Correct semantics first, ARIA only where semantics run out; no deprecated/abstract roles.
- `prefers-reduced-motion` honoured — including for library-driven animations.
- One `main` landmark, one `h1`, unique ids, form fields each with exactly one label.

## Performance

- Stream HTML; split and defer non-critical bundles.
- **Above the fold: `loading="eager"` on the LCP image. Lazy-load only offscreen media.**
  Lazy-loading the hero is the most common self-inflicted LCP regression.
- Modern formats (WebP/AVIF) with explicit dimensions to prevent layout shift.

## Security

- No `eval()`. Strict CSP with nonces or hashes.
- Cookies: `HttpOnly; Secure; SameSite=Lax` for session cookies.
  **`SameSite=Strict` on the session cookie breaks OAuth/OIDC/SAML** — the provider's cross-site
  redirect arrives without the cookie and the callback sees no session (documented redirect loops).
  Put `Strict` on the CSRF token's own cookie; use `None; Secure` only where a flow genuinely needs
  cross-site transmission, and scope it to that flow.
- External links with `target="_blank"` carry `rel="noopener noreferrer"`.

## Audit MCP: setup and failure modes

Register `mcp.frontendchecklist.io` in the client config, with any token in the environment — never
in the repository. Verify with a health check before the first audit of a session.

| Failure | Behaviour |
|---|---|
| MCP unreachable or rate-limited | Run the committed checklist below; **CI exits non-zero** and the waivers note why |
| MCP returns findings | Parse to severities; `Critical`/`High` block merge unless waived in writing in the PR |
| MCP disagrees with a persona review | The mechanical finding wins until someone argues it down in the PR — with reasons |

### Manual fallback (subset — run when the MCP is down)

Document has a lang attribute · one h1 and one main · unique ids · accessible form labels and error
messaging · focus visible · images have alt and dimensions · no mixed content · CSP present ·
session cookie `HttpOnly; Secure; SameSite=Lax` · non-critical JS deferred · page weight under
1500 KB · no console errors in production build.

## Not covered here

This profile is not a design authority and does not replace the audit: it states the rules that are
cheap to check and easy to forget. It says nothing about copy, information architecture or
brand — those are human decisions, and pretending otherwise is how agent-built products end up
looking like agent-built products.
