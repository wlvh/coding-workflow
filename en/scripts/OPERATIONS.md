# Workflow Docs Sync - English Runbook

[中文](../../zh/scripts/OPERATIONS.md) | English

This runbook is the English-derived operations entrypoint. Chinese documents
remain the anchor. The English sync path reads source templates under `en/`
and installs them into canonical target paths such as `AGENTS.md`,
`TESTING.md`, and `.github/pull_request_template.md`.

Each run writes machine evidence to `.coding_workflow/diffs/agent_workorder.md`,
`sync_state.json`, and `PR_BODY.md`. Treat those generated files as the current
run's evidence.

---

## 1. Quick Start

Run English workflow docs sync from the target repository root:

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/en/scripts/sync.sh | bash
```

Before running:

- Do not mix non-sync code, config, or test dirty changes into the target repo.
- If rerunning within the same sync cycle, only core docs, `.gitignore`,
  `PR_BODY.md`, and `.coding_workflow/diffs/` may be dirty.
- If `PR_BODY.md` is not a sync sentinel body, ordinary sync fails fast. Move it,
  delete it, or manually migrate useful text into the agent-owned sync sections.
- If sync warns that `PR_BODY.md` is tracked, do not fix that inside the sync
  flow. Use a separate cleanup PR if the target project wants it untracked.

Ordinary sync outputs:

- `.coding_workflow/diffs/agent_workorder.md`: run-specific machine facts and this runbook's pinned raw URL.
- `.coding_workflow/diffs/pr_body_skeleton.md`: initial sync PR body skeleton when `PR_BODY.md` does not exist.
- `.coding_workflow/diffs/sync_state.json`: machine state used by final gate.
- `.coding_workflow/diffs/upstream_full/`: local mirror of upstream English templates and prompts.

After ordinary sync succeeds, copy PASS 1 through PASS 4 into new chats one at a
time. The executing agent reads `.coding_workflow/diffs/agent_workorder.md`; the
user does not need to read it before starting the next pass.

---

## 2. Sync Agent Passes

Each pass must only edit its owned files and its agent-owned PR body sections.
Never edit `<!-- sync:auto:start -->` to `<!-- sync:auto:end -->`.

Common rules for every pass:

- Use `.coding_workflow/diffs/pr_body_skeleton.md` or current `PR_BODY.md` as the PR body structure authority.
- Do not modify sync sentinels or content outside sentinel sections.
- Do not fill `pr_test_evidence`; only the PR submission agent owns it.
- `agent_execution_evidence` is self-reported read coverage for reviewer spot checks only.
- `Full Document Reconcile` must include upstream semantic delta, adopted where, not adopted because, evidence, and downstream impact.
- Evidence must explicitly cover `class-1 template/missing`, `class-2 upstream`, and `class-3 code/test/behavior drift`.
- Do not quote upstream template markers, sample anchors, angle-bracket placeholders, or TODO sentinels as semantic deltas. Rewrite them descriptively and use upstream raw URLs as evidence.
- At pass end, rerun ordinary English sync:

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/en/scripts/sync.sh | bash
```

### 2.1 PASS 1 - Code Facts / Architecture

```text
Overall goal: complete this workflow docs sync by using ordinary sync outputs
and code evidence to update this pass's owned docs and PR_BODY.md agent-owned
sections. Current task: execute only PASS 1 - Code Facts / Architecture.

Must read:
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/architecture.md`
3. `PR_BODY.md`; initialize it from `.coding_workflow/diffs/pr_body_skeleton.md`
   if missing; stop if the skeleton is missing.
4. `PR_BODY.md` repo_facts_map and the `architecture.md` row in
   full_document_reconcile.
5. Current repo entrypoints, module boundaries, data flow, state model,
   external dependencies, and code-level invariants.

May modify only:
- `architecture.md`
- `PR_BODY.md` repo_facts_map
- `PR_BODY.md` full_document_reconcile row for `architecture.md`
- `PR_BODY.md` agent_execution_evidence row for PASS 1

