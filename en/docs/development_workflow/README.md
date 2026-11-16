# Development Workflow

This is the English overview of the [Chinese semantic source](../../../zh/docs/development_workflow/README.md).
It defines the coding loop supplied by coding-workflow and the behavior required of a consumer such as
Tongxu. The current contract is **coding-loop v2**, adopted in
[DEC-009](../../../zh/docs/development_workflow/decisions.md#dec-009issue-直接驱动的编程回路与固定版本采用).
It does not assert that a consumer already implements every requirement. See the
[version-adoption contract](version_adoption.md) for fixed versions, source ownership, upgrades, and
existing-work compatibility. Decision history remains in the
[Chinese decisions](../../../zh/docs/development_workflow/decisions.md).

## Scope and defaults

The default unit of development is an adopted Issue with observable acceptance conditions. FSD Core
Contract, Repo Impact Forecast, and Target State Bridge are no longer mandatory documents. Retain shared
behavior agreements, material impact findings, or a migration plan when they change real implementation,
coordination, or release decisions. Keep one authoritative requirement instead of rewriting it in several
parallel artifacts.

Issue review and PR review each involve two different companies, independent contexts, and distinct
review lenses. Provider choices are configurable. Two prompts, two sessions, or two models from one
company do not satisfy the cross-company requirement. Actual provider and execution records establish
participation; role names and intended dispatches do not.

One engineering responsibility continues through investigation, implementation, tests, and repairs.
Sessions may change when context or execution must be recovered. The host maintains the actual permission,
workspace, candidate, operation, and evidence boundaries. Existing adequate delegation does not create a
new compulsory plan-approval step.

These sections describe responsibilities, not a requirement for a separate agent, document, or model call
at every heading. Investigation, implementation, and testing may alternate; coordination and progress
reporting continue throughout.

## 1. Receive a requirement in the existing project

Treat multiple Issues at different stages as the normal project context. The secretary first relates new
input to existing goals and work: duplication, extension, upstream output, shared agreement, semantic
conflict, resource conflict, or release-order constraint. Suspected conflicts require investigation before
becoming blockers. New input can supplement existing work instead of automatically creating more Issues.

Persist receipt independently of model dispatch so a busy secretary does not lose incoming requirements.
Keep receipt, association, delivery to the responsible engineer, adoption into a work version, and actual
implementation distinguishable. A delivered message does not prove that the running candidate covers it.

The secretary discovers and routes relevant work. Engineering owners establish technical compatibility;
the user decides substantive product or authority choices. Only affected work or stages wait. Cross-Issue
coordination does not merge permissions or overwrite another owner's active workspace. Several active
Issues do not require unlimited concurrent writers.

## 2. Form an Issue and its acceptance conditions

The Issue author uses the user's original intent, existing decisions, relevant repository facts, and
related work. Include the user goal and observable result, necessary boundaries, acceptance scenarios,
shared agreements or dependencies that actually matter, and unresolved user choices. Do not demand a
large fixed template for every task or re-create the three retired documents as compulsory sections.

Define initial acceptance scenarios now: starting conditions, user actions, expected observations, and
important failure or compatibility behavior. Commands, data, accounts, and environment details can be
completed during engineering. A complex change may include an explanation of how the finished behavior
will work; it is derived from the same requirement and is not another specification or approval gate.

Multiple Issues can reference one shared behavior agreement or one outcome-level acceptance scenario.
PR descriptions and conversations refer to those sources rather than maintaining competing requirements.

## 3. Review the Issue through two independent lenses

Both reviewers receive the original user request and decisions, the same Issue version, traceable shared
repository facts, and relevant related Issues. They may verify decisive facts independently. Shared
material must not force them to trust the author's conclusions or inherit the author's conversation.

- **Completion and acceptance:** identify omissions that prevent the original goal from being met and
  acceptance conditions that cannot distinguish real success. Do not expand the task to every imaginable
  edge case.
- **Minimal sufficiency:** challenge unnecessary requirements, reuse existing capabilities, and propose
  deletion or scope reduction where justified. Do not replace one excessive plan with another large design.

Each reviewer first investigates independently, then exchanges material findings. Neither owes a complete
implementation design, file forecast, or separate test architecture. The Issue author edits the same Issue;
reviewers recheck changed or disputed parts while reusing still-valid evidence.

Separate blocking problems, nonblocking suggestions, and new ideas. Unadopted new ideas stay outside the
current target. Agreement between models does not enlarge user authority. Technical uncertainty remains
engineering evidence work; only substantive choices outside existing delegation go to the user.
Still-applicable material may be reused; an author's declaration that a task is small does not bypass a
required independent review.

## 4. Investigate and implement under continuous responsibility

Bind the actual requirement snapshot, work version, initial code version H0, adopted workflow and prompt
version, and valid delegation before execution. Begin with read-only investigation. If the resulting work
remains within valid delegation, continue without a fixed per-file approval or a second preparation owner.

Predicted files are investigation hints. The host separately enforces:

- **Read scope:** the authorized repository snapshot and the managed workspace's subsequent changes;
  unrelated private paths, credential sources, and other repositories are not implicitly included.
- **Write scope:** controlled modification, creation, deletion, and rename in the permitted workspace and
  resources; check both rename endpoints and path protection, including path traversal or link escapes.
- **Execution scope:** actual code, dependencies, configuration, processes, network, and external effects
  available to tests or commands under the current execution profile.

The engineer may inspect a previously unpredicted caller or create a necessary file within that boundary.
Tests receive the actual candidate and required runtime inputs, not only files the model happened to read.
Mechanical boundaries do not prove that an edit is semantically necessary; engineering and independent
review remain responsible for that judgment.

Implement the smallest sufficient change, maintain project tests and necessary documentation, and self-review.
Choose real tests from the repository and actual environment. Existing project tests may change when their
premise changes; do not weaken the adopted business acceptance criteria to make an implementation pass.
Only add independent assertions where existing coverage is insufficient.

Create or update a draft PR under the project's valid publishing delegation. Record actual changes,
verification, remaining limits, and references to the Issue. Implementation success, local result return,
formal review, merge, deployment, and user acceptance remain different facts.

## 5. Validate the candidate and exercise user paths early

Select evidence for the actual candidate, test definition, and relevant environment. Retain complete
controller-produced execution records, including failures, stops, and unknown results. A model's PASS claim
or a matching command name is not execution evidence.
An implementer being unable to edit a registered script does not establish that another independent author
designed it or that it proves business correctness. Promote temporary probes into permanent tests only
when they cover a real, continuing risk.

Reuse an already valid test execution instead of automatically rerunning it at another stage. Confirm that
its inputs and relevant environment remain applicable and resolve later conflicting failures or unknown
executions before relying on an earlier PASS. This requires consistent success selection, failure handling,
and recovery; removing one final test call alone is insufficient. Repeated runs that actually establish
stability, baseline behavior, or new integration behavior remain justified.

Use the Issue-stage acceptance scenarios as the implementation becomes runnable. Complete their concrete
steps and execute applicable real user paths on the PR candidate, integration candidate, or preview before
merge where possible. Record what requires the deployment environment in advance and verify it there later.
An internal PR proves its contribution; it need not independently demonstrate a whole multi-Issue outcome.

## 6. Review every PR with two companies and exchange evidence

Before formal pass, two reviewers from different companies independently review the same accurate candidate,
adopted Issue, repository rules, and real code and test evidence. Both can discover their own findings and
investigate necessary callers; the second reviewer does not merely evaluate the first reviewer's summary.

The correctness lens emphasizes actual behavior, triggers, and evidence. The impact lens emphasizes callers,
compatibility, shared agreements, related work, and implementation complexity. Both cover the complete
required review scope; lenses are not a partition that leaves part of the candidate unreviewed.

After independent discovery, exchange concrete findings, counterevidence, and decision-relevant gaps. The
original engineer repairs or refutes findings. Both reviewers confirm the changed candidate and the
applicability of reused conclusions. Changes require review of their consequences, not necessarily a fresh
full-repository read. No fixed extra fact-verifier or synthesis agent is required. A clean review needs no
manufactured debate.

Final review outcomes remain:

- `PASS`: no unresolved blocking issue or decision-relevant evidence gap in the reviewed scope;
- `REWORK_REQUIRED`: implementation, documentation, tests, or necessary evidence needs work;
- `OWNER_DECISION_REQUIRED`: a substantive unresolved user choice blocks the affected work.

Nonblocking style suggestions need not reach consensus. Resolve technical disputes through evidence;
refer product choices to the user; retain essential unresolved gaps instead of voting them away. Specialist
investigation is triggered by a concrete gap, not automatically by every finding. Reviews do not grant
merge, deployment, resource, or spending permission.

Cross-company review adds a second review to a clean PR that previously could pass after one reviewer.
Reduced repetition in harder paths does not prove that every task will be cheaper or faster.

## 7. Integrate and receive the accurate result

A valid task may continue from H0 while the default branch advances. Display the actual base and whether it
is behind; integrate long-running work at a useful time. Continuing development, forming a candidate,
integrating with current main, and obtaining authority to publish are separate conditions.

Combine already reviewed immutable members with real combination validation and an independent reception
judgment. Member passes do not automatically establish that the combination works. A new PR retains the
dual-company requirement, with review focused on the composition and interaction where prior evidence
remains applicable.

If conflict repair, adaptation, configuration, dependency, or connection changes alter reviewed behavior,
obtain validation and independent conclusions for the new candidate. Reuse unaffected investigation and
facts; do not relabel old acceptance as acceptance of the new combination.

Final reception checks the adopted scope, exact candidate, applicable dual reviews, actual composition
and scenario evidence, outstanding blockers, and delivery conditions. It does not default to a third
complete code review. Refer a newly discovered gap to the existing review responsibility for focused work.
Merge and release proceed only under the actual effective delegation and target checks.

## 8. Accept the user outcome and explain the result

Acceptance starts in the Issue, becomes executable during development, and runs on suitable candidates.
After merge or deployment, verify only the parts that need that environment or whose evidence changed.
One outcome can include several Issues and PRs; share the outcome scenarios instead of rebuilding the plan
for every internal PR.

An implementation gap returns to the engineering owner. A change of goal, scope, or important semantics
returns to the requirement and decision process. An evidence or environment gap calls for the missing
verification. User acceptance comes from the actual user or an explicitly authorized acceptance mechanism;
passing tests, merging code, or a model's completion statement cannot fabricate it.

Ordinary delivery notes explain the observable change, use, actual verification, and remaining limits.
Provide a deeper mechanism walkthrough or HTML when the change warrants it or the user requests it.
Necessary documentation is maintained with implementation rather than first considered after merge.
The former FSD completeness closure step is not restored as a default gate.

## Throughout: adopted changes, progress, and recovery

Do not rewrite an active execution's target in place. Save incoming amendments separately, distinguish
clarification, in-scope supplement, and scope change, then adopt them at a supported continuation point.
Record the requirement version and work version that consume them, and which candidate implements them.
An adopted goal still requires implementation and verification evidence. Stop or withdrawal requests use
the actual stop mechanism instead of waiting in an ordinary amendment queue.

Old records keep their original bindings. A clarification or scope reduction may allow reuse of unchanged
code and evidence; establish their applicability to the new requirement without rewriting old records or
transferring an old PASS. Unknown effects are reconciled from the original operation before another writer
or retry is started. Engineering responsibility can continue across sessions with accurate saved inputs,
changes, candidates, evidence, unresolved work, and the next action.

Show expected finished behavior separately from actual engineering progress. The project view should reveal
what each item is for, what has actually been achieved, what is active or waiting, and the next useful action.
Distinguish phase, activity, result, and user outcome; use observed timestamps and explicit unknown states.
Do not invent progress percentages or treat model activity as verified advancement. The secretary and UI
read the same underlying records rather than maintaining another authoritative progress ledger.

## Adoption and coverage

The programming instructions come from this repository's fixed canonical sources. Tongxu or another
consumer supplies actual task data and enforces tools, permissions, isolation, and protocol checks. Loading
this README alone does not implement those behaviors. See [version adoption](version_adoption.md).

In-flight old work retains its original workflow, prompts, inputs, authority, and interpretation. New work
uses the selected supported version. Old prepared material does not acquire new write permission, and
unknown old execution cannot be silently migrated or retried. Preserve historical reading after retiring
an old execution path once its remaining responsibilities are settled.

English prose here is derived from the Chinese source. The long prompt bundle remains **en-pending**;
see the [English prompt catalog](../../prompts/README.md). Do not represent untranslated prompts as an
English-ready bundle. This coding-loop change leaves the document synchronization Skill's runtime and
publishing boundary below unchanged.

## Necessary artifacts and optional material

Ordinary work uses the adopted Issue, necessary shared agreements, actual code candidates and validation,
independent review findings, delivery, and outcome-acceptance records. The host reuses existing work and
execution records for accurate relationships; models need not maintain another ledger describing them.

Historical FSD, Bridge, and FSD-closure prompts remain available as optional or historical Chinese material
through the [prompt catalog](../../prompts/README.md). They are excluded from the default v2 source index
and cannot reappear as compulsory prerequisites for every Issue.

Assess complexity using actual benefits and existing work records: preserve necessary independent
challenge while removing repeated transcription, handoffs, and unconditional reruns. No dedicated new
evaluation platform is required to justify simplification. Lack of a trigger alone does not prove that a
mechanism has no value.

## Core project documents

The repository's core templates are language-, framework-, and project-neutral sources that consumers
adapt to their projects. Fixed policy is written as complete rules; project-specific facts use active
project-fill markers, which must be replaced or removed before the target's final checks. Documentation
sync implementation details stay in its canonical Skill instead of being distributed as generic project
rules. The [Directory Map](../../README.md#directory-map) owns the current template roles and entrypoints.

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

### Historical workflow decisions

DEC-008 records the previous development workflow and its experimental procedures. The current coding-loop
contract above replaces its mandatory upstream-document chain and fixed finding-verification sequence.
Its principles of justified complexity, evidence-based decisions, and retirement of redundant work remain
relevant. Read the [Chinese decision history](../../../zh/docs/development_workflow/decisions.md) for exact
supersession and rationale. This redesign does not change DEC-006 or DEC-007 behavior for Workflow Docs Sync.

Key implementation files for the unchanged documentation Skill:

- `../../../zh/skills/workflow-docs-sync/SKILL.md`: orchestration contract.
- `../../../zh/skills/workflow-docs-sync/agents/openai.yaml`: UI metadata.
- `../../../zh/skills/workflow-docs-sync/evals/README.md`: forward-eval cases.
- `../../../zh/skills/workflow-docs-sync/scripts/sync_docs.py`: mechanical preparation and check.
- `../../../tests/test_workflow_docs_sync.py`: regression and real-template quality tests.
