# Testing Flow

Read and follow this guide before submitting any PR or running regression tests. Unless stated otherwise, run commands from the repository root and prefer the project-provided test runner when one exists.

## Testing Philosophy

- Reject tests written only for the sake of tests. Tests should verify behavior and contracts, not implementation trivia.
- Avoid redundancy. If an end-to-end or scenario test already covers a behavior, do not duplicate it with a mock-only unit test unless it gives a much faster feedback loop or covers an edge case the live test cannot cover.
- Keep the suite lean. Regularly remove obsolete tests that no longer provide value.
- Keep tests deterministic. Except for explicit live monitors, tests should not depend on changing production data.
- Keep tests isolated. One test must not depend on another test's order or leftover state.
- Make failures diagnosable. Assertions should explain what was expected and what was observed.
- Keep this document current when test files are added or changed.

## Capability Contract Alignment Tests

When a project uses `capability_contract.json`, `interact.md`, or `docs/business_user_guide.md`, provide a lightweight contract alignment test such as `tests/.../test_capability_contract_alignment.py`.

The test does not verify business logic. It verifies that machine-readable capability contracts and user-readable claims have not obviously drifted.

### anchor_id Extraction

Alignment tests should recursively scan the full `capability_contract.json` tree for objects containing `anchor_id`. Do not hardcode JSON paths, bucket names, array indexes, or the current schema hierarchy.

### Markdown Anchor Syntax

All user-readable documents must reference contract anchors with this exact format:

```text
<!-- capability-anchor: <ANCHOR_ID> -->
```

Rules:

- Do not use variants such as `<!-- anchor: ... -->`, `<!-- ref: ... -->`, or `<!-- contract: ... -->`.
- `<ANCHOR_ID>` must exist in `capability_contract.json`.
- Do not reference JSON paths, array indexes, or schema-internal paths.
- Alignment tests recognize only this syntax.

### What Tests Should Cover

1. `anchor_id` uniqueness.
2. Recursive `anchor_id` extraction.
3. Valid Markdown anchor syntax.
4. No naked placeholder anchors such as `capability-anchor: TODO`.
5. Agent behavior commitments are registered.
6. Not every contract entry must appear in the business guide.
7. Teaching copy style is not a test target.
8. Alignment tests should read local files only and must not call real external services.

### Failure and Warning Rules

- A document references a missing `anchor_id`: fail.
- Duplicate `anchor_id`: fail.
- Naked TODO anchors: fail or high-priority warning.
- Untested behavior with an explicit untested reason: warn, do not fail by default.
- Contract entries missing from the business guide: do not fail unless marked as required for the guide.

## Test Layers and Naming

1. Module-level tests
   - Goal: fast checks for one module's behavior.
   - Naming: `<module_path>/<name>.py` and `tests/<module_path>/test_<name>.py`.
   - These tests should not depend on external services.

2. Contract / scenario / live tests
   - Goal: validate public API contracts, full business scenarios, or external dependencies.
   - Use only when the behavior cannot be covered by faster deterministic tests.

## When to Add or Modify Tests

If a code change fixes a bug not covered by existing tests, add a minimal regression test that reproduces the bug before or with the fix. After the fix, ensure the new test passes in the applicable gate.

Any behavioral code change needs test evidence. If no tests changed, explain why existing tests already cover the behavior and provide rerun evidence.

## Test File Overview

## Recommended Test Gate by Change Type

## Lessons Learned

### Lesson Maintenance Rules

- Add a lesson only when a real defect shows that existing testing guidance could not reliably lead to the right test strategy.
- Update existing lessons by raising abstraction level and clarifying boundaries, not by rewriting them for one implementation detail.
- Merge lessons that describe the same failure mode.
- Delete or rewrite a lesson only when a stronger rule, process, or automation fully replaces it.
- Lessons should guide future testing decisions, not preserve incident chronology.
