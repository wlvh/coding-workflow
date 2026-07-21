# 真实仓库前向验证

在合并前从 clean disposable worktree 调用一次 `$workflow-docs-sync`，用户只提供目标仓库
和语言，不创建 draft PR。验证主 Agent 是唯一写入者、分析与审计只读、没有仓库内运行
状态或 PR body，并保存最终报告中的路径证据、测试命令、审计处置和固定上游 SHA。

## Case A：SEC_metrics

- 从当前真实代码重建 pipeline 语义，不依赖历史 shadow 文件。
- 专门核对 stage 10、11、12 的输入、写入副作用、容错参数和 hard failure 位置。
- 区分 unit tests、golden、report build、repair validation、light review 与 full validation。
- 没有当前部署配置和运行证据时，不得把项目描述为已完成生产调度。
- 文档同步 worktree 只运行低污染检查；会改写 pipeline artifact 的重型命令放到另一个
  锁定同一提交的 disposable clone。

完成条件：九份核心文档通过最终检查；测试与重型验证结果被准确记录；对抗审计没有未
处理 BLOCKER，所有可行动 WARN 已修复；需要新产品决策的问题记入未解决决策。
