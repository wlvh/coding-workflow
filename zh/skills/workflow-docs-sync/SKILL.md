---
name: workflow-docs-sync
description: 从目标 Git 仓库的代码、配置、测试和 committed artifacts 重建事实，最小必要改写 wlvh/coding-workflow 的九份核心工作流文档，运行项目真实测试，并以 fresh-context independent review 或诚实 self-review 收口。用户要求同步、补齐或核对 architecture、capability、interact、business guide、testing 或 governance 文档时使用；一次调用只接收目标仓库、zh/en 语言和成功后是否创建 draft PR。
---

# Workflow Docs Sync

一次调用完成事实重建、必要文档改写、真实测试、复核和机械检查。现有文档与上游模板都是
待验证声明，不是项目事实来源。主 Agent 是目标工作区唯一写入者。

## 输入与固定边界

- 要求目标仓库的 Git 根目录。
- 语言必须由用户选择，且仅允许 `zh` 或 `en`。
- 只有用户明确要求时，才在全部 gate 成功后创建 draft PR。
- 不要求用户提供上游 checkout、SHA、内部命令、Agent 数量或执行顺序。

按以下方式准备：

1. 如果当前 Skill 位于 canonical `wlvh/coding-workflow` Git 根目录，复用该 checkout。
2. 否则在目标仓库外临时 shallow clone `https://github.com/wlvh/coding-workflow.git`；网络失败
   时停止，不回退到缓存模板。
3. 调用：

   ```bash
   python3 <skill-root>/scripts/sync_docs.py prepare \
     --target-repo <target> \
     --upstream-dir <upstream> \
     --language <zh|en>
   ```

4. 只消费单行 JSON，固定返回的 `target_head` 和 `upstream_sha`，整轮复用同一对 SHA。
5. 创建临时 upstream 时立即记录临时根目录。当前 Agent 必须在任何成功、失败或提前停止的
   最终回复前删除它并运行 `test ! -e <temporary-root>`。未通过时登记
   `WDS-UPSTREAM-CLEANUP / BLOCKER`，不得报告完成；Controller 后置清理不能改判本轮成功。
   canonical checkout 不清理。

`prepare` 从固定 Git object 读取模板，并在任何目标写入前确认九份 source path 都存在且为
UTF-8、八份非 PR source 至少含一个 active marker；随后只创建缺失文件，不覆盖已有文档。
上游 dirty worktree 不影响模板 bytes。不得创建 run state、receipt、ledger、Skill 副本、模板
镜像或仓库内 PR body。

## 重建事实并最小改写

写入前至少运行 `git -C <target> ls-files -z` 建立范围。完整调查当前代码、配置、测试、
committed artifacts、可重复运行结果和必要 Git 历史；不得用旧文档证明旧文档正确，也不得
因为内容未出现在近期 diff 中而跳过。

确认文档问题后、任何语义编辑前，先在会话中登记 finding：唯一 ID、`BLOCKER` / `WARN` /
`NOTE`、代码/配置/测试或 artifact 证据、风险和最小修复边界。不得在编辑完成后根据最终 diff
或 reviewer 结论倒填为“写入前 finding”。同一根因、同一证据链和同一修复边界影响多份文档
时合并为一个 finding，不按文件或行机械拆分。多份文档共同声明但代码和测试不存在的能力，
必须在编辑前登记 `BLOCKER`。

- 全量质疑九份文档，只改错误、缺失、失真或失效内容；正确内容保持零 diff。
- 删除没有当前事实证据的强声明。需要产品判断时记录 open decision，不编造结论。
- 保持 `capability_contract.json → interact.md → docs/business_user_guide.md` 的权威方向。
- 清除所有 active project-fill marker；不要使用固定写入顺序、完成百分比、KEEP ledger 或
  过程状态。
- Architecture、Capability / User Behavior、Testing、Governance 是覆盖维度，不是固定四
  Agent 拓扑。可自行调查，也可按模块、调用链、风险或证据类型委派只读工作；所有结论都
  必须回到项目证据。

## 四个覆盖维度

### Architecture

从真实入口向下重建核心调用链，核对系统目的、模块职责、依赖方向、数据流、状态、错误
模型、配置、认证、外部依赖、artifact、副作用、扩展点和架构债务。主动证伪架构不变量，
不得把未来设想写成 active 现状。

### Capability / User Behavior

从入口、UI 或 API 响应、错误、测试和用户可见限制提取已实现能力、拒绝、追问、降级和责任
边界。递归核对稳定 `anchor_id` 与 Markdown 引用。主动寻找多份文档彼此一致、但代码和测试
不存在的共同虚构能力；文档共识不是实现证据。Business guide 只能教学性解释 contract 与
`interact.md` 已确认的内容。

