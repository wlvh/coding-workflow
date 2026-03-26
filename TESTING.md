# 测试流程

在提交任何 PR 或进行回归前，务必阅读并遵循本指南。除非明确说明，否则所有命令均在仓库根目录执行，优先使用 `.\run_tests.ps1` 来降低心智负担。**当 Stage 需要本地服务时**，脚本会自动调用 `start_server.ps1`、等待 `/healthz` 可用，并分阶段执行下列测试。若需在 CI 或 Unix 环境单独运行，可直接采用列出的命令。

## 认证准备（Power BI）

- 需提前安装 Azure CLI，并确保 `AUTH_MODE=azurecli`（可在当前 shell `set`/`$env:`，或 `.env` 中设置 `AZURE_TENANT_ID`）。
- `run_tests.ps1` 若检测到 `AUTH_MODE` 未设置，会默认使用 `azurecli`，以复用 Azure CLI 登录态并避免重复交互登录；如需 `interactive`/`clientsecret`，请显式设置 `AUTH_MODE`。
- 运行包含 Power BI 的阶段（`-Stage powerbi` 或 `-Stage all`）前，`run_tests.ps1` 会自动尝试 `az account get-access-token --resource https://analysis.windows.net/powerbi/api`；若登录态过期，会触发 `az login --tenant <AZURE_TENANT_ID> --use-device-code`，按提示在浏览器确认即可。
- 首次使用可手动预热：`az login --tenant "<你的租户ID>" --use-device-code`，再执行测试，后续在登录态有效期内无需重复确认。

## 测试原则 (Testing Philosophy)

- **拒绝为了测试而测试**：测试代码应当验证行为和契约，而不是实现细节。避免使用脆弱的正则表达式去匹配代码字符串（如统计度量数量），这会导致重构困难。
- **DAX Stub 匹配约定**：测试中的 `fake_execute_dax` 只根据 DAX 顶部的 `-- contract: <tag>` 注释路由返回，不匹配具体 `ROW/SUMMARIZECOLUMNS` 文本；新增查询时先加 tag，再补齐 stub 分支（参考 `tests/contracts/test_api_contract.py`）。
- **避免冗余**：如果一个端到端的实测（如 Power BI Live Test）已经覆盖了某个场景，不要再编写一个仅仅是 Mock 的单元测试来重复验证同一件事，除非该单元测试能提供极快的反馈循环或覆盖了实测无法覆盖的边缘情况。
- **保持精简**：定期审查测试套件，删除不再有价值的过时测试。
- **确定性 (Determinism)**：除非是专门做 Live Monitor，否则测试不应依赖即时变化的生产数据。应使用 Mock 数据或固定的测试数据集，确保测试结果在任何时间、任何环境下都是可重复的。
- **独立性 (Isolation)**：每个测试用例应当是独立的，不应依赖其他测试的执行顺序或残留状态。
- **可读性与诊断性 (Readability & Diagnosability)**：断言失败时应提供清晰的错误信息（例如 `assert actual == expected, f"Expected {expected} but got {actual}"`），让开发者无需 Debug 就能明白哪里出了问题。
- **及时更新**：当测试文件新增或者更改功能时，及时更新本文档。

## 测试分层与命名约定

本仓库中的测试分为两层：

1. 近单元级测试（Module-level Tests）
   - 目标：快速验证单个模块（`core/`, `services/`, `dax/`, `routers/` 中的 `.py` 文件）的行为正确性。
   - 命名规则：
     - 代码文件：`<module_path>/<name>.py`
     - 对应测试：`tests/<module_path>/test_<name>.py`
   - 特点：不依赖外部服务，便于在 `Stage quick` 中频繁运行。
   - 如果文件不存在，自行开发。
