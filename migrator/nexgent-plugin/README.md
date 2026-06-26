# Migrator — 框架/库迁移助手 (Nexgent)

分析代码库 → 识别所有触点 → 生成迁移计划 → 逐步执行 → 每步验证。处理 breaking changes 和废弃 API。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/migrator/nexgent-plugin
```

## 工具

| 工具 | 说明 |
|------|------|
| `migrator_analyze` | 分析迁移目标 |
| `migrator_plan` | 生成迁移计划 |
| `migrator_execute` | 执行迁移步骤 |
| `migrator_verify` | 验证迁移步骤 |
| `migrator_status` | 查看迁移进度 |
| `migrator_rollback` | 回滚迁移步骤 |

## 使用

```bash
# 分析
migrator_analyze {"path": ".", "source": "react", "source_version": "17", "target_version": "18"}

# 生成计划
migrator_plan {"path": "."}

# 执行步骤
migrator_execute {"path": ".", "step_id": 1}

# 验证
migrator_verify {"path": ".", "step_id": 1}

# 查看进度
migrator_status {"path": "."}
```

## 测试

```bash
cd migrator/nexgent-plugin
python -m pytest tests/ -v
```
