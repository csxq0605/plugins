# Incident Response — 生产事故响应

结构化事故处理：分诊 → 定位 → 修复 → 验证 → 复盘。时间线追踪、根因分析、事后报告自动生成。

## 安装

```bash
claude install-plugin github:csxq0605/plugins
```

## 命令

| 命令 | 说明 |
|------|------|
| `/ir start <desc>` | 创建事故记录，开始分诊 |
| `/ir triage [id]` | 严重性分级 (P0-P4) |
| `/ir timeline <event>` | 添加时间线事件 |
| `/ir diagnose [id]` | 根因分析 |
| `/ir fix <action>` | 记录修复动作 |
| `/ir verify <check>` | 验证修复效果 |
| `/ir close [id]` | 关闭事故 |
| `/ir postmortem [id]` | 生成复盘报告 |
| `/ir list` | 列出所有事故 |

## 输出

```
.incidents/
├── INC-001/
│   ├── incident.json     # 事故元数据
│   ├── timeline.json     # 时间线
│   ├── diagnosis.md      # 根因分析
│   ├── fixes.md          # 修复记录
│   └── postmortem.md     # 复盘报告
└── index.json            # 事故索引
```

## 使用场景

- 生产环境故障
- 用户报告错误
- 监控告警触发
- 事后复盘
