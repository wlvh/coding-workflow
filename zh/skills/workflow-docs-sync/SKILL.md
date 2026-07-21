---
name: workflow-docs-sync
description: 在一个会话内把 wlvh/coding-workflow 的九份核心工作流文档同步并项目化到目标 Git 仓库。用户要求同步 workflow docs、补齐或核对 architecture/capability/interact/business guide/testing/governance 文档时使用；只接受目标仓库、可选 zh/en 语言和可选结束后创建 draft PR。
---

# Workflow Docs Sync

在一个会话内完成编排。始终由主 Agent 独占目标工作区写入；领域分析和审计只读。

## 用户输入

- 要求目标仓库路径。
- 语言仅允许 `zh` 或 `en`，未提供时使用 `zh`。
- 未明确要求时不创建 draft PR。
- 不要求或接受用户提供上游 SHA、上游 checkout、内部命令或分析分工。

## 上游解析

1. 先判断当前 Skill 是否位于 canonical `wlvh/coding-workflow` checkout：其 Git 根目录
   必须同时包含当前 Skill 和所选语言的九份模板。满足时直接复用该 checkout。
2. 无法定位 canonical checkout 时，在仓库外创建临时目录并 shallow clone
   `https://github.com/wlvh/coding-workflow.git`。网络失败时停止并报告，不回退到缓存模板。
3. 调用 `scripts/sync_docs.py prepare --target-repo <target> --upstream-dir <upstream>
   --language <zh|en>`，只消费其单行 JSON。
4. 保存返回的 `target_head` 与 `upstream_sha` 于当前会话；整轮使用同一 SHA。
5. 会话结束时清理本轮临时 clone；canonical checkout 不清理。

## 执行流程

1. 主 Agent 读取目标仓库规则、入口、代码、测试和现有文档，建立带路径证据的代码地图。
2. 完整读取 [references/sections.md](references/sections.md)，启动四个相互隔离的只读分析：
   Architecture、Capability / User Behavior、Testing、Governance。明确禁止它们编辑、
   stage、commit 或运行会产生项目 artifact 的命令；发现只在当前会话返回。
3. 平台不支持 subagent 时，主 Agent 按 reference 中四个章节的顺序逐章分析，保持相同
   输出结构和最终用户体验。
4. 主 Agent 合并四份发现，只修改九份核心文档；`.gitignore` 仅在目标项目确有忽略
   需求时修改。不要创建运行记录、模板镜像或工单；整个同步流程不读取、创建、改写或删除
   仓库内 `PR_BODY.md`。
5. 完整读取 [references/audit.md](references/audit.md)，启动一个独立只读对抗性审计。
6. 主 Agent 修复全部 BLOCKER 和所有可行动 WARN，再要求审计者只读轻量复审修复点
   及其跨文档影响。无法闭合的产品判断保留为未解决决策，不得编造事实。
7. 主 Agent 依据目标 `TESTING.md` 和真实代码路径运行必要测试。记录原样命令、结果和
   未运行原因；测试输出不是检查器 receipt。
8. 调用：

   ```bash
   python3 <skill-root>/scripts/sync_docs.py check \
     --target-repo <target> \
     --upstream-dir <upstream> \
     --upstream-sha <prepare 返回的 upstream_sha> \
     --expected-target-head <prepare 返回的 target_head> \
     --language <zh|en>
   ```

9. 检查失败时修复真实问题并重跑相关测试和检查；不得放宽断言、跳过必要测试或引入兼容实现。

## 最终报告

一次性报告：修改文件、代码与测试证据路径、每条测试命令及结果、未解决决策、审计发现
及处置、内部固定的上游 SHA。明确说明机械检查只验证最终仓库状态，不证明分析、审计或
测试的执行历史。

用户要求 draft PR 时，在上述流程成功后使用仓库外临时 Markdown body，把 commit、push
和 draft PR 创建交给通用 GitHub 发布能力。同步脚本不参与发布。