- 示例：`critical_satisfaction` 的近单元级覆盖包含 `tests/core/test_critical_satisfaction.py`、`tests/core/test_pbi_result.py`、`tests/dax/test_critical_satisfaction_dax.py`、`tests/services/test_critical_satisfaction_service.py`、`tests/routers/test_dsat_router.py`；Flow 语义模型迁移相关的近单元级覆盖包含 `tests/core/test_semantic_model_registry.py`、`tests/core/test_utils.py`、`tests/dax/test_flow.py`、`tests/services/test_flow_reports.py`、`tests/routers/test_flow_router.py`；前端 inline script 的语法 smoke，以及 Flow 主 `/api/flow` 刷新竞态、`/api/detail` 下钻竞态、离开 Sankey 视图时的上下文失效与首屏 month probe 视图切换回归放在 `tests/scenarios/test_frontend_js.py`；debug smoke 相关近单元级覆盖放在 `tests/services/test_diagnostic_tools.py`，用于固定 `/api/test` 的 S1-S5 probe、bracketed key 兼容与 blank-first-row 回归；根 contract / legacy gate 的近单元级覆盖包含 `tests/core/test_process_semanticmodel.py`、`tests/core/test_legacy_model_name_gate.py`；仓库根级工具脚本 `run_dax_queries_incremental.py` 的近单元级覆盖放在 `tests/core/test_run_dax_queries_incremental.py`，用于固定 BOM 兼容读取、无 BOM 写回归一化，以及共享严格 parser 复用；仓库根级配置模块 `config.py` 的近单元级覆盖放在 `tests/core/test_config.py`。

2. 契约 / 场景 / Live 测试（Contract / Scenario / Live Tests）
   - 目标：验证对外暴露的 API 契约、完整业务场景和带外部依赖（Power BI / Azure OpenAI）的实测行为。
   - 目录约定：
     - `tests/contracts/`：API 结构与契约测试（例如 `tests/contracts/test_dsat_timeaxis_policy.py` 固化 DSAT 常规端点 event-only timeAxis 约束）。
     - `tests/scenarios/`：如 DSAT 图表、Insights 解析等业务场景。
     - `tests/semantic/`：基于 Azure OpenAI 的自然语言↔semantic↔DAX 语义审稿（仅在 `Stage openai` 运行）。
     - `tests/core/test_deterministic_contract_gate.py`：不依赖 Azure/OpenAI 的 deterministic contract gate（`Stage quick` 默认运行，拦截明显 drift）。
     - `tests/live/`：Power BI / Azure OpenAI 实测（可通过环境变量开启/跳过）。
   - 特点：通常在 `Stage contract`、`Stage powerbi` 和 `Stage openai` 中运行，用于捕捉跨模块问题。

## 何时新增或修改测试

当对代码进行修改时，请按以下规则决定如何操作测试：

1. 修改或新增 API 路由（`routers/*.py`）
   - 必须：
     - 更新或新增对应的 `tests/routers/test_<name>.py` 近单元测试。
   - 视情况：
     - 若改变了对外 JSON 结构、状态码或错误处理逻辑：
       - 更新 `tests/contracts/` 中相关的契约测试。
       - 在提交前至少执行 `Stage contract`。

2. 修改或新增 DAX 查询（`dax/*.py`）
   - 必须：
     - 更新或新增对应的 `tests/dax/test_<name>.py`，验证 DAX 拼接逻辑与 `json_contract.md` 一致。
   - 视情况：
     - 若新增度量或调整现有度量的语义与性能：
       - 增补 `tests/scenarios/` 或 `tests/live/` 中的相关用例。
       - 在提交前执行 `Stage powerbi`。

3. 修改服务层逻辑（`services/*.py`），尤其是 Azure OpenAI 相关逻辑
   - 必须：
     - 更新 `tests/services/test_<name>.py` 中的测试，覆盖新的分支和错误处理。
    - 例如修改 `services/flow_reports.py` 时，应同步维护 `tests/services/test_flow_reports.py`，覆盖 alias-first 解析与新 FQN fallback 路径；若 legacy FQN 已废弃，不应再把它当作运行时 expected path。
   - 视情况：
     - 若改变了 DSAT Insights 行为或依赖新的模型配置：
       - 更新 `tests/scenarios/` 中的 DSAT 相关测试。
       - 在提交前执行 `Stage openai`。

4. 修改核心工具函数或公共组件（`core/*.py`）
   - 必须：
     - 更新 `tests/core/test_<name>.py`。
     - 例如修改 `core/semantic_model_registry.py` 或 `core/utils.py` 时，应同步更新 `tests/core/test_semantic_model_registry.py`、`tests/core/test_utils.py`。
   - 视情况：
     - 若该工具函数被广泛用于 API / DAX 中，应在契约或场景测试中添加一个回归用例。

