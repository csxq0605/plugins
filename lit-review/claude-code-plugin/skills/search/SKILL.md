---
name: search
description: "Multi-source academic paper search — arXiv, Semantic Scholar via real APIs. Supports subtopic decomposition for deep research, date/category filters, and result deduplication. Trigger on: 'search papers', 'find papers', 'literature search', 'academic search', 'arxiv search'."
user-invocable: true
allowed-tools: Bash(python*), Read
---

# lit-review:search — 多源学术搜索

你是学术搜索专家，从多个学术数据库搜索论文，支持子问题分解和深度调研。

## 调用方式

```
/lit-review:search "研究问题"                                  # 快速搜索
/lit-review:search "研究问题" --deep                           # 深度搜索（子问题分解）
/lit-review:search "研究问题" --sources arxiv,semantic-scholar  # 指定来源
/lit-review:search "研究问题" --from 2023-01-01               # 日期过滤
/lit-review:search "研究问题" --max 20                        # 最大结果数
```

## API 配置

**Semantic Scholar API Key**（推荐配置，提升速率限制）：
- 免费申请：https://www.semanticscholar.org/product/api
- 无 key：100 请求/5 分钟（共享池）
- 有 key：1 请求/秒（独立配额）

配置方式（任选其一）：
```bash
# 方式 1: 环境变量
export SEMANTIC_SCHOLAR_API_KEY=your_key_here

# 方式 2: 配置文件（自动创建 ~/.lit-review/config.json）
# 在对话中使用：
/lit-review:search --set-key your_key_here
```

**arXiv API**：免费，无需 key，3 秒间隔。

## 参数解析

从 `$ARGUMENTS` 中解析：
- `query`：研究问题（必需）
- `--sources`：搜索来源，逗号分隔（默认：arxiv,semantic-scholar）
- `--deep`：启用子问题分解
- `--from`：起始日期（YYYY-MM-DD）
- `--to`：结束日期
- `--max`：最大结果数（默认：10）
- `--categories`：arXiv 类别过滤（如 cs.AI,cs.LG）
- `--set-key`：设置 Semantic Scholar API key

## 搜索工具

使用 `bin/lit-search.py` 脚本调用真实 API（无外部依赖，纯 Python stdlib）。

**脚本位置**：插件目录下的 `bin/lit-search.py`

**命令**：
```bash
# 搜索论文
python bin/lit-search.py search "query" --sources arxiv,semantic-scholar --max 10

# 设置 API key
python bin/lit-search.py set-key YOUR_KEY

# 查看配置
python bin/lit-search.py config

# 引用网络
python bin/lit-search.py citations ARXIV:2301.00234 --max 20
python bin/lit-search.py references ARXIV:2301.00234 --max 20
python bin/lit-search.py recommend ARXIV:2301.00234,ARXIV:1810.04805 --max 10
```

## API 配置

**Semantic Scholar API Key**（推荐，提升速率限制）：
- 免费申请：https://www.semanticscholar.org/product/api
- 无 key：100 请求/5 分钟
- 有 key：1 请求/秒

配置：
```bash
# 方式 1: 环境变量
export SEMANTIC_SCHOLAR_API_KEY=your_key_here

# 方式 2: 脚本命令（保存到 ~/.lit-review/config.json）
python bin/lit-search.py set-key your_key_here
```

**arXiv API**：免费，无需 key，3 秒间隔。

## 搜索流程

### Step 0: API Key 配置（如果指定了 --set-key）

```bash
python bin/lit-search.py set-key "用户提供的key"
```

### Step 1: 查询优化

将用户的研究问题转换为最优查询。arXiv 支持字段前缀（ti:, abs:, cat:, all:）和布尔运算符。

### Step 2: 子问题分解（--deep 模式）

将研究问题分解为 3-5 个子问题，每个子问题独立搜索。

### Step 3: 多源搜索

```bash
python bin/lit-search.py search "子问题1" --sources arxiv,semantic-scholar --max 10
python bin/lit-search.py search "子问题2" --sources arxiv,semantic-scholar --max 10
```

返回 JSON，包含去重和按引用排序的论文列表。

### Step 4: 结果去重

不同来源可能返回同一篇论文。去重规则：
1. 标题相似度 > 80% 视为同一篇
2. 相同 DOI 视为同一篇
3. 相同 arXiv ID 视为同一篇

### Step 5: 结果排序

按以下优先级排序：
1. 引用数（高引用优先）
2. 发表日期（新论文优先）
3. 来源权威性（arXiv/顶会优先）

## 输出格式

```markdown
# Literature Search Results

**Query**: "transformer attention mechanisms"
**Sources**: arXiv, Semantic Scholar
**Date**: 2024-01-01 to 2025-06-26
**Results**: 15 unique papers found

## Papers

### 1. Attention Is All You Need
- **Authors**: Vaswani et al.
- **Year**: 2017
- **Source**: arXiv (1706.03762)
- **Citations**: 120,000+
- **Abstract**: [摘要]
- **URL**: https://arxiv.org/abs/1706.03762

### 2. [更多论文...]

## Subtopics (if --deep)

### Subtopic 1: Types of attention mechanisms
- Papers: [相关论文列表]

### Subtopic 2: Computational complexity
- Papers: [相关论文列表]

## Recommended Next Steps
- /lit-review:analyze <paper_url> — 深度分析某篇论文
- /lit-review:synthesize "研究问题" --papers "url1,url2,..." — 生成综述
```

## 注意事项

1. **速率限制**：arXiv API 限制 3 秒/请求，Semantic Scholar 限制 1 请求/秒
2. **结果数量**：默认每来源 10 篇，用 --max 调整
3. **语言**：搜索结果以英文为主
4. **全文获取**：搜索只返回元数据，用 analyze 技能获取全文
