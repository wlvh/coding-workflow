# English Prompt Catalog

Status: **en-pending**. English workflow and version-adoption documentation are available, but the
programming prompt pack awaits translation and semantic-equivalence review.

The [Chinese prompt catalog](../../zh/prompts/README.md) and
[Chinese coding-loop source index](../../zh/prompts/coding_workflow.json) identify the canonical source.
Consumers use that `zh` source pack.

Consumers load each referenced file's complete UTF-8 Markdown, including code blocks, in index order
from one adopted commit. Files already loaded need not be read again. Fixed-source and update requirements
are in the [version-adoption contract](../docs/development_workflow/version_adoption.md).

When a PR changes Chinese prompt semantics and does not update English prompt
coverage, mark `en-pending` in the PR body and keep English README links pointed
to this status page instead of exposing untranslated prompts as English-ready.
