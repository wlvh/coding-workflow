# Coding Workflow

This workflow turns user requirements into an Issue, then delivers usable software through implementation,
testing, and independent review. The current version is **coding-loop v2**; see
[DEC-009](../../../zh/docs/development_workflow/decisions.md#dec-009issue-直接驱动的编程回路与固定版本采用)
for the decisions. The [role prompts and source index](../../../zh/prompts/README.md) are the single
maintenance entrypoint for model instructions. [Version adoption and updates](version_adoption.md)
define how downstream consumers adopt the workflow.

## Goals and default responsibilities

Issue and PR reviews both use **LLMs from two different LLM companies**. Each reviews independently before
the two actually exchange reports and conclusions. The engineering owner continues through investigation,
implementation, and testing. After verification, blocking review findings are repaired in the Codex
fact-verification session; the new version then receives independent review. Once a demonstrable result
has completed the necessary validation, provide a Tech Lead explanation and an entrypoint for user acceptance.

## 1. Express the goal in an Issue and provide an initial acceptance plan

The [Issue author](../../../zh/prompts/issue_agent.md) uses the user's original request, effective decisions,
and necessary repository facts to describe the user's problem, target behavior, necessary boundaries, and
completion criteria. Include actual dependencies, compatibility requirements, and unresolved product choices.

Keep requirements, shared agreements, and acceptance plans in the target project's GitHub Issues or
repository documentation. Put a task-specific requirement directly in its Issue. Store stable agreements
shared across Issues, necessary impact conclusions, or migration plans in the target repository's existing
documentation directories, with relevant Issues referencing specific versions.

**Document a user-perspective acceptance plan before development:** who starts from which real entrypoint,
which inputs and actions they use, what results they should observe, and how to recognize and continue after
important failures. Following the [user acceptance prompt](../../../zh/prompts/user_acceptance.md), the Issue
author writes the acceptance section or references an acceptance document in the target repository. Several
Issues or PRs contributing to one outcome may share one plan.

During development, the engineering owner proposes revisions supported by evidence. The Issue author updates
the document, recording the date, reason, changed items, and effects on existing results while preserving the
original requirements and revision history. Changes to the goal or key criteria return to the Issue's decision
process and the affected requirement review. Every acceptance result identifies the adopted plan version,
code candidate, and environment. Run suitable scenarios as soon as a candidate is runnable, then complete
target-environment-specific checks after deployment.

## 2. Review the Issue with LLMs from two different LLM companies

Give the same Issue version to the two independent reviewers:

- [Completeness and acceptance review](../../../zh/prompts/issue_review_completion.md): check fidelity to the
  original goal, missing necessary behavior, and whether success and important failures can be judged.
  Do not expand the requirement just because more cases are imaginable.
- [Minimum sufficient scope review](../../../zh/prompts/issue_review_minimality.md): prioritize deletion,
  reuse, consolidation, and reduction; check for mechanisms built to solve problems introduced by the proposal
  itself. No fixed reduction percentage is required, and necessary functionality must remain.

In independent contexts, both read the original request, the same Issue, traceable repository facts, and
related work, checking decisive facts when needed. After their initial reviews, follow the
[evidence exchange rules](../../../zh/prompts/review_exchange.md) to exchange original reports and respond
to disagreements. Even when neither finds a blocker, briefly confirm the same version and review coverage.

Separate blocking problems, nonblocking suggestions, and new ideas. New ideas enter the task only after
adoption; agreement between the reviewers does not expand the user's requirements. The Issue author updates
the body, and both reviewers recheck changes and unresolved blockers, giving conclusions for the final
version before handing it to the engineering owner. They may reference unchanged material that remains valid.

## 3. Keep investigation and implementation with the same engineering owner

The [engineering owner](../../../zh/prompts/engineering_owner.md) receives the reviewed Issue, necessary
shared agreements, and acceptance plan, and fixes the requirement version, starting code revision H0, and
adopted workflow version. Begin with read-only investigation, then implement autonomously within the existing
delegation. Make ordinary implementation choices directly; raise specific questions for the user when goals,
key behavior, or actual permissions need to change.

### Trace requirements to implementation and evidence

Use this short prompt to start:

```text
Implement the current Issue.
1. Read AGENTS.md, then follow its document relationships to the applicable SOP.md, TESTING.md, PR_Checklist.md, and interact.md. Where capability_contract.json or docs/business_user_guide.md exists, inspect the public commitments and usage guidance relevant to this task.
2. Extract independently verifiable Spec Units (SUs), reuse their existing IDs, and maintain an SU -> code change -> test -> documentation todo that evolves with the investigation.
3. Follow TESTING.md for test strategy and evidence recording.
4. Identify tests to reuse, parameterize, or add. For cross-module behavior, name the concrete scenario proving the combined path. One scenario may cover several SUs; do not mechanically add a test for every SU or finding.
```

Update the expected file list as investigation progresses. Within the authorized scope, inspect additional
callers and choose the files to create, modify, delete, or rename. Tests use the actual code version, necessary
dependencies, and configuration to cover real execution paths. Ordinary project tests evolve with the
implementation and receive review; changes to key business acceptance criteria follow Section 1.

When changing sessions or continuing after interruption, preserve the adopted versions, actual changes,
validation results, open questions, and next steps. Follow the [common rules](../../../zh/prompts/coding_common.md)
to reconcile the original execution and writing responsibility before continuing.

## 4. Test, self-review, and create a Draft PR

Reuse real project tests and scenarios, parameterizing them or adding assertions to fill coverage gaps.
For changes spanning interfaces, persistence, or user paths, choose validation that demonstrates the combined
behavior. Keep temporary probes as permanent tests only when they cover a real, continuing risk.

Test records identify the exact code version (candidate), validation definition, relevant environment, and
original output. Reuse an effective validation result, but do not select a historical PASS while ignoring
later unresolved failures or unknown results. When coverage gaps, test definitions, environments, or
candidates change, identify affected areas and perform the necessary additional validation. Stability reruns,
baseline experiments, and new combination tests serve different purposes and are not automatically redundant.
Both success and failure recovery reference actual execution records and retain failures and unknown results.

After self-review, necessary documentation, and real validation, the implementer creates or updates a Draft PR
within the effective delegation. Follow the target repository's commit policy and PR template. Keep temporary
PR-body files outside the repository and out of commits. Describe actual changes, validation, and limitations,
reference the Issue, and give the exact candidate and validation evidence to both independent reviewers.

## 5. Review PRs across LLM companies, verify findings within three rounds, and repair in Codex

The two reviewers use [correctness review](../../../zh/prompts/pr_review_correctness.md) and
[impact and necessity review](../../../zh/prompts/pr_review_impact.md), respectively, together with the
[complete PR review standard](../../../zh/prompts/pr_review_system.md). Each independently reviews the same
exact candidate in full, then exchanges original reports under the
[evidence exchange rules](../../../zh/prompts/review_exchange.md).

- Findings state specific triggering conditions, causal paths, impact, and evidence. Inspect callers and run
  authorized validation or reproductions when needed to establish important claims.
- Exchange initial findings and conclusions. Send P0/P1 and other blocking findings requiring action into the
  verification process below as a batch; list nonblocking suggestions separately.
- Reuse unchanged investigation that remains valid. Each new candidate needs both reviewers' conclusions
  matching its actual contents and scope, without mechanically rereading the entire repository.
- Even when neither initial review finds a blocker, briefly exchange conclusions and confirm the same candidate
  and coverage. Resolve factual disputes through evidence, refer product choices to the effective decision-maker,
  and retain key unresolved evidence gaps.
- Ordinary style suggestions need not reach consensus. Bound exchanges by the agreed resources; when there
  is no new evidence or the limit is reached, state the gap and next action rather than repeating indefinitely.

### Verify findings and exchange evidence

Give the same candidate and batch of findings to two new independent verification contexts. OpenAI's Codex uses the
[fact verification prompt](../../../zh/prompts/finding_verification_fact.md) to check whether findings are real,
their triggering paths, reproduction, and severity. An LLM from a different LLM company uses the
[impact verification prompt](../../../zh/prompts/finding_verification_impact.md) to check upstream and downstream
effects, similar entrypoints, root causes, and the smallest sufficient repair. Both first produce independent
verification results, then exchange evidence; Codex synthesizes the results.

After independent verification, allow **at most three exchange rounds** under the
[verification process](../../../zh/prompts/finding_verification.md). Each round addresses specific disagreements
and retains both reports. End early when the conclusions are sufficiently supported. If key evidence is still
missing after three rounds, retain `REWORK_REQUIRED` and list the actions needed to obtain it. Refer product
choices to the user once the relevant facts are clear. If counterevidence refutes the whole batch and the code
remains unchanged, the formal reviewers check that counterevidence and close the findings.

### Repair in the Codex verification session, then review independently

Repair confirmed findings that require changes in the same Codex fact-verification session. The original
writer hands over the actual candidate, existing changes, and evidence; the executor checks writing
responsibility and authorization before enabling writes. That session updates code, necessary tests and
documentation, the PR body, and the Review / Fix Record. If the session cannot be resumed, a successor Codex
session verifies the relevant facts from the original records, then repairs in that session and records the
continuation relationship.

LLMs from two different LLM companies independently review the exact repaired candidate; the repairer cannot
sign its own formal approval. Review actual differences, their effects, and unresolved findings, reusing
investigation that remains valid, to form both reviewers' complete conclusions for the current candidate.
Newly discovered blockers enter verification, exchange, and repair again. Verification conclusions do not
replace formal PR review.

Use `PASS`, `REWORK_REQUIRED`, and `OWNER_DECISION_REQUIRED`. PASS requires completion of all necessary reviews,
with no unresolved blockers or key evidence gaps. A clean PR still requires both complete independent initial
reviews and an actual exchange.

## 6. Handle base changes, integrate, and deliver under the effective delegation

When the original goal and delegation remain valid, work may continue from H0 to form its candidate. Report
the actual base and whether it is behind at delivery; integrate long-running work at an appropriate time.
A moving main branch does not automatically require repeating all investigation, but being able to continue
development does not establish that the result can be merged or released.

The receiver uses the [integration acceptance prompt](../../../zh/prompts/integration_acceptance.md) to check
the exact deliverable, valid conclusions from both LLM companies, combination validation, blockers, and
delivery conditions, reusing valid code-review and validation evidence.

When combining already reviewed immutable members, reuse their valid conclusions and add combination
validation and an independent acceptance judgment. Individual member passes do not establish that the
combination passes. If integration changes code, configuration, dependencies, activation, or connections
in ways that materially affect reviewed content or the applicability of evidence, validate the differences
and effects and obtain matching conclusions from LLMs of both companies. A new integration PR still requires
dual review, which can focus on the combination and new effects. The integrator cannot sign its own independent
approval.

Merge, enable, or deploy under the effective delegation, checking the actual delivered candidate and recording
the result. Complete already authorized actions autonomously.

## 7. Give a Tech Lead explanation after development and accept the user outcome

Once a candidate is ready to demonstrate and has completed the necessary validation, the engineering owner uses the
[post-development explanation prompt](../../../zh/prompts/delivery_explanation.md) to explain actual functionality,
mechanisms, development choices, and acceptance results, helping the user understand and try the outcome:

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
changes, when needed for understanding, or when explicitly requested. State whether the current candidate
has been tested, reviewed, merged, or enabled, and which parts still await the user's experience and confirmation.

Follow the [user acceptance prompt](../../../zh/prompts/user_acceptance.md) to execute the plan's real scenarios.
Verify runnable candidates early, complete checks specific to the target environment after deployment, and
update the delivery explanation. The user can consult the plan for actions, expected results, and execution
evidence before deciding whether to accept. For an outcome spanning several Issues or PRs, validate the
complete user path.

Implementation gaps in the original goal follow Section 5 for verification, repair, and independent review.
Changes to the goal, scope, or key semantics return to the Issue's decision process. Acceptance results
reference the actual plan version, and plan revisions remain recorded. User acceptance corresponds to an
actual user decision or explicit delegation.

## Throughout: requirement changes and recovery

Record new requirements as revisions. The engineering owner determines whether each is a clarification,
an in-scope supplement, or a scope change. The current execution completes or stops under its original input;
at a supported continuation point, record the adopted revision and the work responsible for carrying it
forward. Stop and withdrawal requests go directly through stop controls.

Old candidates and validation results retain their original scope. Explicitly reference facts that can be
reused under the new requirement and continue any necessary changes or validation. Handle old and new work
and workflow upgrades under the [version-adoption rules](version_adoption.md).

## Necessary artifacts and optional material

Ordinary work uses the adopted Issue, necessary shared agreements, code candidates and actual validation,
independent review findings, delivery records, and outcome-acceptance records. Cross-reference these records
and use the project's existing storage locations. For a shared specification or migration plan, use the
[optional material](../../../zh/prompts/README.md#保留的按需历史材料) and state its scope.

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
