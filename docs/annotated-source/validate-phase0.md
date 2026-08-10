# Annotated Source: Phase 0 Validator

Source: `scripts/validate_phase0.py`

## Purpose and architectural role

The validator turns part of the Phase 0 acceptance contract into a repeatable,
CHF 0 check. It uses only the Python standard library, makes no network calls, and
does not validate production behavior.

## Logical walkthrough

- The module docstring names the narrow documentation-validation purpose.
- `Path`, `re`, and `sys` provide filesystem discovery, pattern matching, and an
  observable process exit code.
- `ROOT` derives the repository root from the script location, so execution does
  not depend on the caller's current directory.
- `REQUIRED_FILES` encodes the minimum durable baseline. A missing entry fails the
  phase check rather than relying on memory.
- `REQUIREMENT_RANGES` defines the accepted stable ID sequences. The loop proves
  no number was accidentally skipped.
- Markdown discovery excludes generated dependency and build directories, then
  checks that each repository document begins with one H1, Mermaid fences are
  balanced, local Markdown links resolve, and simple credential-assignment
  patterns do not appear.
- Errors are accumulated so one run teaches everything that needs correction.
- Success prints exact counts; failure prints each finding and exits nonzero.
- The `__main__` guard makes the module executable while leaving its `main`
  function directly testable in a later tooling-test phase.

## Inputs and outputs

Input is the repository filesystem. Output is a concise stdout report and process
status: zero for success, one for any structural error.

## Failure modes and tests

Unreadable files raise an explicit Python error. Missing documents, requirement
IDs, headings, fences, local links, or suspected secret literals return a
controlled failure. Phase 0 executes the validator as its automated evidence;
future phases may add unit fixtures if the script grows.

## Rejected alternative

A third-party Markdown/link tool would provide richer validation but would add a
dependency during a documentation-only phase and may require a network download.
Phase 1 will establish pinned repository-wide tooling. The custom check is kept
narrow so it does not pretend to replace a full Markdown parser or Mermaid CLI.
