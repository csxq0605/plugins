# Atlas — 代码库知识图谱 (Nexgent)

多 Agent 并行探索代码库，生成架构文档、数据流图、依赖分析，构建活的知识地图。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/atlas/nexgent-plugin
```

## 工具

| 工具 | 说明 |
|------|------|
| `atlas_explore` | 并行探索代码库，跨 5 个维度 |
| `atlas_map` | 生成结构化文档到 `.atlas/` |
| `atlas_query` | 基于知识库回答问题 |
| `atlas_diff` | 比较两个代码库结构差异 |

## 使用

```bash
# 探索当前目录
atlas_explore {"path": "."}

# 生成文档
atlas_map {"path": "."}

# 提问
atlas_query {"path": ".", "question": "这个项目怎么工作的？"}

# 比较两个项目
atlas_diff {"path1": "./old", "path2": "./new"}
```

## 输出

```
.atlas/
├── SUMMARY.md          # 摘要
├── index.md            # 主索引
├── raw/                # 原始数据
└── docs/               # 生成的文档
```

## 测试

```bash
cd atlas/nexgent-plugin
python -m pytest tests/ -v
```
