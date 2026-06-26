# Atlas — 代码库知识图谱

多 Agent 并行探索代码库，生成架构文档、数据流图、依赖分析，构建活的知识地图。

## 安装

```bash
claude install-plugin github:csxq0605/plugins
```

## 命令

| 命令 | 说明 |
|------|------|
| `/atlas explore [path]` | 并行探索代码库，生成原始发现 |
| `/atlas map [path]` | 从探索结果生成结构化文档 |
| `/atlas query <question>` | 基于知识库回答代码库相关问题 |
| `/atlas diff [path1] [path2]` | 比较两个代码库的结构差异 |

## 输出

```
.atlas/
├── SUMMARY.md          # 摘要
├── index.md            # 主索引
├── raw/                # 原始探索结果
└── docs/               # 生成的文档
```

## 使用场景

- 新人入职 — 快速理解代码库
- 重构前分析 — 了解影响范围
- 架构评审 — 自动生成文档
- API 文档 — 自动提取 API 表面
