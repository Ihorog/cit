# SYSTEM_WILL — Ci Mobile

## Status: ACTIVE [111]
Date initialized: 2026-03-20

## Module Registry
| Module          | Status  | File |
|-----------------|---------|------|
| priorityEngine  | active  | src/engine/priorityEngine.ts |
| homeworkParser  | dormant | src/engine/homeworkParser.ts |
| cycleModule     | dormant | src/engine/cycleModule.ts |
| CiButton        | active  | src/components/CiButton.tsx |
| CiChat          | active  | src/components/CiChat.tsx |
| InputBar        | active  | src/components/InputBar.tsx |
| MainFocus       | active  | src/components/MainFocus.tsx |
| MainScreen      | active  | src/screens/MainScreen.tsx |
| voiceHandler    | stub    | — |
| imageInput      | stub    | — |

## Evolution Log
- 2026-03-20: Initial scaffold. 15 modules created. PR opened.

## Next Activations
1. Voice handler (real STT)
2. Image picker → OCR → homeworkParser
3. CRDT sync to manifest.json
4. cycleModule UI surface
