# Implementation Proposal Quick Reference

**Quick guide for creating implementation proposals in CIT**

## When Do I Need a Proposal?

✅ **YES - Write a proposal:**
- Adding new API endpoints
- Changing existing API contracts
- Adding new components/modules
- Architectural changes
- New dependencies
- Complex multi-file changes

❌ **NO - Just create PR:**
- Fixing typos
- Simple bug fixes (1 file)
- Documentation updates
- Refactoring (no behavior change)

## Quick Start (5 minutes)

```bash
# 1. Copy template
cd /home/runner/work/cit/cit
cp docs/IMPLEMENTATION_PROPOSAL_TEMPLATE.md \
   docs/proposals/IMPL-$(date +%Y-%m-%d)-my-feature.md

# 2. Edit your proposal
vim docs/proposals/IMPL-*-my-feature.md

# 3. Submit for review
git checkout -b proposal/my-feature
git add docs/proposals/IMPL-*-my-feature.md
git commit -m "Proposal: Add my feature"
git push origin proposal/my-feature

# 4. Create PR on GitHub and tag reviewers
```

## Proposal Checklist

Fill these sections (in order):

1. ✓ **Metadata** - ID, date, author, component
2. ✓ **Executive Summary** - What and why (1-2 paragraphs)
3. ✓ **Problem Statement** - Current situation, pain points, impact
4. ✓ **Proposed Solution** - High-level approach, components, API changes
5. ✓ **Requirements (MUST)** - Functional, non-functional, security
6. ✓ **Forbidden (MUST NOT)** - Constraints and boundaries
7. ✓ **Acceptance Criteria** - Testable "done when" conditions
8. ✓ **Implementation Plan** - Phases with time estimates
9. ✓ **Technical Design** - Data models, code structure, API contracts
10. ✓ **Risks & Mitigations** - What could go wrong, how to prevent
11. ✓ **Review Checklist** - Self-review before submitting

## Key Sections Explained

### Requirements (MUST)
```markdown
- [ ] System MUST do X
- [ ] System MUST handle Y
- [ ] Performance MUST be < Z
```
Make them **testable** and **specific**

### Forbidden (MUST NOT)
```markdown
- [ ] MUST NOT add dependencies
- [ ] MUST NOT break API compatibility
- [ ] MUST NOT commit secrets
```
These are **constraints** you must respect

### Acceptance Criteria
```markdown
- [ ] Can create job via POST /v1/jobs
- [ ] Returns 400 for invalid input
- [ ] Response time < 100ms
```
Write **testable** conditions that define "done"

## Common Patterns

### Adding API Endpoint
```markdown
## Proposed Solution
New endpoint: POST /v1/jobs
- Accepts: {"type": "task", "params": {...}}
- Returns: {"job_id": "uuid", "status": "pending"}

## Requirements
- [ ] MUST validate input
- [ ] MUST return unique job ID
- [ ] MUST persist job data

## Acceptance Criteria
- [ ] curl -X POST /v1/jobs returns 201 with job_id
- [ ] Invalid request returns 400 with error
```

### Modifying Existing Code
```markdown
## Proposed Solution
Modify /chat endpoint to include request_id

## Requirements
- [ ] MUST maintain backward compatibility
- [ ] MUST NOT break existing clients

## Acceptance Criteria
- [ ] Old clients still work (no request_id)
- [ ] New clients get request_id in response
```

### Performance Improvement
```markdown
## Problem Statement
/chat response time is 5s, should be < 1s

## Proposed Solution
Add caching layer for repeated queries

## Requirements
- [ ] MUST reduce latency to < 1s (95th percentile)
- [ ] MUST NOT increase memory > 10MB

## Acceptance Criteria
- [ ] Benchmark shows < 1s for cached queries
- [ ] Memory usage verified < baseline + 10MB
```

## Review Criteria

Before submitting, ask yourself:

- [ ] **Problem is clear** - Would someone unfamiliar understand it?
- [ ] **Solution is specific** - Could someone implement from this?
- [ ] **Requirements are testable** - Can we verify each one?
- [ ] **Risks are identified** - What could go wrong?
- [ ] **Timeline is realistic** - Are estimates reasonable?
- [ ] **No MUST NOT violations** - Respects all constraints?

## Templates for Quick Cases

### Small Feature (< 50 lines)
```markdown
# Feature: Add X

**What:** Add feature X to do Y
**Why:** Users need this because Z
**How:** Modify file.py, add function foo()
**Testing:** 
- [ ] Test case 1
- [ ] Test case 2
**Files:** file.py (~20 lines)
```

### Bug Fix
```markdown
# Fix: Issue with X

**Issue:** #123 - System crashes when Y
**Root Cause:** Missing null check in Z
**Solution:** Add validation before Z
**Testing:**
- [ ] No crash when Y is null
- [ ] Normal operation when Y is valid
**Files:** file.py (~5 lines)
```

## Need Help?

- **Full guide:** [docs/PROPOSAL_GUIDE.md](PROPOSAL_GUIDE.md)
- **Template:** [docs/IMPLEMENTATION_PROPOSAL_TEMPLATE.md](IMPLEMENTATION_PROPOSAL_TEMPLATE.md)
- **Example:** [docs/proposals/EXAMPLE-request-id-tracking.md](proposals/EXAMPLE-request-id-tracking.md)
- **Questions:** Open an issue or ask in PR

## Pro Tips

💡 **Start small** - Your first proposal doesn't need to be perfect

💡 **Use examples** - Show code snippets, API calls, curl commands

💡 **Be specific** - "Response time < 100ms" not "should be fast"

💡 **Think ahead** - What happens at scale? Under errors? Edge cases?

💡 **Get early feedback** - Share draft proposals for review

## Common Mistakes to Avoid

❌ **Too vague**: "Make it better"  
✅ **Specific**: "Reduce /chat latency from 5s to < 1s"

❌ **No acceptance criteria**: "Should work well"  
✅ **Testable**: "99% of requests succeed, < 100ms response"

❌ **Missing constraints**: Just list features  
✅ **Include MUST NOTs**: "No new dependencies, no breaking changes"

❌ **Unrealistic timeline**: "2 days" for complex feature  
✅ **Realistic**: "Phase 1: 3 days, Phase 2: 2 days, Testing: 2 days"

## Workflow Summary

```
Draft → Self-Review → Submit PR → Address Feedback → 
Get Approval → Implement → Test → Merge → Update Status
```

**Typical timeline:**
- Draft: 1-2 hours
- Review: 2-3 days
- Implementation: Per plan
- Total: 1-2 weeks for medium features

---

**Keep this handy!** Bookmark this page for quick reference when creating proposals.

**Last Updated:** 2026-01-25
