# lit-review × team-coord 集成指南

当 lit-review 与 team-coord 共存时，lead 可以 spawn 多个 worker 并行搜索不同子话题/来源。

## 何时使用 team-coord 模式

- 深度调研（--deep 模式），需要覆盖多个子话题
- 多源搜索，每个来源需要独立处理
- 大规模综述（20+ 篇论文）

快速搜索（< 10 篇论文）用单 agent 即可。

## Lead 工作流

### Step 1: 子问题分解

将研究问题分解为 3-5 个子问题。

### Step 2: Spawn 搜索 Workers

每个子问题一个 worker：

```
你是 searcher-1，负责搜索子问题 "What are the different types of attention mechanisms?"。

你的第一个动作：Skill('team-coord:teammate')

任务：在 arXiv 和 Semantic Scholar 上搜索相关论文，返回论文列表（标题、作者、年份、摘要、URL）。
成功标准：找到 5-10 篇高质量论文
依赖：无

⚠️ 硬规则：
- 用 WebSearch 搜索
- 完成后用 SendMessage 把论文列表发给我
- 我负责综合所有 worker 的结果
```

### Step 3: 收集 + 去重

收集所有 worker 的论文列表，去重（标题相似度 > 80% 或相同 DOI）。

### Step 4: Spawn 分析 Workers

对去重后的论文，spawn 分析 worker：

```
你是 analyzer-1，负责分析以下论文：[论文列表]。

你的第一个动作：Skill('team-coord:teammate')

任务：对每篇论文执行深度分析，提取关键发现、方法论、局限性。
成功标准：每篇论文有完整的分析结果
依赖：搜索完成
```

### Step 5: 综合

收集所有分析结果，生成结构化综述。

## 与 Superpowers 对接

lit-review 可以作为 superpowers 工作流的 Step 1（Brainstorming）的一部分：

```
Lead: 用户想实现一个新的 NLP 模型
→ spawn lit-review worker 搜索相关论文
→ 基于搜索结果讨论技术方案
→ 进入 Step 2 (Writing Plans)
```
