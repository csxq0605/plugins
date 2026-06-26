# Migrator — 框架/库迁移助手

分析代码库 → 识别所有触点 → 生成迁移计划 → 逐步执行 → 每步验证。处理 breaking changes 和废弃 API。

## 安装

```bash
claude install-plugin github:csxq0605/plugins
```

## 命令

| 命令 | 说明 |
|------|------|
| `/migrator analyze <src> → <target>` | 分析迁移目标 |
| `/migrator plan` | 生成迁移计划 |
| `/migrator execute [step]` | 执行迁移步骤 |
| `/migrator verify [step]` | 验证迁移步骤 |
| `/migrator status` | 查看迁移进度 |
| `/migrator rollback [step]` | 回滚迁移步骤 |

## 输出

```
.migrations/
├── react-17-to-18/
│   ├── analysis.json     # 分析结果
│   ├── plan.json         # 迁移计划
│   ├── progress.json     # 进度追踪
│   └── steps/            # 步骤详情
└── index.json            # 迁移索引
```

## 使用场景

- 依赖升级（如 React 17→18）
- 框架迁移（如 Express 4→5）
- 处理废弃 API
- 语言版本升级（如 Python 3.9→3.12）
