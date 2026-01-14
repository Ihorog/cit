---
name: Copilot Task (CIT)
about: Well-scoped task for Copilot coding agent
title: "[CIT] "
labels: copilot-task
assignees: ''
---

## Problem statement
<!-- Clear description of what needs to be done -->

## Acceptance criteria
<!-- Checkboxes with specific, testable conditions -->
- [ ] 
- [ ] 
- [ ] 

## Files to modify
<!-- List the specific files that will need changes -->
- `server/cit_server.py`
- `docs/...`

## Manual test commands
<!-- Commands to verify the changes work as expected -->
```bash
# Health check
curl http://127.0.0.1:8790/health

# Test endpoint
curl -X POST http://127.0.0.1:8790/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"test"}'
```

## Additional context
<!-- Any other relevant information, constraints, or notes -->
