# multi-agent (Claude Code Plugin)

一个 Claude Code plugin，提供多 agent 团队协调能力——作为 subagent 和 workflow 的**补充层**。

- **`multi-agent:lead`** — 纯协调者：spawn worker、分配任务、收集结果、shutdown 审批。**不做实际工作。**
- **`multi-agent:teammate`** — 实际执行者：执行任务、向 lead 汇报。可用所有工具（web_search、subagent 等）。

外加可选 reference docs 用于叠加 `superpowers` 软件开发工作流。

## 安装

```bash
claude install-plugin github:csxq0605/plugins
```

## 插件定位：补充层

| 任务复杂度 | 方案 |
|---|---|
| 简单 | 直接执行 |
| 中等 | subagent fan-out |
| 复杂 | **team-coord** — lead 协调多个 worker 并行执行 |

## Subskills

| Subskill | 角色 | 涵盖 |
|---|---|---|
| `multi-agent:lead` | 纯协调者 | spawn、任务分配、shutdown 审批、结果综合 |
| `multi-agent:teammate` | 实际执行者 | inbox sync、dispatch limits、完成报告 |

## 核心设计

- **Lead 绝不做实际工作** — 只做 5 件事：分析 → spawn → 等待 → 综合 → 关闭
- **WHAT vs HOW** — lead 只传任务定义，不重述执行细节
- **Inbox sync** — 两个触发点检查 inbox，避免 rendezvous failure
- **Hub-and-spoke** — 只有 lead 能 spawn/delete，teammate 通过 inbox 通信
- **Shutdown 需用户批准** — 硬规则，防止丢失 in-flight 工作

## License

MIT
