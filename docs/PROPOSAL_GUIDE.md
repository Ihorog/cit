# Implementation Proposal Guide

## Purpose

This guide explains how to create, review, and approve implementation proposals for the CIT project. Following this process ensures that all changes align with project principles and maintain quality standards.

## When to Write a Proposal

Create an implementation proposal when:

- Adding new features or endpoints
- Modifying existing API contracts
- Introducing new components or modules
- Making architectural changes
- Implementing complex bug fixes that affect multiple components
- Adding new dependencies or technologies

**Do NOT write a proposal for:**
- Fixing typos or documentation updates
- Minor bug fixes in a single file
- Refactoring without behavior changes
- Routine maintenance tasks

## Proposal Workflow

```
1. Draft Proposal
   ↓
2. Self-Review (use checklist)
   ↓
3. Submit for Review (create PR)
   ↓
4. Address Feedback
   ↓
5. Get Approval
   ↓
6. Implement (new branch)
   ↓
7. Verify & Merge
   ↓
8. Update Proposal Status
```

## Step-by-Step Guide

### Step 1: Create Proposal Document

1. Copy the template:
   ```bash
   cp docs/IMPLEMENTATION_PROPOSAL_TEMPLATE.md docs/proposals/IMPL-2026-01-25-job-management.md
   ```

2. Fill in the metadata:
   - Proposal ID: `IMPL-YYYY-MM-DD-<short-descriptive-name>`
   - Created date
   - Your GitHub username
   - Target component
   - Related issue numbers (if any)

3. Start with Executive Summary:
   - Write 1-2 paragraphs explaining WHAT and WHY
   - Keep it concise and clear
   - Should be understandable to non-technical stakeholders

### Step 2: Define the Problem

**Be specific and data-driven:**

❌ Bad:
```
Problem: The system is slow.
```

✅ Good:
```
Problem: When processing chat requests that require image analysis,
users experience 30+ second wait times, causing timeout errors.
Affects: 25% of users who send images.
Impact: 40% increase in support tickets over 2 weeks.
```

### Step 3: Describe the Solution

**Use concrete examples:**

❌ Bad:
```
Solution: Make it asynchronous.
```

✅ Good:
```
Solution: Implement a job queue system that:
1. Accepts long-running requests and returns job ID immediately
2. Processes requests in background
3. Allows clients to poll for status
4. Notifies on completion via webhook (optional)

Example flow:
POST /v1/jobs → {job_id: "abc123"}
GET /v1/jobs/abc123 → {status: "running", progress: 45%}
GET /v1/jobs/abc123 → {status: "completed", result: {...}}
```

### Step 4: Define Requirements

**Use the MUST/MUST NOT format:**

Requirements (MUST):
- [ ] Functional requirements - what the system must do
- [ ] Non-functional requirements - performance, scalability, etc.
- [ ] Security requirements - what must be protected

Forbidden (MUST NOT):
- [ ] Technical constraints (no new dependencies)
- [ ] Compatibility constraints (no breaking changes)
- [ ] Policy constraints (no secrets in code)

### Step 5: Set Acceptance Criteria

**Make criteria testable and measurable:**

❌ Bad:
```
- [ ] System works well
- [ ] Users are happy
```

✅ Good:
```
- [ ] Can create job via POST /v1/jobs with valid request
- [ ] Returns 400 error for invalid request
- [ ] Job status changes from pending → running → completed
- [ ] GET /v1/jobs/{id} responds in < 100ms
- [ ] 100 concurrent jobs can be processed without errors
```

### Step 6: Plan Implementation

**Break into phases with time estimates:**

```
Phase 1: Core Infrastructure (3 days)
  Day 1: JobStore class + tests
  Day 2: Job model + state machine
  Day 3: Integration with server

Phase 2: API Layer (2 days)
  Day 4: Endpoints + routing
  Day 5: Error handling + validation

Phase 3: Polish (2 days)
  Day 6: Documentation + examples
  Day 7: Performance testing + fixes
```

### Step 7: Self-Review

Use the review checklist:
- [ ] Executive summary is clear
- [ ] Problem is well-defined with data
- [ ] Solution addresses all pain points
- [ ] Requirements are complete and testable
- [ ] Acceptance criteria are measurable
- [ ] Implementation plan is realistic
- [ ] Risks are identified with mitigations
- [ ] No MUST NOT violations
- [ ] Documentation plan included
- [ ] Testing strategy defined

### Step 8: Submit for Review

1. Create a PR with your proposal:
   ```bash
   git checkout -b proposal/job-management
   git add docs/proposals/IMPL-2026-01-25-job-management.md
   git commit -m "Proposal: Job management system"
   git push origin proposal/job-management
   ```

2. Tag reviewers in the PR description:
   ```markdown
   @reviewer1 @reviewer2 Please review this implementation proposal
   for adding job management to CIT.
   
   Summary: Adds async job tracking to handle long-running operations.
   Impact: Improves UX for image analysis and other slow tasks.
   ```

3. Be responsive to feedback and iterate

### Step 9: Implementation

Once approved:

1. Create implementation branch:
   ```bash
   git checkout -b feature/job-management
   ```

2. Follow the implementation plan from your proposal

3. Reference the proposal in commits:
   ```bash
   git commit -m "Add JobStore class (IMPL-2026-01-25-job-management phase 1)"
   ```

