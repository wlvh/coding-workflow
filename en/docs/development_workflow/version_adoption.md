# Fixed workflow versions and user-requested adoption

This is the English explanation of the
[Chinese adoption contract](../../../zh/docs/development_workflow/version_adoption.md).
It describes the contract a consumer such as Tongxu must implement.

## Source and execution responsibilities

coding-workflow owns the programming loop's natural-language behavior templates: Issue authorship
and review, investigation and implementation, self-review and repair, PR review
and evidence exchange, integration reception, user acceptance, and delivery explanation. This includes
instructions ultimately sent in system messages, developer messages, phase inputs, retries, or repair
requests; file extensions and transport fields do not create an exception.

Tongxu owns actual tool interfaces, permissions, workspaces, isolation, process and network effects,
stopping and recovery, dispatch, output schemas, and result validation. It supplies structured facts such
as the adopted Issue, user amendments, current candidate, available tools, actual scope, and test evidence.
Project instructions and effective user decisions remain identified project inputs. They are not copied
into upstream prompt templates merely to perform a task.

If an interface needs a natural-language programming instruction template, maintain that template in
coding-workflow and fill in actual runtime values. A local role prompt, arbitrary appended task policy,
hard-coded instruction, local translation, or summary must not silently change the adopted programming
rules.

This source-ownership requirement covers the programming loop. It does not move every secretary, account,
installation, or unrelated business-role prompt into coding-workflow.

## Minimal source interface

The canonical source is the
[Chinese source index](../../../zh/prompts/coding_workflow.json), with paths relative to the repository root:

| Field | Meaning |
|---|---|
| `schemaVersion` | Source-index format, currently `1` |
| `workflowId` / `workflowVersion` | Workflow identity and version, currently `coding-loop` / `2` |
| `executionContract` | Explicit controller contract, currently `coding-loop-v2` |
| `language` | Actual prompt source language, currently `zh` |
| `entrypoint` | Human-readable workflow in the same source commit |
| `roles` | Purpose to ordered `promptPaths` |

The index selects source files; it is not a language for arbitrary steps, loops, plugins, or permissions.
The same engineering owner can use different purposes at different stages.

Consumers read the index, README, and referenced files from one exact Git commit. Keep complete source
bytes and verify their content when loading them. Use only the source files applicable to the role instead
of giving every technical role the entire human-readable workflow. The source index owns the role-to-file
mapping; do not duplicate it in hard-coded controller constants.

The source index need not embed its own commit or hashes. The consumer's adoption record reuses existing
work and original-evidence storage to bind the upstream repository and commit, original index bytes and
hash, original source paths/bytes/hashes, ordered prompt composition, complete source-set identity, and the
compatible consumer execution version. Also retain actual providers and models, relevant tool/capability
versions, requirement and execution identity, candidate, authorization references, dynamic inputs, and
assembled messages. This avoids a self-referential release record and makes actual execution traceable.

The UI presents readable versions, source links, which new work they apply to, and unresolved conditions;
users need not hand-write JSON or SHAs. Pinning workflow sources and recording a particular execution does
not require a permanent admission allowlist of native-tool versions, paths, or binary hashes; apply the
consumer's effective minimum requirements and actual capability checks for runtime compatibility.
Verified snapshots can run offline. Missing files, modified bytes,
unknown protocols, or unsupported execution capabilities fail explicitly rather than fetching a moving
branch, substituting local prompts, or replacing the second company with another same-company model.

The canonical bundle is currently Chinese. See the [English prompt status](../../prompts/README.md).
An English product interface or this translated explanation does not turn it into an English bundle.

## User-facing update behavior

Distinguish a request to check for updates from a request to upgrade and enable them. A check reports
differences without switching the selected version. A valid request to upgrade can cover preparation,
implementation, verification, and activation within its delegation; do not add a compulsory approval at
each intermediate step. A substantive choice beyond that delegation still requires the user's decision.

### 1. Select an immutable target

Resolve the selected release or the current upstream default branch to a full commit when the update
starts. All subsequent source reads use that commit. If upstream moves again, show it as another available
update instead of silently changing the active update's target.

### 2. Compare sources and required behavior

Compare the adopted README, index, and all referenced prompt files with the target. Do not check only the
README or only long prompts: either can change independently.

