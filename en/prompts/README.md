# English Prompt Catalog

Status: **en-pending**. English workflow and version-adoption documentation are available, but the
programming prompt pack has not been translated and reviewed for semantic equivalence. This directory
does not expose an English-ready prompt bundle.

The [Chinese prompt catalog](../../zh/prompts/README.md) and
[Chinese coding-loop source index](../../zh/prompts/coding_workflow.json) identify the canonical source.
Their language is explicitly `zh`; an English UI or this English overview does not change that identity.

Consumers load the complete referenced source files from one adopted commit. They do not use a locally
translated, summarized, or rewritten substitute while claiming to run that source version. Adding a
reviewed English bundle is a separate source change, not a silent runtime adaptation.

When a PR changes Chinese prompt semantics and does not update English prompt
coverage, mark `en-pending` in the PR body and keep English README links pointed
to this status page instead of exposing untranslated prompts as English-ready.
