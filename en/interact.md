# User-visible Behavior and Acceptance

## 0. Authority and Scope

`capability_contract.json` is the machine-readable source of truth for capability boundaries. This document
is the source of truth for user-visible behavior and acceptance invariants. `docs/business_user_guide.md`
may only derive explanations from those two sources. Describe only behavior directly observable through a
UI, API response, or other public entrypoint; logs, monitoring, and internal state are not user results.

<!-- project-fill: Describe public entrypoints, scope, and explicit exclusions for this project, then remove this marker. -->

## 1. Audience and Granularity

Write for users, product staff, and acceptance reviewers. Organize by journeys that independently create
user value. Keep one representative for equivalent options, describe composable atomic behavior, and do
not enumerate low-value combinations. Mark future or proposed behavior explicitly.

<!-- project-fill: State the target users and acceptance granularity for this project, then remove this marker. -->

## 2. Supported User Journeys

Every scenario must have current implementation or test evidence and use the fields below. If no journey
is verified, write `Not configured —` with the entrypoints checked and the reason instead of inventing one.

### Scenario

<!-- project-fill: Replace this section with one verified scenario containing User goal, Required context, User action or request, Directly observable result, Failure / degradation / escalation, Acceptance assertion, and capability anchor, then remove this marker. -->

## 3. Cross-cutting User-visible Invariants

Invariants must be directly judgeable by the target reader, trace to the contract through stable capability
anchors, and avoid example values that change with data.

<!-- project-fill: List real cross-journey visible invariants and acceptance evidence. If none exist, write Not applicable with a verified reason, then remove this marker. -->

## 4. Known Limits and Human Escalation

Distinguish currently unsupported behavior, temporary degradation, and future or proposed work. Human
escalation should expose user-recognizable triggers, explanations, and responsible roles without leaking
internal monitoring details.

<!-- project-fill: Add verified limits, degradation, refusal, and human escalation paths with capability anchors. If no path is configured, say so accurately, then remove this marker. -->
