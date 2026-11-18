# Development Workflow

This is the English overview of the repository's human-in-the-loop coding workflow. The Chinese workflow
is the semantic source; this file closes the English meaning for the workflow content changed in this PR.

See
[DEC-008](../../../zh/docs/development_workflow/decisions.md#dec-008开发工作流采用复杂度守恒与可退役实验机制)
for workflow complexity conservation and the review and retirement rules for experimental mechanisms.
[DEC-009](../../../zh/docs/development_workflow/decisions.md#dec-009issue-直接驱动的编程回路与固定版本采用)
records the Issue-driven coding loop. See the [prompt pack and source index](../../prompts/README.md)
and [fixed-version adoption and updates](version_adoption.md).

## Main Flow

1. Define the requirement.

2. Turn the original user requirement, accepted decisions, and necessary repository facts into one executable issue contract. Owner decisions must remain explicit.
   The Issue is the single implementation entry so the Coding Agent does not receive several drifting upstream
   instruction sets in parallel. Owner choices also stay in the Issue; PR bodies, review comments, and chats
   refer back to the Issue instead of creating a second version.

   Shared agreements belong in the target project's GitHub repository documentation; related Issues reference
   the specific version. Before development, write a user-view acceptance plan in the Issue or its referenced
   repository document, for review with the Issue in the next step. Specify the user's real entrypoint, inputs,
   actions, expected results, and important failure cases. Development may revise the plan, recording the date,
   reason, changed items, and effects on existing results. Changes to goals or key criteria return to Issue
   decisions and review. Execution results identify the plan version, code candidate, and environment.

3. Have LLMs from two different LLM companies review the issue through two orthogonal lenses before implementation: requirement and acceptance closure,
   and engineering volume and minimal sufficiency. The Issue Agent from step 2 owns the final edit; the lenses
   advise rather than editing the issue in parallel. The two lenses protect against under-delivery and
   over-engineering rather than duplicating a vote.

   Each first performs a complete review of the same Issue in an independent context, then they exchange their reports and conclusions.
   Even when neither finds a blocker, they actually exchange conclusions and confirm the same object and scope.
   After the author updates the Issue, both recheck changes and unresolved problems and conclude on the final version.

4. Implement the issue after reading `AGENTS.md`, `SOP.md`, `TESTING.md`, `PR_Checklist.md`, `interact.md`,
   and project capability or business-user documents. Map each Spec Unit to code, tests, and documentation,
   and state which tests are reused, parameterized, or used as the real cross-module scenario.
   The same engineering owner continues through investigation, implementation, and testing. Expected file lists
   evolve with investigation; within the existing delegation, read, add, delete, modify, or rename files as needed.
   Implementation remains constrained by repository facts and the Issue rather than a generic coding template.

5. Self-review the patch and deliver a draft PR using the repository's commit policy and tracked PR template.
   The PR body remains outside the target worktree and records actual scope, evidence, review/fix history, open
   decisions, and limits. It is an important formal-review input even though it is not committed to the target
   repository.

6. Have LLMs from two different LLM companies each perform the complete formal PR review with the full review system and task prompt. Each checks Issue
   compliance, bugs, unnecessary architecture or duplicated repair, the external PR body, repository guidance,
   and the realism of test evidence; important claims must be investigated through code execution or a close
   reproduction path. This step discovers problems across the whole PR; the next step only verifies findings
   already raised. Both review the same latest head independently, then exchange findings and conclusions;
   even a clean review requires an actual exchange confirming the same object and coverage.

   The formal reviewer must use exactly three final outcomes:
   - `PASS`: no P0/P1 or other unresolved blocker, with sufficient supporting evidence;
   - `REWORK_REQUIRED`: code, documentation, testing, or evidence still needs correction;
   - `OWNER_DECISION_REQUIRED`: the Issue contains an unresolved owner choice that blocks the current delivery.

7. When review finds a problem, verify it before changing code. Codex focuses on whether the problem is real,
    its trigger path, reproduction, and severity; Claude Code focuses on impact, adjacent entrypoints, whether
    the finding is one instance of a broader problem, and the smallest sufficient fix. Evidence and owner
    decisions resolve disagreement. Codex and Claude Code are the example pairing here; the LLMs actually used
    must come from different LLM companies.

    Finding verification uses the same three outcomes:
    - `PASS`: the finding is refuted or does not constitute a blocker;
    - `REWORK_REQUIRED`: the finding is confirmed, or evidence is insufficient to rule out a blocker;
    - `OWNER_DECISION_REQUIRED`: the Issue contains an unresolved owner choice that affects whether or how far
      the finding should be fixed.

    The operational sequence is:

    1. The Coding Agent completes implementation and self-review, updates the external PR body, and creates or
       updates the draft PR.
    2. Start independent review conversations with LLMs from two different LLM companies and run the full
       step-6 review against the same latest exact head, then exchange conclusions; builder self-review does
       not replace this review.
    3. When both conclude `PASS`, proceed to steps 8–10 and merge or deliver under the existing delegation.
    4. On `REWORK_REQUIRED`, send all P0/P1 and other blocking findings as one batch to one fresh
       Codex verification conversation and one fresh Claude Code verification conversation. Each verifies
       independently before reading the other's report.
       Codex verifies truth, trigger path, reproduction, and severity; Claude Code verifies impact, adjacent
       entrypoints, root cause, and the smallest sufficient fix.
    5. After independent verification, exchange code, tests, reproducible evidence, and the Issue contract for
       at most three rounds, with Codex synthesizing and both parties' actual replies retained. End early when
       conclusions are sufficiently supported. If evidence remains insufficient after three rounds, remain
       `REWORK_REQUIRED` and state the evidence work; model identity never decides correctness. If all findings
       are refuted and code is unchanged, return the evidence to formal reviewers for closure.
    6. When a problem is confirmed and needs repair, receive the original writer's existing changes and
       verification records in that same Codex verification conversation, then instruct it to implement the
       synthesis. Reuse the step-5 PR submission prompt to update code, tests, documentation, review/fix history,
       PR body, and the head commit.
    7. After every repair, start independent review conversations with LLMs from two different LLM companies,
       rerun the step-6 review on the new exact head, and exchange conclusions. Reuse still-valid investigation
       and check differences and impacts. Repeat until both conclude `PASS`; P2 findings may remain but must
       be recorded. The repair conversation cannot sign its own formal approval.
    8. On `OWNER_DECISION_REQUIRED`, add the owner choice to the Issue in readable prose and state which work it
       affects. Pause the affected work while other work continues. After the owner decides, add the conclusion
       and rationale to the same Issue, resume the work, update the PR, and run a fresh step-6 review.

    9. After more than three repairs, reassess whether the implementation can be simplified without losing the
       goal or necessary correctness; leave areas with no clear benefit unchanged.

    When integrating reviewed members, reuse valid review and test evidence and validate the complete combined
    path. If integration changes code, configuration, dependencies, or connections in a way that affects reviewed
    behavior or evidence applicability, validate the changes and have LLMs from both companies conclude on the
    differences and impacts for the new candidate, whether or not a new PR is created.

8. After development and necessary validation of a demonstrable candidate, use the full Tech Lead walkthrough to explain the delivered implementation from actual code
    evidence, then assess user-visible changes, how users employ the result, and whether `AGENTS.md` and linked
    documents provide sufficient guidance. Explain actual development difficulties, alternatives, and tradeoffs,
    and retrospectively assess a roughly half-size solution: what value would remain and what would be lost.
    Use offline-readable HTML, concrete cases, and diagrams to explain mechanisms deeply enough to manually
    trace normal, failed, and recovery paths; source names support verification rather than replace explanation.
    Distinguish implementation facts, design intent, and inference with versioned evidence. Store the walkthrough
    and follow-up in the PR conversation, adding new deployment results to the same explanation.

9. Keep the pre-close FSD acceptance step: inspect main-branch code against every Issue Spec Unit and produce
    `Updates to FSD` for deviations. This step is currently paused because its observed pass rate was
    100% and user-view acceptance found more precise issues, but the step and prompt remain documented.

10. Use the user-view acceptance plan prepared in step 2 and reviewed by both companies, and hand it to Codex
    for actual execution with tools such as Playwright when useful. Run candidate-ready scenarios early and add
    target-environment checks after merge or deployment. For an outcome spanning several Issues or PRs, validate
    the complete user path. Archive results in the PR conversation with the plan version, candidate, and
    environment. Implementation gaps return to step 7 for verification, repair, and review; changes to goals,
    scope, or key semantics return to Issue decisions and recorded plan revisions. This acceptance may create
    follow-up development work.

## Core Artifacts

- `FSD Core Contract` (on demand): a requirement contract that can be implemented, tested, and reviewed.
- `Repo Impact Forecast` (on demand): predicted repository touchpoints, risks, documentation, and test impact.
- `Target State Bridge` (on demand): target user- or caller-visible state and its validation method.
- `Issue`: the single executable development contract, including owner choices that must remain visible.
- User-view acceptance plan: prepared before development, revised with records, and executed through real user paths.
- Tech Lead walkthrough: post-development understanding of functionality, mechanisms, and development tradeoffs.
- External PR body Markdown: temporary review and publishing input derived from the tracked PR template; it
  never enters the target worktree or commit.
- `FSD Completeness Acceptance Report` (paused): the pre-close main-branch check of Spec Units and FSD deviations.
- `Workflow Docs Sync`: one invocation for full fact reconstruction, minimal necessary document changes,
  real tests, fresh-context independent review or honest self-review, and deterministic final checks.

## English Coverage Boundary

Current template roles and entrypoints are maintained in the [Directory Map](../../README.md#directory-map),
without a second role list here that could drift.

English workflow documentation is exposed only when its path is ready. The long prompt pack remains outside
the English-ready surface; see [en/prompts/README.md](../../prompts/README.md). Bilingual template, README,
and development-workflow content changed by a PR must close in that PR. Unchanged historical decisions
retain their recorded translation status.

## Workflow Docs Sync

Invoke `$workflow-docs-sync` once with the target repository, a required `zh` / `en` language choice, and
whether to create a draft PR after success. The Skill resolves the canonical upstream checkout or uses an
external shallow clone, then pins target HEAD and upstream SHA for the entire run.

- Before writing, use at least `git ls-files -z` to establish scope. Follow the
  [canonical Skill](../../../zh/skills/workflow-docs-sync/SKILL.md) for fact and policy verification instead
  of redefining the method here.
- Architecture, Capability / User Behavior, Testing, and Governance are coverage dimensions, not a fixed
  agent topology. The main agent may investigate directly or delegate read-only work by module, call flow,
  risk, or evidence type.
- The main agent is the only target-workspace writer. It questions all nine documents but changes only
  incorrect, missing, or misleading content; correct content stays at zero diff. The workflow creates no
  disposition ledger, run state, or receipt.
- Test environments follow real commands, side effects, CI capabilities, and project policy. Record the
  actual environment, isolation, residue, and cleanup instead of fixing one implementation across projects.
- Review prefers a fresh-context, blind-first independent reviewer. When cognitive isolation is unavailable,
  the final result says self-review and never claims independence. Fix all BLOCKERs and actionable WARNs that
  do not require a new product decision, then recheck their direct effects.
- `sync_docs.py prepare` first validates all nine UTF-8 source templates at the pinned object and language,
  including the non-PR active-marker invariant, then fills only missing templates. `check` rereads that pinned
  source and validates final HEAD, dirty scope, no index/worktree split on editable paths, nine regular UTF-8
  nonempty files, a JSON object, active markers, and an existing `.gitignore` as UTF-8. Final-byte whitespace
  runs with fixed Git rules from a temporary non-repository directory, independent of target attributes. It
  does not parse Markdown or validate capability truth, test levels, prose quality, or execution history. The
  single final-byte path depends on rejecting every dirty path outside the allowlist; relaxing that allowlist
  requires reevaluating whitespace coverage. Split detection aggregates both status sides by path and covers
  an index deletion or rename source followed by an untracked or ignored recreation at that path. It removes
  two publication candidates rather than running a second whitespace check.
- Before any removal or copy, the installer validates source and destination ancestors, source symlinks,
  standard delimiters around Claude frontmatter, and ignored source residue that would be copied. It only
  removes the exact obsolete reviewer Skill and stores no install state or source receipt.
- Keep temporary PR body Markdown outside the repository. Commit, push, and draft-PR creation occur through
  general GitHub publishing capability only after successful checks and only when the user asks.

### DEC-007 Summary

[DEC-007](../../../zh/docs/development_workflow/decisions.md) refines DEC-006 without restoring proxy
controls. It classifies descriptive facts, normative policies, personal or session preferences, and mixed
claims by meaning; configuration proves enforcement but does not silently supersede policy intent, and a
task preference persists only after explicit owner adoption in repository authority.

The capability contract is the single definition point for the canonical anchor form, case-sensitive ID
grammar, and whitespace tolerance. Unsupported forms do not establish alignment, the generic protocol does
not promise exhaustive alias detection, and structural references do not prove claim semantics. An explicit
`test_anchor: null` requires both a nonempty `untested_reason` and `pending_since`; the authoring-rule change
does not raise `schema_version` from `0.1.0`. TESTING defines minimum evidence for escaped bugs, public
contracts, no-test diffs, refactors, and documentation-only gates, while the checklist enforces the
add-or-not-add test decision.
Stable IDs, first-seen evidence, REOPENED events, and candidate/evidence states belong to this repository's
maintenance and canonical Skill/eval evidence contract. Downstream templates defer review records,
actionable feedback, rechecks, and open decisions to target-project policy instead of fixing this vocabulary.

Case A preregisters the selected target and known-stale claims before starting a blind executor. Target code,
configuration, tests, other committed artifacts, upstream candidate, and language stay fixed; round one
commits only its final nine documents, and round two starts from that `second_target_sha` in a new clean
checkout. A zero document diff with no staged, untracked, or ignored residue is `PASS_NOOP`; an added valid
correction is `ROUND1_INCOMPLETE`, and unsupported prose drift is `ROUND2_DRIFT`. Alignment runs directly on
the committed second target instead of a derived test-only identity. Either failure restarts both rounds from
a clean target. This decision adds no parser, ledger, receipt, run state, installer behavior, or
`sync_docs.py` / CLI feature.

### DEC-008 Summary

[DEC-008](../../../zh/docs/development_workflow/decisions.md) applies direct-risk and mechanism-necessity
principles to the development workflow itself. It records the change as accepted net complexity growth rather
than claiming neutrality. Issue and finding cross-checks remain dual-model but use different lenses, while
formal PR review remains a separate, detailed step. Model identity is not the disagreement authority. The
review loop uses only `PASS`, `REWORK_REQUIRED`, and `OWNER_DECISION_REQUIRED` as final outcomes.

Owner choices remain visible in the Issue and are explained in readable prose rather than a fixed schema.
DEC-008 treated conditional issue-readback and Owner Decision as experiments. In the current flow, DEC-009
places the Tech Lead walkthrough after development; Owner Decision remains experimental. Under the
2026-09-24 revision, each is reviewed using actual usage feedback: roughly three uses are a reminder, not a
counting gate. Review may happen earlier when costs or gaps emerge, or after prolonged non-use; do not
manufacture tasks to reach a count. Assess understanding and decision benefits, risk coverage, prevention of
incorrect implementation or wasted waiting, and execution cost. Non-use, an unchanged next action, or the
absence of a risk event alone does not justify retirement; a readback can improve informed judgment without
changing the plan.

Only extra steps, records, or redundant checks may be retired, not necessary authorization boundaries or
substantive owner choices. The owner decides whether to retain, adjust, or retire a procedure based on
available evidence; `PROMOTE`, `MODIFY`, and `RETIRE` remain optional labels. Record the conclusion and reasons
in an existing relevant Issue or PR and update affected workflow guidance. Disclose insufficient evidence;
experimental status is not proof of maturity. No separate counter, tracking file, or dedicated evaluation is
required by this rule. DEC-008's pre-coding readback complemented rather than replaced post-merge implementation
explanation, documentation review, FSD closure checking, and user-view acceptance.

Key implementation files:

- `../../../zh/skills/workflow-docs-sync/SKILL.md`: orchestration contract.
- `../../../zh/skills/workflow-docs-sync/agents/openai.yaml`: UI metadata.
- `../../../zh/skills/workflow-docs-sync/evals/README.md`: forward-eval cases.
- `../../../zh/skills/workflow-docs-sync/scripts/sync_docs.py`: mechanical preparation and check.
- `../../../tests/test_workflow_docs_sync.py`: regression and real-template quality tests.
