# Development Workflow

This is the English overview of the repository's human-in-the-loop coding workflow. The Chinese workflow
is the semantic source; this file closes the English meaning for the workflow content changed in this PR.

## Main Flow

1. Define the requirement.
2. Draft the `FSD Core Contract` with the Pro web model when direct repository exploration is unavailable.
3. Compare the FSD, current repository code, and authoritative documents to produce the `Repo Impact
   Forecast` and `Target State Bridge`.
4. Turn the FSD, forecast, and bridge into an executable issue contract.
5. Implement the issue after reading `AGENTS.md`, `SOP.md`, `TESTING.md`, `PR_Checklist.md`,
   `interact.md`, and project capability or business-user documents.
6. Review business intent first, then implementation correctness, test realism, maintainability, and
   documentation impact. Check the changed scope against `.github/pull_request_template.md`,
   `docs/business_user_guide.md`, `AGENTS.md`, `architecture.md`, `capability_contract.json`, `interact.md`,
   `PR_Checklist.md`, `SOP.md`, and `TESTING.md` where relevant.
7. Verify each reviewer finding through code reading, a minimal reproduction, targeted tests, or a path
   close to real use before changing code. Preserve finding IDs and closure evidence in the existing PR
   review / fix record and GitHub threads; do not create a second reconciliation ledger.
8. Follow the repository's current commit policy. A one-commit approach is a replaceable team default, not
   a universal rule. Build the PR body as temporary Markdown outside the repository from
   `.github/pull_request_template.md`, and let general GitHub publishing capability read it.
9. After merge, summarize runtime mechanisms and tradeoffs from code evidence, then perform user-view
   acceptance when useful.

## Core Artifacts

- `FSD Core Contract`: a requirement contract that can be implemented, tested, and reviewed.
- `Repo Impact Forecast`: predicted repository touchpoints, risks, documentation, and test impact.
- `Target State Bridge`: target user- or caller-visible state and its validation method.
- `Issue`: the executable development contract.
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

Key implementation files:

- `../../../zh/skills/workflow-docs-sync/SKILL.md`: orchestration contract.
- `../../../zh/skills/workflow-docs-sync/agents/openai.yaml`: UI metadata.
- `../../../zh/skills/workflow-docs-sync/evals/README.md`: forward-eval cases.
- `../../../zh/skills/workflow-docs-sync/scripts/sync_docs.py`: mechanical preparation and check.
- `../../../tests/test_workflow_docs_sync.py`: regression and real-template quality tests.
