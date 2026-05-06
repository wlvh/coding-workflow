## Document Relationships

`capability_contract.json` is the machine-readable source of truth for capability boundaries. It answers whether the system can do something.

`interact.md` is the source of truth for user-visible behavior and acceptance invariants. It answers how the system must behave while doing it.

`docs/business_user_guide.md` is the derived teaching document for first-time business users. It answers how business users can start.

When these documents disagree:

1. Capability boundaries follow `capability_contract.json`.
2. User-visible behavior follows `interact.md`.
3. `docs/business_user_guide.md` must be corrected from the first two documents.

## Writing Rules

Any user-visible statement about "can do / cannot do / must ask / must refuse" should reference a stable `anchor_id` from `capability_contract.json` through a hidden Markdown anchor.

Hidden anchors reference stable `anchor_id` values only. They must not reference JSON paths, array indexes, or schema-internal paths.

## 1. Positioning

- Capability groups should follow user mental models, not code modules.
- User experience and acceptance should describe what the user can do, what the user can see, and what value the user receives.

## 2. Audience

Write for ordinary users, PMs, and business stakeholders. Describe only user-visible behavior; do not explain engineering details or implementation.

## 3. Boundaries

- Documentation may lead code only when status is explicit. To prevent code from leading documentation, the PR checklist must require every user-visible behavior change to update `interact.md`.
- Acceptance should be written as invariants, not data-dependent exact values.
- This document is an entrypoint, not an exhaustive authority list.
- Critical failure paths are manually curated. A tasteful PM should decide which failures are exposed to users and which are hidden or degraded.
- Narrative matters: do not write cold click-by-click UI traces. Explain what problem the user is solving, where they go, what they do, and what result they obtain.
- Visibility matters: every example must be directly verifiable through UI or API response. Log-only, monitoring-only, or internal-code state does not belong here.
- Falsifiability matters: each statement should include a concrete acceptance assertion that non-technical users can judge.

## Granularity

The granularity standard for `interact.md` is "what a PM would demo to a CEO." The CEO does not care about every dropdown combination; the CEO cares whether the core business flow works and feels right.

- Equivalence class principle: if ten options share the same business logic, write one representative case.
- Orthogonality principle: describe composable atomic capabilities, not every combination.
- Independent value principle: write a scenario only when it independently answers what value the user receives.

## Examples

```text
# Worth writing
A user wants to understand the escalation trend over the last 30 days.
They enter the Flow Analysis page, select a time range, and see escalation rate
fall from 12% to 8%, supporting the judgment that recent improvements worked.

# Not worth writing
A user opens the Country dropdown, chooses United States, and the dropdown closes.
```

## 4. User-Visible Invariants
