# User-visible Behavior and Acceptance

## 0. Authority and Scope

Existing official user documentation, interface specifications, and accepted policies remain effective
within their respective scopes. `capability_contract.json` registers selected public commitments and
boundaries; this document explains interaction semantics and acceptance; `docs/business_user_guide.md`
provides usage guidance. Generated documents do not override existing authority by filename. Check
descriptive facts against current implementation evidence and normative policy against valid authorization
and policy sources; split mixed statements. Describe only behavior directly observable through a UI, API
response, or other public entrypoint; logs, monitoring, and internal state are not user results.

<!-- project-fill: Describe public entrypoints, this document's scope and exclusions, and cite official documentation, interface specifications, and policy sources effective within their respective scopes, then remove this marker. -->

## 1. Audience and Granularity

Write for users, external calling agents, product staff, and acceptance reviewers. Organize by journeys
that independently create user value. Keep one representative for equivalent options, describe composable
atomic behavior, and do not enumerate low-value combinations. Mark future or proposed behavior explicitly.

<!-- project-fill: State the target users and acceptance granularity for this project, then remove this marker. -->

## 2. Current behavior

Each scenario's current behavior must have implementation or test evidence and use the fields below.
Observed behavior does not automatically become a long-term support commitment; support or refusal policy
needs its own basis. If a scenario is not yet verified, state the entrypoints checked and the evidence gap.
Use `Not configured` only when an applicable entrypoint is confirmed to be unconfigured, and
`Not applicable` only when it is confirmed not to apply.

### Scenario

<!-- project-fill: Replace this section with one verified scenario containing User goal, Required context, User action or request, Directly observable result, Failure / degradation / escalation, Acceptance assertion, and the applicable real contract/reference mechanism or test evidence, then remove this marker. -->

## 3. Cross-cutting User-visible Invariants

Invariants must be directly judgeable by the target reader: if the project adopts a capability-contract
anchor protocol, use its canonical anchors; if it has its own contract/reference mechanism, use that real
mechanism or verifiable test evidence. Do not invent an anchor registry to satisfy this template, and avoid
example values that change with data.

<!-- project-fill: List real cross-journey visible invariants and acceptance evidence. If none exist, write Not applicable with a verified reason, then remove this marker. -->

## 4. Known Limits and Human Escalation

Distinguish support policies with a verified basis, current implementation limits, temporary degradation,
and future or proposed work. Current execution does not imply a promise that behavior will remain the same. Human
escalation describes only confirmed, user-recognizable triggers, visible explanations, and responsible
roles; do not expose internal monitoring details or invent owners or procedures.

<!-- project-fill: Add verified limits, degradation, refusal, and human escalation paths with the applicable real contract/reference mechanism or test evidence. If no path is configured, say so accurately, then remove this marker. -->

## 5. Combination Behavior

When multiple capabilities affect one user-visible result, first check whether existing rules determine
their combined behavior. Shared objects, state, resources, or priorities are investigation prompts, not
automatic escalation triggers. Register an Open question only when facts are established and a substantive
semantic disagreement remains beyond current authorization. When existing rules determine the result,
document Current behavior and validate it directly.

<!-- project-fill: Record important combinations that actually affect the same observable result in this project, their applicable existing rules, and behavior evidence. Do not enumerate low-value combinations. If none apply, state the scope checked and the reason, then remove this marker. -->

## 6. Open questions

Not every project needs an unresolved question. A decision not found does not mean maintainers never made
one; investigate existing rules and current authorization before deciding that a decision is needed.

<!-- project-fill: Keep and complete the four parts below only for a real question meeting the conditions above. If none exist, remove the question skeleton and state the scope checked, then remove this marker. -->

### Question title

Current evidence:
Evidence checked, distinguishing implementation observations from policy sources.

Current behavior / safe boundary:
What callers can actually observe now, and which behavior is not yet confirmed to be dependable.

Decision:
An existing Issue or decision entrypoint; if none was found, say so without inventing an owner or process.

Close when:
Once the decision is implemented, rewrite it as Current behavior and add corresponding behavior tests.

## 7. Interface Entrypoints

Users and external calling agents should start with real public interfaces and their official references.
Internal functions, incidental behavior, and plans do not become official capabilities by being documented
here. This page supplements interaction semantics without replacing interface specifications.

<!-- project-fill: Link to this project's real API, CLI, or protocol and official interface references, identifying scope. Give separate grounds for no such interface, an unconfigured reference, or an entrypoint not yet confirmed, then remove this marker. -->
