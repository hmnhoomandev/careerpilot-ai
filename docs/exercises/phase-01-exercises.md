# Phase 1 Exercises

Try these before reading the answers.

1. Explain why `uv.lock` is committed while `.venv` is ignored.
2. Add a hypothetical `sqlalchemy` import to `packages/core` mentally. Which test
   should fail, and why is that better than waiting for code review?
3. Explain why `uv sync --all-packages --locked` is required in this workspace.
4. Identify the difference between the Docker CLI, Compose plugin, and daemon.
5. Explain why `.env.example` may be committed but `.env` must not be.
6. Why does CI use read-only default GitHub permissions?
7. Why is Semgrep isolated from the normal audited Python environment?
8. What does a passing unit test prove that a successful Next.js build does not?
