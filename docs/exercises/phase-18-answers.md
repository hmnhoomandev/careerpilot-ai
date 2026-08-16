# Phase 18 exercise answers

1. Pod-level network/scheduling or required sidecars can justify GKE. Scale-to-zero and low
   operational ownership favor Cloud Run.
2. The image default protects every runtime; `runAsNonRoot` lets admission/runtime reject a Pod
   that would otherwise start as root. They are complementary layers.
3. HPA adds replicas from metrics, PDB limits voluntary concurrent eviction, and topology spread
   distributes replicas. They do not fix bad code, exhausted regional capacity, dependency
   outages, incorrect metrics or involuntary failures.
4. `database-connection/url` is referenced by API and migration. A real secret must be sourced
   through an approved manager/CSI path; committing a placeholder Secret encourages plaintext,
   unsafe state or accidental use.
5. Verify artifacts, render/policy-check, run the migration Job, roll out the digest, wait for
   status, and run synthetic security/health checks. Roll workload back to a verified digest;
   recover schema forward using the migration runbook.
