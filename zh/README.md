# 编程工作流操作入口

中文 | [English](../en/README.md)

本目录是中文模板、文档、prompt 和操作手册的入口。选择中文后，除共享实现
`../scripts/sync_coding_workflow.py`、兼容入口 `../scripts/sync.sh`、测试和本仓库
GitHub workflow 外，后续路径都应留在 `zh/` 目录树内。

## Quick Start

在目标项目仓库根目录运行中文 workflow docs sync：

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/zh/scripts/sync.sh | bash
```

兼容旧入口仍可用：

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
```

普通 sync 完成后，按 [zh/scripts/OPERATIONS.md](scripts/OPERATIONS.md) 的 PASS 1 到
PASS 4 执行；PR 提交 agent 先补测试证据，经 seal 的 final gate 封存后再发布 PR。

Skill 使用分三类：Studio 从 clean pinned upstream 直接加载 canonical source；
个人安装默认写用户级目录；团队仓库安装必须显式使用 `--scope repo` 并先提交独立
安装 PR。安装副本用简单 `.source.json` 记录 upstream SHA，切换 SHA 前重新安装；
mode 边界由单一 `harness.py` 检查。双平台调用和完整命令见
[modes.md](skills/workflow-docs-sync/references/modes.md)。

## 目录地图

- [zh/AGENTS.md](AGENTS.md)：agent 工作入口、文件简介、代码规范与文档关系。
- [zh/architecture.md](architecture.md)：系统架构、模块边界、数据流和架构不变量。
- [zh/capability_contract.json](capability_contract.json)：能力、边界和 agent 行为承诺的机器可读契约。
- [zh/interact.md](interact.md)：用户可观察行为与验收不变量。
- [zh/TESTING.md](TESTING.md)：测试策略、测试证据和 contract alignment 测试原则。
- [zh/PR_Checklist.md](PR_Checklist.md)：PR 提交、commit、push 和 PR body 使用规则。
- [zh/SOP.md](SOP.md)：标准流程入口。
- [zh/.github/pull_request_template.md](.github/pull_request_template.md)：下游项目继承的中文 PR body 模板。
- [zh/docs/business_user_guide.md](docs/business_user_guide.md)：面向首次接触业务人员的教学文档。
- [zh/docs/development_workflow/README.md](docs/development_workflow/README.md)：完整开发工作流。
- [zh/prompts/](prompts/)：FSD、issue、review 和验收相关长 prompt。
- [zh/scripts/OPERATIONS.md](scripts/OPERATIONS.md)：workflow docs sync 操作手册和 pass prompt 真相源。
- [zh/scripts/sync.sh](scripts/sync.sh)：中文模板 sync 启动入口。
- [zh/scripts/sync_pr_review_system.md](scripts/sync_pr_review_system.md)：中文独立 reviewer 启动 prompt。
- [zh/scripts/install_skills.py](scripts/install_skills.py)：按 user/repo scope 覆盖复制双平台 Skill，并写简单来源记录。
- [zh/docs/development_workflow/decisions.md](docs/development_workflow/decisions.md)：记录 Skill 威胁模型和 AI / 机械事实边界。
- [zh/skills/workflow-docs-sync/](skills/workflow-docs-sync/)：按独立会话执行语义 PASS，由薄 harness 负责边界检查、pinned sync、SUBMIT seal 和 PR 核验。
- [zh/skills/workflow-docs-sync-review/](skills/workflow-docs-sync-review/)：不修改 tracked 项目文件、只写 ignored result 的独立审查 Skill。

## 路径落盘规则

`zh/` 是上游源码前缀，不写入目标项目。sync 安装模板时只剥离开头的 `zh/`，
剥完后按原路径落盘：

- `zh/AGENTS.md` -> `<target>/AGENTS.md`
- `zh/docs/business_user_guide.md` -> `<target>/docs/business_user_guide.md`
- `zh/.github/pull_request_template.md` -> `<target>/.github/pull_request_template.md`

`.github` 的内层结构保持不变；只剥语言前缀，不做其他路径重写。

## 维护边界

中文是锚点，英文是派生层。修改中文模板、prompt、runbook 或开发流程后，应同步检查
英文目录是否需要更新；如果英文暂不覆盖，必须在 PR body 标记 `en-pending`。

根目录 `.github/` 只代表本仓库自己的 GitHub infra，不是下游模板源。下游 PR
模板源在 `zh/.github/` 与 `en/.github/`。
