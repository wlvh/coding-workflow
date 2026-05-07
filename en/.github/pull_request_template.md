<!--
PR body principles:

1. Write only facts completed by this PR, not plans.
2. File lists must come from: git diff --name-only <base>...HEAD.
3. Testing strategy and test evidence follow TESTING.md.
4. User-visible changes are checked against interact.md.
5. Architecture changes are checked against architecture.md.
6. Every review / fix round must be recorded in "Review / Fix Record".
-->

## 1. Background and Goal

---

## 2. Implementation

<!--
Explain the core approach and key tradeoffs.
Do not restate every code change.
-->

---

## 3. Change Scope

<!--
Must come from:
git diff --name-only <base>...HEAD

List only files or directories actually changed in this PR.
Do not list files absent from the current patch.
-->

| File / Directory | Change Type | Notes |
|---|---|---|
|  | Added / Modified / Deleted |  |

---

## 4. Documentation Impact

<!--
List affected documents only. If no documents need updates, write: None.

If this PR changes capability boundaries, check capability_contract.json / interact.md / docs/business_user_guide.md.

If this PR changes user-visible behavior, check interact.md and decide whether docs/business_user_guide.md also needs updates.

If this PR changes what business users can ask, how they ask, how they read results, or when they ask a human, check docs/business_user_guide.md.

If this PR adds "can do / cannot do / must ask / must refuse" statements, confirm each has a capability_contract.json anchor_id or a test anchor.
-->

Affected documents:

- None

Notes:

-

---

## 5. User and Architecture Impact

User-visible change:

- Yes / No
- Notes:

Architecture change:

- Yes / No
- Notes:

---

## 6. Review / Fix Record

<!--
Under the one-commit strategy, this section is the fix history.
Update it after every review, fix, or merge-readiness response.
-->

| Round | Source | Issue Summary | Judgment | Result | Evidence |
|---|---|---|---|---|---|
| R0 | Initial submission | N/A | N/A | Initial implementation |  |
| R1 | Codex / Claude / Human |  | Real / Invalid / Defer | Fixed / Won't fix / N/A |  |

---

## 7. Known Limits and Rollback

Known limits:

-

Rollback:

-

---

## 8. Final Self-Check

- [ ] Current branch is not the main branch.
- [ ] Ran `git diff --name-only <base>...HEAD`.
- [ ] Change Scope matches the actual diff.
- [ ] PR body contains no stale drafts, old branch names, or unimplemented plans.
- [ ] Testing and test evidence follow `TESTING.md`.
- [ ] User-visible changes were checked against `interact.md`.
- [ ] Architecture changes were checked against `architecture.md`.
- [ ] Every review / fix round is recorded in "Review / Fix Record".