Must fill:
- Repo Facts Map with concrete code, document, or command evidence.
- Code facts in `architecture.md` when evidence is sufficient.
- Full Document Reconcile row for `architecture.md`.
- Agent Execution Evidence row for PASS 1.

Finish by rerunning ordinary English sync. If it fails, stop and report the
error; do not hand-edit the auto section.
```

### 2.2 PASS 2 - Capability / User Behavior

```text
Overall goal: complete this workflow docs sync by using ordinary sync outputs
and code evidence to update this pass's owned docs and PR_BODY.md agent-owned
sections. Current task: execute only PASS 2 - Capability / User Behavior.

Precondition:
- In `.coding_workflow/diffs/agent_workorder.md`, PASS 1 owned docs should have
  marker / TODO hits as `none`; otherwise return to PASS 1.

Must read:
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/capability_contract.json`
3. `.coding_workflow/diffs/upstream_full/interact.md`
4. `.coding_workflow/diffs/upstream_full/docs/business_user_guide.md`
5. `PR_BODY.md`
6. Capability-related Repo Facts Map entries and this pass's rows in
   full_document_reconcile.
7. `architecture.md`, `capability_contract.json`, `interact.md`, and
   `docs/business_user_guide.md`.

May modify only:
- `capability_contract.json`
- `interact.md`
- `docs/business_user_guide.md`
- Capability-related Repo Facts Map entries
- Full Document Reconcile rows for this pass
- Agent Execution Evidence row for PASS 2

Must fill:
- Machine-readable capability, boundary, responsibility, and behavior contracts.
- User-visible behavior and acceptance invariants.
- Business-user guide explanations that derive only from the contract and
  interaction docs.
- Full Document Reconcile rows for all three owned docs.
- Agent Execution Evidence row for PASS 2.

Finish by rerunning ordinary English sync. If it fails, stop and report the
error; do not hand-edit the auto section.
```

### 2.3 PASS 3 - TESTING Independent Review

```text
Overall goal: complete this workflow docs sync by using ordinary sync outputs
and code evidence to update this pass's owned docs and PR_BODY.md agent-owned
sections. Current task: execute only PASS 3 - TESTING Independent Review.

Precondition:
- PASS 1 and PASS 2 owned docs should have marker / TODO hits as `none`;
  otherwise return to the owning pass.

Must read:
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/TESTING.md`
3. `PR_BODY.md`
4. Testing-related Repo Facts Map entries and the `TESTING.md` row in
   full_document_reconcile.
5. `TESTING.md`, target project test entrypoints, test inventory, and
   mechanical signal command output.
6. PASS 1/2 owned docs only as needed for test strategy anchors.

May modify only:
- `TESTING.md`
- Testing-related Repo Facts Map entries
- Full Document Reconcile row for `TESTING.md`
- Agent Execution Evidence row for PASS 3

Suggested mechanical signals:
- `find tests -type f -name 'test_*.py' -exec wc -l {} + | sort -n`
- `grep -rh '^def test_\|^class Test' tests/`
- `git log --since='3 months ago' --name-only -- tests/`

Must fill:
- `## TESTING_REVIEW_PACKET` at the top of `TESTING.md`, creating it if
  missing, with existing_test_inventory, redundant_tests,
  missing_high_value_tests, tests_not_worth_adding,
  unit_vs_contract_vs_scenario_vs_e2e_decision, real_failure_modes_covered,
  mock_only_risks, recommended_gate, and
  downstream_requirements_for_PR_Checklist.
- Full Document Reconcile row for `TESTING.md`.
- Agent Execution Evidence row for PASS 3.

Finish by rerunning ordinary English sync. If it fails, stop and report the
error; do not hand-edit the auto section.
```

### 2.4 PASS 4 - Governance / Reverse Closure

```text
Overall goal: complete this workflow docs sync by using ordinary sync outputs
and code evidence to update this pass's owned docs and PR_BODY.md agent-owned
sections. Current task: execute only PASS 4 - Governance / Reverse Closure.

Precondition:
- PASS 1/2/3 owned docs in `.coding_workflow/diffs/agent_workorder.md` should
  have marker / TODO hits as `none`; otherwise return to the owning pass.

