<!--
Write only facts completed by this PR. Derive scope from the actual Git diff, follow TESTING.md for test
evidence, and check user behavior and architecture against interact.md and architecture.md. Do not include
plans, historical drafts, or local uncommitted content.
-->

## 1. Background and Goal

<!-- Explain the problem, goal, linked requirement, and scope explicitly excluded from this PR. -->

## 2. Implementation and Tradeoffs

<!-- Explain the core implementation, key tradeoffs, and rejected alternatives without restating every file diff. -->

## 3. Actual Change Scope

<!-- List actual changes from git diff --name-only <base>...HEAD. Do not keep empty tables or planned files. -->

## 4. Documentation Impact

<!-- List documents actually updated and their evidence. State the current factual basis for affected authorities left unchanged. -->

## 5. User-visible and Architecture Impact

<!-- Describe user-visible and architecture changes separately. If none exist, write None and the evidence checked. -->

## 6. Testing Evidence

- Exact command: Record the command verbatim, or write `Not run`.
- Scope: State the layer, entrypoint, and boundary the command actually proves.
- Result: Record pass, failure, skip, and important counts or errors.
- Not-run reason: Write `Not applicable` when run; otherwise give the concrete reason and risk.
- Environment: Record the actual execution environment, isolation method, side effects, and cleanup result.

## 7. Review / Fix Record

<!-- Record the actual review, actionable feedback, disposition and recheck results, and any open decisions or limits according to this project's delivery policy. -->

## 8. Known Limits, Open Decisions, and Rollback

<!-- Separate known limits, product decisions still open, and executable rollback. Write None when a category is empty. -->

## 9. Final Self-check

- [ ] Actual Change Scope matches the real diff.
- [ ] Test commands, scope, results, and not-run reasons are accurate.
- [ ] User-visible and architecture impact were checked against their authoritative documents.
- [ ] Actionable review feedback required by this project is handled or explicitly recorded as open.
- [ ] The PR body contains no historical draft, unimplemented plan, or wrong base/head.
