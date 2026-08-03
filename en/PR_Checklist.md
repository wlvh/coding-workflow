# PR Submission Checklist

This file is the pre-submission todo. Check only items proven by the current diff, test output, or repository
state; record a reason when an item does not apply. Do not commit, push, or create a PR unless the user
explicitly requests it.

<!-- project-fill: Add project-specific approval, commit, base/head, or release gates. Remove this marker when no project-specific rule applies. -->

## Scope and Git State

- [ ] Resolve `<base>` from the repository default branch and confirm the current and target branches.
- [ ] Inspect `git status`, working-tree diff, staged diff, and `git diff --name-only <base>...HEAD`.
- [ ] Ensure actual scope matches delivery notes and excludes local drafts, secrets, generated debris, and
  unimplemented plans.
- [ ] Treat a one-commit policy as a replaceable team default when the project uses one; otherwise follow
  current repository policy. Rewriting remote history requires explicit authority and lease protection.

## Tests and Evidence

- [ ] Select real commands from `TESTING.md` and current repository configuration; do not infer a runner or
  service from a template.
- [ ] Ensure the decision to add or not add tests follows `TESTING.md` section 4; with no test diff, cite a
  specific covering test and rerun evidence.
- [ ] For each test, record exact command, scope, result, not-run reason, actual environment, and isolation
  method.
- [ ] Ensure environment choice follows command side effects, CI capabilities, and project policy, with
  verifiable records for writes, external state, residue, and cleanup.
- [ ] Describe failures, skips, and validation level accurately; do not present light, golden, or repair
  evidence as full validation.

## Documentation and Contracts

- [ ] Check `AGENTS.md`, `architecture.md`, `capability_contract.json`, `interact.md`, the business guide,
  `TESTING.md`, and `SOP.md` according to actual impact. Give a real no-update reason for affected candidates
  left unchanged; do not edit every document merely for completeness.
- [ ] Keep the authority direction `capability_contract.json → interact.md → business_user_guide.md` for
  capability changes. User-visible claims have current implementation or test evidence and stable anchors.
- [ ] Reference Markdown anchors through the capability contract's contract-defined protocol without copying
  its token here; do not present alignment as sentence-level binding or proof of capability semantics.
- [ ] Check architecture impact across entrypoints, module boundaries, data flow, state, error models,
  external dependencies, artifacts, and side effects.
- [ ] Replace or delete every active project-fill marker while preserving valid Markdown and JSON.

## Review Closure

- [ ] Complete the review gate required by this project's test and delivery policy, and accurately record
  reviewer identity, scope, and limitations.
- [ ] Fix every BLOCKER and actionable WARN that does not require a new product decision. Keep remaining
  issues in open decisions with evidence and impact.
- [ ] Preserve material rounds, REOPENED findings, and SUPERSEDED candidates or evidence. Reopening keeps the
  original finding ID, and finding state is not confused with evidence state.
- [ ] Support a prior miss explanation with evidence or label it `hypothesis` / `unknown`; never invent cause
  merely to fill a field.
- [ ] Evaluate every material finding for promotion to a long-term rule or automated gate, and record why when
  it is not promoted.
- [ ] Rerun affected tests and mechanical checks after fixes, then recheck the final diff and Git state.

## PR Delivery

- [ ] Write only completed facts in the PR body and use `.github/pull_request_template.md` for structure.
- [ ] Follow target-project policy for the PR body draft location, publishing tool, and commit treatment;
  never commit a temporary draft accidentally, and keep the body consistent with the real diff and test
  evidence.
- [ ] Use `<base>` or the repository default branch instead of hardcoding a branch name.
- [ ] Create a draft PR only when requested, and reconfirm title, base, head, body, and actual diff first.
