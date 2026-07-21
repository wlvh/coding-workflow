# 编程工作流操作入口

中文 | [English](../en/README.md)

本目录提供中文核心模板、开发工作流和单会话 `workflow-docs-sync` Skill。

## Quick Start

用户只调用一次 Skill，只提供目标仓库、可选语言和可选 draft PR 意图：

```text
使用 $workflow-docs-sync 同步 `/目标仓库绝对路径`，语言 zh，结束后不要创建 draft PR。
```

主 Agent 是目标工作区唯一写入者；四领域分析和内部对抗性审计都只读。上游 checkout
和 SHA 由 Skill 内部解析，最终检查只验证仓库状态，不证明执行历史。

## Skill 安装

Studio 可直接加载 canonical `zh/skills/workflow-docs-sync/`。个人或团队安装只复制这一个
Skill，不保存来源状态：

```bash
python3 zh/scripts/install_skills.py --upstream-dir <clean-canonical-checkout>
python3 zh/scripts/install_skills.py --scope repo \
  --target-repo <目标仓库> --upstream-dir <clean-canonical-checkout>
```

## 目录地图

- [AGENTS.md](AGENTS.md)：agent 工作入口、代码规范与文档关系。
- [architecture.md](architecture.md)：系统架构、模块边界、数据流和架构不变量模板。
- [capability_contract.json](capability_contract.json)：能力、边界和 agent 行为承诺契约。
- [interact.md](interact.md)：用户可观察行为与验收不变量模板。
- [TESTING.md](TESTING.md)：测试策略和证据规则模板。
- [PR_Checklist.md](PR_Checklist.md)：通用 PR 提交规则模板。
- [SOP.md](SOP.md)：标准流程入口模板。
- [.github/pull_request_template.md](.github/pull_request_template.md)：下游 PR body 模板。
- [docs/business_user_guide.md](docs/business_user_guide.md)：业务人员教学模板。
- [docs/development_workflow/README.md](docs/development_workflow/README.md)：完整开发工作流。
- [docs/development_workflow/decisions.md](docs/development_workflow/decisions.md)：产品实现决策。
- [skills/workflow-docs-sync/](skills/workflow-docs-sync/)：单会话同步 Skill。
- [skills/workflow-docs-sync/references/sections.md](skills/workflow-docs-sync/references/sections.md)：四领域只读分析语义。
- [skills/workflow-docs-sync/references/audit.md](skills/workflow-docs-sync/references/audit.md)：只读对抗性审计语义。
- [skills/workflow-docs-sync/scripts/sync_docs.py](skills/workflow-docs-sync/scripts/sync_docs.py)：内部 `prepare` / `check` 机械接口。
- [scripts/install_skills.py](scripts/install_skills.py)：单 Skill 双平台薄复制器。

## 路径与维护边界

`zh/` 是上游源码前缀，不写入目标项目。安装模板时只剥离开头的 `zh/`；例如
`zh/docs/business_user_guide.md` 落到 `<target>/docs/business_user_guide.md`，
`zh/.github/pull_request_template.md` 落到 `<target>/.github/pull_request_template.md`。

中文是锚点，英文是派生层。修改中文模板、Skill 或开发流程后，必须同步检查英文路径；
暂未覆盖时明确标记 `en-pending`。根目录 `.github/` 是本仓库基础设施，不是下游模板源。
