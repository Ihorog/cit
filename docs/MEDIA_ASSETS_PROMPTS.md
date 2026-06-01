# MEDIA ASSETS & GENERATION PROMPTS — Ci Moment v2

Status: `VISUAL PRODUCTION SPEC`

Purpose: define the minimum media asset set required to support the Ci Moment v2 visual system, product UX, trust surface, artifact sharing, and social/referral loop.

Core formula:

```text
Result → Seal → Artifact → Verify → Repeat → Referral
```

Visual principle:

```text
The product is not decorated by media. Media explains the checkpoint, artifact, verification, and return loop.
```

---

## 0. Global visual direction

### Visual identity

- Premium dark interface.
- Soft black / deep graphite base.
- Gold light for seal, value, artifact, trust.
- Cool blue light for signal, time, clarity, verification.
- Glassmorphism only where it improves depth.
- Minimal symbols, clean geometry, spacious composition.
- No fantasy clutter.
- No heavy esoteric clichés.
- No “AI robot” visual language.
- No medical, legal, financial, fortune-telling, astrology-prediction claims.

### Core motifs

```text
center point
locked minute
glowing ring
sealed artifact
verification mark
time grid
subtle spatial coordinates
reflection / return loop
shareable checkpoint card
```

### Shared negative prompt

Use this negative prompt for all generative assets unless the asset requires otherwise:

```text
low quality, blurry, noisy, cluttered, overdecorated, cartoonish, cheap sci-fi, AI robot, humanoid robot, horoscope wheel, tarot table, mystic fortune teller, medical symbolism, legal symbolism, financial prediction imagery, fake UI text, unreadable letters, distorted typography, watermark, logo of existing brands, stock photo look, aggressive neon, horror, religious iconography, political symbols
```

---

## 1. Hero visual — Landing first screen

### Need

Primary above-the-fold visual for homepage / app entry.

### Purpose

Explain “moment signal” before the user reads too much text.

### Format

- `hero-ci-moment.webp`
- 16:9
- 2400×1350
- also export 1200×675 for OG preview

### Prompt

```text
Create a premium app-like hero visual for a digital product called Ci Moment. A dark graphite background with a luminous central point, a soft golden ring partially orbiting it, subtle blue time-grid lines, and a feeling of a personal moment being locked in time. Minimal, elegant, cinematic, calm, high-end SaaS visual language. No people, no robots, no mystical fortune telling. The image should feel like a symbolic checkpoint: Result → Seal → Artifact → Verify. Deep black, warm gold, cool blue, glass-like depth, soft volumetric glow, clean negative space for headline text on the left. Ultra-detailed, modern product launch aesthetic, 16:9.
```

---

## 2. Ci core mark — central product symbol

### Need

Reusable symbol for logo-like UI, app icon source, loading state, artifact watermark.

### Format

- `ci-core-mark.svg` preferred if generated manually/vectorized
- fallback raster: `ci-core-mark.png`
- transparent background
- 1024×1024

### Prompt

```text
Design a minimal premium abstract symbol for Ci Moment: a small luminous central point surrounded by an incomplete C-shaped golden halo and a thin cool-blue outer resonance line. The symbol must feel like presence, signal, sealed moment, and verification. No letters except the implied abstract C shape. Vector-logo style, high-end, simple, scalable, balanced, dark or transparent background, gold and blue glow, clean geometry, no clutter, no robot, no mystical symbols.
```

---

## 3. Context selection cards — Career / Love / Timing

### Need

Three visual cards for context choice.

### Purpose

Give each context a distinct visual mood without creating heavy illustrations.

### Format

- `context-career.webp`
- `context-love.webp`
- `context-timing.webp`
- 4:3
- 1200×900

### Prompt — Career

```text
Create a premium abstract context card for “Career” in Ci Moment. Dark glass UI surface, subtle forward vector lines, golden point of action, cool blue structure grid, feeling of direction, execution, and controlled movement. No office people, no corporate stock photo, no money symbols. Minimal, elegant, app-like, symbolic, high-end digital product visual, 4:3.
```

### Prompt — Love

```text
Create a premium abstract context card for “Love” in Ci Moment. Dark glass UI surface with two soft luminous points approaching resonance, a warm gold inner glow and a cool blue balancing line, feeling of contact, relation, and mutual signal. No hearts, no couples, no romance clichés. Minimal, elegant, symbolic, app-like, high-end digital product visual, 4:3.
```

### Prompt — Timing

```text
Create a premium abstract context card for “Timing” in Ci Moment. Dark glass UI surface with a locked minute mark, thin circular time arcs, one golden checkpoint, cool blue temporal grid, feeling of rhythm, transition, and the right moment. No clocks with readable numbers, no calendar stock imagery. Minimal, elegant, symbolic, app-like, high-end digital product visual, 4:3.
```

---

## 4. Manifest / processing visual

### Need

Loading / transition visual while the result is generated.

### Format

