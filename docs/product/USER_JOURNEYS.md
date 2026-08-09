# User Journeys

## Journey JRN-001: Evidence-grounded application preparation

1. The user authenticates and enters an isolated personal workspace.
2. The user creates a profile and uploads or records evidence.
3. The system validates, quarantines, parses, and indexes authorized content.
4. The user supplies a job description and optional company information.
5. The system extracts structured requirements and labels untrusted content.
6. Retrieval returns tenant-filtered evidence with source citations.
7. Matching and gap analysis distinguish supported, absent, and uncertain claims.
8. Resume and letter agents produce versioned, cited drafts.
9. Policy checks block unsupported claims and unsafe disclosure.
10. The user edits and approves or rejects each draft.
11. The approved application is tracked; no submission or email occurs.

Expected outcome: a cited, truthful, user-controlled application package.

## Journey JRN-002: Correct information

1. The user opens a profile or derived fact.
2. The UI shows its source and affected derived artifacts.
3. The user corrects the source data.
4. Authorized indexes and caches are invalidated or rebuilt.
5. Audit history records the correction without retaining unnecessary old PII.

## Journey JRN-003: Export and delete

1. The user requests an export or deletion.
2. The system authenticates, authorizes, and requests approval for sensitive
   transfer or destructive action.
3. Export returns a bounded, auditable package through a secure mechanism.
4. Deletion enters a 30-day recoverable window unless immediate deletion applies.
5. Finalization removes source data and propagates to chunks, embeddings, caches,
   replicas, and indexes; minimized audit evidence remains per approved policy.

## Journey JRN-004: Future delegated coach access

1. A job seeker explicitly invites a coach with a purpose and scope.
2. Authorization combines role permissions and candidate-specific attributes.
3. Every coach access and action is audited and visible to the candidate.
4. The candidate can revoke access without deleting their own workspace.

This journey is architectural context only and is not activated initially.

## Journey JRN-005: Failure and recovery

1. A provider, agent node, or worker fails.
2. The UI reports a safe, correlated failure without silent fallback.
3. Idempotent retries or durable recovery continue only within policy and budget.
4. Pending approvals remain valid across restarts or expire explicitly.
5. The user can cancel, retry, or request support and inspect the audit summary.