Establish whether a change alters explanation, prompt behavior within supported interfaces, or execution
behavior that requires controller work. A wording change can alter review or acceptance semantics even
without changing the role list. Record required controller work in the upgrade task.

For example, a new rule requiring two companies to review every PR needs real distinct-provider dispatch,
accurate candidate binding, independent results, evidence exchange, and closure.

### 3. Prepare an inactive candidate version

Store the complete target source set without overwriting the adopted one. Reuse a single adoption record
as the runtime source of truth rather than maintaining one manifest plus separate hard-coded hashes.
Pair the prompt source set with an implemented compatible controller version. An unsupported execution
contract remains an explicit adaptation task; it does not activate partly or fall back silently.

When controller changes are required, use the normal engineering, review, and validation process. The
upgrade job itself retains its previously bound workflow. Runs exercising the proposed new version have
explicit test identities; they do not silently replace the rules judging the upgrade's own completion.

### 4. Verify the changes that matter

Validate complete source loading, source provenance of actual sent instructions, and the behavior changed
by the update. Examples include real cross-company
review, feedback and repair on a new candidate, continued repository investigation, and a controlled new
file that appears in the actual test environment.

Verify that prior work and historical results remain readable under their original definitions. Use
existing records and focused regression scenarios; do not create a general workflow simulator or a second
business-state ledger merely to install an update.

### 5. Activate for new work

Switch the supported prompt-and-controller pair together after the required verification. A failed update
leaves the previous default intact. An activation response must distinguish an imported source candidate,
an adapted and verified version, and a version actually selected for new work.

A rollback changes the default for subsequent work. It does not rewrite already sent executions or their
results. If old work requires an old executable to settle, keep or recover that supported path until its
remaining responsibilities are resolved; do not imply that changing a default pointer reverses external
effects or makes an incompatible controller safe.

## Existing work, pending work, and history

Bind the selected workflow and prompt source set at the explicit work-registration boundary, before the
first model input can drift with a changing global default. Existing work records keep their adopted
requirement, workflow and prompt versions, authority, code origin, candidate, and original execution identity.

- Active old executions continue or are reconciled under their original version. Do not rewrite their
  goal or prompts in place.
- Old prepared work does not acquire new tools, scope, or write authority by being reinterpreted as a new
  engineering-owner request. Explicitly adopt a new work version if it needs the new process.
- An amendment can create a new effective requirement version without silently upgrading its ongoing
  work's workflow. Keep those version identities distinct.
- Unknown execution is reconciled from its original operation, never automatically migrated or retried
  under a new identity.
- Historical source and result validation use the trusted source set adopted for that run, not today's
  default upstream commit and not an untrusted caller's self-declared hash.
- Once old in-flight responsibility is settled, retire its executable path while retaining historical
  reading. There is no requirement to maintain two complete engines indefinitely.

Old test facts can remain true and useful when requirements change. Preserve their original binding and
record the new applicability judgment; neither discard everything mechanically nor relabel an old PASS
as approval of a different goal or candidate.

## Acceptance of an importer or upgrade implementation

The consumer implementation must demonstrate all of the following through its real entrypoints:

1. A check and an upgrade have different effects; an update pins one source commit for its entire run.
2. The runtime loads complete sources from the adopted version without fetching a moving branch or using
   a locally rewritten programming policy as the canonical prompt.
3. Actual role dispatch and candidate-bound results implement the selected execution contract; missing
   behavior cannot be hidden behind successful source import. Both companies actually review the same
   Issue or candidate independently and exchange evidence; one company or a role name is insufficient.
4. Prompt and controller activation is consistent, failure preserves the old default, and new work uses
   the version actually selected.
5. Active, prepared, failed, stopped, unknown, and completed prior work retain their original meaning and
   permissions; recovery and historical reading do not require them to match the latest prompt.
6. A normal-entry engineering task continues investigation, reads material outside the original forecast,
   creates a controlled necessary file, and executes tests against the actual candidate and required inputs.
7. An integration candidate obtains matching validation and independent conclusions; reception reuses
   applicable dual reviews instead of adding a third complete code review.

These are consumer implementation requirements. The existing `workflow-docs-sync` Skill and installer
remain responsible for their documented project-document operations; they are not coding-loop importers.
