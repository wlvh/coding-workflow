# 背景 & 目标（Why）

本次改动是一次主干合并后的最小文档同步。

上一条 Flow 可靠性收口 PR 已经把默认 landing browser gate 收紧到“首屏必须真正 settled，且有效 Sankey 主视图不能只是整排 `--` 占位值”，同时主仓库的 agent/工具链又明确要求“除非用户显式要求，否则不要使用 `git commit --amend`”。

当前文档存在两处轻微漂移：

- `TESTING.md` / `interact.md` 尚未把“有效 Sankey 主视图的可见 KPI 卡片不能全部为 `--`”写成显式断言，导致浏览器 gate 比文档更严格。
- `PR_Checklist.md` 顶部仍把 `git commit --amend` 写成默认动作，和当前 agent 行为规范直接冲突。

本条 PR 的目标，就是把这几处文档语义补齐到与当前仓库真实 gate 一致，不引入任何运行时代码变化。

# 实现方案（How）

- `TESTING.md`
  - 在“浏览器验收（前端/交互）”小节补充默认 landing 的一个真实通过条件：
    - 若页面被判定为有效 Sankey 主视图，而不是显式空态或失败态，则可见 KPI 卡片不能全部显示为 `--`。
  - 目的：让测试文档与 `tests/scenarios/flow_browser_live.mjs` 当前 gate 保持一致。

- `interact.md`
  - 在 `Flow · Sankey（主流程）` 小节新增“有效主视图不得只剩占位值”断言。
  - 目的：把浏览器 gate 的产品语义翻译成用户可见的不变量，避免测试规则成为隐藏知识。

- `PR_Checklist.md`
  - 将“使用 `git commit --amend`”改为“如需在用户明确同意的前提下整理当前 HEAD 提交，可使用 `git commit --amend`”。
  - 目的：避免 checklist 和当前 agent/工具链规则冲突，同时保留人类开发者整理单提交的操作入口。

# 变更范围（What）

以下文件清单直接来自 `git diff --name-only master...HEAD` 的实际输出：

```text
PR_BODY.md
PR_Checklist.md
TESTING.md
interact.md
```

# 测试证据

## 必跑 Stage

- 无
  - 原因：本次仅修改文档与提交流程说明，不涉及运行时代码、测试代码、DAX、router、service、schema 或配置逻辑；按 `TESTING.md` 决策表，`仅改注释 / 文档（无逻辑变更）` 不存在强制 Stage。

## 非适用 Stage

- `quick`：N/A
  - 原因：当前 patch 不改变任何被测行为；不运行 quick 不会降低对本次 patch 的判断确定性。

- `contract`：N/A
  - 原因：未修改 `api_schema.py`、`report_registry.py`、API 输出结构或 contract-enabled endpoint。

- `powerbi`：N/A
  - 原因：未修改 DAX、Power BI 执行链路、live gate 目标或语义模型契约。

- `openai`：N/A
  - 原因：未修改 LLM 调用、语义审稿规范或相关测试。

- 浏览器验收：N/A
  - 原因：本次仅补齐浏览器验收文档断言，不涉及前端运行时行为变化。

# 测试变更清单

- 未修改测试文件。

# 契约 / 架构 / 豁免说明

- `api_schema.py`
  - 未修改。
  - 原因：本次不涉及接口 contract 本身，只同步文档与提交流程说明。

- `report_registry.py`
  - 未修改。
  - 原因：本次没有新增/删除 endpoint，也没有变更 contract enable / exempt 策略。

- `json_contract.md`
  - 未修改。
  - 原因：本次不涉及语义模型对象、白名单或 DAX 引用。

- 用户可见行为
  - 本次没有新增或改变运行时用户行为。
  - 这次只是把已存在的浏览器 gate 语义写回 `TESTING.md` 与 `interact.md`，避免文档落后于现状。

# 文档同步

本条 PR 已同步更新：

- `PR_BODY.md`
- `PR_Checklist.md`
- `TESTING.md`
- `interact.md`

# 最终自检

- 当前分支不是主干，当前分支为 `codex/docs-sync-post-pr66`
- 已按 `git diff --name-only master...HEAD` 反向核对 `PR_BODY.md` 的文件清单
- 已按 `git status` 核对本地变更会随本次提交一并落盘
- PR 描述不包含历史草稿、本地未提交改动或“计划做但未落地”的内容
