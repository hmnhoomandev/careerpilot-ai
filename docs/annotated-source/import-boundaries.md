# Annotated Source: Import Boundary Test

Source: `tests/architecture/test_import_boundaries.py`

## Role

The shared `uv` environment can make any installed import technically available.
This test protects the architectural rule that framework-independent core code
cannot depend outward on adapters or provider SDKs.

## Logical walkthrough

- `ROOT` and `CORE_SOURCE` locate the repository and exact core source tree.
- `FORBIDDEN_CORE_PREFIXES` records outward packages. It is intentionally explicit
  and grows when new adapters/providers arrive.
- `imported_modules` parses source with Python's AST instead of fragile text
  matching. It collects absolute `import` and `from` statements while ignoring
  relative imports internal to the package.
- The architecture test examines every core Python file, builds readable
  violations, and reports them together.

## Inputs, outputs, failures, and testing

Input is trusted repository source. Output is a passing test or a list of path and
module violations. Invalid Python also fails during AST parsing, which is useful.
The test itself executes in the Phase 1 Pytest suite.

## Rejected alternative

Separate virtual environments alone would increase setup cost and still would not
express domain dependency intent. A future architecture tool may extend this AST
check, but the small explicit test is sufficient for the current two packages.
