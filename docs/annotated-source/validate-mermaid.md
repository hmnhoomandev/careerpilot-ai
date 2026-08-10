# Annotated Source: Mermaid Validator

Source: `scripts/validate_mermaid.py`

## Purpose

The script validates actual Mermaid grammar by rendering every Markdown fence with
the pinned Mermaid CLI, improving on Phase 0's fence-balance check.

## Logical walkthrough

- The fence regex extracts diagram bodies from repository Markdown.
- Path filtering skips Git, virtual environments, and generated dependencies.
- The script requires the pinned local `mmdc` binary and finds Chrome from an
  explicit environment value, Linux PATH, or the standard macOS location.
- A temporary Puppeteer configuration, Mermaid input, and SVG output keep generated
  artifacts outside the repository.
- `subprocess.run` receives an argument list and a repository-controlled executable
  path; shell parsing is disabled. Ruff's S603 exception is therefore narrow and
  documented.
- The first rendering failure reports its source path and diagram number; success
  reports the exact count.

The script can fail for missing tooling/browser, syntax errors, rendering errors,
or resource limits. CI and local documentation checks exercise it.
