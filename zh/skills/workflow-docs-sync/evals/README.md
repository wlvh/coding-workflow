# 影子验证协议

三个完整 Case 在 skill 合并后、正式推广前由用户执行。合并前必须先通过本地完整 mode
顺序集成测试和一次真实 Codex Skill smoke run；不能再把主流程首次执行推迟到合并以后。
本协议把既有“手工四个新对话”流程与 mode 化 skill 放在相同输入上对照，确认自动化没有
降低语义质量或扩大写入范围。

## 合并前 Gate

- `tests/test_workflow_sync_skill.py` 必须执行 PREPARE、PASS_1–4、prepare-submit、缺
  `PR Test Evidence` 的 seal 失败、同一 runtime 补证据重试、seal 成功、commit、
  fake GitHub PR 和 finish-submit 的完整机械序列。
- 上述集成测试必须使用真实 skeleton、普通 sync 和真实 final gate；只允许 GitHub
  查询使用 fake，不能替换 `sync.sh`。
- 必须在临时仓库显式调用一次 Codex `$workflow-docs-sync`，保存命令和结果摘要。
- dirty upstream、mode 间越权、per-mode scope、seal 失败重试、无 remote 分支的整轮
  restart、seal 后内容 / executable bit 篡改、非单 commit、漏提交 / 额外提交、远端
  stale body、review verdict、reviewer 绝对 Skill 路径、完整 clean target、PR body
  upstream SHA、执行与 reviewer 安装来源 SHA 及跨平台 invocation metadata 必须有
  回归测试。

## 验证准备

- 每个 Case 准备两个来自同一基线 commit 的独立工作副本。
- 轨道一按 `zh/scripts/OPERATIONS.md` 手工复制 PASS 1–4，并执行既有提交与审查流程。
- 轨道二依次在独立新会话调用 `PREPARE`、`PASS_1`、`PASS_2`、`PASS_3`、
  `PASS_4`、`SUBMIT`，再调用独立审查 skill。
- 两条轨道使用同一个 pinned upstream SHA，不共享对话上下文或未记录的人工判断。

## Case A：缺核心文档的既有代码仓库

选择已有可运行代码、但缺少一个或多个核心 workflow 文档的仓库。验证两条轨道能否用
代码证据补齐缺失文档，同时避免把模板占位、无证据能力或无关治理文件写入结果。

Shadow Case A 的 Skill 轨道还必须证明：PREPARE 后根 `PR_BODY.md` 已作为正式交接
产物存在；每个 PASS 的成功结果同时对应正式 body 中当前 PASS 的 sentinel、heading、
表格宽度、非空责任 cell 和 owned 文档 readiness。删除 `待补充` 但留下空 block / cell
必须失败；表格字面 `|` 必须转义为 `\|` 或改用 `<br>`。这些机械条件不裁定证据真实性，
独立 reviewer 仍负责语义 verdict。仅有 skeleton 不算正式交接或 PASS success。

## Case B：存在 class-2 上游漂移

选择核心文档已项目化、但未吸收当前 upstream 语义更新的仓库。验证两条轨道是否都能
识别 upstream semantic delta，明确采纳位置或不采纳原因，并保持 PASS ownership 闭合。

## Case C：存在 class-3 代码漂移

选择代码、测试或用户可见行为已经变化，但对应架构、能力、测试或治理文档尚未同步的
仓库。验证两条轨道能否从代码证据发现漂移，并由后续 PASS 消费 downstream impact。

## 双轨对比维度

每个 Case 都记录以下同口径证据：

1. final gate 是否通过及全部违规项。
2. 独立 reviewer 的 verdict 与新增 BLOCKER。
3. changed files 的完整集合与两轨差异。
4. pass ownership 之外的越权改动数量。
5. 核心文档中的模板残留数量。
6. `Remaining Human Decisions` 与 `待判断` 的具体条目。
7. 需要人工跨会话搬运信息的次数。
8. agent 结果需要人工纠正的次数与原因。
9. 每个 mode 结果 JSON 是否稳定写入、通过 schema 校验并与会话末条消息一致。

## Go 条件

只有同时满足以下条件，skill 才可进入正式推广：

- 三个 Case 的两条轨道 final gate 全部通过。
- skill 轨道的独立 reviewer 相比手工轨道没有新增 BLOCKER。
- 三个 Case 均为零越权改动。
- skill 轨道在 changed files、模板残留、待判断暴露和语义闭合上不劣于手工轨道。
- 所有 mode 与 review 结果 JSON 均稳定产出、可重复校验，失败结果也如实记录原因。
