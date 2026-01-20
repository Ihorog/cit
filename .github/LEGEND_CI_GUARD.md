# Guard: Legend Ci Documentation Anti-Duplication Rule

## Rule: No Full Legend Ci Documentation Outside ciwiki

**Status:** ENFORCED

### Policy

Legend Ci conceptual documentation must exist **only** in the canonical repository:
- **Canonical source:** `Ihorog/ciwiki/Legend ci/`
- **Single Source of Truth:** All Legend Ci concepts, philosophy, ontology, and theory

### Allowed in this repository (Ihorog/cit)

✅ **ALLOWED:**
- Redirect file (`LEGEND_CI.md`) with link to ciwiki
- References/links to canonical documentation
- Mentions of "Ci System" in context of technical implementation
- Technical implementation details (not conceptual theory)

❌ **FORBIDDEN:**
- Full copies of Legend Ci markdown files
- Duplicated conceptual documentation
- Directories like `Legend ci/` or `legend-ci/` with multiple files
- Re-explaining Legend Ci philosophy/concepts in detail

### Implementation

This guard is enforced through:

1. **Documentation:** This file serves as a policy reference
2. **Code review:** Reviewers must reject PRs that duplicate Legend Ci content
3. **CI checks:** Automated checks can be added to detect forbidden patterns

### Detection Patterns

PRs should be rejected if they:
- Create directories matching `*egend*ci*/` with multiple markdown files
- Add files with names like `01-definition.md`, `02-ontology.md`, etc.
- Contain large blocks of conceptual Legend Ci text (>200 words about Ci philosophy)

### Exceptions

If temporary duplication is absolutely necessary for development:
1. Must be documented in PR description
2. Must include removal plan with timeline
3. Requires explicit approval from maintainers

### References

- **Canonical Legend Ci:** https://github.com/Ihorog/ciwiki/tree/main/Legend%20ci
- **Redirect in this repo:** [LEGEND_CI.md](../LEGEND_CI.md)
- **Task Specification:** ciwiki Legend Ci synchronization (Фаза 1)

---

**Last Updated:** 2026-01-17
**Maintained by:** Repository maintainers
