# Development Workflow

This is the English overview of the [Chinese semantic source](../../../zh/docs/development_workflow/README.md).
It defines the generic coding loop supplied by coding-workflow and the engineering behavior required of
an executing consumer. The current contract is **coding-loop v2**, adopted in
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

The default path is: form an Issue and a user-perspective acceptance plan; review the Issue with two LLM
companies; investigate, implement, and test under one engineering responsibility; perform dual-company PR
review; verify blocking findings and repair them in Codex; integrate and receive the result; accept the user
outcome; and give a Tech Lead explanation after development.

Issue review and PR review each involve **two LLMs from two different LLM companies**, independent contexts,
and distinct review lenses. Provider choices are configurable. Two prompts, two sessions, or two models from
one company do not satisfy the cross-company requirement. Actual provider and execution records establish
participation; role names and intended dispatches do not. If the second company is unavailable, report the
review as incomplete rather than silently reducing the requirement.

One engineering responsibility continues through investigation, implementation, and tests. Verified findings
requiring repair are fixed in the Codex fact-verification session. Handovers preserve the accurate candidate,
changes, evidence, and unresolved questions. The host maintains the actual permission, workspace, candidate,
operation, and evidence boundaries. Existing adequate delegation does not create a new compulsory
plan-approval step.

These sections describe responsibilities, not a requirement for a separate agent, document, or model call
at every heading. Investigation, implementation, and testing may alternate; stopping and recovery remain
relevant throughout. Product-specific secretarial work, project coordination, dashboards, and upgrade
entrypoints belong to the executing product, not this generic engineering workflow.

## 1. Form an Issue and document its initial acceptance plan

The Issue author uses the user's original intent, existing decisions, relevant repository facts, and
related work. Include the user goal and observable result, necessary boundaries, acceptance scenarios,
shared agreements or dependencies that actually matter, and unresolved user choices. Do not demand a
large fixed template for every task or re-create the three retired documents as compulsory sections.

Store requirements, shared agreements, and acceptance plans in the target project's GitHub Issues or
documentation in its GitHub repository. Put a task-specific requirement directly in its Issue. Store stable
agreements shared across Issues in the target repository's existing documentation directories, with each relevant
Issue referencing the specific version. The executing system retains the adopted source, version, and
snapshot for execution and recovery.

**Document a user-perspective acceptance plan before development:** who starts from which real entrypoint,
which inputs and actions they use, what results they should observe, and how to recognize and continue after
important failures. Write the plan in the Issue's acceptance section or link an acceptance document in the
target repository. Several Issues or PRs contributing to one outcome may share one plan.

The plan may be revised during development. Document the revision date, reason, changed items, and effects
on existing results; preserve the original requirements and revision history. Changes to the goal or key
criteria return to the Issue's decision process and the affected requirement review. Every acceptance
result identifies the adopted plan version, code candidate, and environment. Run suitable scenarios as
soon as a candidate is runnable, then complete target-environment-specific checks after deployment.

## 2. Review the Issue with LLMs from two different LLM companies

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

## 3. Investigate and implement under continuous responsibility

Bind the actual requirement snapshot, work version, initial code version H0, adopted workflow and prompt
version, and valid delegation before execution. Begin with read-only investigation. If the resulting work
remains within valid delegation, continue without a fixed per-file approval or a second preparation owner.
Use AGENTS.md and the actual task routing to read relevant instructions, source code, callers, and tests;
do not require a complete reread of every document for every task.

### Trace requirements to implementation and evidence

The short implementation prompt below is backed by the full `engineering_owner` prompt:

```text
Implement the current Issue.
1. Read AGENTS.md, then follow its document relationships to the applicable SOP.md, TESTING.md, PR_Checklist.md, and interact.md. Where capability_contract.json or docs/business_user_guide.md exists, inspect the public commitments and usage guidance relevant to this task.
2. Extract independently verifiable Spec Units (SUs), reuse their existing IDs, and maintain an SU -> code change -> test -> documentation todo that evolves with the investigation.
3. Follow TESTING.md for test strategy and evidence recording.
4. Identify tests to reuse, parameterize, or add. For cross-module behavior, name the concrete scenario proving the combined path. One scenario may cover several SUs; do not mechanically add a test for every SU or finding.
```

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

