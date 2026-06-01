# GUMROAD ATTRIBUTION SPEC — Ci Moment v2

Status: `REQUIRED BEFORE PAID GROWTH`

Checkout must not be a blind redirect.

---

## 1. Required checkout handoff

Every checkout URL must carry enough context to reconcile payment with product state.

```text
artifact_id
verify_hash
session_id
source
utm_source
utm_medium
utm_campaign
return_url
passthrough/custom field
```

---

## 2. Required reconciliation

```text
Gumroad order
→ passthrough / custom field
→ artifact_id / verify_hash
→ session_id
→ source
→ user lifecycle
```

Acceptance rule:

```text
A paid order is not analytically useful until it is matched to an artifact and source.
```

---

## 3. Events

```text
gumroad_checkout_opened
gumroad_order_matched
```

---

## 4. Artifact payment state

Artifact states:

```text
created
checkout_opened
paid_matched
verified
revisited
shared
```

---

## 5. Blocked claims

Do not claim real CAC, LTV, paid conversion, channel quality, or ROAS until orders are matched to artifacts and sources.

Until then, economics remain:

```text
benchmark-based simulation
```
