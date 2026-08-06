# Testing

## 0. Canonical Test Entrypoints

所有 exact command 必须从当前仓库的脚本、任务配置、CI、构建文件或测试框架配置中提取，
并在仓库根目录或明确记录的工作目录验证。不得从本模板猜测语言、runner、服务或阶段名。
已有经过验证的 repository-owned 统一入口时优先使用，并记录它实际覆盖的范围；不存在时不应
仅为满足模板而创建 wrapper。只有多命令编排、服务生命周期或清理步骤长期重复并形成独立
维护收益时，才把 wrapper 作为单独项目改动审查。

<!-- project-fill: 列出当前仓库真实可执行的测试命令、工作目录、环境前提和适用范围；完成后删除此 marker -->

## 1. Testing Philosophy

- 测试验证行为、契约和失败边界，不锁死无用户价值的实现细节。
- 每个新增测试应覆盖真实缺口；已有更高层测试不自动否定快速、可诊断的低层回归测试。
- 默认使用固定输入，避免依赖变化中的生产数据；live test 必须明确标注外部依赖与风险。
- 测试彼此隔离，不依赖执行顺序或残留状态；失败信息应足以定位预期与实际差异。
- 未运行、跳过或只完成静态检查时，准确记录范围和原因，不推断为通过。

## 2. Test Layers and What Each Proves

- **Unit**：证明单个函数、类或模块在隔离输入下的局部行为。
- **Contract**：证明公开 schema、接口、文件格式或跨模块约定。
- **Scenario**：证明多个真实组件串联后的用户或调用方路径。
- **Golden**：证明确定性输入对应的已审查输出；不单独证明外部系统或完整运行链。
- **Report build**：证明报告或交付物可以生成；不自动证明内容业务正确。
- **Repair validation**：证明修复后的 artifact 满足特定 gate；不等同于所有上游阶段正确。
- **Light review**：证明其实现实际检查的有限范围；不得描述成 full validation。
- **Full validation**：只有真实覆盖完整目标路径、依赖和验收边界时才能使用此名称。
- **Live**：证明真实外部依赖下的当次行为；必须记录环境、时间敏感性和不可重复风险。

## 3. Capability Contract Alignment

项目的 alignment test 应在本地递归收集 `capability_contract.json` 中所有对象的稳定
`anchor_id`。它应按 contract rules 定义的协议检查唯一性和 Markdown 引用，
但不硬编码 bucket、JSON path、数组位置或要求所有 contract 条目进入 business guide。

显式使用 `test_anchor: null` 时同时记录非空、具体的 `untested_reason` 和非空 `pending_since`；
已有测试时登记真实测试锚点。Anchor alignment 只证明结构引用、合法 ID 和非悬空等机械事实，
不单独证明句子级绑定或声明的业务语义已经实现。文档声明 alignment test 存在之前，必须确认
目标仓库确有对应测试实现和可执行命令。

<!-- project-fill: 引用目标项目真实 alignment test、命令和覆盖范围；尚未实现时准确写 Not configured 及原因；完成后删除此 marker -->

## 4. Change Type to Required Evidence

1. 可安全、确定性复现的 escaped bug：先建立修复前失败的最小回归测试或 fixture，再改实现。
2. 无法先建立失败测试：保留修复前失败证据，说明无法稳定自动化的原因和剩余风险。
3. 用户可观察行为、公开契约或 schema 变化：默认新增或修改最近边界的 contract/scenario 测试。
4. 无 test diff：指出具体已有测试如何覆盖本次新风险并提供重跑证据；“已有高层测试”不充分。
5. 纯内部重构且行为不变：可不新增测试，但须重跑受影响路径并记录 no-test-change reason。
6. 文档-only gate：只证明实际检查的结构、解析或 alignment 范围，不得冒充运行时行为验证。

<!-- project-fill: 按本项目真实风险映射代码、配置、schema、用户行为、artifact 和文档变更所需测试层级；完成后删除此 marker -->

## 5. Side Effects and Isolation

每条命令先核对写入路径、外部服务、凭据、并发、顺序依赖、清理方式和 CI 政策，再选择足以
隔离其真实副作用的环境。环境可以是 CI、container、独立 checkout、远端测试环境或项目已
验证的其他执行面；不得从本模板固定一种实现。测试记录必须说明实际环境、隔离方式、残留
状态和清理结果。

<!-- project-fill: 标出本项目各命令的副作用、实际隔离环境、清理方式和选择依据；完成后删除此 marker -->

## 6. Test Suite Overview

以稳定测试目录、入口和职责为粒度，不永久镜像每个测试文件。

<!-- project-fill: 概述真实测试套件、关键 fixture、外部依赖和推荐入口；完成后删除此 marker -->

## 7. Known Gaps and Untested Reasons

<!-- project-fill: 列出当前真实覆盖缺口、风险、owner 或触发条件；没有缺口时写 None — 已验证的范围；完成后删除此 marker -->

## 8. Lessons Learned

只记录真实缺陷暴露出的可复用测试决策规则，不保存事故编年史或易漂移命令。若一次事故
来自“各层单独通过但组合失败”，同时保留最小回归测试与覆盖真实边界的 scenario 测试。
同一失效模式合并为更一般的规则；只有知识被更强测试、自动化 gate 或权威规则完整接管时才
退役，不能只因案例变旧而删除。

<!-- project-fill: 写入由真实失败支持、且尚未被更强规则或自动化替代的教训；没有时写 None；完成后删除此 marker -->
