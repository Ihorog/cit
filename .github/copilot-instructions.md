# GitHub Copilot Instructions — Ci Moment v2

Status: `ACTIVE REPOSITORY RULES`

---

## 0. Source of truth

This repository is the clean v2 development surface for Ci Moment / Legend Ci.

The old `Ihorog/ci-moment` repository is historical reference only.

Inherited CIT-specific instructions are not valid for this repository unless explicitly reintroduced in a dedicated integration layer.

---

## 1. Core formula

```text
Result → Seal → Artifact → Verify → Repeat → Referral
```

---

## 2. Must

- Treat artifact and verification as core product objects.
- Track source/session for every meaningful product action.
- Match Gumroad orders to artifacts before making economic claims.
- Keep consent explicit.
- Keep privacy language conservative.
- Add tests for telemetry, artifact, payment attribution, and verification logic.
- Preserve user data and secrets.
- Prefer clear product architecture over inherited MVP shortcuts.

---

## 3. Must not

- Do not copy old MVP assumptions blindly.
- Do not implement cold paid growth before telemetry.
- Do not hardcode private credentials.
- Do not claim attribution works until tested.
- Do not position Ci Moment as advice, prediction, therapy, legal, medical, financial, or life-critical guidance.
- Do not expose internal infrastructure status as public acquisition surface.

---

## 4. Implementation priority

1. Product spec.
2. Telemetry spec.
3. Artifact model.
4. Gumroad attribution.
5. Verify surface.
6. Trust surface.
7. Offer ladder.
8. Dashboard / CRSS.

---

## 5. Acceptance rule

The product direction is valid only when the system can answer:

1. Where did this session come from?
2. Did the user reach Result?
3. Did the user click Seal?
4. Did checkout open?
5. Did a paid order happen?
6. Which artifact was paid for?
7. Did the user verify or revisit?
8. Did the user repeat, share, or join membership?
9. Which channel has the strongest CRSS?
10. What is the real LTV/CAC boundary after data exists?

Until then, economics remain benchmark-based simulation.
