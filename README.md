# team-coord — 多智能体协调插件

为 Claude Code 和 Nexgent 实现的 agent team 协调能力——**作为 subagent 和 workflow 的补充层**。

## 核心定位

| 任务复杂度 | 方案 |
|---|---|
| 简单 | 直接执行 |
| 中等 | subagent fan-out |
| 复杂 | **team-coord** — lead 协调多个 worker 并行执行 |

## 核心设计

### 角色分离

- **Lead（纯协调者）**：分析任务 → spawn worker → 等待汇报 → 综合输出 → 关闭团队。**不做实际工作。**
- **Worker（实际执行者）**：执行任务 → 向 lead 汇报。可用所有工具（web_search、subagent 等）。

### Inbox Sync 协议

解决多 agent 间的消息竞态条件（rendezvous failure）：
- 完成一步后检查 inbox（触发点 1）
- 发送消息前检查 inbox（触发点 2）
- "Read to check, not to act"——先收集再处理

### WHAT vs HOW 原则

Lead 只传 WHAT（identity、task、scope、success criteria），不传 HOW（执行细节）。防止 workers 跳过自己的 skill 流程。

## 目录结构

```
multi-agent/
├── claude-code-plugin/            # Claude Code 插件（纯 SKILL.md 指令）
│   ├── .claude-plugin/plugin.json
│   ├── skills/
│   │   ├── lead/SKILL.md          # Lead 协调协议
│   │   └── teammate/SKILL.md      # Worker 执行协议
│   └── README.md
├── nexgent-plugin/                # Nexgent 插件（Python 工具 + SKILL.md）
│   ├── plugin.json
│   ├── team_tools.py              # 13 个 team 工具定义
│   ├── team_manager.py            # Team 生命周期管理
│   ├── team_core.py               # 数据结构
│   ├── inbox.py                   # 文件 inbox 实现
│   ├── skills/                    # SKILL.md 指令
│   └── tests/                     # 38 个单元测试 + E2E
└── README.md
```

## 测试

```bash
# 单元测试
cd nexgent-plugin && python -m pytest tests/ -v

# E2E 测试（需要 API key）
cd D:/tasks/project/Nexgent/nexgent
python D:/tasks/project/multi-agent/nexgent-plugin/tests/test_real_auto_team.py
```

## License

MIT