## 4. Validate the candidate and exercise user paths early

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

## 5. Review PRs across LLM companies, verify findings within three rounds, and repair in Codex

Two LLMs from two different LLM companies use `pr_review_correctness` and `pr_review_impact`, respectively.
Both independently complete a full review of the same accurate candidate, adopted Issue, repository rules,
and real code and test evidence using the detailed review standard. Both can discover their own findings
and investigate necessary callers; the second reviewer does not merely evaluate the first reviewer's summary.

The correctness lens emphasizes actual behavior, triggers, and evidence. The impact lens emphasizes callers,
compatibility, shared agreements, related work, and implementation complexity. Both cover the complete
required review scope. Complete the initial reviews in independent contexts before exchanging evidence.

- Findings state specific triggering conditions, causal paths, actual impact, and supporting evidence.
  Inspect callers and run authorized validation or reproductions when needed to establish important claims.
- Exchange the initial findings and conclusions. Send P0/P1 and other blocking findings requiring action
  into the verification process below as a batch; list nonblocking suggestions separately.
- Reuse unchanged investigation that remains valid. Each new candidate needs both reviewers' conclusions
  matching its actual contents and scope, without mechanically rereading the entire repository.
- Even when neither initial review finds a blocker, both reviewers must actually exchange conclusions and
  briefly confirm the same candidate, coverage, and any omissions. Retain that exchange without manufacturing
  a debate. Resolve factual disputes through evidence, refer product choices to the user, and retain essential
  unresolved evidence gaps.
- Ordinary style suggestions need not reach consensus. Bound exchanges by the agreed resources; when there
  is no new evidence or the limit is reached, state the gap and next action rather than repeating indefinitely.

### Verify findings and exchange evidence

Give the same candidate and batch of findings to two new independent verification contexts. OpenAI's Codex uses
`finding_verification_fact` to check whether findings are real, their triggering paths, reproduction, and
severity. An LLM from a different LLM company uses `finding_verification_impact` to check upstream and
downstream effects, similar entrypoints, root causes, and the smallest sufficient repair. Both first produce
independent verification results, then exchange evidence; Codex synthesizes the results.

Allow **at most three exchange rounds**, as in the original process. Each round addresses specific
disagreements and retains both reports. End early when the conclusions are sufficiently supported. If key
evidence is still missing after three rounds, retain `REWORK_REQUIRED` and list the actions needed to obtain
it. Refer product choices to the user once the relevant facts are clear. If counterevidence refutes the whole
batch and the code remains unchanged, the formal reviewers check that counterevidence and close the findings.

### Repair in the Codex verification session, then review independently

Repair confirmed findings that require changes in the same Codex fact-verification session. The original
writer hands over the actual candidate, existing changes, and evidence; the executor checks writing
responsibility and authorization before enabling writes. That session updates code, necessary tests and
documentation, the PR body, and the Review / Fix Record. If the session cannot be resumed, reconcile the
original execution first. A successor Codex session verifies the relevant facts from the original records,
then repairs in that session and records the continuation relationship.

Two LLMs from two different LLM companies independently review the exact repaired candidate; the repairer
cannot sign its own formal approval. Review the actual differences, their effects, and unresolved findings,
reusing investigation that remains valid, to form both reviewers' complete conclusions for the current
candidate. Newly discovered blockers enter verification, exchange, and repair again. Verification conclusions
do not replace formal PR review.

Final review outcomes remain:

- `PASS`: all required reviews are complete, with no unresolved blocking issue or key evidence gap;
- `REWORK_REQUIRED`: implementation, documentation, tests, or necessary evidence needs work;
- `OWNER_DECISION_REQUIRED`: a substantive unresolved user choice blocks the affected work.

A clean PR still requires both complete independent initial reviews and an actual exchange.

## 6. Integrate and receive the accurate result

A valid task may continue from H0 while the default branch advances. Report the actual base and whether it
is behind at delivery; integrate long-running work at a useful time. Continuing development, forming a candidate,
integrating with current main, and obtaining authority to publish are separate conditions.

