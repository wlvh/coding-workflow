## 指引
你需要将你被要求完成的SOP的步骤转为todo list进行step by step的完成。

## SOP 原则
* 原则 A：SOP 每一步都用同一种结构：每一步只允许包含三类信息：做什么（动作），去哪看（权威引用，精确到文件/章节），做完如何验收（跑哪个测试/生成哪个 artifact）。除此之外，不允许把规范再讲一遍。
* 原则 B：SOP 不写“会变的列表”，只写“入口”。这样将来就算 Stage 变更、环境变量调整，也只需要改 TESTING.md / 脚本，而 SOP.md 不用动（自然防 drift）。
* 原则 C：SOP.md 绝对不是“规范文档”；它只是“流程骨架 + 指向权威文档/命令/测试”的导航页。发生冲突时：以 tests / 合同 / 规范文档为准，SOP.md 自动作废。
* 例子：如果 PR_Checklist 和 TESTING.md 已经覆盖了“该跑什么、该更新什么、该交付什么产物”，SOP 不再重复 PR/测试细节。反过来，如果 SOP 被迫写 PR/测试细节，说明 Checklist 或 TESTING 有缺口，应该补它们，而不是补 SOP。

## 语义模型迁移入口
* 如果任务触及 DAX 表/列引用、公共过滤、cohort 桥接、executeQueries 结果解析：先看 `AGENTS.md` 的“语义模型迁移约定”和对应文件入口，再按本 SOP 走流程。
* 当前仓库默认做法是 `semantic_model_registry.py + core/utils.py + alias-first parser`；SOP 不重复定义这套规则，只负责告诉你在什么步骤引用它们。

## SOP 0：新增 / 修改分析查询（KPI / 图表）时的落盘原则

0. **先判断是否触碰“语义模型引用 / 结果解析”层**
   * 做什么：
     * 若本次改动涉及 DAX 对象名、过滤器拼接、cohort/TREATAS、Queue/Site 能力、Power BI 返回键解析，先确认应复用 registry / utils / alias-first parser，而不是直接手写表名或复制旧 fallback。
   * 去哪看：
     * 运行时抽象与迁移规则 → `AGENTS.md` 的“语义模型迁移约定”
     * 表/列引用与能力接口 → `core/semantic_model_registry.py`
     * 公共过滤与 cohort 入口 → `core/utils.py`
     * parser 顺序示例 → `services/flow_reports.py`、`services/dsat_reports.py`
   * 如何验收：
     * 新 DAX 主路径不新增裸 `vwpcse_*`
     * parser 主路径采用 `alias/alias family -> 新 FQN fallback`；legacy FQN 只允许留在 registry 的基线 diff 元数据中
     * 对应近单元测试已补齐并按 `TESTING.md` 跑通。

1. **先判断“你在做什么类型的输出”**
   * 去哪看：
     * 输出 JSON 结构（对外契约）→ `api_schema.py`
     * 前端如何消费与字段名依赖 → `static/index.html`
     * 用户可见行为与验收不变量 → `interact.md`
     * DAX 输出形态约束（KPI/分组/TopN 等模板）→ `dax_instruction.md`（模板章节）
   * 如何验收：
     * 改完后跑 `TESTING.md` 要求的 Stage（至少 quick；若改了对外结构，补跑 contract）。
     * 若触及筛选器、URL、图表 hover/click、下载、加载态或错误提示：补执行 `TESTING.md` 的“浏览器验收（前端/交互）”。

2. **KPI（固定指标列表）一律 spec 化，避免口径漂移**
   * 做什么：
     * 将每个 KPI 的 natural/semantic/dax 定义落到 `spec/<module>_metrics.json`（例如 `spec/flow_metrics.json`、`spec/dsat_metrics.json`）。
     * 将该端点需要的 KPI 顺序落到 `spec/<module>_metrics.json.queries.<QueryId>.metrics`（例如 Flow 的 `FlowKPIs`、DSAT 的 `DSATKPIs`）。
     * DAX 构建只做“注入 filters/占位符 + 渲染 spec”，避免在 `dax/*.py` 里硬编码 `ROW("Metric", "...")`。
   * 去哪看：
     * 指标语义枚举与 dax_family 约束 → `spec/nature2semantic2dax.md`
     * 指标规范的渲染入口（loader/render）→ `core/metrics_spec.py`
     * 模块 KPI 查询构建（示例）→ `dax/flow.py` 的 `build_dax_kpis`、`dax/dsat.py` 的 `build_dax_dsat_summary`
     * 模块混合策略说明（KPI spec + 图表骨架）→ `dax/<module>.py` 文件头注释（DSAT summary 走 spec，其余走代码骨架）
   * 如何验收：
     * 单元：`tests/core/test_metrics_spec.py`、`tests/dax/test_flow.py`/`tests/dax/test_dsat.py`
     * 语义一致性（如涉及 flow 指标语义审稿）→ 按 `TESTING.md` 的 openai Stage 执行。

