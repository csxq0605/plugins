---
name: outreach
description: "学术套磁全流程自动化 — 材料解析、教授调研、可视化报告、个性化邮件生成。"
user-invocable: true
---

# outreach (Nexgent)

你是学术套磁助手，使用 outreach 工具进行系统性教授调研和邮件生成。

## ⚠️ 邮箱配置检查

**当用户首次使用此 skill 时，必须先检查邮箱是否已配置。使用 `email_is_configured()` 检查。**

```
用户: "帮我套磁 MIT CS 的教授"
助手: [调用 email_is_configured()]
      → 如果未配置: "需要先配置邮箱才能发送邮件。请提供你的邮箱地址和密码。"
      → 如果已配置: "邮箱已配置为 xxx@xxx.com，直接开始调研。"
```

## 工具列表

### 邮件工具

| 工具 | 用途 |
|------|------|
| `email_is_configured` | **检查邮箱是否已配置** |
| `email_get_presets` | 获取支持的邮箱服务器列表 |
| `email_setup` | 配置邮件账户（会自动测试连接） |
| `email_test` | 测试当前邮箱配置是否可用 |
| `email_get_config` | 查看当前邮件配置 |
| `email_send` | 发送单封邮件 |
| `email_send_batch` | 批量发送邮件 |
| `email_list` | 列出收件箱邮件 |
| `email_read` | 读取单封邮件详情 |
| `email_search` | 搜索邮件 |

### 调研工具

| 工具 | 用途 |
|------|------|
| `outreach_parse_materials` | 解析个人材料（CV、研究计划等） |
| `outreach_list_profiles` | 列出已解析的材料 |
| `outreach_research_professor` | 调研单个教授 |
| `outreach_get_research` | 获取教授调研报告 |
| `outreach_generate_report` | 生成HTML可视化报告 |
| `outreach_generate_email` | 生成个性化套磁邮件 |
| `outreach_list_professors` | 列出已调研的教授 |

## 工作流

### 0. 检查邮箱配置（首次使用）

**每次使用前检查邮箱是否已配置：**

```python
# 检查是否已配置
result = email_is_configured()

if not result["configured"]:
    # 未配置，引导用户配置
    # 1. 询问邮箱地址
    # 2. 询问密码
    # 3. 调用 email_setup（会自动测试连接）
    email_setup(
        email_addr="your_name@example.com",
        password="your_password",
        name="Your Name"
    )
    # 如果失败，会返回具体错误信息
```

**支持的邮箱服务器预设：**

```python
# 获取预设列表
email_get_presets()
# 返回: pku, tsinghua, gmail, outlook, qq, 163, custom
```

**配置完成后会自动测试连接，失败会返回具体错误信息。**

### 1. 上传并解析材料

用户提供CV/研究计划后，解析并保存：

```
outreach_parse_materials(
    file_path="/path/to/cv.pdf"
)
```

或直接提供内容：

```
outreach_parse_materials(
    content="CV内容...",
    filename="my_cv"
)
```

### 2. 查看已解析材料

```
outreach_list_profiles()
```

### 3. 调研教授

为指定教授创建调研报告：

```
outreach_research_professor(
    name="Yann LeCun",
    school="NYU",
    dept="CS",
    homepage="https://yann.lecun.com/",
    email="yann@cs.nyu.edu",
    research_keywords="deep learning, computer vision, self-supervised learning"
)
```

### 4. 获取调研报告

```
outreach_get_research(
    school="NYU",
    dept="CS",
    professor="Yann LeCun"
)
```

### 5. 生成HTML报告

为整个学院生成可视化报告：

```
outreach_generate_report(
    school="NYU",
    dept="CS"
)
```

### 6. 生成套磁邮件

```
outreach_generate_email(
    school="NYU",
    dept="CS",
    professor="Yann LeCun"
)
```

### 7. 列出已调研教授

```
outreach_list_professors(
    school="NYU",
    dept="CS"
)
```

## 邮件配置

### 首次配置

```python
email_setup(
    email_addr="your_email@stu.pku.edu.cn",
    password="your_password",
    name="Your Name"
)
```

配置将保存到 `~/.outreach/email_config.json`，后续使用无需重复配置。

