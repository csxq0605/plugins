# 🎓 Outreach Plugin — 学术套磁全流程自动化

一套完整的学术套磁自动化工具，支持 Claude Code 和 Nexgent 两个平台。

## 安装

### Claude Code

```bash
claude install-plugin github:csxq0605/plugins
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/outreach/nexgent-plugin
```

## 功能特性

- 📧 **邮箱配置**：自动检测并引导配置，支持多种邮箱，配置后自动测试连接
- 📄 **材料解析**：自动解析 CV、研究计划、成绩单等材料
- 🔍 **教授调研**：深度调研教授的研究方向、发表统计、学生去向、导师风格
- 📊 **可视化报告**：生成交互式 HTML 报告，支持搜索、排序、筛选
- ✉️ **邮件生成**：基于调研报告生成个性化套磁邮件
- 🎯 **匹配度分析**：自动评估与教授的研究方向匹配度
- 📬 **邮件收发**：基于 IMAP/SMTP 协议的完整邮件功能

## 支持的邮箱

| 邮箱 | 预设 | 说明 |
|------|------|------|
| 北京大学 | `pku` | mail.stu.pku.edu.cn |
| 清华大学 | `tsinghua` | mail.tsinghua.edu.cn |
| Gmail | `gmail` | 需要应用专用密码 |
| Outlook | `outlook` | outlook.office365.com |
| QQ邮箱 | `qq` | 需要应用专用密码 |
| 163邮箱 | `163` | 需要开启IMAP/SMTP |
| 自定义 | `custom` | 自己指定服务器 |

## 目录结构

```
outreach/
├── claude-code-plugin/        # Claude Code 插件
│   ├── .claude-plugin/plugin.json
│   ├── CLAUDE.md
│   ├── README.md
│   ├── scripts/
│   │   ├── pipeline.py        # 调研自动化脚本
│   │   ├── email_setup.py     # 邮箱配置脚本
│   │   ├── email_send.py      # 邮件发送脚本
│   │   ├── email_batch.py     # 批量发送脚本
│   │   └── email_list.py      # 邮件查看脚本
│   ├── skills/outreach/
│   │   └── SKILL.md
│   └── templates/
│       ├── index.html
│       └── style.css
└── nexgent-plugin/            # Nexgent 插件
    ├── __init__.py
    ├── plugin.json
    ├── README.md
    ├── outreach_tools.py      # 调研工具定义
    ├── email_tools.py         # 邮件工具定义
    ├── references/
    ├── skills/outreach/
    │   └── SKILL.md
    └── tests/
        ├── __init__.py
        ├── test_outreach.py
        └── pytest.ini
```

## 工作流程

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

## 使用方式

### Claude Code

```bash
# 配置邮箱
/outreach "配置邮箱"

# 上传材料
/outreach "这是我的CV"

# 调研教授
/outreach "调研 MIT CS"

# 生成报告
/outreach "生成报告 MIT CS"

# 生成邮件
/outreach "生成邮件 MIT CS"

# 发送邮件
/outreach "发送邮件给 MIT CS Professor_Name"
```

### Nexgent

```python
# 配置邮箱
email_setup(email_addr="...", password="...", preset="pku")

# 解析材料
outreach_parse_materials(file_path="cv.pdf")

# 调研教授
outreach_research_professor(
    name="Kaiming He",
    school="MIT",
    dept="CS",
    homepage="https://kaiminghe.com/",
    research_keywords="computer vision"
)

# 生成报告
outreach_generate_report(school="MIT", dept="CS")

# 生成邮件
outreach_generate_email(school="MIT", dept="CS", professor="Kaiming He")

# 发送邮件
email_send(to="...", subject="...", body="...")
```

## 测试

```bash
# 单元测试
cd outreach/nexgent-plugin && python -m pytest tests/ -v
```

## 配置文件

- 邮箱配置: `~/.outreach/email_config.json`
- 调研数据: `~/.outreach/schools/`
- 个人材料: `~/.outreach/profiles/`

## 与 Email 插件的关系

- **Email Plugin**：独立的邮件收发功能
- **Outreach Plugin**：学术套磁全流程（包含邮件功能）

Outreach 插件内置了邮件功能，可以独立使用。如果只需要邮件功能，可以使用独立的 Email 插件。

## License

MIT