3. **图表/明细（分组数据集）优先代码化：spec 只承载可复用“指标口径”，不承载“整段查询骨架”**
   * 做什么：
     * 将图表查询骨架（`SUMMARIZECOLUMNS/ADDCOLUMNS/TOPN`、两阶段性能优化、分组维度组合等）写在 `dax/<module>.py`。
     * 复用的“指标口径”（同一个指标在多个图表/端点被引用、且需要稳定语义）优先沉淀为语义模型度量（查 `json_contract.md`），或抽为 spec 的 metric/shared_vars（按模块策略）。
   * 去哪看：
     * 可用表/列/度量白名单 → `json_contract.md`
     * DAX 写法与性能范式 → `dax_instruction.md`（模板 B/C 等）
     * 运行时语义模型引用规则 → `AGENTS.md` 的“语义模型迁移约定”、`core/semantic_model_registry.py`
     * 过滤注入与 “Unspecified” 约束 → `core/utils.py`（`filters_dax`）与 `AGENTS.md` 的业务知识约定
   * 如何验收：
     * 单元：对应 `tests/dax/test_<module>.py` 与 `tests/routers/test_<module>_router.py`
     * 若影响 API 输出结构或前端解析：补跑 `TESTING.md` 的 contract Stage。
## SOP 1：新增 / 修改 KPI 时的标准流程

1. **收集业务输入**
   * 要求用户按以下要求写清楚：
        - metric_id：遵循现有命名，保持 `queries.<KPIQueryId>.metrics` 中的顺序不被打乱（例如 FlowKPIs/DSATKPIs）。
        - natural.zh / natural.en：双语口径。
        - 模块归属：flow/dsat/...，需写清适用范围。
        - 时间口径：timeAxis 行为（create/close/event 或 none）。
        - axis_semantics
        - 需要的维度过滤：国家/队列/产品/语言等。
        - 计算方式提示：是否使用模型度量（measure_ref），还是需要 distinctcount/percentile 等。
   * 如果用户没有提供完整信息，严禁进行下一步的开发。

2. **生成 &校对structured_natural**
   * 从 natural + axis_semantics 产出一个结构化 JSON（即使不落盘，也要能贴在 PR 描述里）：
      * subject（case/flow/survey）；
      * target_event (escalation / closure / self_help_deflection / fcr / fwr …)；
      * 是否是 ratio；
      * base_population_hint / numerator_hint；
      * 时间行为以 `axis_semantics` 为准。
   * 按 nature2semantic2dax.md 4.1 节 schema 校验。

3. **维护semantic枚举与规范文档**
   * 先确定`spec/nature2semantic2dax.md`所有 semantic 字段取值，再检查枚举是否需要扩展
   * 一旦涉及语义规则变更（semantic 枚举 / dax_family 约束 / 占位符白名单等）：先更新 `spec/nature2semantic2dax.md` 的 `semantic_contract_json`（machine-readable contract），再更新对应自然语言解释段落（避免 drift）。
   * 如果用到了新的 semantic 取值（type/subject/base_population_kind/…）：
     * 先更新 `spec/nature2semantic2dax.md` 对应枚举小节；
     * 按`spec/nature2semantic2dax.md`第7章的触发条件自检一下，确认是不是“必须更新”的场景。
   * 所有小类枚举必须在 nature2semantic2dax.md 里有定义：
     * 如果没有，就先在文档 3.x 小节加枚举说明，再回到 JSON 填值。

