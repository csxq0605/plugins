# team-coord (Nexgent Plugin)

Nexgent 插件，提供多 agent 团队协调能力——作为 subagent 和 workflow 的**补充层**。

- 13 个 team 协调工具
- Lead 纯协调，Worker 做实际工作
- 文件 inbox 实现 + 共享任务列表

## 安装

```bash
# 在 Nexgent 交互界面中执行：
/plugin install https://github.com/csxq0605/plugins/tree/master/multi-agent/nexgent-plugin
```

## 工具列表

| 工具 | 权限 | 用途 |
|------|------|------|
| `team_create` | Lead | 创建团队 |
| `team_spawn` | Lead | 生成 worker |
| `team_close` | Lead | 关闭团队（归档+清理） |
| `team_shutdown` | Lead | 请求关闭 worker |
| `team_tool_search` | Anyone | 加载工具 schema |
| `team_send_message` | Anyone | 发送消息 |
| `team_check_inbox` | Anyone | 检查收件箱 |
| `team_add_task` | Anyone | 添加任务 |
| `team_list_tasks` | Anyone | 列出任务 |
| `team_claim_task` | Anyone | 认领任务 |
| `team_complete_task` | Anyone | 完成任务 |
| `team_report_status` | Anyone | 向 lead 汇报 |
| `team_request_subordinate` | Anyone | 请求增派人手 |

## 测试

```bash
# 单元测试（38 个）
python -m pytest tests/ -v

# E2E 测试
cd D:/tasks/project/Nexgent/nexgent
python D:/tasks/project/multi-agent/multi-agent/nexgent-plugin/tests/test_real_auto_team.py
```