4.1 修改配置或认证基础模块（例如 `config.py`、`core/auth.py`）
   - 必须：
     - 更新对应的近单元测试（例如 `tests/core/test_config.py`、`tests/core/test_auth.py`）。
   - 提交前：
     - 至少执行 `Stage quick`，确认配置解析与认证参数注入不会在 import 或凭据初始化阶段回归。

4.2 修改仓库根级工具脚本（例如 `process_semanticmodel.py`）
   - 必须：
    - 更新对应的 `tests/core/test_<script_name>.py`，覆盖 CLI 参数、关键推断逻辑或外部依赖注入点；例如 `run_dax_queries_incremental.py` 需覆盖 BOM 兼容读取、写回编码归一化，以及共享 parser 的 fail-fast 行为。
   - 提交前：
     - 至少执行 `Stage quick`，确认脚本可被测试导入且不会破坏仓库静态门禁。

4.3 修改前端入口或用户交互（例如 `static/index.html`）
   - 必须：
     - 更新相关 `tests/scenarios/` 或等价的浏览器验收脚本，覆盖本次改动涉及的筛选器、URL 状态、图表 hover/click、下载、加载态或错误提示。
     - 若行为变化对用户可见：同步更新 `interact.md`。
   - 提交前：
     - 至少执行 `Stage quick`，确保现有前端场景/语法 gate 不回归。
     - 再按本文“浏览器验收（前端/交互）”执行浏览器验收，并保留可追溯证据。

5. 发现 Bug 但现有测试未覆盖
   - 必须：
     - 先新增一个能重现 Bug 的测试，再修复实现。
   - 若该 Bug 是用户可见问题、跨模块问题或真实线上事故：
     - 回归测试不得仅停留在 module-level；
     - 必须补一个 contract / scenario / browser / e2e 中至少一种更高层验证。

> 总结：**任何代码变更都应至少有一个对应测试的变更**。如果你发现自己修改了代码但不需要修改任何测试，请停下来重新检查，通常说明测试覆盖不足。

## 关键查询与错误语义回归

- 适用范围：修改关键查询、singleton 查询、`core/pbi_result.py`、service 侧补 0/降级逻辑，或 router 的 `400/500/unknown` 分层时，除常规模块测试外还应补本节回归。
- 关键查询测试至少覆盖：`results/tables/rows` 缺失或类型错误、`rows[*]` 非 dict、合法空结果与非法坏结构的区分；若查询选择宽松模式而非 `strict_structure=True`，测试或 PR 说明必须证明“空结果”是预期语义。
- singleton 查询测试至少覆盖：`0` 行、`>1` 行，以及单行缺少关键字段/返回非法状态值时的 fail fast；禁止仅测试“正常 1 行”然后在实现里静默取首行。
- 若 service 存在补 0、降级或 `unknown` 语义，测试必须同时覆盖：
  - 合法缺失如何补齐（如 bucket/path 缺失）
  - 非法结构如何 fail fast（如重复行、窗口外 bucket、未知枚举值、关键列缺失）
  - 哪些外部依赖故障允许降级，哪些本地契约错误必须暴露为 5xx
- 若 router 修改了状态码、错误处理逻辑或 fail-fast 语义，必须补 `tests/routers/*`；如未新增/修改 `tests/contracts/*`，PR 描述必须写清豁免理由，并说明由哪些 `tests/services/*`、`tests/routers/*` 或 `tests/scenarios/*` 覆盖。
- 可参考的近单元模板：`tests/services/test_critical_satisfaction_service.py`（关键查询/补 0/坏结构回归）、`tests/routers/test_dsat_router.py`（400/500/unknown 分层回归）、`tests/core/test_pbi_result.py`（`strict_structure` 回归）。

## 变更类型与推荐 \run_tests.ps1 测试阶段（决策表）

`run_tests.ps1` 支持四个阶段，可组合使用（`-Stage all` 按顺序运行全部）。若改动包含用户可见前端交互，除下表中的 Stage 外，还应补执行下文的“浏览器验收（前端/交互）”：

