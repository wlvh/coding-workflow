# 编程工作流

## 主流程

1. **确定需求**
   输入：需求、`AGENTS.md`、其他仓库权威文档。
   输出：足够明确的需求边界，供后续制定 FSD。

2. **网页端 Pro 模型制定 `FSD Core Contract`**
   使用长 prompt：[prompts/fsd_core_contract.md](prompts/fsd_core_contract.md)
   备注：当前默认前提是 GPT 5.4 Pro 不能自由探索本地代码和 GitHub，所以 FSD 先做黑盒契约。

3. **Target State Bridge Agent 根据 `FSD + 当前仓库代码 + 仓库权威文档` 产出 `Repo Impact Forecast` 和 `Target State Bridge`**
   使用长 prompt：[prompts/target_state_bridge.md](prompts/target_state_bridge.md)
   强制要求：`Repo Impact Forecast` 必须区分 `Must / Likely / Maybe`，绝不把预测写成承诺。
   强制要求：`Target State Bridge` 必须输出 `interact.md Delta`，如果不是 `No change`，必须给出 draft 文案。
   强制要求：必须输出 `Verification Matrix`，格式为 `TS / AC -> 测试目录 -> Stage`。
   拆分规则：如果预估修改量超过 3000 行，拆成主 issue 和 sub issue。sub issue 必须独立验收、独立回滚、独立 code review。

4. **Issue Agent 写 issue**
   使用长 prompt：[prompts/issue_agent.md](prompts/issue_agent.md)
   目标：把 `FSD`、`Repo Impact Forecast` 和 `Target State Bridge` 固化成开发契约。

5. **Coding Agent 按 issue 开发**
   短 prompt：

   ```text
   按照 issue 完成本次编程开发。
   ```

   备注：这里不再重复注入 `FSD`、`Repo Impact Forecast`、`Target State Bridge`，因为它们已经被 issue 吸收。

6. **GPT 5.4 Pro 负责代码审核**
   预审核短 prompt：

   ```text
   你即将进行代码审核。从 FSD / PR_Body 的内容和 AGENTS.md 中的项目文件简介分析如果还需要哪些文件（开发完成后的版本）才能完成代码审核，现在告诉我，最多十个文件。
   ```

   正式审核系统 prompt：[prompts/pr_review_system.md](prompts/pr_review_system.md)
   正式审核任务短 prompt：

   ```text
   对 XX 项目的 PR XX（head XX）进行严格详细全面的代码审查。PR_BODY.md 是你重要的参考材料。并额外检查：
   * 是否满足 FSD Core Contract
   * 是否达到 Target State Bridge
   * 是否遵守 TESTING.md / AGENTS.md / PR_Checklist.md
   ```

   既有 PR 提交短 prompt：

   ```text
   在既有分支的既有 PR 上提交本地全部代码，记得保持 PR 的 commits 为 1 个，PR_BODY.md 需要覆盖已有 PR 和本地全部修改内容。备注：PR_BODY.md 也是重要的代码审核材料之一。
   ```

   新 PR 提交短 prompt：

   ```text
   遵守 PR_Checklist.md 进行 PR 提交，PR_BODY.md 需要覆盖本地全部修改内容。备注：PR_BODY.md 也是重要的代码审核材料之一。
   ```

7. **如果 review 有问题，先验证问题是否真实存在，再决定是否修**
   给 Codex GPT 5.4 thinking 和 Opus 的短 prompt：

   ```text
   先不动代码，先检查实习生给出的问题是否存在，如存在请列出证据并分析是否值得增加复杂度来修复，并评估实习生的建议是否最优。如果不是，给出你的方案。
   ```

   执行顺序：先让 Codex 和 Opus 分别判断，再把 Opus 的意见发给 Codex 要求出综合分析版本。
   处理分歧：如果双方分歧仍然很大，再把 GPT 5.4 对 Opus 的反驳发给 Opus，让 Opus 重新分析后按自己的方案执行。
   修复后：继续复用“既有 PR 提交短 prompt”覆盖 PR_BODY 并保持 commit 为 1 个。
   备注：同一个 PR 的 patch 不需要每次重新完整粘贴给 GPT，可以在原对话里覆盖最新 patch，避免上下文过时。

8. **如果 review 没有问题，在 PR 评论区输入 `/claude-merge-check`**
   自动化文件：[.github/workflows/claude-merge-readiness.yml](.github/workflows/claude-merge-readiness.yml)
   作用：做 merge-readiness 检查，而不是重复做 code review。
   通过规则：无问题则在 PR 评论区输入 `/claude-merge-check`，通过后再合入主干。

9. **PR 合并后，用网页端 GPT 的 apps 功能做 tech lead 总结**
   总结短 prompt：

   ```text
   当前 PR XX 已经完成。站在 tech lead 的视角详细地综合评估当前代码分支这个 PR 以什么方式完成了什么任务，给这个项目带来了什么改变和影响，下一步的未来展望是什么？这个 PR 开发完成后，用户有什么可感知的改变吗？
   ```

   追问短 prompt：

   ```text
   根据你的观察，AGENTS.md 及其内联的文档有没有需要更新的地方？
   ```

10. **Issue 关闭前，再从主干代码检查 FSD 是否真正开发完成**
    使用长 prompt：[prompts/issue_closure_fsd_acceptance.md](prompts/issue_closure_fsd_acceptance.md)
    目的：从主干代码倒查 issue 中的每个 `Spec Unit` 是否已实现，并强制输出 `Updates to FSD`（如有偏差）。

11. **再问 GPT 5.4 thinking：如何从用户视角验收这次 PR**
    短 prompt：

    ```text
    如何以用户的角度来验收这次的 PR？
    ```

    下一步：把这份用户视角验收建议交给 Codex，必要时结合 Playwright 等交互工具，真的走一遍验收。
    备注：这一步有可能直接产生新的开发计划。

## 核心产物

- `FSD Core Contract`：把需求翻译成可实现、可测试、可审核的契约。
- `Repo Impact Forecast`：预测 FSD 与当前仓库的真实触点、风险、文档和测试影响。
- `Target State Bridge`：定义开发完成后用户 / 调用方应该看到什么状态，以及如何验证。
- `Issue`：把契约、范围、任务拆解、文档更新预测、测试更新预测、验收条件固化。
- `PR_BODY.md`：覆盖当前 PR 和本地全部修改内容，是 review 的重要输入材料。
- `Merge Readiness Report`：判断当前 PR 是否具备合并条件。
- `FSD 完备性验收报告`：Issue 关闭前的最后一道契约核查。


