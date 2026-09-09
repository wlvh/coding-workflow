# PR Submission Checklist

This file is the pre-submission todo. Verify factual items against the current diff, test output, or
repository state, and policy items against valid authorization and policy sources; check only completed
items. `Not applicable` needs grounds for inapplicability; `Not configured` requires confirmation that an
applicable mechanism is unconfigured. Mark insufficient evidence as not yet confirmed. Do not commit, push,
or create a PR unless the user explicitly requests it.

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
  `TESTING.md`, and `SOP.md` according to actual impact. State the current factual or policy basis for affected
  authorities left unchanged; do not edit every document merely for completeness.
- [ ] Existing official user documentation, interface specifications, and accepted policies remain effective
  within their respective scopes. The contract registers selected commitments and boundaries, interact
  explains interaction semantics, and the guide provides usage instructions; filenames do not override
  existing authority.
- [ ] User-visible facts have current implementation or test evidence, and normative policy has valid
  authorization and policy sources. Split mixed statements for verification and check the project's real
  contract/reference mechanism.
- [ ] When a project adopts a contract anchor protocol, reference and validate under that protocol; when it
  uses its own contract/reference mechanism, check that real mechanism or test evidence. Do not invent an
  anchor to satisfy this template, and do not present structural alignment as sentence-level binding or
  proof of capability semantics.
- [ ] Check architecture impact across entrypoints, module boundaries, data flow, state, error models,
  external dependencies, artifacts, and side effects.
- [ ] Replace or delete every active project-fill marker while preserving valid Markdown and JSON.

## Review Closure

- [ ] Complete the review gate required by this project's test and delivery policy, and accurately record
  reviewer identity, scope, and limitations.
- [ ] Bind each review conclusion to the content actually reviewed, such as a diff or commit. After that
  content changes, the prior conclusion is invalid; re-review the affected content.
- [ ] Handle actionable review feedback according to this project's policy. Keep recheck evidence for resolved
  items and record the impact and required decision for anything left open.
- [ ] Open questions resolved by this change have been rewritten as Current behavior in `interact.md`, with
  corresponding behavior tests added. If none apply, state the scope checked.
- [ ] Rerun affected tests and mechanical checks after fixes, then recheck the final diff and Git state.

## PR Delivery

- [ ] Write only completed facts in the PR body and use `.github/pull_request_template.md` for structure.
- [ ] Follow target-project policy for the PR body draft location, publishing tool, and commit treatment;
  never commit a temporary draft accidentally, and keep the body consistent with the real diff and test
  evidence.
- [ ] Use `<base>` or the repository default branch instead of hardcoding a branch name.
- [ ] Create a draft PR only when requested, and reconfirm title, base, head, body, and actual diff first.
