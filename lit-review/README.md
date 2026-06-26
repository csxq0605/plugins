# lit-review — 科研文献调研流水线

多源学术搜索（arXiv API、Semantic Scholar API）、引用网络分析、子问题分解、结构化综述生成。

## 安装

### Claude Code

```bash
/plugin marketplace add csxq0605/plugins
/plugin install lit-review@plugins
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/lit-review/nexgent-plugin
```

## Semantic Scholar API Key 配置

**必须配置**，否则 Semantic Scholar 搜索会被限速（100 请求/5 分钟共享池）。

免费申请：https://www.semanticscholar.org/product/api

### Claude Code 版本

在对话中执行：

```
/lit-review:search --set-key your_api_key_here
```

或手动创建 `~/.lit-review/config.json`：

```json
{"semantic_scholar_api_key": "your_api_key_here"}
```

或设置环境变量：

```bash
export SEMANTIC_SCHOLAR_API_KEY=your_api_key_here
```

### Nexgent 版本

在对话中使用工具：

```
lit_set_key(key="your_api_key_here")
```

或手动创建 `~/.lit-review/config.json`（同上）。

或设置环境变量 `SEMANTIC_SCHOLAR_API_KEY`（同上）。

### 读取优先级

两个版本共用同一份配置，读取顺序：

1. 环境变量 `SEMANTIC_SCHOLAR_API_KEY`（最高优先级）
2. 配置文件 `~/.lit-review/config.json`

## 使用

### Claude Code

```bash
# 搜索论文（arXiv + Semantic Scholar）
/lit-review:search "transformer attention mechanisms"

# 深度搜索（子问题分解）
/lit-review:search "LLM agents" --deep

# 指定来源和过滤
/lit-review:search "reasoning" --sources arxiv,semantic-scholar --max 20 --year 2023-2025

# 分析单篇论文
/lit-review:analyze https://arxiv.org/abs/1706.03762

# 生成综述
/lit-review:synthesize "研究问题" --papers "url1,url2,..."
```

### Nexgent

```
# 创建工作区
lit_create_workspace(topic="Attention Mechanisms")

# 搜索论文（调用真实 API）
lit_search_web(query="transformer attention", sources="arxiv,semantic-scholar", max_results=10)

# 添加到工作区
lit_add_paper(workspace_id="ws-0001", title="Attention Is All You Need", ...)

# 引用网络
lit_citations(paper_id="ARXIV:1706.03762")
lit_references(paper_id="ARXIV:1706.03762")
lit_recommend(paper_ids=["ARXIV:1706.03762"])

# 综合分析
lit_synthesize(workspace_id="ws-0001")
```

## 3 个子技能

| 子技能 | 功能 |
|--------|------|
| `search` | 多源 API 搜索、子问题分解、结果去重 |
| `analyze` | 论文摘要、方法论分析、关键发现提取 |
| `synthesize` | 分类法构建、趋势分析、研究空白识别、综述生成 |

## Nexgent 工具列表

| 类别 | 工具 | 功能 |
|------|------|------|
| 配置 | `lit_set_key` | 设置 Semantic Scholar API key |
| 配置 | `lit_get_config` | 查看当前配置 |
| 工作区 | `lit_create_workspace` | 创建研究工作区 |
| 工作区 | `lit_list_workspaces` | 列出所有工作区 |
| 论文 | `lit_add_paper` | 添加论文到工作区 |
| 论文 | `lit_get_paper` | 获取论文详情 |
| 论文 | `lit_list_papers` | 列出工作区论文 |
| 论文 | `lit_search_local` | 本地关键词搜索 |
| 分析 | `lit_add_analysis` | 添加论文分析结果 |
| 分析 | `lit_synthesize` | 获取综合数据 |
| API | `lit_search_web` | arXiv + Semantic Scholar 搜索 |
| API | `lit_citations` | 获取引用某篇论文的论文 |
| API | `lit_references` | 获取某篇论文引用的论文 |
| API | `lit_recommend` | 基于种子论文推荐 |

## License

MIT
