---
name: lit-review
description: "Systematic literature review for Nexgent — multi-source academic search, paper management, analysis tracking, and synthesis."
user-invocable: true
---

# lit-review (Nexgent)

你是学术研究助手，使用 lit-review 工具进行系统性文献调研。

## 工具列表

| 工具 | 用途 |
|------|------|
| `lit_create_workspace` | 创建研究工作区 |
| `lit_add_paper` | 添加论文到工作区 |
| `lit_get_paper` | 获取论文详情 |
| `lit_list_papers` | 列出工作区论文 |
| `lit_search_local` | 本地论文搜索 |
| `lit_add_analysis` | 添加论文分析结果 |
| `lit_synthesize` | 获取综合数据（分布、趋势、高引） |
| `lit_list_workspaces` | 列出所有工作区 |

## 工作流

### 1. 创建工作区

```
lit_create_workspace(topic="Transformer Attention Mechanisms")
```

### 2. 搜索并添加论文

使用 WebSearch 搜索论文，然后添加到工作区：

```
lit_add_paper(
    workspace_id="ws-0001",
    title="Attention Is All You Need",
    authors=["Vaswani", "Shazeer", "Parmar"],
    year=2017,
    abstract="The dominant sequence transduction models...",
    url="https://arxiv.org/abs/1706.03762",
    source="arxiv",
    citations=120000
)
```

### 3. 分析论文

对每篇论文执行深度分析，记录结果：

```
lit_add_analysis(
    workspace_id="ws-0001",
    paper_id="abc123",
    type="methodology",
    content="Proposes self-attention mechanism that replaces RNNs..."
)
```

### 4. 查看综合数据

```
lit_synthesize(workspace_id="ws-0001")
```

返回：
- 论文数量和总引用数
- 按年份/来源的分布
- 最高引用论文
- 最新论文

### 5. 搜索本地论文

```
lit_search_local(workspace_id="ws-0001", query="attention mechanism")
```

## 搜索来源

- **arXiv**: 预印本，CS/Physics/Math/Stats
- **Semantic Scholar**: 引用网络、推荐系统
- **Google Scholar**: 最广泛的学术搜索

## 最佳实践

1. **先创建再搜索**：每个研究主题一个工作区
2. **及时记录分析**：搜索后立即分析，不要积压
3. **使用综合数据**：定期查看 lit_synthesize 了解覆盖情况
4. **本地搜索**：论文多了以后用 lit_search_local 快速定位
