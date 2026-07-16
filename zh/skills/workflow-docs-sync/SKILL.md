---
name: workflow-docs-sync
description: 当需要把工作流文档同步（workflow docs sync）的 PASS 流程项目化为独立会话、分 mode 执行时使用。
---

## 调用协议

- 只接受 `PREPARE`、`PASS_1`、`PASS_2`、`PASS_3`、`PASS_4`、`SUBMIT` 六种 mode。
- 每个 mode 必须在独立新会话中调用；本 skill 不创建隔离上下文，也不声称替调用方完成跨平台上下文隔离。
- 每次调用必须显式提供目标仓库、clean pinned upstream 路径、完整 SHA 和 mode；命令见 `references/modes.md`。
- Studio 直接加载 canonical Skill；已安装副本通过 `.source.json` 记录来源 SHA，切换 SHA 后必须重新安装。
- mode 顺序、边界快照和 SUBMIT 起点保存在 ignored `.coding_workflow/skill_runtime/`；确定性结果保存在 ignored `.coding_workflow/skill_results/`。
- AI 负责 PASS 语义判断和文档改写；调用方按 `references/modes.md` 解析当前 Skill
  根目录的绝对路径，再运行其中 `scripts/harness.py` 的机械命令。

## 通用执行规则

1. 只通过文件和 JSON 传递状态，不依赖前一会话聊天摘要。
2. PASS 语义真相源始终是 pinned upstream 的 `zh/scripts/OPERATIONS.md`；Skill 不复制或扩写 PASS prompt。
3. `start-pass` 返回当前标题、owned 文件、允许的 PR body section 和 prompt 行号；只执行 code block 中标记为“Skill 模式”的语义部分。
4. 不运行 code block 的人工 curl；pinned 普通 sync 由调用方在 `finish-pass` 中执行。
5. 不修改 sync auto 区、其他 PASS 文件或未授权 PR body section。
6. harness 非零退出时立即停止，不跨 mode 补做或静默降级。

## 各 mode 语义

### PREPARE

调用方运行 `harness.py prepare`。它校验仓库和 pinned upstream、运行普通 sync、
初始化 run state 并写 PREPARE result。AI 不做项目语义改写。

### PASS_1 至 PASS_4

1. 调用方先运行 `harness.py start-pass --mode <PASS>`。
2. 按返回的 pinned prompt 位置执行 Skill 模式语义部分。
3. 只修改返回的 owned 文件和 PR body sections。
4. 调用方运行 `harness.py finish-pass --mode <PASS>`；它检查本 mode delta、运行 pinned sync、写结果并推进顺序。

### SUBMIT

1. 调用方运行 `harness.py prepare-submit`，建立 active、unsealed 基线；此时
   `submit_ready=false`，且尚未执行 final gate。
2. AI 按 OPERATIONS.md 的 evidence 阶段运行测试，只填写 `PR Test Evidence`，不得
   commit、push 或更新远端 PR。
3. 调用方运行 `harness.py seal-submit`。它要求 HEAD 未变化、基线后只有提交阶段
   owned section 被编辑，再运行真实 pinned final gate；成功后封存 workflow 内容、
   本地 PR body 和精确提交路径，并设置 `submit_ready=true`。
4. AI 进入 seal 后发布阶段，按封存路径 commit、push 并更新远端 body。调用方最后
   运行 `harness.py finish-submit`，把 sealed 内容绑定实际 commit 和远端 PR。

`seal-submit` 失败不会退出 active SUBMIT，也不会要求删除 runtime。若只是提交证据
不完整，修正 `PR Test Evidence` 后原地重试。若错误暴露 PASS-owned 文档问题，保留
当前失败 runtime 作为证据，从失败仓库本地 clone 同一 `start_head`，在独立 checkout
恢复原 head 分支和真实发布 remote，再从 PREPARE 到 PASS_4 完整重跑；不得把当前
内容设成新 baseline，也不需要中间 commit。

## 停止条件

- mode 顺序错误、mode 间出现新编辑或项目 HEAD 提前变化。
- 当前 PASS 修改非 owned 路径或未授权 PR body section。
- upstream 缺失、dirty 或 SHA 不匹配。
- pinned sync 失败，或 seal 的 final gate 尚未通过。
- seal 后 workflow 内容 / executable bit / PR body 变化，新增 commit 数不是 1，或实际
  提交路径不精确等于 sealed allowed set。
- 远端 PR number、base、head 或 body 与本地事实不一致。
