# Agent Working Guide

## Authority Map

- Check descriptive facts against current code, configuration, tests, committed artifacts, and reproducible
  results. Check normative policy against valid project authorization and policy sources; split mixed
  statements. Documents cannot independently prove their own factual claims.
- Existing official user documentation, interface specifications, and accepted policies remain effective
  within their respective scopes. Generated documents do not override existing authority by filename;
  resolve conflicts through the project's existing scope and supersession rules.
- `architecture.md` defines system structure and boundaries; `TESTING.md` defines test entrypoints and
  evidence levels; `PR_Checklist.md` defines delivery checks; `SOP.md` keeps only stable process entrypoints.
- `capability_contract.json` registers selected public commitments and boundaries; `interact.md` explains
  interaction semantics; `docs/business_user_guide.md` provides usage guidance and navigation to official
  interfaces. Each respects the authority scopes above.

<!-- project-fill: List existing official project documentation, interface specifications, and policy sources, with their respective scopes and existing conflict-resolution rules, then remove this marker. -->

## Task Routing

Choose an entrypoint for the current task, then follow relevant evidence. Do not require all nine documents
to be read in full for every task.

| Task | Start with | Then verify |
|---|---|---|
| Local fix or internal implementation | `TESTING.md` | Relevant implementation and existing tests |
| User-visible behavior change | `interact.md`, `TESTING.md` | Official interfaces, failure paths, and behavior tests |
| Public capability or data agreement change | `capability_contract.json`, `architecture.md`, `interact.md` | Corresponding implementation, callers, and validation |
| Shared component change | `architecture.md`, `TESTING.md` | Entrypoints using that component and relevant regressions |
| Project use or external invocation | `docs/business_user_guide.md`, official interface references | Actual API, CLI, or protocol |
| Merge or release | `PR_Checklist.md`, PR template | Actual diff, tests, and documentation |
| Unresolved public semantics | Open questions in `interact.md`, related Issue | Existing rules, current authorization, and project decisions |

- Facts are unclear: continue investigating.
- Internal implementations differ but external behavior is equivalent: choose the simplest approach that
  fits the project's style.
- Facts are established, but a substantive disagreement about public semantics remains beyond current
  authorization: ask the maintainer/owner a concrete question.

Maintain propagation relationships only in
[Change propagation in architecture.md](architecture.md#change-propagation). Investigate relevant
relationships and find the corresponding validation in `TESTING.md`. Update affected content only; for an
affected document left unchanged, state its factual or policy basis in delivery notes. Derive encoding,
lint, formatter, build, and type rules from real repository configuration, not this template.

`Not applicable` means verified inapplicability; `Not configured` means an applicable mechanism has not been
configured; not yet confirmed means insufficient evidence. These are not interchangeable. State the scope
checked and the reason; never present insufficient evidence as inapplicability.

## Repository Overview

Describe stable modules, entrypoints, and responsibilities. Do not permanently mirror `git ls-files`.

### Core Configuration

<!-- project-fill: List real configuration entrypoints and responsibilities. If none apply, write Not applicable with a verified reason, then remove this marker. -->

### Runtime Entrypoints

<!-- project-fill: List real user, service, job, or CLI runtime entrypoints, then remove this marker. -->

### Core Modules

<!-- project-fill: Summarize core implementation by stable module boundaries, not individual files, then remove this marker. -->

### Domain Logic

<!-- project-fill: Identify modules containing domain rules and their authoritative tests or contracts, then remove this marker. -->

### Generated Artifacts and External State

<!-- project-fill: List committed or generated artifacts, persisted state, and external systems. If none exist, write Not applicable with a verified reason, then remove this marker. -->

## Collaboration

- The primary executor owns final judgments, deliverables, and writes; delegated results must be reviewed
  and synthesized before use.
- Assign non-overlapping path ownership before parallel writes; follow the target project's policy for the
  isolation method.
- Divide work dynamically by module, call flow, risk, or evidence type; do not require a fixed agent count
  or schedule.
- Agreement, voting, or consensus is not evidence. Important conclusions must trace to the corresponding
  factual evidence or valid policy sources.
- Investigation and review tasks are read-only by default; when changes are needed, hand them off explicitly
  to an executor who owns the affected paths.

<!-- project-fill: Add verified project collaboration or ownership rules. If none exist, remove this marker. -->

## Architecture

Read `architecture.md` within its stated scope and follow the existing specifications it references.
Rebuild affected call paths from real entrypoints before a change, then verify invariants, module
responsibilities, data contracts, state, side effects, and failure paths afterward.

## Testing

Read `TESTING.md` completely before testing and derive exact commands from repository configuration. Do not
present light, mock, golden, or local repair success as a higher validation level. Choose the execution
environment from command side effects, CI capabilities, and project policy, with isolation and cleanup
verified before execution.

## SOP

Read the corresponding `SOP.md` entry for a standard process. Follow this project's actual audit,
recoverability, and delivery policy for whether execution records are stored, where, and for how long.

## PR Delivery

- Follow `PR_Checklist.md` and `.github/pull_request_template.md`; write delivery facts from the actual Git
  diff, test output, and final repository state.
- Resolve the default branch from the repository instead of hardcoding it. Follow target-project policy for
  PR body draft location and publishing; never commit temporary drafts accidentally, and keep the body
  consistent with the real diff and test evidence.
- Do not commit, push, or create a PR unless the user explicitly requests it.

## Project-specific Conventions

<!-- project-fill: Derive project conventions from machine enforcement such as lint, formatter, compiler, and build configuration, plus current repository or team instructions and accepted decisions that apply to this scope. Distinguish machine-enforced from owner-declared rules and identify authority, scope, and conflicts checked. Keep personal or session preferences only when explicitly adopted as project policy and persisted in repository authority. If none are verifiable, write None and the configuration and governance scope checked, then remove this marker. -->
