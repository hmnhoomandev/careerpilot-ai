# Restate durable-effect lab

This standalone project journals a workflow and retryable durable step using the
official local Restate test harness. The harness starts a pinned Restate 1.7.0
container and an ephemeral SDK endpoint; inputs and effects are synthetic.

The Python SDK is MIT licensed. The Restate server uses the Business Source
License 1.1 with an additional-use grant, which is a materially different
boundary requiring license review before any adoption. This lab makes no
production decision: Temporal remains CareerPilot's durable-workflow owner.
