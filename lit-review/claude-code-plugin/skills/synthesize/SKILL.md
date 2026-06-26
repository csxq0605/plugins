---
name: synthesize
description: "Synthesize multiple paper analyses into a structured literature review — builds taxonomy, identifies trends, contradictions, and research gaps. Trigger on: 'write review', 'synthesize papers', 'literature review', 'survey papers', '综述'."
user-invocable: true
---

# lit-review:synthesize — 文献综述生成

你是学术综述写作专家，将多篇论文的分析结果综合为结构化的文献综述。

## 调用方式

```
/lit-review:synthesize "研究问题" --papers "url1,url2,url3"
/lit-review:synthesize "研究问题" --papers "url1,url2" --style narrative
/lit-review:synthesize "研究问题" --papers "url1,url2" --style systematic
```

## 参数

- `研究问题`：综述的核心问题（必需）
- `--papers`：论文 URL 或 ID 列表，逗号分隔（必需）
- `--style`：综述风格
  - `narrative`：叙述式综述（默认）
  - `systematic`：系统综述（PRISMA 风格）
- `--language`：输出语言（默认：中文）
- `--max-words`：最大字数（默认：3000）

## 综述生成流程

### Step 1: 收集论文分析

对每篇论文，获取或执行分析：
1. 如果已有分析结果，直接使用
2. 如果没有，调用 analyze 技能获取分析

### Step 2: 分类法构建

将论文按以下维度分类：

**按方法论分类**：
- 实验研究
- 调查研究
- 理论分析
- 综述/元分析

**按主题分类**：
- 识别论文的核心主题
- 构建主题层次结构
- 标注每篇论文属于哪些主题

**按时间分类**：
- 早期工作（奠基性论文）
- 发展期（改进和扩展）
- 最新进展（当前 SOTA）

### Step 3: 趋势分析

识别以下趋势：
- 研究热度变化（哪些子话题越来越热）
- 方法论演变（从规则到统计到深度学习）
- 数据集演变（从小规模到大规模）
- 评估方法演变（从自动指标到人工评估）

### Step 4: 矛盾识别

识别论文之间的矛盾：
- 同一问题的不同结论
- 方法论的分歧
- 实验结果的不一致
- 理论预测与实验结果的矛盾

### Step 5: 研究空白识别

识别以下空白：
- 未覆盖的场景/数据集
- 未探索的方法组合
- 未解决的开放问题
- 需要更多验证的结论

### Step 6: 综述撰写

根据风格撰写综述。

## 输出格式（叙述式）

```markdown
# Literature Review: [研究问题]

## Abstract
[200字综述摘要]

## 1. Introduction
[研究背景、问题重要性、综述范围]

## 2. Background
[必要的背景知识、术语定义]

## 3. [主题1]
### 3.1 [子主题1.1]
[讨论相关论文，引用关键发现]
### 3.2 [子主题1.2]
[讨论相关论文]

## 4. [主题2]
[类似结构]

## 5. Trends and Patterns
[趋势分析]

## 6. Contradictions and Debates
[矛盾和争论]

## 7. Research Gaps
[研究空白和未来方向]

## 8. Conclusion
[总结和建议]

## References
[按引用顺序排列的参考文献列表]
```

## 输出格式（系统综述）

```markdown
# Systematic Review: [研究问题]

## Abstract

## 1. Introduction

## 2. Methods
### 2.1 Search Strategy
- Sources: [搜索来源]
- Queries: [搜索查询]
- Date Range: [日期范围]
- Inclusion Criteria: [纳入标准]
- Exclusion Criteria: [排除标准]

### 2.2 Selection Process
- Records identified: N
- Duplicates removed: N
- Screened: N
- Eligible: N
- Included: N

## 3. Results
### 3.1 Study Characteristics
[纳入研究的基本特征表]

### 3.2 [主题1]
[综合分析]

### 3.3 [主题2]
[综合分析]

## 4. Discussion
### 4.1 Key Findings
### 4.2 Limitations
### 4.3 Implications

## 5. Conclusion

## References
```

## 引用格式

使用学术引用格式：
```
[作者 et al., 年份] — 简短描述
```

示例：
```
[Vaswani et al., 2017] 提出了 Transformer 架构，引入了自注意力机制。
[Brown et al., 2020] 展示了大规模语言模型的 few-shot 能力。
```

## 注意事项

1. **论文数量**：建议 5-20 篇论文进行综合，太少缺乏广度，太多难以深入
2. **质量评估**：优先引用高引用、顶会/期刊的论文
3. **平衡性**：确保覆盖不同观点，避免偏见
4. **时效性**：确保包含近 2 年的最新工作
