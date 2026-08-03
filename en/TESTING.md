# Testing

## 0. Canonical Test Entrypoints

Derive every exact command from current repository scripts, task configuration, CI, build files, or test
framework configuration, and verify it from the repository root or a recorded working directory. Do not
infer a language, runner, service, or phase from this template.
Prefer a verified repository-owned unified entrypoint when one exists and record what it actually covers;
otherwise, do not create a wrapper only to satisfy this template. Review a wrapper as a separate project
change only when repeated multi-command orchestration, service lifecycle, or cleanup steps provide independent
maintenance value.

<!-- project-fill: List executable test commands, working directories, environment prerequisites, and scope from the current repository, then remove this marker. -->

## 1. Testing Philosophy

- Test behavior, contracts, and failure boundaries without locking in implementation details that have no
  user value.
- Each new test should cover a real gap. A higher-level test does not automatically make a fast,
  diagnosable lower-level regression redundant.
- Use fixed inputs by default instead of changing production data. Mark live tests with their external
  dependencies and risks.
- Keep tests isolated from order and residual state, and make failures explain expected versus actual
  behavior.
- Record scope and reason accurately when a test is not run, skipped, or limited to static checks; do not
  infer a pass.

## 2. Test Layers and What Each Proves

- **Unit**: proves local behavior of one function, class, or module under isolated input.
- **Contract**: proves a public schema, interface, file format, or cross-module agreement.
- **Scenario**: proves a user or caller path through multiple real components.
- **Golden**: proves reviewed output for deterministic input; it does not alone prove external systems or
  the complete runtime chain.
- **Report build**: proves a report or deliverable can be generated; it does not automatically prove
  business correctness.
- **Repair validation**: proves a repaired artifact satisfies a specific gate; it does not prove every
  upstream phase is correct.
- **Light review**: proves only the limited scope its implementation checks; never describe it as full
  validation.
- **Full validation**: use this name only when the complete target path, dependencies, and acceptance
  boundary are actually covered.
- **Live**: proves one run against real external dependencies; record environment, time sensitivity, and
  reproducibility risk.

## 3. Capability Contract Alignment

An alignment test belongs to the target project's test suite, not the documentation sync checker. It
should recursively collect stable `anchor_id` values from every object in `capability_contract.json` and
use the protocol defined by the contract rules to check uniqueness and Markdown references without
hardcoding buckets, JSON paths, array positions, or requiring every contract entry to appear in the
business guide.

When `test_anchor: null` is explicit, record both a nonempty, concrete `untested_reason` and a nonempty
`pending_since`; register the real test anchor when a test exists. Anchor alignment proves only mechanical
facts such as a structural reference, a valid ID, and no dangling target. It does not by itself prove
sentence-level binding or that claim semantics are implemented. Before claiming an alignment test exists,
verify its implementation and command in the target repository.

<!-- project-fill: Cite the target project's real alignment test, command, and scope. If it is not implemented, write Not configured and the reason, then remove this marker. -->

## 4. Change Type to Required Evidence

1. For a safely and deterministically reproducible escaped bug, establish the smallest regression test or
   fixture that fails before the fix, then change the implementation.
2. When a test cannot establish a failing test first, preserve pre-fix failure evidence and state why stable
   automation is unavailable and what risk remains.
3. For user-visible behavior, public contract, or schema changes, add or update the nearest-boundary contract
   or scenario test by default.
4. With no test diff, identify the specific existing test that covers the new risk and provide rerun evidence;
   “an existing high-level test” is not sufficient.
5. A behavior-preserving internal refactor may add no test, but rerun affected paths and record the
   no-test-change reason.
6. A documentation-only gate proves only the structure, parsing, or alignment it actually checks; it is not
   runtime behavior validation.

<!-- project-fill: Map code, configuration, schema, user behavior, artifact, and documentation changes to evidence levels using actual project risk, then remove this marker. -->

## 5. Side Effects and Isolation

Before running a command, identify its write paths, external services, credentials, concurrency, ordering,
cleanup, and CI policy, then choose an environment that isolates those real side effects. The environment
may be CI, a container, a separate checkout, a remote test environment, or another project-validated
execution surface; this template does not prescribe one implementation. Record the actual environment,
isolation method, residual state, and cleanup result.

<!-- project-fill: Identify side effects, actual isolation environment, cleanup, and selection rationale for each project command, then remove this marker. -->

## 6. Test Suite Overview

Describe stable test directories, entrypoints, and responsibilities instead of permanently listing every
test file.

<!-- project-fill: Summarize the real test suites, important fixtures, external dependencies, and recommended entrypoints, then remove this marker. -->

## 7. Known Gaps and Untested Reasons

<!-- project-fill: List current coverage gaps, risk, owner, or trigger. If none are known, write None and the verified scope, then remove this marker. -->

## 8. Lessons Learned

Record reusable test-decision rules supported by real failures, not incident chronology or volatile
commands. If a failure came from layers passing independently while their combination failed, keep both a
minimal regression and a scenario test that crosses the real boundary.
Merge the same failure mode into a more general rule. Retire it only when a stronger test, automated gate,
or authoritative rule fully carries the knowledge, never merely because the example is old.

<!-- project-fill: Add lessons supported by real failures and not replaced by stronger rules or automation. If none exist, write None, then remove this marker. -->
