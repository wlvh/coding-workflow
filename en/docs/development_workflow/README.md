# Coding Workflow

## 1. Write the Issue

Inspect relevant code and existing functionality, then write an implementable Issue covering:

- The user's problem and the expected behavior.
- The scope, necessary interfaces, and compatibility requirements.
- Initial conditions, actions, expected results, and important failure behavior for acceptance.

Add shared agreements, data migration, or staged release plans to the Issue or linked documentation when
needed. Split work into sub-Issues only when distinct owners will work in parallel and the work can be
implemented and accepted independently.

Use the [Issue writing prompt](../../../zh/prompts/issue_agent.md).

## 2. Review the Issue

Use **two LLMs from two different LLM companies**, in independent contexts, to review the same Issue
version, original request, and relevant code facts:

- [Completeness and acceptance](../../../zh/prompts/issue_review_completion.md): Does it reflect the user's goal, cover necessary behavior, and provide acceptance criteria that distinguish success from failure?
- [Minimum sufficient scope](../../../zh/prompts/issue_review_minimality.md): Which requirements can be removed, combined, or met with existing capabilities? How can the goal be achieved with fewer changes?

Both LLMs review independently before exchanging findings. The Issue author updates the body, and both
reviewers check the changes and unresolved problems. Resolve blockers before implementation; list newly
suggested features separately for the user to decide whether to adopt.

## 3. Implement, test, and submit a PR

The same engineering owner (the coding agent) handles investigation, implementation, testing, and subsequent fixes.
Read relevant source code, callers, and tests according to project conventions. Choose the smallest
sufficient implementation and adjust the change scope as investigation progresses. Record decisions
affecting goals, public interfaces, or compatibility agreements in the Issue.

Reuse existing code and tests, adding validation for new behavior, important failure paths, and interactions
between modules. Run the Issue's user scenarios as soon as the code is runnable. Reuse valid test results
when candidate contents, test definitions, and necessary environments match; investigate subsequent failures
before relying on a conclusion.

Complete self-review, update affected usage guides and project documentation, and create or update a Draft PR.
Describe actual changes, test results, and unresolved problems, and link the Issue. When changing sessions,
hand over the current code, verified results, open questions, and next steps.

Use the [engineering owner prompt](../../../zh/prompts/engineering_owner.md).

## 4. Review the PR and address feedback

Use **two LLMs from two different LLM companies**, in independent contexts, to each review the same code
version in full. Both use the [complete PR review standard](../../../zh/prompts/pr_review_system.md), with
additional focus on [correctness](../../../zh/prompts/pr_review_correctness.md) and
[impact and necessity](../../../zh/prompts/pr_review_impact.md), respectively.

Both first inspect code and tests independently, then exchange findings and conclusions using the
[evidence exchange prompt](../../../zh/prompts/review_exchange.md). Even when neither initial review finds
a blocker, they must briefly exchange conclusions and confirm the code version, coverage, and any omissions.

Each finding states its triggering conditions, code evidence, and actual impact. The original engineering
owner fixes the problem or provides counterevidence. Both reviewers check the changes and their effects,
then give conclusions for the updated code version. Resolve technical disputes through source code, tests,
or reproductions; refer product choices to the user. Proceed to integration after both reviewers approve.

## 5. Integrate and release

Combine the changes with the target branch and related work. Verify interfaces, configuration, dependencies,
and complete usage paths, reusing test and review conclusions that remain applicable.

When integration changes code, configuration, dependencies, activation, or connections in ways that materially
affect reviewed behavior or the applicability of prior evidence, perform additional validation and have both reviewing LLMs
give conclusions on the new version's differences and effects. Focus the review on affected areas.

Use the [integration acceptance prompt](../../../zh/prompts/integration_acceptance.md) to check the final
version, review conclusions, and validation results. Have a reviewing LLM confirm delivery conditions,
then merge and release according to the project's process.

## 6. Accept the user outcome

Check the outcome through real usage entrypoints using the Issue's scenarios. Start acceptance on a runnable
candidate as early as possible, then complete checks specific to the target environment after deployment.
Accept outcomes spanning multiple PRs together.

Return implementation gaps in the original goal to the engineering owner for repair. Update the Issue first
when goals, scope, or key behavior change. Delivery notes explain where the result is, how to use it, what
was verified, and what limitations remain. Use examples or diagrams to explain complex mechanisms.

Use the [user acceptance prompt](../../../zh/prompts/user_acceptance.md) and
[delivery notes prompt](../../../zh/prompts/delivery_explanation.md).

## Related resources

- [Chinese prompt sources and source index](../../../zh/prompts/README.md)
- [English prompt status](../../prompts/README.md)
- [Version adoption for automation tools](version_adoption.md)
- [Project documentation synchronization and repository maintenance](../../README.md)
