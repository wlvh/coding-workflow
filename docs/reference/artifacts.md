# 关键产物说明

这套工作流围绕少数几个核心产物运转。每个阶段只消费上一个阶段已经落地的产物，避免上下文漂移。

## 产物清单

| 产物 | 作用 | 主要生产者 | 主要消费者 |
| --- | --- | --- | --- |
| 需求 | 定义业务目标、边界和约束 | 人类 | FSD 制定阶段 |
| FSD Core Contract | 把需求翻译成可实现、可测试的契约 | 网页端 Pro 模型 | Bridge、Issue、Review |
| Repo Impact Forecast | 预测 FSD 与当前仓库的触点和风险 | Target State Bridge Agent | Issue、开发、Review |
| Target State Bridge | 定义上线后应观察到的目标状态与验证矩阵 | Target State Bridge Agent | Issue、开发、Review |
| Issue | 把契约、范围、任务拆解和验收条件固化 | Issue Agent | Coding Agent、Reviewer |
| PR_BODY.md | 汇总本地全部修改、测试、风险和用户可见变化 | 开发者或 Coding Agent | Reviewer、合并治理 |
| Review Findings | 审核阶段发现的问题和修复建议 | GPT 5.4 Pro / Codex / Opus | 开发修复回合 |
| Merge Readiness Report | 判断当前 PR 是否具备可合并性 | Claude merge-readiness workflow | PR 合并决策 |
| FSD 完备性验收报告 | 在主干代码上倒查 issue 是否真正完成 | 网页端 GPT | Issue 关闭决策 |
| 用户视角验收建议 | 站在最终用户角度补齐验收动作 | GPT 5.4 thinking | Codex 二次验收 |

## 推荐阅读顺序

1. 先读 [README.md](../../README.md) 的主流程。
2. 再看对应阶段说明文件。
3. 需要执行时，再打开对应的 `prompts/` 文件复制 prompt。
4. 需要自动化合并治理时，再看 workflow 文件。

## 设计原则

1. 契约前置：所有实现和审核都以后续可验证的契约为准，而不是靠临场口头补充。
2. 产物接力：下一阶段只基于已经固化的产物工作，减少模型间理解偏差。
3. 预测不承诺：涉及仓库触点、模块影响、代码量的内容只写预测，不写保证。
4. 用户可见优先：所有 Done 定义都要能落到调用方、文档、测试和交付状态上。
