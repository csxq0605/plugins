# Incident Response — 生产事故响应 (Nexgent)

结构化事故处理：分诊 → 定位 → 修复 → 验证 → 复盘。时间线追踪、根因分析、事后报告自动生成。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/incident-response/nexgent-plugin
```

## 工具

| 工具 | 说明 |
|------|------|
| `ir_start` | 创建事故记录 |
| `ir_triage` | 严重性分级 |
| `ir_timeline` | 添加时间线事件 |
| `ir_diagnose` | 根因分析 |
| `ir_fix` | 记录修复动作 |
| `ir_verify` | 验证修复效果 |
| `ir_close` | 关闭事故 |
| `ir_postmortem` | 生成复盘报告 |
| `ir_list` | 列出所有事故 |

## 使用

```bash
# 创建事故
ir_start {"title": "API 返回 500 错误", "severity": "P1"}

# 分诊
ir_triage {"severity": "P0", "affected_services": ["api-gateway"]}

# 记录时间线
ir_timeline {"event": "正在调查数据库连接"}

# 诊断
ir_diagnose {"root_cause": "连接池耗尽"}

# 修复
ir_fix {"action": "增加连接池大小到 100"}

# 验证
ir_verify {"check": "错误率恢复正常"}

# 关闭
ir_close {"resolution": "已修复"}

# 生成复盘报告
ir_postmortem {"lessons": ["需要更好的监控"]}
```

## 测试

```bash
cd incident-response/nexgent-plugin
python -m pytest tests/ -v
```
