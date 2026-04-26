# 测试流程

在提交任何 PR 或进行回归前，务必阅读并遵循本指南。除非明确说明，否则所有命令均在仓库根目录执行，优先使用 `.\run_tests.ps1` 来降低心智负担。**当 Stage 需要本地服务时**，脚本会自动调用 `start_server.ps1`、等待 `/healthz` 可用，并分阶段执行下列测试。若需在 CI 或 Unix 环境单独运行，可直接采用列出的命令。

## 测试原则 (Testing Philosophy)

- **拒绝为了测试而测试**：测试代码应当验证行为和契约，而不是实现细节。避免使用脆弱的正则表达式去匹配代码字符串（如统计度量数量），这会导致重构困难。
- **避免冗余**：如果一个端到端的实测（如 Power BI Live Test）已经覆盖了某个场景，不要再编写一个仅仅是 Mock 的单元测试来重复验证同一件事，除非该单元测试能提供极快的反馈循环或覆盖了实测无法覆盖的边缘情况。
- **保持精简**：定期审查测试套件，删除不再有价值的过时测试。
- **确定性 (Determinism)**：除非是专门做 Live Monitor，否则测试不应依赖即时变化的生产数据。应使用 Mock 数据或固定的测试数据集，确保测试结果在任何时间、任何环境下都是可重复的。
- **独立性 (Isolation)**：每个测试用例应当是独立的，不应依赖其他测试的执行顺序或残留状态。
- **可读性与诊断性 (Readability & Diagnosability)**：断言失败时应提供清晰的错误信息（例如 `assert actual == expected, f"Expected {expected} but got {actual}"`），让开发者无需 Debug 就能明白哪里出了问题。
- **及时更新**：当测试文件新增或者更改功能时，及时更新本文档。

## capability contract alignment 测试原则

当项目引入 `capability_contract.json`、`interact.md`、`docs/business_user_guide.md` 等用户能力文档时，应提供一个轻量的 contract alignment 测试，例如 `tests/.../test_capability_contract_alignment.py`。

该测试的目的不是验证具体业务逻辑，而是验证“机器可读能力契约”和“用户可读文档声明”之间没有明显漂移。

### anchor_id 提取原则

alignment 测试提取 `capability_contract.json` 中的 `anchor_id` 时，应优先采用递归全树扫描，而不是按固定 JSON path 提取。

原因：
- `capability_contract.json` 的 schema 可能演化；
- 未来可能新增能力桶，例如 `failure_modes`、`escalation_paths`；
- 文档锚点引用的是稳定 `anchor_id`，不应依赖当前 JSON 层级结构。

测试原则：
- 递归遍历 JSON 中所有对象；
- 只要对象包含 `anchor_id` 字段，就纳入 anchor 集合；
- 不把具体能力名、类型桶路径或数组下标硬编码进测试。

### Markdown anchor 引用语法

所有用户可读文档引用 `capability_contract.json` 中的 `anchor_id` 时，必须使用统一格式：

```text
<!-- capability-anchor: <ANCHOR_ID> -->
```

规则：
- 只允许这一种格式。
- 不允许 `<!-- anchor: ... -->`、`<!-- ref: ... -->`、`<!-- contract: ... -->` 等变体。
- `<ANCHOR_ID>` 必须是 `capability_contract.json` 中存在的稳定 `anchor_id`。
- 不允许引用 JSON path、数组下标或 schema 内部路径。
- alignment 测试只识别这一种格式。

### 测试应覆盖的原则

1. `anchor_id` 唯一性
   - `capability_contract.json` 中所有可被文档引用的对象，只要包含 `anchor_id` 字段，就必须拥有唯一、稳定的 `anchor_id`。
   - 不允许重复 `anchor_id`。
   - 不允许文档引用不存在的 `anchor_id`。

2. `anchor_id` 提取方式
   - 测试应优先递归扫描整个 `capability_contract.json`，收集所有对象中的 `anchor_id`。
   - 不应把能力类型桶、JSON path、数组下标或当前 schema 层级硬编码进测试。
   - schema 演化时，测试应尽量无需修改。

3. Markdown 锚点语法
   - 所有文档中引用 contract anchor 时，必须使用统一格式：

     ```text
     <!-- capability-anchor: <ANCHOR_ID> -->
     ```

   - alignment 测试只识别这一种格式。
   - 不允许其他变体。
   - 不允许引用 JSON path、数组下标或 schema 内部路径。

4. 文档锚点不应出现裸 TODO
   - Markdown 中不应出现 `capability-anchor: TODO` 或 `test-anchor: TODO`。
   - 暂时不可测的契约应集中登记在 `capability_contract.json`，使用 `test_anchor: null` 并写明 `untested_reason` 或 `pending_since`。

