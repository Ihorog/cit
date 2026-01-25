# Implementation Proposals

This directory contains implementation proposals for CIT features and major changes.

## Purpose

Implementation proposals provide a structured way to:
- Document design decisions before implementation
- Gather feedback from reviewers
- Track requirements and acceptance criteria
- Maintain historical context for future reference

## Structure

```
docs/proposals/
├── README.md (this file)
├── IMPL-2026-01-25-job-management.md
├── IMPL-2026-02-01-webhook-support.md
└── archive/
    └── IMPL-2025-12-15-deprecated-feature.md
```

## Naming Convention

Proposals use the format: `IMPL-YYYY-MM-DD-<short-name>.md`

Examples:
- `IMPL-2026-01-25-job-management.md`
- `IMPL-2026-01-30-rate-limiting.md`
- `IMPL-2026-02-05-multi-model-support.md`

## Proposal Lifecycle

1. **Draft** - Initial proposal created, under development
2. **Under Review** - Submitted for team review
3. **Approved** - Reviewed and approved, ready for implementation
4. **Rejected** - Not approved, moved to archive/
5. **Implemented** - Completed and merged to main
6. **Superseded** - Replaced by newer proposal, moved to archive/

## Quick Start

1. Copy the template:
   ```bash
   cp docs/IMPLEMENTATION_PROPOSAL_TEMPLATE.md docs/proposals/IMPL-$(date +%Y-%m-%d)-my-feature.md
   ```

2. Fill in the sections (see [PROPOSAL_GUIDE.md](../PROPOSAL_GUIDE.md))

3. Submit for review:
   ```bash
   git checkout -b proposal/my-feature
   git add docs/proposals/IMPL-*-my-feature.md
   git commit -m "Proposal: Add my feature"
   git push origin proposal/my-feature
   # Create PR on GitHub
   ```

## Guidelines

- Read [PROPOSAL_GUIDE.md](../PROPOSAL_GUIDE.md) before creating a proposal
- Use [IMPLEMENTATION_PROPOSAL_TEMPLATE.md](../IMPLEMENTATION_PROPOSAL_TEMPLATE.md) as a starting point
- Keep proposals focused on a single feature or change
- Update proposal status as work progresses
- Move completed/rejected proposals to archive/ after 6 months

## Active Proposals

Currently active proposals:

*None yet - this is the first proposal system setup*

## Archived Proposals

See [archive/](archive/) for historical proposals.

## Resources

- [Implementation Proposal Template](../IMPLEMENTATION_PROPOSAL_TEMPLATE.md)
- [Proposal Guide](../PROPOSAL_GUIDE.md)
- [CIT Architecture](../ARCHITECTURE.md)
- [Copilot Instructions](../../.github/copilot-instructions.md)

## Contact

For questions about the proposal process, open an issue or ask in the PR.
