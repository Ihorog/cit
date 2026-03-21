# PRODUCT_SPEC — Ci Mobile

## Core Rules
- One focus per screen
- Floating Ci button (bottom-right, thumb zone)
- Bottom sheet chat (half → full)
- No tab navigation
- No dashboards, no lists on main screen
- Chat is the primary operator

## Screens
1. **MainScreen** — full screen, header (date/time/group), one MainFocus block, CiButton
2. **CiChat** (bottom sheet) — messages, InputBar

## Components
| Component   | Role |
|-------------|------|
| CiButton    | Floating action, opens chat; long-press → voice stub |
| MainFocus   | Renders highest-priority FocusObject (color + shape) |
| CiChat      | Full chat UI inside bottom sheet |
| InputBar    | [ + ] [ text ] [ mic ] — minimal controls |

## Priority Engine
`score = importance × urgency × timeRelevance × ciAlignment × clarity`

## Data
- Static mock: Papa (Казкар), Mama (Багіра), Masha (Мавка)
- Future: CRDT sync via manifest.json