- `manifest-loop.mp4` or `manifest-loop.webm`
- 5–7 seconds seamless loop
- 1080×1080 and 1920×1080 variants

### Prompt

```text
Create a seamless premium loading animation for Ci Moment. A dark spatial field with a small central luminous point, subtle blue grid lines converging, a golden ring forming and dissolving around the point, like a moment being aligned and sealed. Calm, precise, not flashy, no text, no logos, no people, no robots. High-end app interaction animation, smooth loop, glassmorphism atmosphere, dark graphite, gold and blue light.
```

---

## 5. Result state visuals — Proceed / Hold / Not Now

### Need

Three result visuals matching deterministic algorithm states.

### Format

- `result-proceed.webp`
- `result-hold.webp`
- `result-not-now.webp`
- 1:1
- 1400×1400

### Prompt — Proceed

```text
Create a premium square visual for a Ci Moment result state: PROCEED. Dark graphite background, central golden signal opening forward, subtle blue coordinate lines, feeling of a path becoming clear. Symbolic, minimal, calm confidence, no arrows as literal icons, no text, no people, no robots, no prediction imagery. High-end digital artifact aesthetic, 1:1.
```

### Prompt — Hold

```text
Create a premium square visual for a Ci Moment result state: HOLD. Dark graphite background, central luminous point balanced between a warm gold half-ring and a cool blue stabilizing arc, feeling of alignment before action. Symbolic, minimal, calm, no warning signs, no text, no people, no robots. High-end digital artifact aesthetic, 1:1.
```

### Prompt — Not Now

```text
Create a premium square visual for a Ci Moment result state: NOT NOW. Dark graphite background, central signal softly closed by a thin golden boundary, cool blue fading grid, feeling of a moment passing without failure. Symbolic, minimal, calm, not negative, no stop signs, no red alerts, no text, no people, no robots. High-end digital artifact aesthetic, 1:1.
```

---

## 6. Sealed artifact visual

### Need

Visual basis for the paid artifact and verify page.

### Format

- `sealed-artifact-card.webp`
- 3:4
- 1600×2133
- also 1:1 crop for social

### Prompt

```text
Create a premium digital artifact card for Ci Moment. A dark glass card floating in space, with a central golden seal, subtle blue verification lines, abstract encoded marks, and an empty clean area where an artifact code can be placed later by UI. The card should feel collectible, verified, personal, and calm. No readable fake text, no QR code unless abstract, no people, no robots, no mystical objects. High-end product artifact, cinematic depth, 3:4 vertical.
```

---

## 7. Verify page trust visual

### Need

Hero/side visual for `/verify/[hash]`.

### Format

- `verify-trust-visual.webp`
- 16:9
- 1800×1012

### Prompt

```text
Create a premium verification visual for Ci Moment. Dark background, a sealed digital artifact connected to a thin blue verification line and a soft golden confirmation point. The feeling should be trust, proof, and calm validation. No checkmark cliché, no legal stamp, no blockchain cliché, no fake readable text. Minimal, elegant, app-like, high-end trust surface, 16:9.
```

---

## 8. Share card / referral object

### Need

OpenGraph and social share visual template.

### Format

- `share-card-template.webp`
- 1200×630

### Prompt

```text
Create a premium social share card background for Ci Moment. Dark graphite gradient, central sealed moment point, subtle gold ring, cool blue time grid, large clean negative space for dynamic text and artifact code overlay. It should look like a valuable personal checkpoint, not a horoscope or prediction. Minimal, elegant, high-end, highly legible when text is added later, 1200×630.
```

---

## 9. PWA / app icon family

### Need

App install icon, favicon, mobile shortcut.

### Format

- `icon-192.png`
- `icon-512.png`
- `favicon.svg`
- `apple-touch-icon.png`

### Prompt

```text
Design a premium minimal app icon for Ci Moment. A central luminous gold point with an incomplete C-shaped golden ring and a thin blue resonance edge, on a deep graphite background. It must be readable at small sizes, simple, iconic, not text-heavy, no robots, no mystical clichés. Modern app icon, high contrast, rounded-square safe composition.
```

---

## 10. Trust surface illustrations

### Need

Small visuals for public explanation pages.

### Format

- `trust-what-is-ci.webp`
- `trust-how-seal-works.webp`
- `trust-privacy.webp`
- `trust-not-advice.webp`
- 16:10
- 1400×875

### Prompt — What is Ci Moment

```text
Create a premium explanatory illustration for “What is Ci Moment?” A dark elegant interface space with a central moment point, gentle gold glow, subtle blue coordinates, and a feeling of personal clarity. No people, no robots, no fortune telling. Minimal SaaS trust visual, 16:10.
```

### Prompt — How sealing works

```text
Create a premium explanatory illustration showing how a moment becomes a sealed digital artifact. Use abstract steps: signal point, golden seal ring, artifact card, verification line. No text, no fake UI labels, no people. Dark graphite, gold and blue, clean product diagram style, 16:10.
```

### Prompt — Privacy