4. **设计DAX**
   * DAX 编写规范 → 看 dax_instruction.md（尤其 registry-first 对象引用、日期过滤、度量引用、自检清单）。
   * 可用表/列/度量/关系 → 查 json_contract.md。
   * 语义模型对象引用、Queue/Site/cohort 能力 → 查 `AGENTS.md` 的“语义模型迁移约定”、`core/semantic_model_registry.py`、`core/utils.py`。
   * dax_family 的结构要求/必需占位符/必需事实表 → 以 spec/nature2semantic2dax.md 为准。
   * 落盘位置：spec/<module>_metrics.json.metrics.<metric_id>.dax（例如 `spec/flow_metrics.json`、`spec/dsat_metrics.json`）。
   * 使用 metrics_spec 渲染 DAX 并确认无占位符残留

5. **测试**
   * 按 TESTING.md 选择 Stage。
   * 语义报告应生成在 artifacts/semantic_reports/* 并随 PR 提供。
   * 测试失败时优先按 `TESTING.md` 的“语义审稿失败怎么排查”定位；如需理解报告结构再看 SOP 2。

6. **PR提交**
   * PR DoD：逐条执行 PR_Checklist.md。

7. **如果只修改现有 KPI 的口径 / 语义 / DAX**
   * 先确认改的是哪一层
     * 只改 natural → 跳到步骤 5；
     * 只改 semantic → 步骤 3+5；
     * 只改 DAX → 步骤 4+5
     * 三者都有变 → 从步骤 2 开始完整执行
   * 确定后按照对应步骤进行修改和测试     
---

## SOP 2：使用语义 LLM 报告调试指标

1. **先确认你跑到了语义审稿**
   * 去哪看：`TESTING.md` 的 `openai` Stage（以及“语义审稿失败怎么排查”小节）。
   * 如何验收：报告会落盘到 `artifacts/semantic_reports/`，文件名形如：
     * `<module>_natural_semantic_report.md`（natural↔semantic）
     * `<module>_semantic_dax_report.md`（semantic↔DAX）

2. **按报告结构读（先看信息密度最高的块）**
   打开对应 Markdown 报告（示例：`artifacts/semantic_reports/flow_semantic_dax_report.md`）建议按顺序看：
   * 运行信息：确认是不是你这次 commit；
   * 规则版本：确认 spec/contract 版本与 hash 可追溯；
   * 审稿结果：聚焦 `ok=false` 的 metric_id 与 issues；
   * 诊断信息：必要时再看 raw_responses/parsed 对照 prompt 排查。

3. **修复优先级（先规则/口径，再实现）**
   * natural↔semantic：优先修 `spec/<module>_metrics.json` 的 natural/semantic，必要时补 `spec/nature2semantic2dax.md`（以 `semantic_contract_json` 为准）。
   * semantic↔DAX：优先修 DAX 使其满足 dax_family/占位符/measure_ref 约束；若规范缺口，再回到 `spec/nature2semantic2dax.md` 补齐契约与解释。
   * 修复后按 `TESTING.md` 重跑对应 Stage，直至通过。
  * 如果发现 dax_family 设计本身不合理（例如如果需要对 ≥3 个 metric 做同类修改，说明规范有缺口），再反推去改规范
  
## SOP 3：新增分析场景 / API 的标准流程（流程骨架）

### 适用范围

* 新增一个“分析场景”交付：新增/扩展 FastAPI endpoint，返回结构化分析数据（表格/趋势/榜单/聚合）；可选再提供 insights/LLM endpoint。

### 1) 收集场景业务输入（Scenario Brief）

* **做什么（动作）**

  * 固化：场景名称/场景 ID、目标用户价值、关键输出（必须返回哪些表/字段）、默认 timeAxis/timeGrain、过滤器范围、阈值策略（minSample/topN/空数据处理）、错误处理（400/500/降级/返回空结构）。
  * 输入不完整 **不得进入下一步开发**（避免“边写边猜”）。
* **去哪看（权威引用）**

  * 输入字段模板可参考 SOP1 的“收集业务输入”（natural/timeAxis/axis_semantics/过滤维度的思想同样适用到场景层）。
* **做完如何验收（验收）**

  * PR 描述中贴出 Scenario Brief（至少：输入/输出/默认行为/边界处理/需要的表与度量清单）。


### 2) 定义对外 API 契约（Request / Response / Error）

* **做什么（动作）**

  * 明确：endpoint path、HTTP method、请求体 schema、响应 schema（字段名/类型/可空规则/排序稳定性）、错误码（400/422/500）与错误信息格式。
  * 若新增/修改任何 report endpoint：**必须同步更新 `report_registry.py`（端点级 SSOT）**，补齐 method/path/schema/default payload/timeAxis policy/contract 豁免理由。
  * 若新增/修改对外响应结构：**必须同步更新 `api_schema.py` 的 schema 定义**（避免“文档与行为不一致”）。
* **去哪看（权威引用）**

  * 端点级 SSOT（method/path/payload/豁免）→ `report_registry.py`
  * Response schema 定义 → `api_schema.py`
  * FastAPI 入口与路由注册 → `main.py`、`routers/*`
  * 契约/场景测试目录约定 → `tests/contracts/`、`tests/scenarios/`
* **做完如何验收（验收）**

  * 至少新增/更新一个契约测试用例（`tests/contracts/`），并按 TESTING.md 跑 `Stage contract`（包含 registry lint 与 endpoint coverage gate）。

### 3) 数据可用性与白名单校验（Contract Gate）

* **做什么（动作）**

  * 为场景中每个输出字段列出来源：来自哪个 fact/dim、用哪个 measure/column、是否需要关系、是否需要 TREATAS/桥接。
  * 若所需表/列/度量不在白名单中：先补合同/导出器，再继续实现。
  * （可选）若场景强依赖 key 映射假设（1:1、无 blank、无 1:N）：设计一个最小 data_quality 检查并在 meta 回显。
* **去哪看（权威引用）**

  * 可用表/列/度量/关系白名单 → `json_contract.md`
* **做完如何验收（验收）**

  * 提供“字段溯源表”（输出字段 → 合同中的表/列/度量），并在 DAX/测试中禁止引用未在合同出现的对象（由 `tests/dax/*` 兜底）。

### 4) 设计与实现 DAX 查询（dax/*）

* **做什么（动作）**

  * 新增/修改 `dax/<module>.py` 的 `build_dax_<scenario>`：

    * 语义模型对象引用统一经 `core/semantic_model_registry.py`/`core/utils.py` 输出，不在业务 DAX builder 中裸写旧模型对象名。
    * 过滤器入口统一：复用 `sanitize_filters + filters_dax`
    * timeAxis 行为符合模块约定（涉及 cohort 生命周期：按约定处理 dimdate / REMOVEFILTERS / TREATAS）
    * KPI 行集：优先 spec 驱动（`spec/<module>_metrics.json` + `core/metrics_spec.py` 渲染），避免在 `dax/*.py` 硬编码 KPI 列表与表达式。
    * 契约 stub 路由：DAX 顶部添加 `-- contract: <tag>` 注释，并在测试的 `fake_execute_dax` 按 tag 匹配返回（参考 `tests/contracts/test_api_contract.py`），避免匹配 DAX 具体文本导致“伪漂移”。
* **去哪看（权威引用）**

  * DAX 编写规范 → `dax_instruction.md`
  * 可用对象白名单 → `json_contract.md`
  * semantic/dax_family/占位符约束 → `spec/nature2semantic2dax.md`
  * KPI spec 渲染入口与校验入口 → `core/metrics_spec.py`
* **做完如何验收（验收）**

  * 新增/更新 `tests/dax/test_<module>.py` 验证：过滤注入、占位符无残留、关键结构（如 TREATAS/REMOVEFILTERS）存在。
  * 按 TESTING.md 至少跑 `Stage quick`。

### 5) 实现服务编排与 API 路由（services/* + routers/*）

* **做什么（动作）**

  * 建议拆分职责：

    * `services/<scenario>.py`：做参数 normalize（fail fast）、执行一个或多个 DAX、组装 response、补 meta 回显（便于排障与契约一致性）。
    * `routers/<module>.py`：只负责 request/response 的入口与调用 service（保持薄）。
  * 若 service 需要解析 Power BI 返回行：parser 主路径统一采用 `alias/alias family -> 新 FQN fallback`；legacy FQN 只允许保留在 registry 的基线 diff / migration forensics 元数据里，而不是重新回到运行时 helper 链路。
  * 若新增文件：同步更新 AGENTS.md 的文件入口说明（测试文件不在此要求内）。
* **去哪看（权威引用）**

  * 分层分工入口说明 → `AGENTS.md`
  * Power BI 执行入口 → `services/pbi.py`
  * parser 顺序示例 → `services/flow_reports.py`、`services/dsat_reports.py`
* **做完如何验收（验收）**
 
  * 新增/更新 `tests/routers/test_<module>_router.py`（路由层近单元测试）；对外结构变更必须跑 `Stage contract`。

### 5.A) 若场景包含关键查询 / singleton 查询 / 显式降级监控

* **做什么（动作）**

  * 先判定当前查询属于普通查询、关键查询、singleton 查询还是可降级监控。
  * 再按权威规则决定：是否启用严格结构读取、是否 enforce exactly-one-row、是否允许补 0 / `unknown`、是否需要产出 risk artifact。
  * 若改动波及错误码、降级或 fail-fast 语义，同步规划 `services/*`、`routers/*` 与必要场景测试，并在 PR 描述中写清取舍。
* **去哪看（权威引用）**

  * 规则定义 → `AGENTS.md` 的“关键查询契约与错误分层约定”
  * 测试要求 → `TESTING.md` 的“关键查询与错误语义回归”
  * 提交流程硬约束 → `PR_Checklist.md`
* **做完如何验收（验收）**

  * 对应 `tests/core/*`、`tests/services/*`、`tests/routers/*` 或 `tests/scenarios/*` 已补齐并按 `TESTING.md` 跑通。
  * 若命中 risk artifact 触发条件，相关 artifact 已生成并在 PR 描述中引用。
  * PR 描述已写清 strict / singleton / 补 0 / 降级 / 错误分层的最终取舍。

### 5.1) 如新增聚合 Report（/api/report）

* **做什么（动作）**
  * 使用 `services/report_engine.py` 作为统一编排骨架：以 `run_aggregate_report` 为入口（normalize_request → run_reports；失败统一 `log_report_error`）。
  * 聚合端点本身与可选子报告都必须在 `report_registry.py` 注册（聚合端点纳入 contract；子报告复用既有 report_id 与 schema）。
  * `/api/report` 的 response schema 在 `api_schema.py` 显式组合子报告 schema（`reports.<id>` 复用单端点结构，避免重新发明数据结构）。
  * addons 仅以 `report_registry.py` 的 `ADDON_REGISTRY` 声明并默认关闭；非确定性能力必须显式 opt-in。
  * Roadmap：addons 可演进为“可组合的分析能力插件”（packs/profiles）。建议通过显式选择 profile/pack 展开一组 addons；
    `enabled_by_default` 仅作为推荐元数据，runtime 不做隐式自动启用。
* **做完如何验收（验收）**
  * `tests/contracts/test_report_aggregate_contract.py` 覆盖默认 reports、timeAxis policy 回显与 unknown report_id 400。
  * `tests/contracts/test_router_thin_gate.py` 通过（router 不得直接触达底层执行入口）。

### 6) 如包含洞察/LLM：实现 Insights 服务与 schema 兜底（services/llm.py）

* **做什么（动作）**

  * 若场景需要洞察：新增 `POST /api/<module>/<scenario>/insights`（或复用既有路径风格，如 `POST /api/dsat/insights`）。
  * 输出严格 JSON schema；解析失败时提供可控降级（空数组 / fallback 文本），禁止凭空推断数据事实。
* **去哪看（权威引用）**

  * OpenAI/services 变更的测试要求与 Stage 选择 → `TESTING.md`
* **做完如何验收（验收）**

  * 新增/更新 `tests/services/test_llm.py`（或对应测试），并按 TESTING.md 视情况跑 `Stage openai`。

### 7) 如引入新指标/新语义枚举/新模块 spec：同步治理（Spec & Semantic & Startup Validation）

* **做什么（动作）**

  * 新 dax_family / 新 semantic 枚举：更新 `spec/nature2semantic2dax.md` 并补齐约束。
  * 新增模块 spec：

    * 在 `core/metrics_spec.py` 注册模块入口；
    * 提供对应 `validate_<module>_spec`（或未来抽象 `validate_metrics_spec(module=...)`）并确保 **`main.py` 启动期会执行校验**（Fail Fast）。
* **去哪看（权威引用）**

  * 语义枚举与模板族权威规范 → `spec/nature2semantic2dax.md`
  * spec 加载/渲染/校验入口 → `core/metrics_spec.py`
  * 启动期校验入口 → `main.py`
* **做完如何验收（验收）**

  * `tests/core/test_metrics_spec.py` 覆盖新增/修改的 spec 校验；
  * 本地启动服务能正常启动（spec 校验通过）；若故意破坏 spec，应在启动期直接报错并中断启动（Fail Fast）。

### 8) 测试阶段选择与交付产物（按 TESTING.md）

* **做什么（动作）**

  * 根据改动落点（routers/dax/services/spec/semantic）选择必跑 Stage；每次改代码至少同步改一处测试。
  * 若改动包含页面入口、筛选器、图表 hover/click、下载、加载或错误态等用户可见交互：除常规 Stage 外，补规划浏览器验收。
* **去哪看（权威引用）**

  * Stage 决策表与命令入口 → `TESTING.md`
  * 浏览器验收触发条件与证据要求 → `TESTING.md` 的“浏览器验收（前端/交互）”
  * 用户可见断言入口 → `interact.md`
* **做完如何验收（验收）**

  * 完成本次变更的必跑 Stage 且通过；如涉及语义审稿，附上对应 artifacts 报告。
  * 如命中用户可见交互触发条件，浏览器验收产物已生成，且覆盖项可回溯到 `interact.md`。

### 9) PR 提交（DoD）

* **做什么（动作）**

  * 逐条执行 PR_Checklist.md；需要豁免必须在 PR 描述解释原因。
* **去哪看（权威引用）**

  * PR 合规与测试阶段要求入口 → `AGENTS.md`
* **做完如何验收（验收）**

  * Checklist 全部勾选；测试 Stage 可追溯；对外契约变更有 contract test 覆盖。



## SOP 4：语义治理入口（已拆分，避免 drift）

> 说明：SOP 4 不再承载会漂移的“Stage/命令/报告字段”细节；这里只保留入口导航。发生冲突时，以 `TESTING.md` / 测试实现为准。

* **语义审稿触发条件**
  * 改动 `spec/*_metrics.json` 的 natural/semantic/dax/axis_semantics，或改动语义契约/审稿 runner/prompt/gate。
* **Stage 选择 / 命令 / 产物**
  * 统一入口 → `TESTING.md`（`openai` Stage + “语义审稿失败怎么排查”小节）。
* **规则更新优先 machine-readable contract**
  * 统一入口 → SOP 1（先改 `spec/nature2semantic2dax.md` 的 `semantic_contract_json`，再补自然语言解释）。
* **新模块接入（禁止硬编码清单）**
  * 统一入口 → SOP 3 的 “Spec & Semantic & Startup Validation”（只在 `core/metrics_spec.py` 注册模块 + 启动期校验；避免在测试/脚本里堆模块列表）。
* **失败定位顺序**
  * 统一入口 → `TESTING.md` 的”语义审稿失败怎么排查”；报告阅读建议见 SOP 2。

## SOP 5：语义模型核心指标发现流程（Metric Discovery Funnel）

### 适用范围

* 当接入一个新的 Power BI 语义模型（Dataset）时，发现“组织已认可/推荐展示”的核心指标清单与分类体系（常见实现：Atlas/Mapping/Metric Registry 表；或度量 `DisplayFolder` 约定）。
* 本 SOP 的输出用于后续 bundles/metrics_catalog 沉淀，以及决定哪些指标需要 spec 化（见 SOP 1）。

### 前置条件

* 已有目标 Dataset 的读取权限，并能通过 `services/pbi.py` 的 `execute_dax()` 执行 DAX（含 `INFO.VIEW.*`）。
* 如本仓库会接管该模型：先导出/更新 `json_contract.md`（权威入口见 `TESTING.md` 的 “json_contract.md（语义模型契约）导出与验收”）。

### 1) 契约快照（json_contract.md）

* **做什么（动作）**
  * 确认 `json_contract.md` 与目标 Dataset 对应且为最新；否则按 `TESTING.md` 的入口重新导出。
* **去哪看（权威引用）**
  * 导出与验收入口 → `TESTING.md` 的 “json_contract.md（语义模型契约）导出与验收”
  * 契约内容（可用 measures/relationships/date_axis/facts/dimensions）→ `json_contract.md`
* **做完如何验收（验收）**
  * 按 `TESTING.md` 的 Fail Fast 命令验收 `json_contract.md` 可解析且 `counts` 合理。

### 2) 元数据盘点（INFO.VIEW.*）

* **做什么（动作）**
  * 用 `INFO.VIEW.TABLES()` / `INFO.VIEW.COLUMNS()` / `INFO.VIEW.MEASURES()` / `INFO.VIEW.RELATIONSHIPS()` 拉取四张元数据视图，形成“全局地图”（表/列/度量/关系计数 + 表清单）。
  * （可选）表角色推断（fact/dim/other）：以导出器/推断逻辑为准，不在 SOP 写死命名规则。
* **去哪看（权威引用）**
  * DAX 执行入口 → `services/pbi.py`
  * 元数据提取与表分类入口 → `process_semanticmodel.py`（`LLMModelDocLite._fetch_metadata` / `LLMModelDocLite._analyze`）
* **做完如何验收（验收）**
  * 产出表清单（至少含：table_name、is_hidden、description、列数/度量数、是否 auto date），并解释与 `json_contract.md.counts.tables` 的差异来源（hidden/auto date 等）。

### 3) 枢纽度量定位（Hub Measures）

* **做什么（动作）**
  * 优先基于 `json_contract.md.measures[*].depends_on` 统计每个度量的依赖扇出（被依赖的 measures/columns 数），按扇出排序找出若干候选“枢纽度量”（常见为 Mapping/Atlas/指标入口度量）。
  * 若根 `json_contract.md` 的 `depends_on` 因当前 REST `INFO.VIEW.MEASURES()` 元数据缺口而退化：改用 `INFO.VIEW.MEASURES()` 的 Expression 文本或风险工件做补救，不要把空 `depends_on` 当成“无依赖”的真相。
* **去哪看（权威引用）**
  * 依赖图与宿主表信息 → `json_contract.md` 的 `measures` 段（`depends_on`、`table`）
  * 兜底元数据来源 → `INFO.VIEW.MEASURES()`（通过 `services/pbi.py`）
* **做完如何验收（验收）**
  * 产出“枢纽度量清单”：`measure | host_table | fan_out | depends_on_measures/columns 摘要`；并明确是否存在候选“指标注册入口”。

### 4) 指标注册表探查（Atlas / Metric Registry Table）

* **做什么（动作）**
  * 对 Step 3 命中的 `host_table`，用 `INFO.VIEW.COLUMNS()` 判断是否为“指标注册表”（具备：指标名列 + 分类列 + 排序列等）。
  * 仅用 `TOPN` 采样（避免全表 dump）生成注册表快照（例如 `Category | Metric | Order`）。
  * 对注册表中的每条 Metric 名做存在性校验：必须能在模型 measures 中命中（以 `json_contract.md` 或 `INFO.VIEW.MEASURES()` 为准）。
  * 若 Atlas 仅出现在 contract/元数据而未进入 runtime API/registry，先登记范围评估结论；不要在没有专门 issue 的情况下直接接入运行时。
* **去哪看（权威引用）**
  * 表/列元数据 → `INFO.VIEW.TABLES()` / `INFO.VIEW.COLUMNS()`（通过 `services/pbi.py`）
  * measures allowlist → `json_contract.md` 的 `measures` 键集合
* **做完如何验收（验收）**
  * 注册表快照中 Metric 名 100% 命中 measures（未命中项必须给出原因与处理建议：命名差异/已下线/权限不可见）。

### 5) 覆盖对账 + 数据健康（Spec & Data Health）

* **做什么（动作）**
  * 覆盖对账：将“核心指标集（注册表或替代分类）”与本仓库 `spec/*_metrics.json` 的 KPI 清单做差集对账；需要新增 KPI 的按 SOP 1 推进。
  * 数据健康：针对核心指标涉及的关键 fact↔dim 关系，产出 blank_fk_ratio / orphan_count / coverage 等证据化指标；阈值与颜色分级以实现/规则为准，不在 SOP 写死。
* **去哪看（权威引用）**
  * Spec KPI 清单 → `spec/*_metrics.json`
  * Spec 语义枚举与 dax_family 约束 → `spec/nature2semantic2dax.md`
  * 新增 KPI 的流程骨架 → SOP 1
  * 关系清单 → `json_contract.md` 的 `relationships`
  * 关系体检入口 → `process_semanticmodel.py`（`LLMModelDocLite._profile_relationships_lite`）
* **做完如何验收（验收）**
  * 产出“覆盖对账表”与“关系健康报告”；并要求 RED/YELLOW 风险在后续 spec/endpoint 的 meta 中可追溯回显（避免静默风险）。
