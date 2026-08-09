# CareerPilot AI Execution Plans

## Plan format

Every phase plan must state:

1. Objective and approved phase.
2. In-scope requirements and acceptance criteria.
3. Deliverables and expected files.
4. Architecture and security decisions.
5. Privacy, migration, deployment, and cost impact.
6. Risks and mitigations.
7. Automated verification commands.
8. Manual verification steps and expected results.
9. Explicit exclusions.
10. Stop condition and exact next approval command.

Plans are living documents. Update status without erasing decisions or evidence.

## Active plan: Phase 0

**Objective:** establish the complete product-discovery and architecture baseline
without production application code or cloud resources.

### Scope

- Product vision, personas, jobs-to-be-done, journeys, scope, metrics.
- Stable functional and non-functional requirements.
- Domain glossary and conceptual domain model.
- Architecture views, responsibility boundaries, and technology decisions.
- Agent-role classification and production-versus-lab separation.
- Initial STRIDE threat model, privacy assessment, risks, and cost assumptions.
- Durable repository governance, traceability, learning material, and review.

### Verification

- Run the Phase 0 document and requirement-ID validator.
- Run available Markdown and Mermaid checks without installing dependencies.
- Inspect links and the complete Git diff.
- Confirm no production application code or cloud resource exists.

### Exclusions

- Application or agent implementation.
- Dependency installation or workspace scaffolding.
- Database schemas or migrations.
- Cloud projects, APIs, billing, resources, deployments, or live-model calls.
- Phase 1 developer-environment remediation, including Docker Compose.

### Stop condition

Complete `docs/reviews/phase-00-review.md`, summarize the acceptance checklist,
and wait for:

`APPROVE PHASE 0 AND START PHASE 1`
