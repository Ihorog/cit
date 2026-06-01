# INTERNAL ALGORITHM SPEC — Ci Moment v2

Status: `NO-AI CORE ENGINE`

Purpose: define a deterministic internal algorithm for Ci Moment that does not require Groq, OpenAI, Anthropic, or any other AI provider to produce the core product result.

---

## 1. Core decision

Ci Moment core must not depend on AI inference.

AI may be added later only as an optional explanation, personalization, or narrative layer.

```text
Core result = deterministic algorithm
Optional interpretation = AI layer
```

This protects the product from:

- external API cost;
- model downtime;
- rate limits;
- unpredictable outputs;
- compliance risk from opaque AI advice;
- unstable unit economics.

---

## 2. Algorithm role

The internal algorithm generates a symbolic personal moment signal from controlled inputs.

It must return:

```text
context
locked_minute
phase
polarity
resonance_score
status
signal_label
artifact_seed
explanation_key
```

The result is a symbolic checkpoint, not advice and not prediction.

---

## 3. Inputs

Minimum inputs:

```text
context: career | love | timing
locked_minute: integer
```

Optional non-sensitive inputs:

```text
intention_length
selected_tone
returning_user_flag
```

Avoid collecting raw private intentions unless explicit consent exists.

---

## 4. Deterministic layers

### 4.1 Time lock

```text
locked_minute = floor(timestamp_ms / 60000)
```

The moment is bound to a specific UTC minute.

### 4.2 Context weight

```text
career = 11
love = 17
timing = 23
```

### 4.3 Ci phase

Seven-phase cycle:

```text
0 signal
1 attention
2 threshold
3 alignment
4 action
5 seal
6 return
```

### 4.4 Polarity

```text
+  = open movement
=  = balanced pause
-  = closed / not now
```

### 4.5 Resonance score

A stable score from 0 to 100 derived from:

```text
locked_minute
context_weight
phase
cycle position
```

### 4.6 Status mapping

```text
0..34   → NOT_NOW
35..66  → HOLD
67..100 → PROCEED
```

---

## 5. Output example

```json
{
  "context": "timing",
  "lockedMinute": 29677914,
  "phase": "alignment",
  "polarity": "=",
  "resonanceScore": 58,
  "status": "HOLD",
  "signalLabel": "Align before action",
  "artifactSeed": "ci-29677914-timing-58",
  "explanationKey": "hold_alignment"
}
```

---

## 6. Product boundary

Display copy must remain conservative:

```text
This is a personal moment signal, not advice or prediction.
```

Do not generate claims like:

- “you should quit your job”;
- “this person loves you”;
- “this will happen tomorrow”;
- “financial outcome is guaranteed”.

---

## 7. Why this is better than AI-only execution

| Criterion | No-AI core | AI core |
|---|---|---|
| Cost | near zero | variable |
| Reliability | stable | provider-dependent |
| Speed | instant | network/model latency |
| Legal risk | lower | higher |
| Result repeatability | guaranteed | not guaranteed |
| Artifact verification | simple | harder |
| Product identity | stronger | diluted |

---

## 8. Optional AI layer

AI can later be used only after the deterministic result exists.

Allowed AI use:

```text
result explanation
ritual copy variants
share card wording
personal archive reflection
support/chat assistant
```

Blocked AI use:

```text
core status decision
payment eligibility
life advice
sensitive profiling
legal/medical/financial prediction
```

---

## 9. Acceptance criteria

The internal algorithm is valid when:

1. Same input always produces same output.
2. No external AI/API is required.
3. Result can be generated offline.
4. Artifact can be verified later from stored algorithm version and input.
5. Output is symbolic, not advisory.
6. The UI can render the full Result → Seal → Artifact flow without AI.

---

## 10. Operating principle

```text
AI is optional surface.
Algorithm is product core.
```
