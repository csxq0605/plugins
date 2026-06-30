# 🚀 Outreach Plugin — 快速开始指南

## 5 分钟快速上手

### Codex 安装

在 Codex App 的插件市场页面添加 GitHub marketplace：

```text
Marketplace source: csxq0605/plugins
Ref: master
Sparse paths:
  .agents
  outreach/codex-plugin
```

然后安装 `outreach` 插件：

```text
Marketplace: csxq0605-plugins
Plugin: outreach
```

不需要 clone 仓库，也不需要填写本地路径。安装后重新开启一个 Codex 对话。

### Codex 用户

```text
# 1. 配置邮箱（首次使用会自动检测并引导）
用 outreach 配置邮箱

# 2. 上传你的CV
用 outreach 解析我的 CV

# 3. 调研目标学校的教授
用 outreach 调研 MIT CS

# 4. 生成可视化报告
用 outreach 生成报告 MIT CS

# 5. 生成套磁邮件
用 outreach 生成邮件 MIT CS

# 6. 发送邮件
用 outreach 发送邮件给 MIT CS Kaiming_He
```

### Claude Code 用户

```bash
# 1. 配置邮箱（首次使用会自动检测并引导）
/outreach "配置邮箱"
# 或直接运行: python scripts/email_setup.py --email your@gmail.com --password pass --preset gmail

# 2. 上传你的CV
/outreach "这是我的CV"

# 3. 调研目标学校的教授
/outreach "调研 MIT CS"

# 4. 生成可视化报告
/outreach "生成报告 MIT CS"

# 5. 生成套磁邮件
/outreach "生成邮件 MIT CS"

# 6. 发送邮件
/outreach "发送邮件给 MIT CS Kaiming_He"
```

### Nexgent 用户

```python
# 1. 配置邮箱（首次使用会自动检测并引导）
email_setup(
    email_addr="your_name@gmail.com",
    password="your_password",
    name="Your Name",
    preset="gmail"  # 可选: pku, tsinghua, gmail, outlook, qq, 163
)

# 2. 解析CV
outreach_parse_materials(file_path="~/Documents/cv.pdf")

# 3. 调研教授
outreach_research_professor(
    name="Kaiming He",
    school="MIT",
    dept="CS",
    homepage="https://kaiminghe.com/",
    research_keywords="computer vision, deep learning"
)

# 4. 生成报告
outreach_generate_report(school="MIT", dept="CS")

# 5. 生成邮件
outreach_generate_email(school="MIT", dept="CS", professor="Kaiming He")

# 6. 发送邮件
email_send(
    to="kaiminghe@mit.edu",
    subject="Prospective PhD Student - Your Name - Computer Vision",
    body="[从email_draft.md复制的内容]"
)
```

## 完整工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  Step 0: 检查邮箱配置（自动检测）                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  已配置 → 跳过                                       │    │
│  │  未配置 → 引导配置 → 自动测试连接                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
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
│                          ↓                                  │
│  Step 7: 发送邮件                                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  试运行 → 确认 → 正式发送 → 记录日志                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 文件位置

### Codex 版本
```
plugins/outreach/codex-plugin/
├── .codex-plugin/plugin.json   # Codex 插件配置
├── skills/outreach/SKILL.md    # Skill 定义
├── scripts/
│   ├── pipeline.py             # 调研自动化脚本
│   ├── email_setup.py          # 邮箱配置脚本
│   ├── email_send.py           # 邮件发送脚本
│   ├── email_batch.py          # 批量发送脚本
│   └── email_list.py           # 邮件查看脚本
└── templates/                  # 报告模板
```

### Claude Code 版本
```
plugins/outreach/claude-code-plugin/
├── skills/outreach/SKILL.md    # Skill定义
├── scripts/
│   ├── pipeline.py             # 调研自动化脚本
│   ├── email_setup.py          # 邮箱配置脚本
│   ├── email_send.py           # 邮件发送脚本
│   ├── email_batch.py          # 批量发送脚本
│   └── email_list.py           # 邮件查看脚本
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

### Codex

| 用户请求 | 说明 |
|------|------|
| `用 outreach 配置邮箱` | 配置邮箱（自动测试连接） |
| `用 outreach 查看邮箱配置` | 查看当前邮箱配置 |
| `用 outreach 测试邮箱` | 测试邮箱连接 |
| `用 outreach 解析我的 CV` | 上传材料 |
| `用 outreach 调研 MIT CS` | 调研教授 |
| `用 outreach 调研 MIT CS --direction AI` | 按方向调研 |
| `用 outreach 生成报告 MIT CS` | 生成HTML报告 |
| `用 outreach 生成邮件 MIT CS` | 生成邮件草稿 |
| `用 outreach 查看 MIT CS Prof_Name` | 查看调研结果 |
| `用 outreach 发送邮件给 MIT CS Prof_Name` | 发送套磁邮件 |
| `用 outreach 批量发送 MIT CS` | 批量发送邮件 |
| `用 outreach 查看收件箱` | 查看邮件列表 |

### Claude Code

| 命令 | 说明 |
|------|------|
| `/outreach "配置邮箱"` | 配置邮箱（自动测试连接） |
| `/outreach "查看邮箱配置"` | 查看当前邮箱配置 |
| `/outreach "测试邮箱"` | 测试邮箱连接 |
| `/outreach "这是我的CV"` | 上传材料 |
| `/outreach "调研 MIT CS"` | 调研教授 |
| `/outreach "调研 MIT CS --direction AI"` | 按方向调研 |
| `/outreach "生成报告 MIT CS"` | 生成HTML报告 |
| `/outreach "生成邮件 MIT CS"` | 生成邮件草稿 |
| `/outreach "查看 MIT CS Prof_Name"` | 查看调研结果 |
| `/outreach "发送邮件给 MIT CS Prof_Name"` | 发送套磁邮件 |
| `/outreach "批量发送 MIT CS"` | 批量发送邮件 |
| `/outreach "查看收件箱"` | 查看邮件列表 |

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
