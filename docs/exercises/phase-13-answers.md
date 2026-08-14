# Phase 13 exercise answers

1. Publish acknowledgement covers broker acceptance only; downstream processing is separate.
2. The consumer-specific inbox receipt keyed by event ID makes the second delivery a no-op.
3. The sequence cursor detects the gap; after sequence 1 succeeds, replay can accept sequence 2.
4. A digest supports correlation without retaining possibly sensitive or hostile content.
5. Show a measured cross-runtime need for Dapr. For Pub/Sub, document region availability,
   IAM, security/privacy, retention, latency, quota, cost, and explicit owner approval.
