# Architecture

## 0. Scope and Update Triggers

This document is the authority for the current system structure. Update or confirm the relevant section
when runtime entrypoints, module boundaries, call flows, data contracts, state, error models, external
dependencies, authentication, configuration, artifacts, side effects, extension points, or architecture
debt change. Every claim must come from current implementation, configuration, tests, committed artifacts,
or reproducible evidence.

<!-- project-fill: Describe the system boundary, exclusions, and project-specific update triggers, then remove this marker. -->

## 1. System Purpose

<!-- project-fill: In no more than five sentences, describe verified users, inputs, outputs, and core value, then remove this marker. -->

## 2. Runtime Entrypoints and Main Flows

<!-- project-fill: Describe main call flows, important branches, and final outputs from real entrypoints. If there is no runtime entrypoint, write Not applicable with a verified reason, then remove this marker. -->

## 3. Architecture Invariants

Each invariant should state the positive constraint, scope, falsification method, and consequence of
violation. Do not present a vision or proposed design as a current invariant.

<!-- project-fill: Add architecture invariants supported by code, configuration, or tests. If none exist, write Not applicable with a verified reason, then remove this marker. -->

## 4. Module Responsibility Boundaries

Describe stable modules by responsibility, non-responsibility, permitted dependencies, and forbidden
dependencies. Do not copy the repository tree file by file.

<!-- project-fill: Describe core module boundaries and dependency direction with precise implementation evidence, then remove this marker. -->

## 5. Data Flow and Data Contracts

<!-- project-fill: Describe how inputs are parsed, transformed, validated, and emitted, including schema, version, and boundary contracts. If there is no data flow, write Not applicable with a verified reason, then remove this marker. -->

## 6. State and Persistence Model

<!-- project-fill: Describe in-process state, persistence, caches, idempotency, and lifecycle. If there is no persisted state, write Not applicable with a verified reason, then remove this marker. -->

## 7. Error and Failure Model

<!-- project-fill: Describe real validation, degradation, retry, hard-failure, rollback, and user-visible error boundaries, then remove this marker. -->

## 8. External Dependencies, Authentication, and Configuration

<!-- project-fill: List real external dependencies, authentication boundaries, configuration sources, and missing-configuration behavior. If none exist, write Not applicable with a verified reason, then remove this marker. -->

## 9. Artifacts and Side Effects

<!-- project-fill: Distinguish committed, generated, and ephemeral artifacts, and describe file, network, service, or other side effects and isolation. If none exist, write Not applicable with a verified reason, then remove this marker. -->

## 10. Extension Points and Architecture Debt

Mark future or proposed items explicitly; do not present them as current capabilities or existing extension
points.

<!-- project-fill: List evidence-backed extension interfaces, known architecture debt, impact, and review triggers. If none exist, write None with a verified reason, then remove this marker. -->
