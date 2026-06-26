# Superpowers Workflow — lit-review 集成

当用户要求使用 superpowers 工作流时，lit-review 在以下阶段被调用：

## Step 1: Brainstorming 阶段

在讨论需求时，使用 lit-review 搜索相关论文和技术方案，为设计决策提供学术依据。

### 调用方式

```
# 搜索相关论文
lit_search_web(query="attention mechanism transformer", sources=["arxiv", "semantic_scholar"])

# 创建研究工作区
lit_create_workspace(topic="Feature X Design")

# 添加论文到工作区
lit_add_paper(workspace_id=..., title=..., authors=..., ...)

# 综合分析
lit_synthesize(workspace_id=...)
```

### 与 team-coord 集成

Lead 可 spawn 多个 worker 并行搜索不同子主题：
- Worker A → 搜索算法相关论文
- Worker B → 搜索系统设计相关论文
- Worker C → 搜索性能优化相关论文

Lead 合并所有 worker 的搜索结果，生成综合调研报告。

### 输出格式

调研结果可用于：
- vision.md 中的技术背景
- specs 中的参考文献
- ADR 中的决策依据