Combine already reviewed immutable members with real combination validation and an independent reception
judgment. Member passes do not automatically establish that the combination works. A new PR retains the
dual-company requirement, with review focused on the composition and interaction where prior evidence
remains applicable.

If conflict repair, adaptation, configuration, dependency, activation, or connection changes materially alter
reviewed content or the applicability of evidence, validate the differences and their effects. Both reviewing
LLMs, from two different LLM companies, must provide matching conclusions on those differences and effects for
the new candidate, even if tests pass, no defect has yet been found, and no new PR is created. Reuse unaffected
investigation and facts; do not
relabel old acceptance as acceptance of the new combination. The integrator cannot self-approve independent
reception or review.

Final reception checks the adopted scope, exact candidate, applicable dual reviews, actual composition
and scenario evidence, outstanding blockers, and delivery conditions. It does not default to a third
complete code review. Refer a newly discovered gap to the existing review responsibility for focused work.
Merge and release proceed only under the actual effective delegation and target checks.

## 7. Accept the user outcome and give a Tech Lead explanation after development

Acceptance starts in the Issue, becomes executable during development, and runs on suitable candidates.
After merge or deployment, verify only the parts that need that environment or whose evidence changed.
One outcome can include several Issues and PRs; share the outcome scenarios instead of rebuilding the plan
for every internal PR.

Turn an implementation gap in the original goal into an evidenced finding and follow Section 5 for
verification, repair, and independent review. A change of goal, scope, or important semantics returns to the
Issue and decision process. An evidence or environment gap calls for the missing verification. Acceptance
results reference the plan version actually used, and plan revisions remain documented. User acceptance
comes from the actual user or an explicitly authorized acceptance mechanism; passing tests, merging code,
or a model's completion statement cannot fabricate it.

After development, use `delivery_explanation` to explain the delivered functionality, actual mechanisms,
and choices made during development in terms of user outcomes:

```text
Development is complete. From a Tech Lead's perspective, use the actual code, development records, and acceptance results to help me understand:
1. The original goal, core value, and how much has actually been completed.
2. How users work before and after the change, with concrete cases showing inputs, actions, results, and important failures.
3. How the key mechanisms work and how the modules cooperate, so I can manually walk through normal, failure, and recovery paths.
4. Problems encountered during development, alternatives considered, and why the final approach was chosen; which complexity was removed or retained, with its costs and supporting evidence.
5. Looking back, if development effort were reduced by about 50%, what would the smallest solution be? What would it retain or give up, and which judgments remain assumptions?
6. Which version of the user-perspective acceptance plan was used, the results, why the plan changed, and remaining limits and necessary follow-up.
```

Give every outcome an explanation proportionate to its complexity. Use detailed HTML or diagrams for major
changes, when needed for understanding, or when explicitly requested. Necessary documentation is maintained
with implementation rather than first considered after merge. The former FSD completeness closure step is
not restored as a default gate.

## Throughout: requirement changes and recovery

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

The executing consumer supplies actual task data and enforces tools, permissions, isolation, and protocol
checks. Existing-work compatibility, historical reading, and changes to the default workflow version follow
the [version-adoption contract](version_adoption.md); product-specific coordination and progress views are
outside this document.

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
contract above replaces its mandatory upstream-document chain.
Its principles of justified complexity, evidence-based decisions, and retirement of redundant work remain
relevant. Read the [Chinese decision history](../../../zh/docs/development_workflow/decisions.md) for exact
supersession and rationale. This redesign does not change DEC-006 or DEC-007 behavior for Workflow Docs Sync.

Key implementation files for the unchanged documentation Skill:

- `../../../zh/skills/workflow-docs-sync/SKILL.md`: orchestration contract.
- `../../../zh/skills/workflow-docs-sync/agents/openai.yaml`: UI metadata.
- `../../../zh/skills/workflow-docs-sync/evals/README.md`: forward-eval cases.
- `../../../zh/skills/workflow-docs-sync/scripts/sync_docs.py`: mechanical preparation and check.
- `../../../tests/test_workflow_docs_sync.py`: regression and real-template quality tests.
