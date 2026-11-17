# English Prompt Catalog

Status: **en-pending**. English workflow and version-adoption documentation are available, but the
programming prompt pack awaits translation and semantic-equivalence review.

The [Chinese prompt catalog](../../zh/prompts/README.md) and
[Chinese coding-loop source index](../../zh/prompts/coding_workflow.json) identify the canonical source.
Consumers use that `zh` source pack.

The index includes separate `finding_verification_fact` and `finding_verification_impact` purposes.
They load the common rules, the shared finding-verification procedure, and their own focus prompt, in
that order. Codex verifies facts and an LLM from another LLM company verifies impact independently;
they exchange evidence for up to three rounds. Confirmed problems are repaired in the Codex fact-verification
session, then returned to independent formal PR review by LLMs from two different companies.

The Issue author maintains the acceptance plan and its documented revisions, incorporating changes
supported by the engineering owner's findings. A demonstrable candidate receives a Tech Lead explanation
after necessary validation so the user can try and assess it; deployment-specific results are added later.

Consumers load the complete referenced source files from one adopted commit. They do not use a locally
translated, summarized, or rewritten substitute while claiming to run that source version. A reviewed
English bundle must be published as an explicit source change.

When a PR changes Chinese prompt semantics and does not update English prompt
coverage, mark `en-pending` in the PR body and keep English README links pointed
to this status page instead of exposing untranslated prompts as English-ready.
