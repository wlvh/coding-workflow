# Architecture

## 0. Scope and Update Triggers

本文档是当前系统结构的权威说明。新增或删除运行入口、模块边界、调用链、数据契约、状态、
错误模型、外部依赖、认证、配置、artifact、副作用、扩展点或架构债务时，必须更新或确认
对应章节。内容必须来自当前实现、配置、测试、committed artifacts 或可重复运行证据。

<!-- project-fill: 说明本文档覆盖的系统边界、排除项和本项目特有更新触发条件；完成后删除此 marker -->

## 1. System Purpose

<!-- project-fill: 用不超过五句话说明服务对象、输入、输出和核心价值；只写已验证的当前事实；完成后删除此 marker -->

## 2. Runtime Entrypoints and Main Flows

<!-- project-fill: 从真实入口描述主要调用链、关键分支和最终输出；如无运行时入口，写 Not applicable — 已验证原因；完成后删除此 marker -->

## 3. Architecture Invariants

每条不变量应包含正向约束、适用边界、可证伪方式和违反后果。愿景或 proposed 设计不得写成
当前不变量。

<!-- project-fill: 写入有代码、配置或测试证据的架构不变量；没有时写 Not applicable — 已验证原因；完成后删除此 marker -->

## 4. Module Responsibility Boundaries

以稳定模块和职责为粒度，说明负责什么、不负责什么、允许依赖和禁止依赖；不要逐文件复制
仓库目录。

<!-- project-fill: 描述核心模块边界及依赖方向，并引用精确实现证据；完成后删除此 marker -->

## 5. Data Flow and Data Contracts

<!-- project-fill: 描述输入如何被解析、转换、验证并输出，以及 schema、版本和边界契约；无数据流时写 Not applicable — 已验证原因；完成后删除此 marker -->

## 6. State and Persistence Model

<!-- project-fill: 说明进程内状态、持久化、缓存、幂等性和生命周期；无持久化状态时写 Not applicable — 已验证原因；完成后删除此 marker -->

## 7. Error and Failure Model

<!-- project-fill: 说明 validation、降级、重试、hard failure、回滚和用户可见错误的真实边界；完成后删除此 marker -->

## 8. External Dependencies, Authentication, and Configuration

<!-- project-fill: 列出真实外部依赖、认证边界、配置来源和缺失配置时的行为；没有时写 Not applicable — 已验证原因；完成后删除此 marker -->

## 9. Artifacts and Side Effects

<!-- project-fill: 区分 committed、generated、ephemeral artifacts，并说明文件、网络、服务或其他副作用及隔离要求；没有时写 Not applicable — 已验证原因；完成后删除此 marker -->

## 10. Extension Points and Architecture Debt

future / proposed 项目必须显式标注状态，不得伪装为当前能力或既有扩展点。

<!-- project-fill: 列出有证据的扩展接口、已知架构债务、影响和触发重审条件；没有时写 None — 已验证原因；完成后删除此 marker -->