Must read:
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/PR_Checklist.md`
3. `.coding_workflow/diffs/upstream_full/SOP.md`
4. `.coding_workflow/diffs/upstream_full/AGENTS.md`
5. `.coding_workflow/diffs/upstream_full/.github/pull_request_template.md`
6. `PR_BODY.md`
7. The whole Full Document Reconcile table and Remaining Human Decisions.
8. `PR_Checklist.md`, `SOP.md`, `AGENTS.md`, and
   `.github/pull_request_template.md`.
9. PASS 1/2/3 owned docs only where downstream impact closure requires it.

May modify only:
- `PR_Checklist.md`
- `SOP.md`
- `AGENTS.md`
- `.github/pull_request_template.md`
- Full Document Reconcile rows for this pass
- Remaining Human Decisions
- Agent Execution Evidence row for PASS 4

Must fill:
- How downstream impacts from PASS 1/2/3 are consumed by governance docs.
- PR template inherit / override decision.
- Remaining Human Decisions, or `none` when no unresolved decision remains.
- Agent Execution Evidence row for PASS 4.

Finish by rerunning ordinary English sync. If it fails, stop and report the
error; do not hand-edit the auto section.
```

---

## 3. PR Submission Agent

After PASS 4, start the PR submission agent. It must rely on `PR_BODY.md` Full
Document Reconcile / Remaining Human Decisions and final gate, not on chat
summaries.

```text
Current task: execute only the PR Submission Agent. Do not fill PASS 1/2/3/4
semantic content.

Must read:
1. `PR_Checklist.md`
2. `TESTING.md`
3. `.github/pull_request_template.md`
4. `PR_BODY.md`
5. `.coding_workflow/diffs/sync_state.json`
6. `PR_BODY.md` Full Document Reconcile table
7. `PR_BODY.md` PR Test Evidence
8. `PR_BODY.md` Upstream Drift Log
9. `PR_BODY.md` Agent Execution Evidence
10. `PR_BODY.md` Remaining Human Decisions

Before submission:
- Confirm current branch is not main / master / default branch.
- Use `git status --short` to separate sync files, PR_BODY.md, tests, and
  unrelated changes. Do not submit unrelated changes.
- Use `git diff --name-only <base>...HEAD` and `git diff --name-only` to keep
  PR_BODY.md change scope accurate.
- Ensure Full Document Reconcile covers all core docs and contains no
  `待补充`.
- Ensure four Agent Execution Evidence PASS rows are filled.
- If Upstream Drift Log is not `none`, tell the reviewer to re-check current
  upstream raw URLs.
- Run required tests per `TESTING.md` and PR_BODY.md, then write commands,
  results, and N/A reasons into PR Test Evidence.
- Before submit, run:
  `curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/en/scripts/sync.sh | bash -s -- --final`

Submission scope:
- Submit only this sync's core docs, `.gitignore`, necessary tests, and
  target-project-allowed PR_BODY.md.
- Do not submit `.coding_workflow/diffs/`, temporary clones, unrelated code,
  unrelated config, or stale drafts.
- `PR_BODY.md` is local PR body scratch by default; do not commit it unless the
  target project explicitly allows that.
```

---

## 4. Sync PR Review

After the PR submission agent provides a PR URL, start the independent reviewer:

```text
You are the PR reviewer for a workflow-docs sync PR. Review PR <URL> using the
PR body's Sync Review Contract and the commit-pinned English reviewer prompt raw
URL. For the English flow, that reviewer prompt should point to
`en/scripts/sync_pr_review_system.md`.

Open every raw URL listed in the PR body upstream sections and compare them
against the PR head's core docs. Also inspect PR Test Evidence, Upstream
Drift Log, and Agent Execution Evidence. Agent Execution Evidence is self-report
only and does not replace reviewer spot-checks of PR body evidence paths.
```

Outcomes:

- PASS: proceed to user-view acceptance.
- WARN: explain why the risk is acceptable in PR body, then proceed.
- BLOCKER: mechanical problems return to sync pass and ordinary sync; semantic
  problems require evidence or user judgment, then rerun PR submission and
  review.
