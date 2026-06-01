# TELEMETRY SPEC — Ci Moment v2

Status: `REQUIRED FOR ECONOMICS`

The core blocker for Ci Moment is the broken measurement loop between product events, checkout, artifact, source attribution, and repeat behavior.

---

## 1. Measurement loop

```text
source
→ session
→ result
→ seal click
→ checkout open
→ paid order
→ artifact
→ verify
→ repeat
→ membership
→ referral
```

---

## 2. Required events

```text
page_view
context_selected
threshold_confirmed
result_rendered
seal_clicked
gumroad_checkout_opened
gumroad_order_matched
artifact_verified
repeat_visit_30d
membership_started
membership_renewed
membership_canceled
```

---

## 3. Required event fields

```text
event_id
session_id
anonymous_user_id
source
utm_source
utm_medium
utm_campaign
referrer
route
context
artifact_id
verify_hash
checkout_id
order_id
membership_id
device_type
country_optional
timestamp
```

Privacy rule:

```text
Do not collect unnecessary personal data.
Prefer pseudonymous IDs, hashes, aggregated analytics, and explicit consent for email lifecycle.
```

---

## 4. CRSS

```text
CRSS = result_view_rate × seal_click_rate × repeat_rate_30d
```

Meaning:

```text
CRSS measures whether a channel produces stable reaction, not just traffic.
```

Use CRSS to rank channels:

- SEO / docs;
- referral / artifact sharing;
- email / reactivation;
- organic social;
- partner traffic;
- retargeting;
- cold paid traffic.

Cold paid traffic stays blocked until telemetry and LTV are proven.