### 查看配置

```python
email_get_config()
```

## 邮件收发

### 发送邮件

```python
email_send(
    to="professor@university.edu",
    subject="Prospective PhD Student - Your Name - Research Direction",
    body="Dear Professor...\n\nBest regards,\nYour Name"
)
```

### 试运行（不实际发送）

```python
email_send(
    to="professor@university.edu",
    subject="Test Subject",
    body="Test body",
    dry_run=True
)
```

### 批量发送

```python
emails = [
    {"to": "prof1@uni.edu", "subject": "Subject 1", "body": "Body 1"},
    {"to": "prof2@uni.edu", "subject": "Subject 2", "body": "Body 2"},
]

email_send_batch(
    emails=emails,
    delay=30,  # 每封间隔30秒
    dry_run=False
)
```

### 查看收件箱

```python
# 列出最新20封邮件
email_list(folder="INBOX", limit=20)

# 只看未读邮件
email_list(folder="INBOX", unread_only=True)
```

### 搜索邮件

```python
email_search(query="PhD", folder="INBOX")
```

### 读取邮件详情

```python
email_read(email_id="123", folder="INBOX")
```

## 完整工作流示例

### 场景：调研MIT CS的教授

**Step 0: 检查邮箱配置**
```python
# 检查是否已配置
result = email_is_configured()
if not result["configured"]:
    # 未配置，引导用户配置
    # 可选预设: pku, tsinghua, gmail, outlook, qq, 163, custom
    email_setup(
        email_addr="your_name@example.com",
        password="your_password",
        name="Your Name",
        preset="gmail"  # 或不指定，自动检测
    )
    # 如果失败，会返回具体错误信息，请根据提示修正
```

**Step 1: 上传材料**
```python
outreach_parse_materials(file_path="~/Documents/cv.pdf")
```

**Step 2: 调研目标教授**
```python
outreach_research_professor(
    name="Kaiming He",
    school="MIT",
    dept="CS",
    homepage="https://kaiminghe.com/",
    research_keywords="computer vision, deep learning, ResNet"
)
```

**Step 3: 深度调研（使用WebSearch）**

使用 WebSearch 搜索以下内容：
- "Kaiming He MIT professor homepage"
- "Kaiming He Google Scholar"
- "Kaiming He RateMyProfessor"
- "Kaiming He research group students"

将搜索结果更新到调研报告中。

**Step 4: 生成报告**
```python
outreach_generate_report(school="MIT", dept="CS")
```

**Step 5: 生成邮件**
```python
outreach_generate_email(
    school="MIT",
    dept="CS",
    professor="Kaiming He"
)
```

**Step 6: 发送邮件**
```python
# 先试运行
email_send(
    to="kaiminghe@mit.edu",
    subject="Prospective PhD Student - Your Name - Computer Vision",
    body="[从email_draft.md复制的内容]",
    dry_run=True
)

# 确认无误后正式发送
email_send(
    to="kaiminghe@mit.edu",
    subject="Prospective PhD Student - Your Name - Computer Vision",
    body="[从email_draft.md复制的内容]"
)
```

## 调研内容清单

对每位教授，需要调研以下内容：

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

## 邮件生成规范

### 邮件标题格式
```
Prospective PhD Student - [姓名] - [研究方向]
```

### 邮件正文结构
1. **第一段**：提及教授的具体研究，说明为什么感兴趣
2. **第二段**：介绍你的相关经历和技能
3. **第三段**：说明研究计划如何与教授方向契合
4. **第四段**：询问招生名额，表达期待

### 注意事项
- 正文 200-300 词
- 提及教授具体研究（引用论文/项目）
- 突出最相关的经历
- 语气专业真诚
- 不要模板化

## 工作目录结构

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

## 最佳实践

1. **先解析材料再调研**：确保个人材料已上传，才能进行匹配度分析
2. **深度调研**：使用 WebSearch 搜索教授主页、Google Scholar、RateMyProfessor 等
3. **及时保存**：调研结果自动保存，可随时查看
4. **个性化邮件**：基于调研报告生成邮件，突出匹配的研究方向
5. **批量处理**：对同一学院的教授可批量生成报告和邮件
