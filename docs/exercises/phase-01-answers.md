# Phase 1 Exercise Answers

1. The lockfile is a portable exact dependency resolution. `.venv` contains
   machine-specific generated installs and is reproducible from the lockfile.
2. `test_core_does_not_import_outward_dependencies` fails with the source path and
   forbidden module. Automated enforcement catches drift on every change.
3. Root sync alone installs default root dependencies but may omit member runtime
   dependencies. `--all-packages` installs the API and core members consistently.
4. The CLI sends Docker commands, Compose interprets multi-container definitions,
   and the daemon actually creates containers. Installing one does not start the
   others.
5. The example documents variable names and safe defaults. `.env` contains local
   credentials or configuration and is ignored to prevent disclosure.
6. A compromised action cannot write repository contents unless a job explicitly
   grants the narrow permission it needs.
7. Current Semgrep pins an MCP version with advisories. Only the local SAST command
   is needed, so an isolated group avoids contaminating the normal environment and
   never exposes the unused MCP server.
8. The unit test proves a specific rendered semantic behavior. The build proves
   compilation and production bundling but does not assert intended content.