5. agent 行为承诺登记
   - 凡是文档中声明“必须追问 / 必须拒绝 / 不得猜测 / 必须降级 / 必须解释”的行为，应在 `capability_contract.json` 中有对应 `anchor_id`。
   - 如果有自动化测试，应登记测试锚点。
   - 如果暂时没有自动化测试，应显式说明不可测原因，而不是散落 TODO。

6. 不要求所有 contract 条目都出现在 business guide
   - `docs/business_user_guide.md` 是教学派生文档，只覆盖最常见路径。
   - alignment 测试不应盲目要求 `capability_contract.json` 中每个能力都出现在 business guide。
   - 只有被标记为必须文档化、用户可见、或指南必提的条目，才要求在指定文档中出现。

7. 不测试教学文案风格
   - alignment 测试不判断业务指南写得是否好看。
   - 它只检查能力声明、行为承诺和锚点是否一致。
   - 普通“好问法 / 坏问法 / 使用建议”不应被过度机器化。

8. 不依赖外部服务
   - alignment 测试应只读取本地文件。
   - 不应调用真实 API、数据库、BI 服务或 LLM。
   - 它应该稳定、快速、可在普通回归阶段运行。

### 测试失败与警告原则

- 文档引用了不存在的 `anchor_id`：应失败。
- contract 中出现重复 `anchor_id`：应失败。
- Markdown 中出现裸 TODO 锚点：应失败或至少高优先级警告。
- 行为承诺缺少测试锚点但已登记不可测原因：可警告，不必默认失败。
- contract 中存在未被 business guide 引用的能力：默认不失败，除非该条目标记为必须进入业务指南。

## 测试分层与命名约定

本仓库中的测试分为两层：

1. 近单元级测试（Module-level Tests）
   - 目标：快速验证单个模块（`core/`, `services/`, `dax/`, `routers/` 中的 `.py` 文件）的行为正确性。
   - 命名规则：
     - 代码文件：`<module_path>/<name>.py`
     - 对应测试：`tests/<module_path>/test_<name>.py`
   - 特点：不依赖外部服务，便于在 `Stage quick` 中频繁运行。
   - 如果文件不存在，自行开发。

2. 契约 / 场景 / Live 测试（Contract / Scenario / Live Tests）
   - 目标：验证对外暴露的 API 契约、完整业务场景和带外部依赖（Power BI / Azure OpenAI）的实测行为。
   - 目录约定：
   - 特点：

## 何时新增或修改测试

当对代码进行修改时，请按以下规则决定如何操作测试：

1. 发现 Bug 但现有测试未覆盖
   - 必须：
     - 先新增一个能重现 Bug 的测试用例（近单元或场景测试皆可），再修复实现。
   - 修复完成后：
     - 确保新增测试在所有适用的 Stage 中稳定通过。

> 总结：任何行为性代码变更都必须有测试证据。默认应新增或修改测试；如果没有测试变更，必须说明为什么现有测试已经覆盖，并提供对应测试或验收的重跑证据。

## 测试文件简介

## 变更类型与推荐 \run_tests.ps1 测试阶段（决策表）

## 教训模块（Lessons Learned）

### 教训模块维护规则：
  - 新增：只有当一次真实缺陷暴露出“现有测试规范无法稳定引导出正确测试策略”时，才新增教训条目；普通实现细节、一次性操作步骤或仅对当前目录结构有效的说明不要进入该模块。
  - 更新：优先提升既有条目的抽象层级、补充适用边界与反例，而不是因为具体实现变化就重写整条教训；具体 case 可以保留，但规则部分必须在脱离当前仓库后仍然成立。
  - 合并：若多个教训条目实质上描述的是同一类测试失效模式，应合并为一条更通用的规则，并把具体案例压缩为简短背景，而不是按模块或事故时间线持续堆叠。
  - 删改：只有当旧教训已被更高层、可持续执行的规则、流程或自动化机制完整替代时，才允许删改；判断标准是“知识是否被替代”，不是“案例是否过时”。
  - 约束：教训模块服务于未来的测试决策，而不是维护事故编年史。具体 case 可以保留作为说明材料，但任何删改都不能破坏后来者对“为什么会漏测、以后该补哪类测试”的理解。
  - 如果某次事故最终定位到“测试分层都测了，但没测组合”，则修复 PR 必须同时包含两部分：
     - 一个能稳定复现事故的最小回归测试。
     - 一段写回 `TESTING.md` 的教训，总结“现有测试为什么会漏”，而不是只记录“这次是哪个模块坏了”。
  - 推荐落点：
     - 若只涉及单个消费者，在该消费者对应的 `tests/unit/test_<consumer>.py` 中补回归测试。
     - 若涉及多个模块编排，或只有串起来才会暴露错误，则补到 `tests/scenario/`。

### Case 1
