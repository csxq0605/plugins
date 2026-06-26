# 🚀 Outreach Plugin — 快速开始指南

## 5 分钟快速上手

### Claude Code 用户

```bash
# 1. 上传你的CV
/outreach "这是我的CV"

# 2. 调研目标学校的教授
/outreach "调研 MIT CS"

# 3. 生成可视化报告
/outreach "生成报告 MIT CS"

# 4. 生成套磁邮件
/outreach "生成邮件 MIT CS"
```

### Nexgent 用户

```python
# 1. 解析CV
outreach_parse_materials(file_path="~/Documents/cv.pdf")

# 2. 调研教授
outreach_research_professor(
    name="Kaiming He",
    school="MIT",
    dept="CS",
    homepage="https://kaiminghe.com/",
    research_keywords="computer vision, deep learning"
)

# 3. 生成报告
outreach_generate_report(school="MIT", dept="CS")

# 4. 生成邮件
outreach_generate_email(school="MIT", dept="CS", professor="Kaiming He")
```

## 完整工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 上传材料                                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  CV.pdf / research_plan.md / transcripts.pdf        │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Step 2: 解析提取                                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  姓名、邮箱、学校、研究方向、技能、GPA                │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Step 3: 选择学校学院                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  MIT CS / Stanford CS / CMU CS / ...                │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Step 4: 调研教授                                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  主页 → Scholar → RateMyProfessor → 学生去向        │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Step 5: 生成报告                                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  HTML可视化报告（可搜索、排序、筛选）                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Step 6: 生成邮件                                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  个性化邮件草稿（基于调研报告）                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 文件位置

### Claude Code 版本
```
plugins/outreach/claude-code-plugin/
├── skills/outreach/SKILL.md    # Skill定义
├── scripts/pipeline.py         # 自动化脚本
└── templates/                  # 报告模板
```

### Nexgent 版本
```
plugins/outreach/nexgent-plugin/
├── plugin.json                 # 插件配置
├── __init__.py                 # 工具注册
├── outreach_tools.py           # 工具实现
└── skills/outreach/SKILL.md    # Skill定义
```

### 工作数据
```
~/.outreach/
├── inbox/              # 上传的原始文件
├── profiles/           # 解析后的材料
├── schools/            # 调研数据
│   └── MIT_CS/
│       ├── professors.csv
│       ├── report.html
│       └── Kaiming_He/
│           ├── research.md
│           └── email_draft.md
└── logs/               # 发送日志
```

## 常用命令速查

### Claude Code

| 命令 | 说明 |
|------|------|
| `/outreach "这是我的CV"` | 上传材料 |
| `/outreach "调研 MIT CS"` | 调研教授 |
| `/outreach "调研 MIT CS --direction AI"` | 按方向调研 |
| `/outreach "生成报告 MIT CS"` | 生成HTML报告 |
| `/outreach "生成邮件 MIT CS"` | 生成邮件草稿 |
| `/outreach "查看 MIT CS Prof_Name"` | 查看调研结果 |

### Nexgent

| 工具 | 说明 |
|------|------|
| `outreach_parse_materials(file_path)` | 解析材料 |
| `outreach_list_profiles()` | 列出材料 |
| `outreach_research_professor(...)` | 调研教授 |
| `outreach_get_research(...)` | 获取调研 |
| `outreach_generate_report(...)` | 生成报告 |
| `outreach_generate_email(...)` | 生成邮件 |
| `outreach_list_professors(...)` | 列出教授 |

## 调研内容清单

- [x] 基本信息（姓名、职称、实验室、方向）
- [x] 发表统计（h-index、论文数、顶会数量）
- [x] 学生去向（毕业生就业情况）
- [x] 研究组分析（组内规模、发文周期）
- [x] 导师风格（指导方式、学生评价）
- [x] 匹配度分析（方向匹配、技能匹配）
- [x] 申请建议（是否招生、最佳时间）

## 邮件模板

```
SUBJECT: Prospective PhD Student - [姓名] - [研究方向]

Dear Professor [姓名],

[提及教授的具体研究，说明为什么感兴趣]

[介绍你的相关经历和技能]

[说明研究计划如何与教授方向契合]

[询问招生名额，表达期待]

Best regards,
[姓名]
[学校/专业]
[邮箱]
```

## 注意事项

1. **隐私保护**：个人信息仅用于邮件生成，不对外分享
2. **频率控制**：调研时每请求间隔 3-5 秒
3. **数据准确性**：调研数据来自公开来源，建议人工核实
4. **缓存利用**：已调研的教授不会重复调研

## 下一步

- 查看 [EXAMPLES.md](EXAMPLES.md) 获取详细使用示例
- 查看 [README.md](README.md) 了解完整功能