4. Create PR when ready, linking to the proposal:
   ```markdown
   Implements: docs/proposals/IMPL-2026-01-25-job-management.md
   
   Phase 1: Core Infrastructure
   - [x] JobStore class
   - [x] Job model
   - [x] Unit tests
   ```

### Step 10: Update Proposal Status

After merge:

1. Update proposal metadata:
   ```markdown
   **Status:** Implemented
   **Implementation PR:** #456
   **Released:** v2.2.0
   ```

2. Add lessons learned section:
   ```markdown
   ## Lessons Learned
   
   What went well:
   - JobStore design was flexible enough for unforeseen use cases
   
   What could be improved:
   - Underestimated testing time by 1 day
   - Should have added metrics earlier
   ```

## Review Guidelines

### For Reviewers

When reviewing proposals, check:

1. **Clarity**
   - Is the problem clearly stated?
   - Is the solution easy to understand?
   - Are examples provided?

2. **Completeness**
   - Are all affected components identified?
   - Are edge cases considered?
   - Is rollback plan viable?

3. **Feasibility**
   - Are time estimates realistic?
   - Are resources available?
   - Are dependencies identified?

4. **Alignment**
   - Follows CIT principles (minimal, stdlib-only, etc.)?
   - Consistent with existing architecture?
   - Maintains backward compatibility?

5. **Quality**
   - Are acceptance criteria testable?
   - Is documentation plan adequate?
   - Are risks properly mitigated?

### For Approvers

Before approving, verify:

- [ ] Proposal reviewed by at least 2 people
- [ ] All major concerns addressed
- [ ] Timeline is realistic
- [ ] Resources are allocated
- [ ] No show-stopper risks
- [ ] Aligns with project roadmap
- [ ] Benefits justify the effort

## Common Mistakes

### Mistake 1: Too Vague

❌ Problem:
```
Users want better performance.
```

✅ Better:
```
Users experience 5-second delays when uploading files > 10MB.
Survey shows 60% would use the feature more if it was faster.
Benchmark: Current 5s, Target: < 1s, Best-in-class: 0.3s
```

### Mistake 2: Solution Looking for a Problem

❌ Bad:
```
Problem: We don't have a blockchain.
Solution: Add blockchain to CIT.
```

✅ Good:
```
Problem: Users cannot verify message authenticity.
Evidence: 3 support tickets about message tampering concerns.
Solution: Add cryptographic signatures (consider blockchain as one option).
```

### Mistake 3: Missing Constraints

❌ Bad:
```
Requirements:
- [ ] MUST add job queue
```

✅ Better:
```
Requirements:
- [ ] MUST add job queue with stdlib only (no Redis)
- [ ] MUST maintain < 100MB memory with 1000 active jobs
- [ ] MUST be backward compatible with existing /chat endpoint
- [ ] MUST NOT require additional system dependencies
```

### Mistake 4: Untestable Acceptance Criteria

❌ Bad:
```
- [ ] System is reliable
- [ ] Code is maintainable
```

✅ Better:
```
- [ ] 99.9% of job status queries succeed (measured over 1000 requests)
- [ ] Code coverage > 80% for new components
- [ ] Cyclomatic complexity < 10 for all new functions
```

## Templates for Common Scenarios

### Small Feature Addition

Use simplified template:
```markdown
# Feature: Add /debug Endpoint

## What
Add GET /debug endpoint that returns server diagnostics.

## Why
Needed for troubleshooting deployment issues.

## How
1. Add route handler in cit_server.py
2. Return JSON with: uptime, memory, request_count, errors
3. Add auth check (only localhost)

## Testing
- [ ] Returns 200 OK with valid JSON
- [ ] Returns 403 from non-localhost
- [ ] All fields present in response

## Files Changed
- server/cit_server.py (~20 lines)
- docs/API.md (document endpoint)
```

### Bug Fix Proposal

```markdown
# Fix: Race Condition in Job Status Updates

## Issue
Jobs sometimes show incorrect status due to concurrent updates.

## Root Cause
No locking mechanism when writing to job files.

## Solution
Add file locking using fcntl.flock() before writes.

## Testing
- [ ] 10 concurrent status updates complete successfully
- [ ] No corrupt job files after stress test
- [ ] No deadlocks after 1000 iterations

## Risks
- Performance: flock() adds ~1ms overhead
- Mitigation: Acceptable for correctness

## Files Changed
- server/job_store.py (add _lock_file method)
```

## FAQs

**Q: How detailed should the proposal be?**  
A: Detailed enough that someone can implement it without asking questions. Include code examples for complex parts.

**Q: What if requirements change during implementation?**  
A: Update the proposal! Create a "Changes Since Approval" section noting what changed and why.

**Q: Can I skip the proposal for urgent bug fixes?**  
A: For critical security fixes, yes. But document the fix afterward in a "Retrospective Proposal" for future reference.

**Q: How long should proposal review take?**  
A: Target 2-3 days for reviews. Complex proposals may need 1 week.

**Q: What if my proposal is rejected?**  
A: Common reasons: not aligned with roadmap, too complex, better alternatives exist. Ask for specific feedback and iterate or archive the proposal.

## Related Documents

- [IMPLEMENTATION_PROPOSAL_TEMPLATE.md](IMPLEMENTATION_PROPOSAL_TEMPLATE.md) - The actual template
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- [AGENTS.md](../.github/AGENTS.md) - Copilot agent guidelines
- [copilot-instructions.md](../.github/copilot-instructions.md) - Global Copilot rules

## Version History

- v1.0 (2026-01-25): Initial guide created
