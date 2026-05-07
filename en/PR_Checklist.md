# PR Submission Checklist

## Commit / Push Strategy

This project defaults to "one PR, one commit + PR body records review and fix rounds."

Goals:

- Keep public PR history easy to review.
- Avoid making reviewers or LLMs reason from commit timeline noise.
- Use the PR body's Review / Fix Record as the durable review history.

Rules:

1. One PR should normally keep one commit.
2. After every review / fix round, update the PR body's Review / Fix Record first.
3. Merge fixes into the current commit with `git commit --amend`.
4. Push rewritten PR branches with `git push --force-with-lease`; never use bare `git push --force`.
5. Use `.github/pull_request_template.md` as the PR body template.
6. `.github/pull_request_template.md` is a long-term template file; do not submit it directly as the PR body.
7. `PR_BODY.md` is a local temporary PR body draft generated from the template. It is not committed and is important review input.

## Capability Contract and User Documentation Sync

- [ ] If this PR changes `capability_contract.json`, check whether `interact.md` and `docs/business_user_guide.md` need matching updates. If not, explain why in the PR body.
- [ ] If this PR changes "can do / cannot do / must ask / must refuse" claims in `interact.md` or `docs/business_user_guide.md`, confirm those claims anchor to `capability_contract.json`, `interact.md`, or tests.
- [ ] If this PR adds agent behavior commitments such as "must ask", "must refuse", "must not guess", or "must degrade", register a stable `anchor_id` in `capability_contract.json` and add test evidence or an explicit untestable reason.
- [ ] If this PR changes what business users can ask, how they ask, how they read results, or when they ask a human, check `docs/business_user_guide.md`.

## PR Submission Steps

Convert this checklist into a step-by-step todo list before submitting a PR.

Use this fixed flow to avoid submitting the long-term template as the PR body:

```bash
cp .github/pull_request_template.md PR_BODY.md
# Fill PR_BODY.md
gh pr create --title "<title MMDD>" --body-file PR_BODY.md --head <feature-branch> --base master
```

Before submitting:

- [ ] Write a structured summary with background / goal, implementation, and change scope.
- [ ] Confirm the current branch is not the main branch.
- [ ] Inspect local changes with git diff and confirm no intended file is missing.
- [ ] Use `git diff --name-only <base>...HEAD` to verify the PR body's change scope.
- [ ] Use `TESTING.md` as the testing authority: decide whether tests need changes, which tests to run, and how to record evidence.
- [ ] If tests were added or changed, update the test file overview or relevant testing notes in `TESTING.md`.
- [ ] If files were added or changed, update the matching document overview where required.
- [ ] If user-visible behavior changed, update `interact.md` and ensure acceptance evidence covers it.
- [ ] Before the final commit, compare `git diff --name-only <base>...HEAD`, `git status`, and `PR_BODY.md` to ensure the PR body contains no stale drafts, local-only changes, or unimplemented plans.
