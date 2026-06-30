# 🎓 Outreach Plugin — 使用示例

## ⚠️ 首次使用必读

**使用此插件前，必须先配置邮箱。插件会在用户首次使用时主动询问并引导配置。**

## Codex 使用示例

### 示例 1：首次使用完整流程

```text
# 1. 配置邮箱（首次使用必须）
用 outreach 配置邮箱

# 2. 上传你的CV
用 outreach 解析我的 CV，并帮我调研 MIT CS 的教授

# 3. 查看已解析的材料
用 outreach 查看我的材料

# 4. 调研特定方向的教授
用 outreach 调研 MIT CS 的 AI 方向教授

# 5. 生成报告
用 outreach 生成报告 MIT CS

# 6. 为所有教授生成邮件
用 outreach 生成邮件 MIT CS

# 7. 发送邮件
用 outreach 发送邮件给 MIT CS Kaiming_He
```

## Claude Code 使用示例

### 示例 1：首次使用完整流程

```bash
# 1. 配置邮箱（首次使用必须）
/outreach "配置邮箱"

# 2. 上传你的CV
/outreach "这是我的CV，请帮我调研MIT CS的教授"

# 3. 查看已解析的材料
/outreach "查看我的材料"

# 4. 调研特定方向的教授
/outreach "调研 MIT CS 的 AI 方向教授"

# 5. 生成报告
/outreach "生成报告 MIT CS"

# 6. 为所有教授生成邮件
/outreach "生成邮件 MIT CS"

# 7. 发送邮件
/outreach "发送邮件给 MIT CS Kaiming_He"
```

### 示例 2：使用CSV文件

```bash
# 1. 准备CSV文件（格式：name,school,email,homepage,department,research_keywords,notes）
# 2. 使用CSV调研
/outreach "调研 MIT CS --csv professors.csv"

# 3. 生成报告
/outreach "生成报告 MIT CS"
```

### 示例 3：批量处理

```bash
# 1. 调研多个学校
/outreach "调研 MIT CS"
/outreach "调研 Stanford CS"
/outreach "调研 CMU CS"

# 2. 生成所有学校的报告
/outreach "生成报告 MIT CS"
/outreach "生成报告 Stanford CS"
/outreach "生成报告 CMU CS"
```

## Nexgent 使用示例

### 示例 1：首次使用完整流程

```python
# 1. 配置邮箱（首次使用必须）
email_setup(
    email_addr="your_name@stu.pku.edu.cn",
    password="your_password",
    name="Your Name"
)

# 2. 解析CV
result = outreach_parse_materials(file_path="~/Documents/cv.pdf")
print(result)

# 3. 查看已解析材料
profiles = outreach_list_profiles()
print(profiles)

# 4. 调研教授
result = outreach_research_professor(
    name="Kaiming He",
    school="MIT",
    dept="CS",
    homepage="https://kaiminghe.com/",
    email="kaiminghe@mit.edu",
    research_keywords="computer vision, deep learning, ResNet"
)
print(result)

# 5. 获取调研报告
research = outreach_get_research(
    school="MIT",
    dept="CS",
    professor="Kaiming He"
)
print(research)

# 6. 生成HTML报告
report = outreach_generate_report(school="MIT", dept="CS")
print(report)

# 7. 生成邮件
email = outreach_generate_email(
    school="MIT",
    dept="CS",
    professor="Kaiming He"
)
print(email)

# 8. 发送邮件
email_send(
    to="kaiminghe@mit.edu",
    subject="Prospective PhD Student - Your Name - Computer Vision",
    body="[从email_draft.md复制的内容]"
)
```

### 示例 2：批量调研

```python
# 教授列表
professors = [
    {"name": "Kaiming He", "school": "MIT", "dept": "CS",
     "homepage": "https://kaiminghe.com/", "research_keywords": "computer vision"},
    {"name": "Yann LeCun", "school": "NYU", "dept": "CS",
     "homepage": "https://yann.lecun.com/", "research_keywords": "deep learning"},
    {"name": "Geoffrey Hinton", "school": "Toronto", "dept": "CS",
     "homepage": "https://www.cs.toronto.edu/~hinton/", "research_keywords": "neural networks"}
]

# 批量调研
for prof in professors:
    result = outreach_research_professor(**prof)
    print(f"✅ {prof['name']}: {result['success']}")

# 生成所有报告
for school_dept in ["MIT_CS", "NYU_CS", "Toronto_CS"]:
    school, dept = school_dept.split("_")
    report = outreach_generate_report(school=school, dept=dept)
    print(f"✅ {school_dept}: {report['professor_count']} professors")
```

### 示例 3：使用 WebSearch 深度调研

