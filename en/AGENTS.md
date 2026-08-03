# Agent Working Guide

## Authority Map

- Current code, configuration, tests, committed artifacts, and reproducible results are project facts.
- `architecture.md` defines system structure and boundaries; `TESTING.md` defines test entrypoints and
  evidence levels; `PR_Checklist.md` defines delivery checks; `SOP.md` keeps only stable process entrypoints.
- `capability_contract.json` defines capability boundaries, `interact.md` defines user-visible behavior and
  acceptance, and `docs/business_user_guide.md` only derives explanations from the first two.
- Existing documents are claims to verify against implementation; they cannot prove themselves correct.

<!-- project-fill: Add other authoritative project sources and conflict precedence, then remove this marker. -->

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

## Change Impact Rules

- Update or confirm `architecture.md` when module boundaries, runtime call flow, data flow, state, error
  model, external dependencies, or extension points change.
- For capability changes, update or confirm `capability_contract.json` first, then inspect `interact.md`
  and the business guide. For user-visible behavior changes, update or confirm `interact.md` first.
- Tests remain factual evidence; keep exact commands, fixtures, layers, and isolation details in
  `TESTING.md` only.
- Not every change requires every document to change. Give a current, evidence-based no-update reason for
  each affected candidate document left unchanged.
- Derive encoding, lint, formatter, build, and type rules from real repository configuration, not this
  template.

## Collaboration

- The primary executor owns final judgments, deliverables, and writes; delegated results must be reviewed
  and synthesized before use.
- Assign non-overlapping path ownership before parallel writes; follow the target project's policy for the
  isolation method.
- Divide work dynamically by module, call flow, risk, or evidence type; do not require a fixed agent count
  or schedule.
- Agreement, voting, or consensus is not evidence. Important conclusions must trace to repository facts and
  reproducible validation.
- Investigation and review tasks are read-only by default; when changes are needed, hand them off explicitly
  to an executor who owns the affected paths.

<!-- project-fill: Add verified project collaboration or ownership rules. If none exist, remove this marker. -->

## Architecture

Treat `architecture.md` as the architecture authority. Rebuild affected call paths from real entrypoints
before a change, then verify invariants, module responsibilities, data contracts, state, side effects, and
failure paths afterward.

## Testing

Read `TESTING.md` completely before testing and derive exact commands from repository configuration. Do not
present light, mock, golden, or local repair success as a higher validation level. Choose the execution
environment from command side effects, CI capabilities, and project policy, with isolation and cleanup
verified before execution.

## SOP

Read the corresponding `SOP.md` entry for a standard process. Keep execution checklists in the current
session; do not create repository run state, receipts, or temporary process documents.

## PR Delivery

- Follow `PR_Checklist.md` and `.github/pull_request_template.md`; write delivery facts from the actual Git
  diff, test output, and final repository state.
- Resolve the default branch from the repository instead of hardcoding it. Follow target-project policy for
  PR body draft location and publishing; never commit temporary drafts accidentally, and keep the body
  consistent with the real diff and test evidence.
- Do not commit, push, or create a PR unless the user explicitly requests it.

## Project-specific Conventions

<!-- project-fill: Derive project conventions from machine enforcement such as lint, formatter, compiler, and build configuration, plus current repository or team instructions and accepted decisions that apply to this scope. Distinguish machine-enforced from owner-declared rules and identify authority, scope, and conflicts checked. Keep personal or session preferences only when explicitly adopted as project policy and persisted in repository authority. If none are verifiable, write None and the configuration and governance scope checked, then remove this marker. -->
