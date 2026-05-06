# <project name>: First-Time Business User Guide

> Status: experimental
> Audience: business users
> Scope: <project / agent / app name>
> Capability boundary source: `capability_contract.json`
> User-visible behavior source: `interact.md`
> Rule: This guide is a derived teaching document. It must not declare independent capabilities. Any "can do / cannot do / must ask / must refuse" statement must anchor to `capability_contract.json`, `interact.md`, or tests.
> Template note: all `<angle-bracket placeholders>`, sample case titles, and generic business scenarios are scaffolding only. Replace them with real project business questions before publishing.

This is a cross-project template. In a concrete project, keep only what a first-time business user truly needs; do not turn it into a complete feature manual.

## 1. Start Here: What Value Does It Provide?

Use three to five sentences to explain what business problem the system helps solve, what information it takes as input, and what judgment support it returns.

Do not independently promise new capabilities here. Capability statements must trace back to `capability_contract.json` or `interact.md`.

## 2. Best-Fit Business Questions

- **Sample capability: answer status, trend, or anomaly questions about one clear object**
  <!-- capability-anchor: CAPABILITY.sample_supported_question -->
  Replace this with a real project capability, written in business-user language.

## 3. Capability Boundaries

The current version does not support the following capabilities, though future versions may:

- **Sample boundary: comparing multiple objects in one request is not supported yet**
  <!-- capability-anchor: BOUNDARY.sample_multi_object_comparison_not_supported -->
  Replace this with a real project capability boundary.

## 4. Responsibility Boundaries

The system intentionally does not do the following:

- **Sample responsibility boundary: it does not make final business decisions for humans**
  <!-- capability-anchor: RESPONSIBILITY.sample_no_final_business_decision -->
  The system may provide evidence, explanations, and risk signals, but final business decisions remain with the responsible human.

## 5. First Use: Classify Your Question

Classify the question first, then provide context. Keep only the three to five most common question types, for example:

- I want to check whether one object changed noticeably.
- I want to understand why an abnormal result may have happened.
- I want to know whether current data is sufficient for a judgment.

## 6. What Context Should You Provide?

Business users should usually provide:

- Target object: which customer, product, region, model, or process you care about.
- Time range: which period matters.
- Judgment purpose: trend judgment, anomaly diagnosis, health check, or result explanation.
- Business context: known campaigns, strategy changes, or data definition changes.

If critical context is missing, the agent should ask follow-up questions instead of guessing.
<!-- capability-anchor: BEHAVIOR.sample_requires_context_before_answer -->

## 7. Common Business Cases

### Case 1: Check Whether One Object Is Abnormal

#### Business Question

I want to know whether `<object>` has changed abnormally recently.

#### Can This System Do It?

It can assist only when the capability is declared in `capability_contract.json` and the input context is sufficient.

#### Recommended Prompt

Please check whether `<object>` changed abnormally during `<time range>` and explain the main evidence.

#### What You Should See

You should see a conclusion, key evidence, limitations, and suggested next steps.

#### How to Read the Result

First check whether the evidence supports the conclusion, then decide whether more data or a responsible person is needed.

#### When Not to Ask This Way

Do not ask for a direct final judgment when the target object, time range, or data definition is unclear.

### Case 2: Understand Why a Result Changed

#### Business Question

I want to understand why `<metric / result>` changed.

#### Can This System Do It?

It should answer only when the project declares the corresponding explanation capability and data is sufficient.

#### Recommended Prompt

Please explain the change in `<metric / result>` during `<time range>`, separating verified evidence from inference.

#### What You Should See

You should see candidate causes, evidence sources, uncertain parts, and suggested missing information.

#### How to Read the Result

Do not treat inference as fact. Before making decisions, confirm key data sources and owners.

#### When Not to Ask This Way

Do not ask the system to make a final business decision when you actually need accountable human judgment.

### Case 3: Decide Whether to Escalate to a Human

#### Business Question

I want to know whether this issue can continue through system analysis, or whether I should ask an engineer, data owner, or model owner.

#### Can This System Do It?

If the project has the corresponding behavior commitment, the system should explain what input is needed and when to escalate.

#### Recommended Prompt

Please decide whether this issue can continue through system analysis. If not, explain who should be involved and why.

#### What You Should See

You should see missing conditions, escalation reasons, and suggested responsible roles.

#### How to Read the Result

If identity is ambiguous, data definitions are unclear, external systems are failing, or the decision is high risk, confirm with the responsible human first.