| 变更类型                               | 必跑 Stage      | 视情况增补 Stage      |
|----------------------------------------|-----------------|-----------------------|
| 仅改注释 / 文档（无逻辑变更）          | 可跑 quick      | -                     |
| 修改 core/utils 等基础工具             | quick           | contract（若影响 API）|
| 修改 `config.py`、`core/auth.py` 等配置/认证基础模块 | quick | contract（若影响 API） |
| 修改 `process_semanticmodel.py` 等仓库根级工具脚本 | quick | powerbi（若要验证真实导出链路） |
| 修改 routers/* 路由或响应结构          | quick, contract | powerbi（若牵涉 DAX） |
| 修改 `dax/*.py` DAX 构建逻辑           | quick           | powerbi, contract     |
| 修改 `spec/*_metrics.json`（例如 `spec/flow_metrics.json`、`spec/dsat_metrics.json`；natural/semantic/dax/axis_semantics/golden_tests） | quick, openai   | powerbi（大改 DAX 或调整 golden_tests/性能）、contract（若影响 API） |
| 修改 services/llm 或 OpenAI 调用逻辑   | quick           | openai, contract      |
| 修改 semantic 规范或 LLM 审稿逻辑（`spec/nature2semantic2dax.md`、`tests/semantic/`） | quick           | openai（语义审稿）    |
| 修改 `static/index.html` 或任何用户可见前端交互 | quick | 浏览器验收（见下节）、contract（若影响 API） |
| 修改测试代码本身                       | quick           | 与被测模块同级的其他 Stage |

对应阶段命令（`run_tests.ps1` 已封装好）：

- `quick`：`pytest tests/core tests/services tests/dax tests/routers tests/scenarios tests/test_lint.py tests/test_no_wild_dax.py`（包含 deterministic contract gate、legacy model name gate，不依赖 Azure/OpenAI）
- `contract`：直接执行 `pytest tests/contracts`（不启动本地服务）
- `powerbi`：启动本地服务后执行 `pytest tests/live/test_dsat_queries_live.py tests/live/test_api_contract_live.py tests/live/test_flow_metrics_golden.py tests/live/test_critical_satisfaction_key_mapping_quality_live.py`（自动设置 `RUN_DSAT_DAX_TESTS=1`、`RUN_API_CONTRACT_TESTS=1`、`RUN_FLOW_GOLDEN_TESTS=1`、`RUN_CRITICAL_SAT_KEY_MAPPING_TESTS=1`）
  - 可选：设置 `LIVE_TEST_ANCHOR_DATE=YYYY-MM-DD` 固定 live 测试的日期窗口，便于复现与对比。
- `openai`：启动本地服务后执行 `python tests/live/test_azure_openai.py --mode quick`、`python tests/live/test_azure_openai.py --mode full`，再运行 `pytest tests/live/test_insights.py`（自动设置 `RUN_OPENAI_LIVE_TESTS=1`），以及语义审稿 `pytest tests/semantic`（自动设置 `RUN_SEMANTIC_LLM_TESTS=1`，并默认 `SEMANTIC_LLM_MODE=batch`、`SEMANTIC_LLM_BATCH_SIZE=8`）
  - 语义审稿支持 `SEMANTIC_LLM_BATCH_SIZE`（默认 1；openai Stage 默认用 8 以减少调用次数；可在运行前显式设置环境变量覆盖）。

## 浏览器验收（前端/交互）

- 适用范围：修改 `static/index.html`，或改变用户可观察行为（例如筛选器、默认视图、URL 同步、下载、加载态、错误提示、图表 tooltip / click drill-down / 局部失败展示）。
- 验收入口：优先使用可复现的浏览器自动化（如 Playwright）；若仓库当前尚未固化 browser stage，可使用临时脚本或等价浏览器工具，但必须生成可追溯证据。
- 仓库内正式脚本：`.\scripts\run_browser_acceptance.ps1`
  - 环境要求：浏览器验收依赖当前锁定的 Playwright/Node 运行时，执行前需确保本地 `Node.js >= 18`；脚本会在安装依赖和登录 Azure 前先做版本 fail fast。
  - 语义要求：只允许使用真实浏览器 + 真实本地服务 + 真实 `/api/*` 返回；禁止在浏览器验收里打桩或伪造 `/api/flow`、`/api/detail`、`/api/dsat/*` 数据。
- 当前覆盖：`tests/scenarios/flow_browser_live.mjs` 会验证首屏自动加载会离开 Pending，并且只在 Flow bootstrap 真正 settled 后进入“有效 Sankey 或显式空态”的稳定状态，避免 hinted-month explicit-empty fallback 的中间态被默认 landing gate 假绿；若页面被判定为有效 Sankey 主视图，则可见 KPI 卡片不能全部显示为 `--`，避免“底层 payload 勉强非空、但用户实际看到的是一整排不可解释占位值”的结果被误判为通过；同时覆盖 Event/Month 历史月主视图，以及通过真实 Sankey hover tooltip、真实 click 与真实“下载 CSV”按钮触发的明细表/CSV 链路；历史月默认会运行时探测最近一个可渲染 month，但只会在 `/api/flow` 明确返回 `has_renderable_flow_data=false` 时继续 lookback，malformed 200 会直接使 live gate 失败；也可用 `CASE_FLOW_HISTORY_MONTH=YYYY-MM` 固定复现。
- 非 live 的前端确定性回归：`tests/scenarios/test_frontend_js.py` 会在 quick 阶段用 Node VM 装载 `static/index.html` 的 inline script，固定主 `/api/flow` 请求在同筛选器重复刷新时只接受最后一次响应写回，且旧失败不会在新结果已落地后补弹过期错误；同时固定 `/api/detail` 在连续点击不同 edge 时会立即失效旧表格/旧下载且只接受最后一次响应写回，并覆盖“首屏 bootstrap 不得把 URL/user filters 降级成 auto”“auto provenance 不得因普通刷新或切换 DSAT/Flow 视图静默升级成 user”“真实 filter change 必须先把 provenance 升级为 user，再驱动下一次共享 filters 请求”“latest-month hint 只能前移、浏览旧历史月不得回退 hint”“mixed-bad-edge / malformed 200 / 负 totals 不得被 probe / hinted month / 正式 fetch / session cache 误判成 explicit empty 或成功结果”“负数 detail rows 不得被渲染成合法表格/CSV”“detail edge-specific shape drift 不得伪装成合法空列 / `--`”“DSAT 临时 `event` 时间轴不得污染共享 storage/URL”“主筛选器变化、切换到 DSAT 或空态失效后，旧明细不得回写或重新启用 CSV”“hinted month 命中 explicit empty 时，default landing settled 状态必须等 replacement fetch 落地后才置真”“首屏 month probe 期间切走 Sankey 不得继续隐藏执行 `fetchFlow()`”，以及明细/Top 风险组合/洞察/tooltip 中的动态文本必须按纯文本渲染、不允许把后端或 LLM 返回值当成 HTML 注入 DOM 的回归，不依赖 live 网络时序；`tests/scenarios/test_flow_browser_live.py` 则在 quick 阶段固定浏览器 live 历史月分类 helper与首屏默认 gate 语义，确保自动 lookback 只跳过显式 empty 月份、首屏 error-state 不会被放过，且默认首屏不会把所有 KPI 卡片都显示为 `--` 的结果误判为通过。
- 最小覆盖面：
  - 首屏加载：确认页面不会长期停留在 `Pending Filters`、空白图表或纯占位态，默认视图能加载。
  - 筛选器与 URL：确认时间粒度/时间轴/多选筛选器/URL 之间同步；重新打开 URL 后，控件状态与结果口径可复现。
  - 图表交互：若改动涉及 ECharts 或明细下钻，至少验证 1 个真实 hover tooltip 与 1 个真实 click/drill-down 或等价交互。
  - 加载/失败路径：若改动涉及加载态、局部失败、AI 洞察或下载，至少覆盖 1 条对应路径。
- 证据要求：PR 描述中注明使用的工具/脚本、覆盖的 `interact.md` 断言，以及截图、trace、报告摘要或产物路径；若不适用，必须写清原因。
## contract Stage（registry 驱动）

- 端点级 SSOT：`report_registry.py`（method/path/schema/default payload/timeAxis policy/豁免原因）。
- contract stage 入口：`pytest tests/contracts`（不启动服务），其中包含：
  - `tests/contracts/test_registry_lint.py`：字段完整性 + 豁免理由强制
  - `tests/contracts/test_endpoint_coverage.py`：FastAPI 实际 /api/* 路由 vs registry 覆盖率 gate
  - `tests/contracts/test_api_contract.py`：按 registry 遍历 contract.enabled=true 的端点，校验响应结构符合 `api_schema.py`
  - `tests/contracts/test_report_registry_report_id_consistency.py`：/api/report 的 report_id allowlist 一致性 gate（schema/engine/registry）
  - `tests/contracts/test_report_aggregate_contract.py`：/api/report 聚合端点专项断言（默认 reports + policy 回显 + 子报告 schema 复用）
  - `tests/contracts/test_router_thin_gate.py`：router 薄化静态 gate（routers 不得直接触达底层执行入口）
  - `tests/contracts/test_dsat_dax_required_columns.py`：DSAT DAX 必填列兜底 guardrail（COALESCE 防止 BLANK 省略 key）
- 失败如何解读：
  - coverage gate 报 missing routes：说明新增了 `/api/*` 路由但未更新 `report_registry.py` 且不在白名单（或 method 不一致）。
  - registry lint 报 exempt_reason：说明 contract.enabled=false 的 entry 未写清豁免原因。
- 起服务后的同源 smoke：`python -m scripts.contract_smoke`（同样按 registry 遍历 contract.enabled=true 的端点）。

## json_contract.md（语义模型契约）导出与验收

- 什么时候必须更新：语义模型表/列/度量/关系/别名白名单发生变化，或本次变更新增引用了合同中不存在的对象（常见表现：`tests/dax/*` 或 contract gate 报错“未在合同中声明”）。
- 导出入口（权威定义）：`json_contract.md` 由语义模型导出器生成；当前入口命令为 `python process_semanticmodel.py --output-path json_contract.md --profile-mode light`。若导出方式/脚本发生变化，只在本节更新入口说明即可（避免把命令分散在 SOP/Checklist 里造成 drift）。
- 导出后如何验收（Fail Fast）：
  - JSON/编码可读：`python -c "import json; json.load(open('json_contract.md', encoding='utf-8-sig')); print('json_contract ok')"`（兼容 UTF-8 BOM）。
  - 基础 sanity：`python -c "import json; p=json.load(open('json_contract.md', encoding='utf-8-sig')); c=p.get('counts') or {}; assert c.get('tables',0)>0 and c.get('measures',0)>0 and c.get('relationships_active_non_auto',0)>0, c; print('counts ok', c)"`。
- 旧模型名 gate：`python scripts/legacy_model_name_gate.py`；根 contract、根归档模板 `dax_queries_pcsev2.json` 与生产代码高风险路径中不应再出现非 allowlist 的裸 `vwpcse_*` 或 `legacy_*` helper 名字；`artifacts/**` 不在此 gate 范围内。
  - 然后按“变更类型决策表”选择 Stage（通常至少 `quick`；若涉及 API 输出结构则补 `contract`；若涉及语义审稿链路则补 `openai`）。
  - 已知限制：若当前 REST `INFO.VIEW.MEASURES()` 未返回 Expression/FormatString，则 `json_contract.md.measures[*].category/depends_on/format` 可能退化为 advisory 元数据；请同时查看 `artifacts/semantic_agent/*measure*risk*.json`。

## 语义审稿（tests/semantic）失败怎么排查

- 先用 `Stage quick` 复现 deterministic gate：`.\run_tests.ps1 -Stage quick` 更快且不依赖 Azure/OpenAI；若 quick 未通过（包含 deterministic contract gate），先修到通过再跑 `Stage openai`。
- 先确认没有被 skip：直接 `pytest tests/semantic` 默认会 skip，需 `RUN_SEMANTIC_LLM_TESTS=1`；优先用 `.\run_tests.ps1 -Stage openai` 跑到语义审稿（会自动设置 `RUN_SEMANTIC_LLM_TESTS=1`）。
- 先 deterministic，后 LLM：报错含 `DeterministicContractGateError`/`DeterministicGateCrash` 时，优先修 spec/语义契约/占位符/measure_ref 等；否则再看报告的 `诊断信息`（raw_responses/parsed）排查 prompt/解析问题。
- 报告路径与阅读顺序：`artifacts/semantic_reports/<module>_*_report.md` → `运行信息` → `规则版本` → `审稿结果` → `诊断信息`。

只要完成本次变更“必跑”的 Stage 并通过，才允许提交 PR；若选择了 `-Stage all`，则需四个阶段都通过。若命中“浏览器验收（前端/交互）”的触发条件，还需补做该节要求的浏览器验收并在 PR 描述附证据。若某阶段失败，请先根据日志修复，再重新运行对应阶段直至通过。任何豁免都必须在 PR 描述中说明原因与补救计划。
