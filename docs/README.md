# CIT Documentation Index

Welcome to the CIT documentation! This index helps you find the right documentation for your needs.

## Quick Links

- [README](../README.md) - Project overview and quick start
- [Architecture](ARCHITECTURE.md) - System architecture and design
- [Proposal Guide](PROPOSAL_GUIDE.md) - How to create implementation proposals

## Documentation Structure

### Getting Started
- [README.md](../README.md) - Main project documentation
  - Installation and setup
  - Quick start guide
  - API examples
  - Web UI overview

- [README_DEPLOY.md](../README_DEPLOY.md) - Deployment guide (Ukrainian)
  - System overview
  - Technologies used
  - Deployment instructions
  - Vercel configuration

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
  - Component overview
  - Data flow
  - Security considerations
  - Versioning

- [LEGEND_CI.md](../LEGEND_CI.md) - Conceptual framework
  - Ci philosophy
  - Core principles
  - System vision

### API Documentation
- [API_ANALYSIS_SUMMARY.md](API_ANALYSIS_SUMMARY.md) - API analysis
- [UNIFIED_API.md](UNIFIED_API.md) - Unified API specification

### Development Process
- [PROPOSAL_GUIDE.md](PROPOSAL_GUIDE.md) - **Implementation proposal guide**
  - When to write proposals
  - Step-by-step guide
  - Review guidelines
  - Common mistakes
  - Templates for common scenarios

- [IMPLEMENTATION_PROPOSAL_TEMPLATE.md](IMPLEMENTATION_PROPOSAL_TEMPLATE.md) - **Proposal template**
  - Complete template with all sections
  - Use as starting point for new proposals
  - Includes examples and placeholders

- [proposals/](proposals/) - Active and archived proposals
  - [proposals/README.md](proposals/README.md) - Proposal directory index
  - [proposals/EXAMPLE-request-id-tracking.md](proposals/EXAMPLE-request-id-tracking.md) - Example proposal
  - [proposals/archive/](proposals/archive/) - Archived proposals

### Releases & Changes
- [RELEASE_v2.1.md](RELEASE_v2.1.md) - v2.1 release notes
  - New features
  - Changes
  - Migration guide

- [CHANGELOG.md](../CHANGELOG.md) - Change history
  - Version history
  - Notable changes

### Configuration & Deployment
- [VERCEL_SETUP.md](VERCEL_SETUP.md) - Vercel deployment setup
  - Configuration guide
  - Environment variables
  - CI/CD setup

- [SECURE_ACCESS.md](SECURE_ACCESS.md) - Security configuration
  - Access control
  - Authentication
  - Best practices

### System Operations
- [HOME_NODE_NODES_REGISTRY.md](HOME_NODE_NODES_REGISTRY.md) - Node registry
- [HOME_NODE_PASSPORT_SAMSUNG.md](HOME_NODE_PASSPORT_SAMSUNG.md) - Device passport

## Documentation by Role

### For New Contributors
1. Start with [README.md](../README.md)
2. Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. Review [.github/copilot-instructions.md](../.github/copilot-instructions.md)
4. Check [PROPOSAL_GUIDE.md](PROPOSAL_GUIDE.md) before making changes

### For Developers
- [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the system
- [PROPOSAL_GUIDE.md](PROPOSAL_GUIDE.md) - Plan your changes
- [IMPLEMENTATION_PROPOSAL_TEMPLATE.md](IMPLEMENTATION_PROPOSAL_TEMPLATE.md) - Document your design
- [proposals/](proposals/) - See examples and active work

### For Reviewers
- [PROPOSAL_GUIDE.md](PROPOSAL_GUIDE.md) - Review guidelines section
- [proposals/](proposals/) - Proposals under review
- [.github/copilot-instructions.md](../.github/copilot-instructions.md) - Project rules

### For DevOps/Deployment
- [README_DEPLOY.md](../README_DEPLOY.md) - Deployment overview
- [VERCEL_SETUP.md](VERCEL_SETUP.md) - Vercel configuration
- [SECURE_ACCESS.md](SECURE_ACCESS.md) - Security setup

## Documentation Standards

### File Naming
- Use SCREAMING_CASE for major docs: `ARCHITECTURE.md`, `PROPOSAL_GUIDE.md`
- Use kebab-case for proposals: `IMPL-2026-01-25-feature-name.md`
- Use descriptive names: `VERCEL_SETUP.md` not `SETUP.md`

### Structure
- Start with clear title and metadata
- Include table of contents for long docs (>500 lines)
- Use consistent heading hierarchy (H1 for title, H2 for sections)
- Provide examples and code samples
- Keep language clear and concise

### Maintenance
- Update docs when code changes
- Mark deprecated docs clearly
- Archive old docs to preserve history
- Review docs quarterly for accuracy

## Contributing to Documentation

### Improving Existing Docs
1. Create a branch: `git checkout -b docs/improve-architecture`
2. Make your changes
3. Submit PR with clear description of improvements

### Adding New Documentation
1. Check if topic fits in existing doc
2. If new doc needed, follow naming conventions
3. Add entry to this index
4. Link from related documents
5. Submit PR for review

### Writing Style Guide
- **Be clear:** Use simple language, avoid jargon
- **Be concise:** Get to the point quickly
- **Be helpful:** Include examples and common pitfalls
- **Be accurate:** Test all code examples
- **Be consistent:** Follow existing doc patterns

## Related Resources

### External Documentation
- [Python Documentation](https://docs.python.org/3/) - Python stdlib reference
- [Next.js Documentation](https://nextjs.org/docs) - Web framework docs
- [OpenAI API Documentation](https://platform.openai.com/docs) - OpenAI API reference

### Project Resources
- [GitHub Repository](https://github.com/Ihorog/cit)
- [ciwiki Repository](https://github.com/Ihorog/ciwiki) - Canonical source of truth
- [Issues](https://github.com/Ihorog/cit/issues) - Bug reports and feature requests

## Getting Help

- Check this documentation index first
- Search existing issues on GitHub
- Read the [PROPOSAL_GUIDE.md](PROPOSAL_GUIDE.md) for process questions
- Review [.github/copilot-instructions.md](../.github/copilot-instructions.md) for development rules

---

**Last Updated:** 2026-01-25  
**Maintained By:** CIT Development Team

*This index is a living document. If you notice missing or outdated information, please submit a PR.*