### Testing

盘点真实 runner、命令、fixture、层级、外部依赖、副作用和必要顺序。测试环境由真实命令、
副作用、CI 能力和项目政策决定，可以是 CI、container、独立 checkout、远端环境或其他已
验证环境；记录 exact command、scope、result、not-run reason、环境、隔离和清理结果。

目标 `TESTING.md` 要求多个解释器时，分别运行并记录每个解释器的命令和结果；不能运行时分别
记录 not-run reason。一个解释器的结果不能替代另一个解释器。

验证层级不得膨胀。Unit、contract、scenario、golden、report build、repair validation、light
review、full validation 和 live test 只能按实际覆盖范围表述；未运行不得报告为通过。

### Governance

在前三维事实稳定后核对 `AGENTS.md`、`PR_Checklist.md`、`SOP.md` 与 PR template。命令、路径、
默认分支、发布和部署声明必须有当前证据。跨项目模板不得混入仅属于 Workflow Docs Sync 的
内部执行语境、pin、reviewer 拓扑或隔离实现。PR body 只能位于目标仓库外。

## Fresh-context review

优先使用 `independent` reviewer：提供 fresh context、完整仓库只读访问和同一 `target_head`。
Reviewer 在 blind-first 初始阶段不得读取主 Agent 的任何中间产物；必须先从代码、配置、
测试和 committed artifacts 独立重建高风险事实并形成 findings。初始 findings 形成后，才可
读取最终候选文档和原始 Git diff，检查遗漏、最小改写与跨文档影响。

Reviewer 不编辑、stage、commit、push，也不把复核过程写入目标仓库。无法提供认知隔离时，
执行完整 self-review，并在最终报告原样写：

```text
Review mode: self-review; independent review was not available
```

不得把 self-review 称为 independent。用户明确要求 independent review 而平台无法提供时，
停止在发布前。

review mode 为 `independent` 时，最终报告必须记录 reviewer 会话或线程标识、启动时间和认知
隔离边界；缺少这些证据时，不得仅凭主 Agent 声明认定 independent。

Reviewer 使用同一受控 severity。每个 finding 包含唯一 ID、severity、证据、风险和预期修复
边界：

- `BLOCKER`：当前候选会产生错误、虚构、越权、不可复现交付或关键风险遗漏，必须修复后才能
  收口。
- `WARN`：存在实质性质量或维护风险；除非需要新的产品决策，否则必须修复。
- `NOTE`：不改变可交付性的观察或后续建议，不作为 gate。

主 Agent 修复全部 BLOCKER 和无需新产品决策的 actionable WARN，请 reviewer 复核 finding
对应修改及直接跨文档影响，并重跑受影响测试。不得用新增状态文件、额外 Agent、词表或代理
指标代替本应覆盖该风险的场景、review 或真实 eval。

## 最终检查与报告

运行固定 SHA 的最终检查：

```bash
python3 <skill-root>/scripts/sync_docs.py check \
  --target-repo <target> \
  --upstream-dir <upstream> \
  --upstream-sha <prepare 返回的 upstream_sha> \
  --expected-target-head <prepare 返回的 target_head> \
  --language <zh|en>
```

`check` 从 `upstream_dir` 的 object store 按 `upstream_sha` 与 language 重读并验证同一 source
contract，再验证目标 HEAD、dirty allowlist、editable path 无 index/worktree 分叉、九份普通
文件、UTF-8、非空、JSON object、active marker，以及存在时为 UTF-8 的 `.gitignore`。唯一
final bytes 的 whitespace 检查在临时非 Git 目录以固定 Git 规则运行，不继承目标仓库
attributes、用户 global attributes 或 system attributes。它不解析 Markdown 标题或 fence，
不判断文案质量、capability 真实性、测试层级或业务指南可读性，也不证明调查、测试或 review
曾执行。

最终报告必须包含：

- `target_head`、`upstream_sha`、language 和真实 review mode；
- 修改文档及代码、配置、测试或 artifact 证据；
- 每条测试的 exact command、scope、result、not-run reason、环境与隔离方式；
- review finding、修复、复核结果和 open decisions；
- mechanical check 结果，并明确它只证明最终状态。

用户要求 draft PR 时，只有上述流程成功后才使用仓库外临时 Markdown body；commit、push 和
draft PR 创建交给通用 GitHub 发布能力，同步脚本不参与发布。
