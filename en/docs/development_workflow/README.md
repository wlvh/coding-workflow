# Development Workflow

This is the English overview of the repository's human-in-the-loop coding workflow. The Chinese workflow
is the semantic source; this file closes the English meaning for the workflow content changed in this PR.

See
[DEC-008](../../../zh/docs/development_workflow/decisions.md#dec-008开发工作流采用复杂度守恒与可退役实验机制)
for workflow complexity conservation and the review and retirement rules for experimental mechanisms.

## Main Flow

1. Define the requirement.

2. Draft the black-box `FSD Core Contract` with the Pro web model.
   The FSD fixes the user-observable contract without designing around the current implementation; repository
   touchpoints, compatibility, and implementation context belong to the next Bridge step.

3. Compare the FSD, current repository code, and authoritative documents to produce the `Repo Impact
   Forecast` and `Target State Bridge`.
   The Bridge aligns the black-box requirement with repository facts and separates predictions from commitments
   without rewriting the FSD's user goal.

4. Turn the FSD, forecast, and bridge into one executable issue contract. Owner decisions must remain explicit.
   The Issue is the single implementation entry so the Coding Agent does not receive several drifting upstream
   instruction sets in parallel. The sole normative definition of `OWNER_DECISION_REQUIRED`, the `OD-xxx`
   record, and its lifecycle lives in
   [`zh/prompts/issue_agent.md`](../../../zh/prompts/issue_agent.md); the overview, Bridge, and review prompts
   only reference it.

5. Review the issue through two orthogonal lenses before implementation: requirement and acceptance closure,
   and engineering volume and minimal sufficiency. The Issue Agent from step 4 owns the final edit; the lenses
   advise rather than editing the issue in parallel. The two lenses protect against under-delivery and
   over-engineering rather than duplicating a vote.

6. Run an issue readback before coding for high-risk issues. It explains the planned runtime chain, necessary
   work packages, long-term complexity, a half-size alternative, test composition, and owner choices. It is an
   owner-understanding step rather than a second specification source or approval-state machine.

7. Implement the issue after reading `AGENTS.md`, `SOP.md`, `TESTING.md`, `PR_Checklist.md`, `interact.md`,
   and project capability or business-user documents. Map each Spec Unit to code, tests, and documentation,
   and state which tests are reused, parameterized, or used as the real cross-module scenario.
   The Coding Agent receives the Issue rather than the FSD, Forecast, and Bridge again because those inputs have
   already been consolidated into the Issue; implementation remains constrained by repository facts rather than
   a generic coding template.

8. Self-review the patch and deliver a draft PR using the repository's commit policy and tracked PR template.
   The PR body remains outside the target worktree and records actual scope, evidence, review/fix history, open
   decisions, and limits. It is an important formal-review input even though it is not committed to the target
   repository.

9. Have Codex perform the formal PR review with the full review system and task prompt. It checks Issue
   compliance, bugs, unnecessary architecture or duplicated repair, the external PR body, repository guidance,
   and the realism of test evidence; important claims must be investigated through code execution or a close
   reproduction path. This step discovers problems across the whole PR; the next step only verifies findings
   already raised.

   The formal reviewer must use exactly three final outcomes:
   - `PASS`: no P0/P1 problem;
   - `REWORK_REQUIRED`: code, documentation, testing, or evidence still needs correction;
   - `OWNER_DECISION_REQUIRED`: use only under the canonical Owner Decisions rule in
     `zh/prompts/issue_agent.md`, and cite the Issue's `OD-xxx`.

10. When review finds a problem, verify it before changing code. Codex focuses on whether the problem is real,
    its trigger path, reproduction, and severity; Claude Code focuses on impact, adjacent entrypoints, whether
    the finding is one instance of a broader problem, and the smallest sufficient fix. Evidence and owner
    decisions resolve disagreement.

    Finding verification uses the same three outcomes:
    - `PASS`: the finding is refuted or does not constitute P0/P1;
    - `REWORK_REQUIRED`: the finding is confirmed, or evidence is insufficient to rule out P0/P1;
    - `OWNER_DECISION_REQUIRED`: use only under the canonical Owner Decisions rule in
      `zh/prompts/issue_agent.md`, and cite the Issue's `OD-xxx`.

    The operational sequence is:

    1. The Coding Agent completes implementation and self-review, updates the external PR body, and creates or
       updates the draft PR.
    2. Start a fresh Codex conversation and run the full step-9 review against the latest exact head; builder
       self-review does not replace this review.
    3. On `PASS`, proceed to merge and the post-merge steps.
    4. On `REWORK_REQUIRED`, send each P0/P1 finding to fresh Codex and Claude Code verification conversations.
       Codex verifies truth, trigger path, reproduction, and severity; Claude Code verifies impact, adjacent
       entrypoints, root cause, and the smallest sufficient fix.
    5. Give Claude Code's analysis to Codex for synthesis. If disagreement remains, exchange only code, tests,
       reproducible evidence, and the Issue contract for at most three rounds. If evidence is still insufficient,
       remain `REWORK_REQUIRED` and state the evidence work; model identity never decides correctness.
    6. When the synthesis is `REWORK_REQUIRED`, continue in the Codex verification conversation with an explicit
       instruction to implement the synthesis. Then reuse the step-8 PR submission prompt to update code, tests,
       documentation, review/fix history, PR body, and the head commit.
    7. After every repair, start a fresh Codex conversation and rerun the full step-9 review on the new exact
       head. Repeat until `PASS`; P2 findings may remain but must be recorded.
    8. On `OWNER_DECISION_REQUIRED`, the active execution owner writes or updates the canonical `OD-xxx` under
       `zh/prompts/issue_agent.md`: the current Coding Agent does so during implementation, while the Codex
       conversation responsible for synthesis and repair does so during review or finding verification. Pause
       only the record's `Blocks`; let `Unblocked` work continue. After the owner decision, the Coding Agent or
       Codex that will resume the blocked work updates the same record, resumes the work, updates the PR, and
       runs a fresh step-9 review.

    This step describes only how an Owner Decision enters the review and repair loop. It does not redefine the
    decision criteria, record shape, or lifecycle.

11. After merge, use the full Tech Lead walkthrough to explain the delivered implementation from final code
    evidence, then assess user-visible changes, how users employ the result, and whether `AGENTS.md` and linked
    documents provide sufficient guidance. Store both in the PR conversation.

12. Keep the pre-close FSD acceptance step: inspect main-branch code against every Issue Spec Unit and produce
    `Updates to FSD` for deviations. The current workflow may pause this step because its observed pass rate was
    100% and user-view acceptance found more precise issues, but the step and prompt remain documented.

13. Create a user-view acceptance plan through agreement between the web GPT and Claude Code, archive it in the
    PR conversation, and hand it to Codex for actual execution with tools such as Playwright when useful. This
    acceptance may create follow-up development work.

## Core Artifacts

- `FSD Core Contract`: a requirement contract that can be implemented, tested, and reviewed.
- `Repo Impact Forecast`: predicted repository touchpoints, risks, documentation, and test impact.
- `Target State Bridge`: target user- or caller-visible state and its validation method.
- `Issue`: the single executable development contract. Its Owner Decisions section is maintained under the sole
  normative rule in `zh/prompts/issue_agent.md`.
- Conditional issue readback: owner-facing understanding for high-risk issues; it is not a second authority
  source and does not replace post-merge implementation explanation or user-view acceptance.
- External PR body Markdown: temporary review and publishing input derived from the tracked PR template; it
  never enters the target worktree or commit.
- `FSD Completeness Acceptance Report`: the pre-close main-branch check of Spec Units and FSD deviations.
- `Workflow Docs Sync`: one invocation for full fact reconstruction, minimal necessary document changes,
  real tests, fresh-context independent review or honest self-review, and deterministic final checks.

## English Coverage Boundary

English workflow documentation is exposed only when its path is ready. The long prompt pack remains outside
the English-ready surface; see [en/prompts/README.md](../../prompts/README.md). Bilingual template, README,
and development-workflow content changed by a PR must close in that PR. Unchanged historical decisions
retain their recorded translation status.

## Workflow Docs Sync

Invoke `$workflow-docs-sync` once with the target repository, a required `zh` / `en` language choice, and
whether to create a draft PR after success. The Skill resolves the canonical upstream checkout or uses an
external shallow clone, then pins target HEAD and upstream SHA for the entire run.

- Before writing, use at least `git ls-files -z` to establish scope and reconstruct facts from code,
  configuration, tests, committed artifacts, reproducible results, and necessary Git history. Existing
  documents and upstream templates are hypotheses.
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

The canonical Owner Decision definition and record lifecycle live only in `zh/prompts/issue_agent.md`;
the Bridge, workflow overview, and review prompts reference that source rather than duplicating it.
Conditional issue readback and the Owner Decision mechanism are experimental and reviewed after three
applicable PRs with `PROMOTE`, `MODIFY`, or `RETIRE` as the outcomes. Pre-coding readback complements rather
than replaces post-merge implementation explanation, documentation review, FSD closure checking, and
user-view acceptance.

Key implementation files:

- `../../../zh/skills/workflow-docs-sync/SKILL.md`: orchestration contract.
- `../../../zh/skills/workflow-docs-sync/agents/openai.yaml`: UI metadata.
- `../../../zh/skills/workflow-docs-sync/evals/README.md`: forward-eval cases.
- `../../../zh/skills/workflow-docs-sync/scripts/sync_docs.py`: mechanical preparation and check.
- `../../../tests/test_workflow_docs_sync.py`: regression and real-template quality tests.