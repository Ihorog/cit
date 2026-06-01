# Ci Moment v2

Status: `NEW DEVELOPMENT SURFACE`

Ci Moment v2 is a clean rebuild of the product direction.

Old repository `Ihorog/ci-moment` is historical reference only.

---

## Core formula

```text
Result → Seal → Artifact → Verify → Repeat → Referral
```

---

## Product definition

Ci Moment is a personal moment signal and symbolic checkpoint.

It helps a user move through:

```text
Attention
→ Context
→ Threshold
→ Result
→ Seal
→ Artifact
→ Verify
→ Repeat
→ Referral / Membership
```

Boundary:

```text
Not advice. Not prediction. Not therapy. Not financial, legal, medical, or life-critical guidance.
```

---

## Current development truth

Read first:

- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md)
- [`docs/TELEMETRY_SPEC.md`](docs/TELEMETRY_SPEC.md)
- [`docs/GUMROAD_ATTRIBUTION_SPEC.md`](docs/GUMROAD_ATTRIBUTION_SPEC.md)
- [`docs/TRUST_SURFACE_SPEC.md`](docs/TRUST_SURFACE_SPEC.md)
- [`.github/copilot-instructions.md`](.github/copilot-instructions.md)

---

## Technical direction

Primary stack:

```text
Next.js
TypeScript
Vercel
Supabase with RLS
Cloudflare event layer
Gumroad checkout attribution
```

---

## Immediate implementation path

```text
1. Clean app skeleton
2. Telemetry event utility
3. Session / UTM capture
4. Artifact generation
5. Verify page
6. Seal CTA with checkout attribution
7. Order reconciliation
8. CRSS dashboard
```

---

## Development commands

```bash
npm install
npm run dev
npm run type-check
npm run build
```

---

## Active principle

```text
Not traffic → sale.
Result → Seal → Artifact → Verify → Repeat → Referral.
```
