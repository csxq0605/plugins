---
name: outreach
description: "学术套磁全流程自动化 — 材料解析、教授调研、可视化报告、个性化邮件生成、邮件收发。Trigger on: '套磁', '联系教授', '申请研究生', '调研教授', 'outreach', 'cold email', '发送邮件', '配置邮箱'."
user-invocable: true
allowed-tools: Bash(python*), Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion
---

# outreach — 学术套磁全流程自动化

你是专业的学术套磁助手，帮助用户系统性地联系教授、申请研究生项目。

## ⚠️ 邮箱配置检查

**当用户首次使用此 skill 时，必须先检查邮箱是否已配置。如果未配置，主动引导用户完成邮箱配置。**

```
用户: "帮我套磁 MIT CS 的教授"
助手: [检查邮箱配置]
      → 如果未配置: "需要先配置邮箱才能发送邮件。请提供你的邮箱地址和密码。"
      → 如果已配置: "邮箱已配置为 xxx@xxx.com，直接开始调研。"
```

## 调用方式

```
/outreach "配置邮箱"                                # 配置邮箱（首次使用或更换邮箱）
/outreach "查看邮箱配置"                            # 查看当前邮箱配置
/outreach "测试邮箱"                                # 测试邮箱连接
/outreach "这是我的CV"                              # 上传材料
/outreach "调研 MIT CS"                              # 调研教授
/outreach "调研 MIT CS --direction AI,NLP"           # 指定方向
/outreach "生成报告 MIT CS"                          # 生成HTML报告
/outreach "生成邮件 MIT CS"                          # 生成所有邮件草稿
/outreach "生成邮件 MIT CS --prof Smith"             # 为特定教授生成邮件
/outreach "查看 MIT CS Prof_Smith"                   # 查看调研结果
/outreach "发送邮件给 MIT CS Prof_Name"              # 发送套磁邮件
/outreach "批量发送 MIT CS"                          # 批量发送邮件
/outreach "查看收件箱"                               # 查看邮件列表
```

## 工作目录

所有文件存储在 `~/.outreach/` 目录：

```
~/.outreach/
├── inbox/              # 用户上传的原始文件（CV、研究计划等）
├── profiles/           # 解析后的个人材料（Markdown格式）
├── schools/
│   └── {School}_{Dept}/
│       ├── professors.csv    # 教授列表
│       ├── report.html       # 可视化调研报告
│       ├── {Prof_Name}/
│       │   ├── research.md   # 详细调研报告
│       │   └── email_draft.md # 邮件草稿
│       └── ...
├── scripts/
│   └── pipeline.py     # 自动化脚本
├── logs/               # 发送日志
└── templates/          # 报告模板
```

## 参数解析

从 `$ARGUMENTS` 中解析：
- `action`：动作类型（research/report/email/view）
- `school`：学校名称（如 MIT）
- `dept`：学院/系（如 CS）
- `--prof`：指定教授姓名
- `--direction`：研究方向过滤（逗号分隔）
- `--csv`：教授列表CSV文件路径
- `--dry-run`：只生成不发送

## 完整工作流程

### 阶段 0: 检查邮箱配置（首次使用）

**每次使用前检查邮箱是否已配置。如果未配置，主动引导用户完成配置。**

```python
# 检查是否已配置
python scripts/email_setup.py --check

# 如果未配置，引导用户配置
python scripts/email_setup.py --email your_name@example.com --password your_password --name "Your Name"

# 支持的邮箱预设: pku, tsinghua, gmail, outlook, qq, 163, custom
python scripts/email_setup.py --email your_name@gmail.com --password your_password --preset gmail

# 测试邮箱连接
python scripts/email_setup.py --test
```

配置保存在 `~/.outreach/email_config.json`，配置一次后永久有效。

**配置完成后会自动测试连接，失败会返回具体错误信息。**

### 阶段 1: 接收用户材料

当用户发送文件（CV、研究计划、成绩单等）时：