```text
Create a premium privacy visual for Ci Moment. A small golden artifact protected inside a transparent glass boundary, with minimal blue data lines reduced into anonymous points. Feeling of data minimization and control. No locks as cliché if possible, no cybersecurity stock imagery, no people, no text. Elegant, calm, 16:10.
```

### Prompt — Not advice

```text
Create a premium boundary visual for Ci Moment. A symbolic signal card separated from external decision outcomes by a soft transparent boundary. The image should communicate: personal checkpoint, not prediction or professional advice. No warning signs, no law/medical/finance symbols, no text, no people. Minimal, calm, high-end trust surface, 16:10.
```

---

## 11. Pricing / offer ladder visuals

### Need

Visual support for Free check → Seal → Bundle → Membership.

### Format

- `offer-ladder.webp`
- 16:9
- 1800×1012

### Prompt

```text
Create a premium abstract offer ladder visual for Ci Moment. Four ascending glass cards in a dark space: free signal, single seal, bundle archive, membership loop. Use subtle gold highlights for value and blue lines for continuity. No readable text, no money symbols, no salesy stock imagery. Clean SaaS pricing visual, elegant, 16:9.
```

---

## 12. Empty / error / fallback visuals

### Need

Non-destructive states for unavailable verify, local-only persistence, payment not matched.

### Format

- `state-local-only.webp`
- `state-not-found.webp`
- `state-pending-match.webp`
- 1:1
- 1200×1200

### Prompt — Local only

```text
Create a calm premium fallback visual for Ci Moment: local-only artifact state. A small golden point held inside a local glass circle, with cloud lines faintly absent in the background. It should feel safe and temporary, not broken. No text, no warning icons, dark graphite, gold and blue, 1:1.
```

### Prompt — Not found

```text
Create a calm premium fallback visual for Ci Moment: artifact not found. A dim blue verification line searching through a dark grid, with a soft golden point missing from its expected position. No red errors, no harsh warning signs, no text. Elegant, respectful, 1:1.
```

### Prompt — Pending match

```text
Create a calm premium fallback visual for Ci Moment: payment/order match pending. A sealed golden artifact and a blue external checkout line almost connected but not yet joined. Feeling of waiting for confirmation, not failure. No text, no warning signs, high-end digital product style, 1:1.
```

---

## 13. Social short-form backgrounds

### Need

TikTok / Reels / Shorts visual loops for organic/referral acquisition.

### Format

- `social-loop-signal.mp4`
- `social-loop-seal.mp4`
- `social-loop-verify.mp4`
- 9:16
- 1080×1920
- 5–8 seconds

### Prompt — Signal

```text
Create a vertical premium animated background for short-form video. Dark graphite space, a small blue signal appears, moves toward a golden central point, then stabilizes. No text, no people, no robots, no fortune telling. Calm, hypnotic, high-end digital ritual aesthetic, 9:16 seamless loop.
```

### Prompt — Seal

```text
Create a vertical premium animated background for short-form video. A golden ring slowly closes around a central point, forming a sealed moment artifact, with subtle blue time-grid lines behind it. No text, no people, no robots. Calm, elegant, high-end product aesthetic, 9:16 seamless loop.
```

### Prompt — Verify

```text
Create a vertical premium animated background for short-form video. A sealed golden artifact connects to a cool blue verification line, then emits a soft confirmation glow. No text, no people, no robots, no legal stamp cliché. Calm, trustworthy, high-end digital product aesthetic, 9:16 seamless loop.
```

---

## 14. Asset naming convention

```text
/public/media/hero-ci-moment.webp
/public/media/ci-core-mark.svg
/public/media/context-career.webp
/public/media/context-love.webp
/public/media/context-timing.webp
/public/media/manifest-loop.webm
/public/media/result-proceed.webp
/public/media/result-hold.webp
/public/media/result-not-now.webp
/public/media/sealed-artifact-card.webp
/public/media/verify-trust-visual.webp
/public/media/share-card-template.webp
/public/media/icon-192.png
/public/media/icon-512.png
/public/media/favicon.svg
/public/media/apple-touch-icon.png
/public/media/trust-what-is-ci.webp
/public/media/trust-how-seal-works.webp
/public/media/trust-privacy.webp
/public/media/trust-not-advice.webp
/public/media/offer-ladder.webp
/public/media/state-local-only.webp
/public/media/state-not-found.webp
/public/media/state-pending-match.webp
/public/media/social-loop-signal.webm
/public/media/social-loop-seal.webm
/public/media/social-loop-verify.webm
```

---

## 15. Minimum viable media set

For first deploy, generate only:

```text
1. hero-ci-moment.webp
2. ci-core-mark.svg/png
3. context-career.webp
4. context-love.webp
5. context-timing.webp
6. result-proceed.webp
7. result-hold.webp
8. result-not-now.webp
9. sealed-artifact-card.webp
10. verify-trust-visual.webp
11. share-card-template.webp
12. icon-512.png
```

All other assets can be added in the second visual pass.
