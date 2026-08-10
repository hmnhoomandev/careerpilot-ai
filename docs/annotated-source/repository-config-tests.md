# Annotated Source: Repository Configuration Tests

Source: `tests/unit/test_repository_config.py`

## Role and walkthrough

- `ROOT` makes file lookup independent of the command directory.
- `load_yaml` uses `yaml.safe_load` because repository YAML is data, not executable
  Python objects.
- The Compose test pins the pgvector image, asserts loopback-only port exposure,
  and requires explicit password configuration.
- The CI test proves the workflow parses, default permissions remain read-only,
  and the expected backend/frontend jobs exist.

Inputs are trusted committed YAML files. Schema mistakes outside these invariants
can still fail in Docker or GitHub, so later tooling supplements rather than
replaces these tests. Phase 1 also runs `docker compose config --quiet` locally.
