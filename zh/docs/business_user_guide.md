# Project Use Guide

本指南帮助项目使用者和外部调用 Agent 理解：解决什么问题、需要什么输入、得到什么结果、
不做什么、正式接口在哪里，以及何时需要帮助。已有正式用户文档、接口规范和已接受政策
继续在各自覆盖范围内有效；本页负责使用说明和必要补充，不因文件名覆盖既有权威。

成熟项目可以将本页收缩为短桥接页：明确原正式文档在相应范围内仍是正文权威，提供导航和
必要补充，已被覆盖的问题直接引用对应章节，不重复改写整份指南。`capability_contract.json`
登记选定的承诺与边界，`interact.md` 展开交互语义；使用说明须与它们及既有正式文档的适用
内容一致，不把内部实现、偶然行为或规划写成公开承诺。

## 0. Documentation and Interface Entrypoints

<!-- project-fill: 指向已有正式用户文档及真实 API、CLI 或协议参考，注明各自覆盖范围和本页补充内容；区分经核实不适用的入口、适用但尚未配置的参考和证据不足而尚未确认的内容；完成后删除此 marker -->

## 1. Value

<!-- project-fill: 用三到五句话说明项目解决的问题、适合的使用者、所需输入和可观察输出，或引用已覆盖这些问题的正式文档；完成后删除此 marker -->

## 2. Typical Uses

<!-- project-fill: 用使用者能理解的语言说明适合的任务和用法，引用相应正式文档、接口参考或已登记的承诺；当前能力须有实现证据，不为满足本页强行登记 contract 条目；完成后删除此 marker -->

## 3. Capability and Responsibility Boundaries

<!-- project-fill: 说明项目不做什么、当前限制和调用方或人类的责任，引用既有公开承诺与有效政策依据，并区分实现观察；future / proposed 必须显式标注；完成后删除此 marker -->

## 4. Context to Provide

<!-- project-fill: 说明真实入口要求的输入、格式、权限和其他必要上下文，引用相应正式接口说明；完成后删除此 marker -->

## 5. Representative Real Cases

只保留一到三个有当前实现或测试证据的真实案例，也可引用正式文档中的已核实案例。没有
适用案例时删除本节并说明已检查范围；尚未核实则说明证据缺口，不写成 `Not configured`。
不要保留通用 Case 骨架。

<!-- project-fill: 写入一到三个真实案例，包括问题、推荐请求、可见结果、结果解读和升级条件；完成后删除此 marker -->

## 6. Reading Results

<!-- project-fill: 说明用户会得到什么、如何解读成功或失败结果，以及下一步可做什么；核对正式接口说明与 interact.md 中对应的可见行为；完成后删除此 marker -->

## 7. Human Escalation

<!-- project-fill: 按既有支持政策和已确认的交互语义，说明何时需要帮助、可联系的角色与真实路径；没有配置路径与尚未确认应分别说明，不编造责任人或流程；完成后删除此 marker -->

## 8. Feedback and Ownership

<!-- project-fill: 写入已确认的文档 owner、反馈入口和适用的紧急升级方式；确实未配置的适用项写 Not configured，证据不足的项写尚未确认并说明已检查范围；完成后删除此 marker -->
