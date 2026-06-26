# 🎓 Outreach Plugin — 学术套磁全流程自动化

一套完整的学术套磁自动化工具，支持 Claude Code 和 Nexgent 两个平台。

## ⚠️ 邮箱配置检查

**使用此插件前，会自动检查邮箱是否已配置。如果未配置，会主动引导用户完成配置。配置一次后永久有效。**

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

## 平台支持

### Claude Code 版本

位置：`plugins/outreach/claude-code-plugin/`

使用方式：
```bash
/outreach "这是我的CV"
/outreach "调研 MIT CS"
/outreach "生成报告 MIT CS"
/outreach "生成邮件 MIT CS"
```

### Nexgent 版本

位置：`plugins/outreach/nexgent-plugin/`

可用工具：
- `outreach_parse_materials` — 解析个人材料
- `outreach_list_profiles` — 列出已解析材料
- `outreach_research_professor` — 调研教授
- `outreach_get_research` — 获取调研报告
- `outreach_generate_report` — 生成HTML报告
- `outreach_generate_email` — 生成套磁邮件
- `outreach_list_professors` — 列出已调研教授

## 工作流程

```
上传材料 → 解析提取 → 选择学校学院 → 调研教授 → 生成报告 → 生成邮件
   ↓           ↓           ↓            ↓          ↓         ↓
 CV/PDF     提取信息     搜索教授     主页/Scholar   HTML     个性化
 研究计划   研究方向     生成CSV     学生去向      可视化    邮件草稿
 成绩单     技能经历                 导师风格      报告
```

## 目录结构

```
~/.outreach/
├── inbox/              # 用户上传的原始文件
├── profiles/           # 解析后的个人材料
├── schools/
│   └── {School}_{Dept}/
│       ├── professors.csv    # 教授列表
│       ├── report.html       # 可视化报告
│       ├── {Prof_Name}/
│       │   ├── research.md   # 调研报告
│       │   └── email_draft.md # 邮件草稿
│       └── ...
├── logs/               # 发送日志
└── templates/          # 报告模板
```

## 调研内容

### 基本信息
- 全名、职称、所属实验室/组
- 研究方向（详细列出）
- 联系方式、邮箱

### 发表统计
- Google Scholar 数据：h-index、总论文数、引用数
- 近 5 年每年发文数量
- 主要发表会议/期刊（Top 5）
- CCF-A 会议论文数量（特别是大模型/LLM 方向）
- 代表性论文（最近 3-5 篇）

### 学生去向
- 毕业生去向（业界/学术界）
- 毕业生现在在哪些公司/学校
- 平均毕业年限

### 研究组分析
- 当前组内学生/博后数量
- 组内研究氛围
- 近年发文周期

### 导师风格
- 指导风格（放养/严格/合作型）
- 学生评价（RateMyProfessor 等）

### 匹配度分析
- 研究方向匹配度（1-10 分）
- 技能匹配度（1-10 分）
- 申请成功率评估
- 建议的切入点

### 申请建议
- 是否在招生
- 最佳联系时间
- 邮件中应重点强调的内容

## 邮件模板

```
SUBJECT: Prospective PhD Student - [姓名] - [研究方向]

Dear Professor [姓名],

[第一段：提及教授的具体研究，说明为什么感兴趣]

[第二段：介绍你的相关经历和技能]

[第三段：说明研究计划如何与教授方向契合]

[第四段：询问招生名额，表达期待]

Best regards,
[姓名]
[学校/专业]
[邮箱]
```

## 调研方法优先级

1. 教授个人主页 → 最权威
2. Google Scholar → 发表数据
3. 学院官网 → 招生信息
4. Semantic Scholar → 论文详情
5. RateMyProfessor → 学生评价
6. OpenReview → 审稿风格

## 邮件功能

### 邮箱配置

**插件会自动检测邮箱是否已配置。如果未配置，会引导用户完成配置。配置一次后永久有效。**

#### Claude Code
```bash
# 检查是否已配置
python scripts/email_setup.py --check

# 配置邮箱（自动测试连接）
python scripts/email_setup.py --email your_name@gmail.com --password your_password --name "Your Name"

# 使用预设配置
python scripts/email_setup.py --email your_name@stu.pku.edu.cn --password your_password --preset pku

# 测试邮箱连接
python scripts/email_setup.py --test

# 查看当前配置
python scripts/email_setup.py --info
```

#### Nexgent
```python
# 检查是否已配置
result = email_is_configured()

# 获取支持的预设
email_get_presets()

# 配置邮箱（自动测试连接）
email_setup(
    email_addr="your_name@gmail.com",
    password="your_password",
    name="Your Name",
    preset="gmail"  # 可选，自动检测
)

# 测试邮箱连接
email_test()

# 查看当前配置
email_get_config()
```

### 发送邮件

#### Claude Code
```bash
# 发送单封邮件
python scripts/email_send.py --to professor@university.edu --subject "Subject" --body "Body"

# 试运行
python scripts/email_send.py --to professor@university.edu --subject "Subject" --body "Body" --dry-run

# 批量发送
python scripts/email_batch.py --csv professors.csv --delay 30 --dry-run
python scripts/email_batch.py --csv professors.csv --delay 30
```

#### Nexgent
```python
# 发送单封邮件
email_send(
    to="professor@university.edu",
    subject="Subject",
    body="Body"
)

# 批量发送
emails = [
    {"to": "prof1@uni.edu", "subject": "Subject 1", "body": "Body 1"},
    {"to": "prof2@uni.edu", "subject": "Subject 2", "body": "Body 2"},
]
email_send_batch(emails=emails, delay=30)
```

### 查看邮件

#### Claude Code
```bash
# 查看收件箱
python scripts/email_list.py --limit 20

# 只看未读
python scripts/email_list.py --unread

# 搜索邮件
python scripts/email_list.py --search "PhD"

# 读取邮件
python scripts/email_list.py --read 123
```

#### Nexgent
```python
# 列出邮件
email_list(folder="INBOX", limit=20)

# 搜索邮件
email_search(query="PhD", folder="INBOX")

# 读取邮件
email_read(email_id="123", folder="INBOX")
```

### 邮件日志

所有发送记录保存在 `~/.outreach/logs/` 目录，格式：

```
---
Time: 2024-01-15T10:30:00
To: professor@university.edu
Subject: Prospective PhD Student - ...
Status: SUCCESS
Detail: 发送成功
```

## 注意事项

1. **隐私保护**：用户的 CV、成绩等个人信息仅用于邮件生成，不对外分享
2. **频率控制**：批量调研时每请求间隔 3-5 秒，避免被封
3. **数据准确性**：调研数据来自公开来源，标注信息来源和置信度
4. **缓存利用**：已调研的教授不会重复调研，除非用户要求更新
5. **邮件安全**：批量发送时每封间隔 30 秒，避免被标记为垃圾邮件

## 快速开始

### Claude Code

```bash
# 1. 上传材料
/outreach "这是我的CV和研究计划"

# 2. 调研教授
/outreach "调研 MIT CS"

# 3. 生成报告
/outreach "生成报告 MIT CS"

# 4. 生成邮件
/outreach "生成邮件 MIT CS"
```

### Nexgent

```python
# 1. 解析材料
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

## 依赖

### Claude Code 版本
- Python 3.7+
- pdfplumber（可选，用于解析PDF）
- python-docx（可选，用于解析Word）

### Nexgent 版本
- Python 3.7+
- 无额外依赖

## 许可证

MIT License