```python
# 1. 先创建调研模板
result = outreach_research_professor(
    name="Fei-Fei Li",
    school="Stanford",
    dept="CS",
    homepage="https://profiles.stanford.edu/fei-fei-li",
    research_keywords="computer vision, ImageNet, AI"
)

# 2. 使用 WebSearch 搜索详细信息
# 在对话中使用 WebSearch 工具：
# WebSearch("Fei-Fei Li Stanford professor homepage")
# WebSearch("Fei-Fei Li Google Scholar")
# WebSearch("Fei-Fei Li RateMyProfessor")
# WebSearch("Fei-Fei Li research group students")

# 3. 将搜索结果更新到调研报告
# 使用 Edit 工具更新 ~/.outreach/schools/Stanford_CS/Fei-Fei_Li/research.md

# 4. 生成报告和邮件
report = outreach_generate_report(school="Stanford", dept="CS")
email = outreach_generate_email(school="Stanford", dept="CS", professor="Fei-Fei Li")
```

## CSV 文件格式

教授列表CSV文件格式：

```csv
name,school,email,homepage,department,research_keywords,notes
Kaiming He,MIT,kaiminghe@mit.edu,https://kaiminghe.com/,CS,"computer vision, deep learning, ResNet",CV方向大牛
Yann LeCun,NYU,yann@cs.nyu.edu,https://yann.lecun.com/,CS,"deep learning, self-supervised learning",图灵奖得主
Geoffrey Hinton,Toronto,geoffrey.hinton@gmail.com,https://www.cs.toronto.edu/~hinton/,CS,"neural networks, deep learning",深度学习之父
```

## 调研报告示例

```markdown
# Kaiming He 调研报告

## 1. 基本信息
- **全名**: Kaiming He
- **职称**: Professor
- **所属实验室**: MIT CSAIL
- **研究方向**: Computer Vision, Deep Learning, Self-supervised Learning
- **联系方式**: kaiminghe@mit.edu
- **个人主页**: https://kaiminghe.com/

## 2. 发表统计
- **总发表论文数**: 200+
- **h-index**: 150+
- **近 5 年发文**:
  - 2024: 15 篇
  - 2023: 20 篇
  - 2022: 18 篇
  - 2021: 12 篇
  - 2020: 10 篇
- **CCF-A 会议（LLM 方向）**:
  - 2024: CVPR x3, NeurIPS x2, ICCV x2
  - 2023: CVPR x4, NeurIPS x3, ICML x2
- **代表性论文**:
  1. Deep Residual Learning for Image Recognition - CVPR, 2016
  2. Masked Autoencoders Are Scalable Vision Learners - CVPR, 2022
  3. Exploring Simple Siamese Representation Learning - CVPR, 2021

## 3. 学生去向
- 毕业生 A → Google Research
- 毕业生 B → Meta AI
- 毕业生 C → Stanford Professor
- **平均毕业年限**: 5 年

## 4. 研究组分析
- **组内人数**: 15-20 人
- **发文周期**: 每年 3-5 篇顶会
- **研究氛围**: 合作型，鼓励探索新方向

## 5. 导师风格
- **指导风格**: 合作型，给予学生自由度
- **学生评价**: 非常支持学生发展，经常一对一讨论

## 6. 匹配度分析
- **研究方向匹配**: 8/10
- **技能匹配**: 7/10
- **申请成功率**: 中等
- **建议切入点**: 强调计算机视觉和深度学习经验

## 7. 申请建议
- **是否招生**: 是，每年招收 2-3 名 PhD
- **最佳联系时间**: 9-11月（申请季前）
- **邮件重点**: 突出计算机视觉项目经验，提及对自监督学习的兴趣
```

## 邮件示例

```
SUBJECT: Prospective PhD Student - John Doe - Computer Vision

Dear Professor He,

I am writing to express my strong interest in your research on self-supervised learning and computer vision. Your work on Masked Autoencoders (MAE) particularly caught my attention because it demonstrates how simple yet effective pre-training strategies can learn powerful visual representations.

I am currently a Master's student at Peking University, majoring in Computer Science. My research experience includes developing novel object detection algorithms using transformers, where I achieved state-of-the-art results on COCO dataset. I have also published two papers at CVPR 2024 on visual representation learning.

I believe my background in computer vision and deep learning aligns well with your current work on self-supervised learning. Specifically, I am interested in exploring how masked image modeling can be extended to video understanding and 3D vision, which could contribute to your group's research on scalable visual learning.

I would be grateful to know if you have any openings for PhD students in your group for Fall 2025. I have attached my CV and research statement for your reference.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
John Doe
Computer Science, Peking University
john@example.com
```

## 常见问题

### Q: 如何更新已调研的教授信息？
A: 删除对应的调研文件，重新运行调研命令：
```bash
rm ~/.outreach/schools/MIT_CS/Kaiming_He/research.md
/outreach "调研 MIT CS --prof Kaiming He"
```

### Q: 如何查看生成的HTML报告？
A: 报告文件在 `~/.outreach/schools/{School}_{Dept}/report.html`，直接用浏览器打开即可。

### Q: 如何自定义邮件模板？
A: 编辑生成的邮件草稿文件 `~/.outreach/schools/{School}_{Dept}/{Prof}/email_draft.md`

### Q: 调研结果不准确怎么办？
A: 手动编辑调研报告文件，补充或修正信息。调研报告是Markdown格式，易于编辑。
