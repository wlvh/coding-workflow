# Development Workflow

This is the English overview of the repository's human-in-the-loop coding workflow. The Chinese workflow
is the semantic source; this file closes the English meaning for the workflow content changed in this PR.

## Workflow Complexity Conservation

Any added or expanded step, prompt section, gate, state, long-lived artifact, role, or mechanical control must
state whose next action it changes, the independent risk it controls, why current mechanisms are insufficient,
and what it replaces, merges, narrows, or removes. A mechanism that does not change an actor's next action
must not be added. Extend an existing mechanism instead of creating a parallel one when possible. Prescribe a
fixed output structure only when a machine consumer or a specific downstream decision depends on it; otherwise
state the behavioral obligation without mandatory headings or checklists.

Evidence-backed net complexity growth is allowed when the owner explicitly accepts it, but it must be recorded
honestly and carry observable review and retirement conditions. See
[DEC-008](../../../zh/docs/development_workflow/decisions.md#dec-008开发工作流采用复杂度守恒与可退役实验机制).

## Main Flow

1. Define the requirement.
2. Draft the black-box `FSD Core Contract` with the Pro web model when direct repository exploration is
   unavailable.
3. Compare the FSD, current repository code, and authoritative documents to produce the `Repo Impact
   Forecast` and `Target State Bridge`.
4. Turn the FSD, forecast, and bridge into one executable issue contract. Owner decisions must remain explicit
   and state what is being decided, whether the evidence required to decide can be obtained legally, the local
   blocking scope, and the safe default.
5. Review the issue through two blind-first, orthogonal lenses before implementation. One model checks
   requirement closure and acceptance decidability; the other checks engineering volume, whether roughly half
   the work can be removed, whether the proposal creates problems that require more machinery, and whether
   tests can be reused or parameterized. The Issue Agent from step 4 owns the edit; the two lenses advise and
   do not edit the issue directly. They exchange challenges once; model agreement is not evidence, and product
   tradeoffs remain with the owner.
6. Run an issue readback before coding only when the issue involves irreversible side effects, cross-module
   state / persistence / retry / recovery / concurrency, or an unresolved owner tradeoff. The readback explains
   the runtime chain, necessary work packages, long-term complexity, a half-size alternative, test composition,
   and owner choices. Owner approval binds the issue revision that was actually read; material changes to scope,
   acceptance, work-package boundaries, failure semantics, or owner decisions invalidate approval.
7. Implement the approved issue after reading `AGENTS.md`, `SOP.md`, `TESTING.md`, `PR_Checklist.md`,
   `interact.md`, and project capability or business-user documents. Map each Spec Unit to code, tests, and
   documentation, and state which tests are reused, parameterized, or used as the real cross-module scenario.
8. Self-review the patch and deliver a draft PR using the repository's commit policy and the tracked PR
   template. The PR body remains outside the target worktree and records actual scope, evidence, review/fix
   history, open decisions, and limits.
9. Independently review the current exact head blind-first. Freeze the current findings before reading the
   previous two review reports. Review judgments must distinguish reproduced behavior, code-derived inference,
   and unreviewed claims; environment or permission limits are reasons for unreviewed coverage. Material missing
   coverage returns `REQUEST_EVIDENCE`, not PASS or an instruction to modify code.
10. Verify each finding through two orthogonal lenses. The fact verifier does not read history and decides
    `CONFIRMED`, `REFUTED`, or `REQUEST_EVIDENCE`. The systemic verifier first classifies the current state
    owner, persistence protocol, and side-effect chain, then reads history to decide `LOCAL_FIX`,
    `SYSTEMIC_FIX`, `SPEC_REVISION_REQUIRED`, or `OWNER_DECISION_REQUIRED`. Reproducible evidence,
    repository authority, and the owner decide disagreements; model identity does not. Two counterintuitive
    actions are mandatory: `SPEC_REVISION_REQUIRED` stops code changes and returns to the Bridge, while
    `OWNER_DECISION_REQUIRED` pauses only the blocked work and lets unblocked work continue.
11. Stop patch-by-patch repair and return to the Bridge when the prior fix creates the new P0/P1, two rounds
    hit the same entrypoint / state owner / persistence protocol / side-effect chain, or the same chain still
    needs new durable state, checkpoints, persistent artifacts, recovery branches, or terminal semantics after
    a repair round. The final review outcome is exactly one of `PASS`, `REWORK_REQUIRED`,
    `SPEC_REVISION_REQUIRED`, `OWNER_DECISION_REQUIRED`, or `REQUEST_EVIDENCE`.
12. Merge under the target project's acceptance policy after PASS. Existing merge-readiness and issue-closure
    tools remain optional rather than universal main-flow steps. When an issue readback already happened,
    post-merge explanation is limited to implementation deltas, changed tradeoffs, residual risk, and follow-up
    issues instead of repeating the full mechanism walkthrough.

## Core Artifacts

- `FSD Core Contract`: a requirement contract that can be implemented, tested, and reviewed.
- `Repo Impact Forecast`: predicted repository touchpoints, risks, documentation, and test impact.
- `Target State Bridge`: target user- or caller-visible state and its validation method; it also receives a
  scoped state-space redesign after `SPEC_REVISION_REQUIRED`.
- `Issue`: the single executable development contract, including explicit owner decisions and work-package
  blocking scope.
- Conditional issue readback: owner-facing understanding and revision-bound approval for high-risk issues; it
  is not a second authority source.
- External PR body Markdown: temporary review and publishing input derived from the tracked PR template;
  it never enters the target worktree or commit.
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
principles to the development workflow itself. It records this change as accepted net complexity growth rather
than claiming neutrality. Issue and finding cross-checks remain dual-model but use orthogonal lenses; evidence
replaces model identity as the disagreement authority. Review must not treat unreviewed claims as verified. A
divergence gate returns systemic gaps to the Bridge, while owner decisions must include a legal evidence path
and local blocking scope.

The divergence gate, conditional issue readback, and owner-decision contract are experimental. Each is reviewed
after three applicable PRs, with `PROMOTE`, `MODIFY`, or `RETIRE` as the only outcomes. A mechanism that never
fires or fires without changing the next action retires by default unless new concrete risk evidence supports
retention.

Key implementation files:

- `../../../zh/skills/workflow-docs-sync/SKILL.md`: orchestration contract.
- `../../../zh/skills/workflow-docs-sync/agents/openai.yaml`: UI metadata.
- `../../../zh/skills/workflow-docs-sync/evals/README.md`: forward-eval cases.
- `../../../zh/skills/workflow-docs-sync/scripts/sync_docs.py`: mechanical preparation and check.
- `../../../tests/test_workflow_docs_sync.py`: regression and real-template quality tests.