# PR提交检查清单
注意：你必须一一完成check清单（等价于todo list）并最终提交pr，任何偷懒和跳过都会让用户暴跳如雷。
为了保持代码简洁，节约代码审核者的上下文窗口，如需在用户明确同意的前提下整理当前 HEAD 提交，可使用 git commit --amend（仅覆盖当前 HEAD 一条提交；如需合并多条提交，请先 git reset --soft <基准> 或 git rebase -i 做 squash 后再提交）。
使用 gh pr create --title（修改主题+MMDD日期） --body-file（建议使用 `PR_BODY.md`） --head <feature-branch> --base master 来创建PR，固定指令避免遗漏参数。始终牢记你可以使用gh工具。
在提交 PR 前的确认清单，你需要将其转为todo list进行step by step的完成：
- [ ] 撰写结构化的工作总结，至少包含以下小节，确保下一个开发人员能顺利接手继续开发：
  - 背景 & 目标（Why）：本次改动解决了什么问题？关联哪些 Issue / 需求？
  - 实现方案（How）：核心思路、关键设计决策、有无其他候选方案。
  - 变更范围（What）：主要修改了哪些模块/文件（可按目录分组列出）；文件清单必须来自 `git diff --name-only <base>...HEAD` 的实际输出，禁止写未出现在当前 patch 中的文件。
- [ ] 确认当前分支不是主干，并调用 git diff 工具仔细分析本地修改，确认无遗漏
- [ ] 已用 `git diff --name-only <base>...HEAD` 反向核对 `PR_BODY.md` 的“变更范围/测试文件”清单：diff 中有但 PR_BODY 未列的已补齐，PR_BODY 中列了但 diff 中不存在的已删除
- [ ] 测试策略以 `TESTING.md` 为准：按“变更类型决策表”选择并跑通必跑 Stage（优先使用 `.\run_tests.ps1`）；PR 描述必须分别提供：
  - 测试证据（Stage + 命令 + 关键输出摘要/日志/CI link；不适用的 Stage 标注 N/A 并写清原因）
  - 测试变更清单（实际新增/修改了哪些测试文件；若仅重跑 Stage 而未修改测试文件，必须明确写“未修改测试文件，仅重跑 <Stage> 作为 gate”）
- [ ] 若本次改动包含用户可见前端交互（例如 `static/index.html`、筛选器、URL 状态、图表 hover/click、下载、加载态、错误提示）：已按 `TESTING.md` 执行浏览器验收，并在 PR 描述附上覆盖的 `interact.md` 断言与证据（截图/trace/报告摘要/产物路径）
- [ ] 所有度量都引用了 json_contract.md 中的定义
- [ ] 没有在路由/服务层重复定义度量计算逻辑（遵循 json_contract.md 中的语义模型度量）
- [ ] DAX 查询包含注释说明引用了哪些契约度量
- [ ] 若修改了 API 输出结构：已同步更新 `api_schema.py`（response schema）与前端/调用方解包逻辑（例如 `static/index.html`），并通过 contract tests
- [ ] 若修改了状态码、错误处理逻辑或 fail-fast 语义：已同步更新 `tests/contracts/` 中相关用例；如未新增/修改 contract test，必须在 PR 描述中写清豁免理由，并说明由哪些近单元/场景测试覆盖
- [ ] 若新增/修改关键查询：已说明是否使用 `extract_rows(..., strict_structure=True)`；若未使用，PR 描述已写清为什么宽松空结果仍是合法语义
- [ ] 若新增/修改 singleton 查询（如单值 meta/data_quality/`ROW(...)` 查询）：service 已 enforce exactly-one-row，未静默取首行或补默认值
- [ ] 若引入补 0、降级或 `unknown` 语义：已明确“合法缺失”和“非法结构”的边界，并有对应近单元/场景测试
- [ ] 若修改 router 错误分层：已按错误来源/异常类型而非异常文案映射 `400/500/unknown`，并有对应测试证明
- [ ] 若存在非 blocker 但会导致 drift、部分生效或数据质量不可信的风险：已产出 risk artifact，或在 PR 描述中说明本次不需要 artifact 的原因
- [ ] 已更新 `report_registry.py`（新增/修改/豁免理由），确保 endpoint 级 SSOT 不漂移
- [ ] 若本次改动按 `TESTING.md` 决策表要求跑 `Stage contract`：确保通过（contract stage 覆盖 registry lint/coverage/router-thin/api schema 等确定性 gate）
- [ ] 若新增/修改了语义模型对象（表/列/度量/关系）并影响白名单，已更新 `json_contract.md`（按 `TESTING.md` 的 “json_contract.md（语义模型契约）导出与验收” 小节更新，并在 PR 中附上生成日志或 diff。）
- [ ] 若修改了 DAX 逻辑，确认 `json_contract.md` 中的定义允许
- [ ] 确认新的 DAX 查询在 Power BI 中的执行时间在可接受范围内（参考 Power BI Live Test 的输出）
- [ ] 检查所有本次新增/修改的测试文件是否遵循了 `TESTING.md` 中的测试原则
- [ ] 是否新增/修改了 semantic 枚举值？如果是，已更新 `spec/nature2semantic2dax.md`
- [ ] 是否新增/修改了 dax_family 逻辑或占位符要求？如果是，已更新 `spec/nature2semantic2dax.md`
- [ ] 若本次变更类型在 `TESTING.md` 决策表中要求 `Stage openai`：已运行并附 `artifacts/semantic_reports/*_report.md`（或其摘要/链接），且报告可追溯到本次 git sha。
- [ ] 当有文件新增和修改后，确认对应的文档已更新。例如新增了测试文件，就需要更新在`TESTING.md`，有代码脚本的功能被修改，更新在`AGENTS.md`的## 文件简介。
- [ ] 任何用户可见的行为变化（入口/输出结构/默认行为/错误提示/排序稳定性）都必须同步更新`interact.md`，并确保浏览器验收覆盖了对应断言
- [ ] 最终提交前，已重新对照 `git diff --name-only <base>...HEAD`、`git status` 与 `PR_BODY.md`，确认 PR 描述不包含历史草稿、本地未提交改动或“计划做但未落地”的内容
