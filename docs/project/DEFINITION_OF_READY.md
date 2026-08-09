# Definition of Ready

A phase is ready only when:

- The previous phase is accepted with the exact transition command.
- The working tree is clean or existing changes are understood and non-overlapping.
- In-scope requirement IDs and acceptance criteria are identified.
- Scope, exclusions, architecture boundaries, and owner decisions are explicit.
- Required ADRs and upstream contracts have been inspected.
- Data, migration, privacy, security, observability, deployment, and cost impacts
  are assessed.
- Paid services or external mutations have explicit authorization, if applicable.
- Local prerequisites and test environments are available or a safe alternative is
  documented.
- Risks have owners or mitigations.
- Automated and manual verification plans exist.
- Learning objectives and required annotated-source work are identified.