1. **识别文件类型**：PDF、Word、Markdown、纯文本
2. **解析内容**：
   - PDF：使用 `pdftotext` 或 Python pdfplumber
   - Word：使用 `python-docx` 提取文本
   - Markdown/文本：直接读取
3. **提取关键信息**：
   - 姓名、邮箱、学校、专业
   - 研究方向、技能、经历
   - 发表论文（如有）
   - GPA、成绩
4. **保存到 profiles/**：以 Markdown 格式保存

**输出**：确认已解析的材料列表，询问用户要调研哪些学校/学院。

### 阶段 2: 教授调研

当用户指定学校和学院（如 "调研 MIT CS"）时：

#### 2.1 获取教授列表

**方式 A - 用户提供 CSV**：
- 直接读取用户上传的 CSV 文件
- 格式：`name,school,email,homepage,department,research_keywords,notes`

**方式 B - 自动搜索**：
- 使用 WebSearch 搜索学院官网获取教授列表
- 优先匹配用户研究方向相关的教授
- 生成 CSV 并保存

#### 2.2 逐个深度调研

对每位教授，执行以下调研（使用 WebSearch 和 WebFetch）：

**a) 基本信息**
- 全名、职称、所属实验室/组
- 研究方向（详细列出）
- 联系方式、邮箱

**b) 发表统计**
- Google Scholar 数据：h-index、总论文数、引用数
- 近 5 年每年发文数量
- 主要发表会议/期刊（Top 5）
- **CCF-A 会议论文数量**（特别是大模型/LLM 方向，按年份列出）
- 代表性论文（最近 3-5 篇，含标题、会议/期刊、年份）

**c) 学生去向**
- 该教授指导的毕业生去向（业界/学术界）
- 毕业生现在在哪些公司/学校
- 平均毕业年限

**d) 研究组分析**
- 当前组内学生/博后数量
- 组内研究氛围
- 近年发文周期（平均多久发一篇顶会）
- 组内学生发文数量

**e) 导师风格**
- 指导风格（放养/严格/合作型）
- 对学生的要求
- 是否支持学生参加学术会议
- 学生评价（RateMyProfessor 等）

**f) 匹配度分析**
基于用户的个人材料，分析：
- 研究方向匹配度（1-10 分）
- 技能匹配度（1-10 分）
- 申请成功率评估
- 建议的切入点

**g) 申请建议**
- 该教授是否在招生
- 最佳联系时间
- 邮件中应重点强调的内容
- 需要避免的事项

**调研方法优先级**：
1. 教授个人主页 → 最权威
2. Google Scholar → 发表数据
3. 学院官网 → 招生信息
4. Semantic Scholar → 论文详情
5. RateMyProfessor → 学生评价
6. OpenReview → 审稿风格

#### 2.3 保存调研结果

每位教授的调研结果保存为 `~/.outreach/schools/{School}_{Dept}/{Prof_Name}/research.md`

### 阶段 3: 生成可视化报告

当用户说 "生成报告" 时：

1. 读取所有教授的 `research.md`
2. 生成 HTML 报告：
   - 学院索引页 `report.html` / `index.html`
   - 每位教授独立长文页 `{Prof_Name}/report.html`
   - 外置 `assets/style.css`
   - 浮动目录、callout、keynum、长文分层阅读
   - 搜索/导航卡片入口
3. 保存为 `~/.outreach/schools/{School}_{Dept}/report.html`，并同步生成每位教授独立页
4. 告知用户报告路径，可直接在浏览器打开

### 阶段 4: 生成邮件

当用户说 "生成邮件" 时：

1. 读取教授调研报告（research.md）
2. 读取用户个人材料（profiles/）
3. 基于匹配度分析，生成个性化邮件：
   - 标题格式：`Prospective PhD Student - [姓名] - [研究方向]`
   - 正文 200-300 词
   - 提及教授具体研究（引用论文/项目）
   - 突出用户最相关的经历
   - 语气专业真诚
4. 保存为 `~/.outreach/schools/{School}_{Dept}/{Prof_Name}/email_draft.md`
5. 展示邮件草稿供用户审核

## 输出格式规范

### 调研报告格式

```markdown
# {教授姓名} 调研报告

## 1. 基本信息
- 全名：
- 职称：
- 所属实验室：
- 研究方向：
- 联系方式：

## 2. 发表统计
- 总发表论文数：
- h-index：
- 近 5 年发文：
  - 2024: X 篇
  - 2023: X 篇
  - ...
- CCF-A 会议（LLM 方向）：
  - 2024: NeurIPS x2, ICML x1
  - ...
- 代表性论文：
  1. [标题] - [会议/期刊], [年份]
  2. ...

## 3. 学生去向
- 毕业生 A → [公司/学校]
- 毕业生 B → [公司/学校]
- 平均毕业年限：X 年

## 4. 研究组分析
- 组内人数：
- 发文周期：
- 研究氛围：

## 5. 导师风格
- 指导风格：
- 学生评价：

## 6. 匹配度分析
- 研究方向匹配：X/10
- 技能匹配：X/10
- 申请成功率：
- 建议切入点：

## 7. 申请建议
- 是否招生：
- 最佳联系时间：
- 邮件重点：
```

### 邮件格式

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

## 工具脚本

使用 `scripts/pipeline.py` 进行批量处理：

```bash
# 解析材料
python scripts/pipeline.py setup

# 调研教授
python scripts/pipeline.py research --school MIT --dept CS

# 生成报告
python scripts/pipeline.py report --school MIT --dept CS

# 生成邮件
python scripts/pipeline.py email --school MIT --dept CS --all --dry-run

# 全流程
python scripts/pipeline.py full --school MIT --dept CS --dry-run
```

## 注意事项

1. **隐私保护**：用户的 CV、成绩等个人信息仅用于邮件生成，不对外分享
2. **频率控制**：批量调研时每请求间隔 3-5 秒，避免被封
3. **数据准确性**：调研数据来自公开来源，标注信息来源和置信度
4. **缓存利用**：已调研的教授不会重复调研，除非用户要求更新

## 用户交互指令

| 指令 | 说明 |
|------|------|
| "这是我的 CV/材料" | 接收并解析材料 |
| "调研 [学校] [学院]" | 开始调研教授 |
| "调研 [学校] [学院] 的 [方向] 教授" | 调研特定方向教授 |
| "生成报告" | 生成 HTML 可视化报告 |
| "生成邮件" | 生成所有教授的邮件草稿 |
| "给 [教授名] 生成邮件" | 为特定教授生成邮件 |
| "查看 [教授名] 调研" | 查看特定教授调研结果 |
| "配置邮箱" | 配置邮件账户 |
| "发送邮件给 [教授名]" | 发送套磁邮件 |
| "批量发送" | 批量发送邮件 |
| "查看收件箱" | 查看邮件列表 |

## 邮件功能

### 邮箱配置

**首次使用时检查并配置邮箱：**

```bash
# 检查是否已配置
python scripts/email_setup.py --check

# 配置邮箱（支持多种邮箱）
python scripts/email_setup.py --email your_name@gmail.com --password your_password --name "Your Name"

# 使用预设配置
python scripts/email_setup.py --email your_name@stu.pku.edu.cn --password your_password --preset pku

# 测试邮箱连接
python scripts/email_setup.py --test

# 查看当前配置
python scripts/email_setup.py --info
```

**支持的邮箱预设：**
- `pku` - 北京大学邮箱
- `tsinghua` - 清华大学邮箱
- `gmail` - Gmail
- `outlook` - Outlook/Hotmail
- `qq` - QQ邮箱
- `163` - 163邮箱
- `custom` - 自定义服务器

配置保存在 `~/.outreach/email_config.json`，配置一次后永久有效。

### 发送邮件

```python
# 发送单封邮件
python scripts/email_send.py --to professor@university.edu --subject "Subject" --body "Body"

# 试运行
python scripts/email_send.py --to professor@university.edu --subject "Subject" --body "Body" --dry-run

# 批量发送
python scripts/email_batch.py --csv professors.csv --delay 30
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
