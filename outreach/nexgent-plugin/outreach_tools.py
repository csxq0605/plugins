#!/usr/bin/env python3
"""
Outreach Tools for Nexgent
学术套磁全流程自动化工具集
"""

import os
import json
import csv
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 配置文件放在 ~/.outreach/ (用户级配置)
CONFIG_DIR = Path.home() / ".outreach"

# 任务文件默认放在当前目录/.outreach/ (项目级)
# 可通过 path 参数指定其他位置
DEFAULT_TASK_DIR = Path.cwd() / ".outreach"

def get_task_dir(path=None):
    """获取任务目录，优先使用指定路径，否则用当前目录"""
    if path:
        return Path(path).resolve() / ".outreach"
    return DEFAULT_TASK_DIR

# 这些变量在工具调用时根据 path 参数初始化
OUTREACH_DIR = None
INBOX_DIR = None
PROFILES_DIR = None
SCHOOLS_DIR = None
LOGS_DIR = None
TEMPLATES_DIR = None

def init_dirs(path=None):
    """初始化目录结构"""
    global OUTREACH_DIR, INBOX_DIR, PROFILES_DIR, SCHOOLS_DIR, LOGS_DIR, TEMPLATES_DIR
    OUTREACH_DIR = get_task_dir(path)
    INBOX_DIR = OUTREACH_DIR / "inbox"
    PROFILES_DIR = OUTREACH_DIR / "profiles"
    SCHOOLS_DIR = OUTREACH_DIR / "schools"
    LOGS_DIR = OUTREACH_DIR / "logs"
    TEMPLATES_DIR = OUTREACH_DIR / "templates"
    for d in [INBOX_DIR, PROFILES_DIR, SCHOOLS_DIR, LOGS_DIR, TEMPLATES_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def outreach_parse_materials(file_path: str = None, content: str = None, filename: str = "material", path: str = None) -> Dict[str, Any]:
    """
    解析用户上传的个人材料（CV、研究计划、成绩单等）

    Args:
        file_path: 文件路径（可选）
        content: 文件内容（可选，与file_path二选一）
        filename: 文件名（当使用content时）
        path: 项目根路径，任务文件将存储在 <path>/.outreach/

    Returns:
        解析结果，包含提取的关键信息
    """
    init_dirs(path)

    if file_path:
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {file_path}"}

        if path.suffix in (".md", ".txt"):
            text = path.read_text("utf-8")
        elif path.suffix == ".pdf":
            try:
                import pdfplumber
                with pdfplumber.open(str(path)) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            except ImportError:
                return {"success": False, "error": "需要安装 pdfplumber: pip install pdfplumber"}
        elif path.suffix in (".docx", ".doc"):
            try:
                import docx
                doc = docx.Document(str(path))
                text = "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                return {"success": False, "error": "需要安装 python-docx: pip install python-docx"}
        else:
            return {"success": False, "error": f"不支持的文件格式: {path.suffix}"}

        filename = path.stem
    elif content:
        text = content
    else:
        return {"success": False, "error": "请提供 file_path 或 content"}

    # 保存到 inbox
    inbox_file = INBOX_DIR / f"{filename}.md"
    inbox_file.write_text(text, "utf-8")

    # 提取关键信息
    info = _extract_info(text)

    # 保存到 profiles
    profile_file = PROFILES_DIR / f"{filename}.md"
    profile_content = f"# {filename}\n\n{text}"
    if info:
        profile_content += "\n\n## 提取信息\n\n"
        for key, value in info.items():
            profile_content += f"- **{key}**: {value}\n"
    profile_file.write_text(profile_content, "utf-8")

    return {
        "success": True,
        "filename": filename,
        "inbox_path": str(inbox_file),
        "profile_path": str(profile_file),
        "extracted_info": info,
        "text_length": len(text)
    }


def _extract_info(text: str) -> Dict[str, str]:
    """从文本中提取关键信息"""
    info = {}

    # 邮箱
    email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    if email_match:
        info["邮箱"] = email_match.group()

    # 学校
    school_patterns = [
        r'(?:University|Universität|大学)\s+(?:of\s+)?(\w+)',
        r'(\w+(?:\s+\w+)?)\s+(?:University|Universität|大学)',
    ]
    for pattern in school_patterns:
        school_match = re.search(pattern, text, re.IGNORECASE)
        if school_match:
            info["学校"] = school_match.group(1)
            break

    # GPA
    gpa_match = re.search(r'GPA[:\s]*(\d+\.?\d*)\s*/\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if gpa_match:
        info["GPA"] = f"{gpa_match.group(1)}/{gpa_match.group(2)}"

    # 研究方向
    research_keywords = []
    keywords = ["machine learning", "deep learning", "NLP", "natural language processing",
                 "computer vision", "CV", "AI", "artificial intelligence", "reinforcement learning",
                 "LLM", "large language model", "transformer", "neural network",
                 "机器学习", "深度学习", "自然语言处理", "计算机视觉", "人工智能"]
    for kw in keywords:
        if kw.lower() in text.lower():
            research_keywords.append(kw)
    if research_keywords:
        info["研究方向关键词"] = ", ".join(research_keywords[:5])

    return info


def outreach_list_profiles(path: str = None) -> Dict[str, Any]:
    """
    列出所有已解析的个人材料

    Returns:
        材料列表
    """
    profiles = []
    for f in PROFILES_DIR.glob("*.md"):
        content = f.read_text("utf-8")
        # 提取前200字作为摘要
        summary = content[:200].replace("\n", " ").strip()
        if len(content) > 200:
            summary += "..."
        profiles.append({
            "name": f.stem,
            "path": str(f),
            "size": f.stat().st_size,
            "summary": summary
        })

    return {
        "success": True,
        "count": len(profiles),
        "profiles": profiles
    }


def outreach_research_professor(
    name: str,
    school: str,
    dept: str,
    homepage: str = "",
    email: str = "",
    research_keywords: str = "",
    path: str = None
) -> Dict[str, Any]:
    """
    调研单个教授，生成详细调研报告

    Args:
        name: 教授姓名
        school: 学校名称
        dept: 院系
        homepage: 个人主页URL（可选）
        email: 邮箱（可选）
        path: 项目根路径，任务文件将存储在 <path>/.outreach/
        research_keywords: 研究方向关键词（可选）

    Returns:
        调研结果
    """
    init_dirs(path)

    # 创建目录
    school_dir = SCHOOLS_DIR / f"{school}_{dept}"
    prof_dir = school_dir / name.replace(" ", "_")
    prof_dir.mkdir(parents=True, exist_ok=True)

    research_file = prof_dir / "research.md"

    # 检查是否已有调研结果
    if research_file.exists():
        return {
            "success": True,
            "cached": True,
            "message": "已有调研结果，使用 --force 强制更新",
            "research_path": str(research_file)
        }

    # 加载个人材料
    profile_summary = ""
    for f in PROFILES_DIR.glob("*.md"):
        content = f.read_text("utf-8")
        profile_summary += f"\n### {f.stem}\n{content[:500]}\n"

    # 生成调研报告模板
    report = f"""# {name} 调研报告

## 1. 基本信息
- **全名**: {name}
- **职称**: [待调研]
- **所属实验室**: [待调研]
- **研究方向**: {research_keywords or '[待调研]'}
- **联系方式**: {email or '[待调研]'}
- **个人主页**: {homepage or '[待调研]'}

## 2. 发表统计
- **总发表论文数**: [待调研]
- **h-index**: [待调研]
- **近 5 年发文**:
  - 2024: [待调研]
  - 2023: [待调研]
  - 2022: [待调研]
  - 2021: [待调研]
  - 2020: [待调研]
- **CCF-A 会议（LLM 方向）**: [待调研]
- **代表性论文**:
  1. [待调研]
  2. [待调研]
  3. [待调研]

## 3. 学生去向
- [待调研]
- **平均毕业年限**: [待调研]

## 4. 研究组分析
- **组内人数**: [待调研]
- **发文周期**: [待调研]
- **研究氛围**: [待调研]

## 5. 导师风格
- **指导风格**: [待调研]
- **学生评价**: [待调研]

## 6. 匹配度分析
- **研究方向匹配**: [待评估]
- **技能匹配**: [待评估]
- **申请成功率**: [待评估]
- **建议切入点**: [待评估]

## 7. 申请建议
- **是否招生**: [待调研]
- **最佳联系时间**: [待调研]
- **邮件重点**: [待调研]

---
*调研时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*状态: 模板已生成，需要使用 WebSearch 进行深度调研*
"""

    # 保存调研报告
    research_file.write_text(report, "utf-8")

    # 保存教授信息到CSV
    csv_path = school_dir / "professors.csv"
    professor_info = {
        "name": name,
        "school": school,
        "email": email,
        "homepage": homepage,
        "department": dept,
        "research_keywords": research_keywords,
        "notes": ""
    }

    # 追加到CSV
    file_exists = csv_path.exists()
    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "school", "email", "homepage", "department", "research_keywords", "notes"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(professor_info)

    return {
        "success": True,
        "cached": False,
        "professor": name,
        "school": school,
        "dept": dept,
        "research_path": str(research_file),
        "csv_path": str(csv_path),
        "message": f"调研模板已生成: {research_file}\n请使用 WebSearch 搜索以下内容进行深度调研:\n1. {name} {school} professor homepage\n2. {name} Google Scholar\n3. {name} RateMyProfessor"
    }


def outreach_get_research(school: str, dept: str, professor: str, path: str = None) -> Dict[str, Any]:
    """
    获取教授的调研报告

    Args:
        school: 学校名称
        dept: 院系
        professor: 教授姓名
        path: 项目根路径，任务文件将存储在 <path>/.outreach/

    Returns:
        调研报告内容
    """
    init_dirs(path)

    prof_dir = SCHOOLS_DIR / f"{school}_{dept}" / professor.replace(" ", "_")
    research_file = prof_dir / "research.md"

    if not research_file.exists():
        return {
            "success": False,
            "error": f"未找到 {professor} 的调研报告"
        }

    content = research_file.read_text("utf-8")

    # 检查是否有邮件草稿
    email_file = prof_dir / "email_draft.md"
    email_draft = email_file.read_text("utf-8") if email_file.exists() else None

    return {
        "success": True,
        "professor": professor,
        "school": school,
        "dept": dept,
        "research_path": str(research_file),
        "content": content,
        "has_email_draft": email_draft is not None,
        "email_draft": email_draft
    }


def outreach_generate_report(school: str, dept: str, path: str = None) -> Dict[str, Any]:
    """
    生成HTML可视化报告

    Args:
        school: 学校名称
        dept: 院系
        path: 项目根路径，任务文件将存储在 <path>/.outreach/

    Returns:
        报告生成结果
    """
    init_dirs(path)

    school_dir = SCHOOLS_DIR / f"{school}_{dept}"
    if not school_dir.exists():
        return {
            "success": False,
            "error": f"未找到 {school}_{dept} 的调研数据"
        }

    professors_data = []
    for prof_dir in sorted(school_dir.iterdir()):
        if prof_dir.is_dir() and prof_dir.name != "__pycache__":
            research_file = prof_dir / "research.md"
            if research_file.exists():
                content = research_file.read_text("utf-8")
                professors_data.append({
                    "name": prof_dir.name.replace("_", " "),
                    "dir": prof_dir.name,
                    "content": content,
                    "parsed": _parse_research(content)
                })

    if not professors_data:
        return {
            "success": False,
            "error": "没有调研数据"
        }

    # 生成HTML报告
    html = _render_html(school, dept, professors_data)

    # 保存报告
    report_path = school_dir / "report.html"
    index_path = school_dir / "index.html"
    report_path.write_text(html, "utf-8")
    index_path.write_text(html, "utf-8")

    # 复制样式文件
    assets_dir = school_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    return {
        "success": True,
        "school": school,
        "dept": dept,
        "professor_count": len(professors_data),
        "report_path": str(report_path),
        "index_path": str(index_path),
        "message": f"HTML报告已生成: {report_path}"
    }


def _parse_research(content: str) -> Dict[str, Any]:
    """解析调研Markdown为结构化数据"""
    data = {
        "h_index": _extract_field(content, r"h-index[:\s]*(\d+)"),
        "total_pubs": _extract_field(content, r"(?:总[发发表]*|total)[:\s]*(\d+)"),
        "match_score": _extract_field(content, r"(?:匹配度|匹配)[^\d]*(\d+)"),
        "sections": {}
    }

    # 按 ### 分割章节
    sections = re.split(r'^### ', content, flags=re.MULTILINE)
    for sec in sections[1:]:
        lines = sec.strip().split("\n")
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        data["sections"][title] = body

    return data


def _extract_field(text: str, pattern: str) -> str:
    """提取字段"""
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1) if m else "N/A"


def _render_html(school: str, dept: str, professors_data: List[Dict]) -> str:
    """渲染HTML报告"""
    cards_html = ""
    for p in professors_data:
        parsed = p["parsed"]
        sections = parsed.get("sections", {})

        # 提取各部分内容
        basic = sections.get("1. 基本信息", "暂无")
        pubs = sections.get("2. 发表统计", "暂无")
        students = sections.get("3. 学生去向", "暂无")
        group = sections.get("4. 研究组分析", "暂无")
        style = sections.get("5. 导师风格", "暂无")
        match = sections.get("6. 匹配度分析", "暂无")
        advice = sections.get("7. 申请建议", "暂无")

        match_score = parsed.get("match_score", "N/A")
        h_index = parsed.get("h_index", "N/A")
        total_pubs = parsed.get("total_pubs", "N/A")

        match_color = "#22c55e" if match_score not in ("N/A",) and int(match_score) >= 7 else "#eab308" if match_score not in ("N/A",) and int(match_score) >= 4 else "#ef4444"

        cards_html += f"""
<div class="prof-card" onclick="this.classList.toggle('expanded')">
  <div class="prof-header">
    <div class="prof-name">{p['name']}</div>
    <div class="prof-stats">
      <span class="stat">📊 h-index: <b>{h_index}</b></span>
      <span class="stat">📄 论文: <b>{total_pubs}</b></span>
      <span class="stat" style="color:{match_color}">🎯 匹配: <b>{match_score}/10</b></span>
    </div>
    <div class="expand-hint">点击展开详情 ▼</div>
  </div>
  <div class="prof-body">
    <div class="tabs">
      <button class="tab active" onclick="event.stopPropagation();showTab(this,'basic')">基本信息</button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'pubs')">发表统计</button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'students')">学生去向</button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'group')">研究组</button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'style')">导师风格</button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'match')">匹配度</button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'advice')">申请建议</button>
    </div>
    <div class="tab-content" id="basic">{_md_to_html(basic)}</div>
    <div class="tab-content" id="pubs" style="display:none">{_md_to_html(pubs)}</div>
    <div class="tab-content" id="students" style="display:none">{_md_to_html(students)}</div>
    <div class="tab-content" id="group" style="display:none">{_md_to_html(group)}</div>
    <div class="tab-content" id="style" style="display:none">{_md_to_html(style)}</div>
    <div class="tab-content" id="match" style="display:none">{_md_to_html(match)}</div>
    <div class="tab-content" id="advice" style="display:none">{_md_to_html(advice)}</div>
    <div class="prof-actions">
      <button class="btn btn-draft" onclick="event.stopPropagation();">生成邮件草稿</button>
      <button class="btn btn-send" onclick="event.stopPropagation();">发送邮件</button>
    </div>
  </div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{school} {dept} 教授调研报告</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }}
.header {{ text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; margin-bottom: 30px; border: 1px solid #334155; }}
.header h1 {{ font-size: 2em; color: #f8fafc; margin-bottom: 10px; }}
.header .subtitle {{ color: #94a3b8; font-size: 1.1em; }}
.header .meta {{ color: #64748b; margin-top: 10px; }}
.stats-bar {{ display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-bottom: 30px; }}
.stat-box {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px 30px; text-align: center; min-width: 150px; }}
.stat-box .num {{ font-size: 2em; font-weight: bold; color: #38bdf8; }}
.stat-box .label {{ color: #94a3b8; font-size: 0.9em; margin-top: 5px; }}
.prof-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; margin-bottom: 16px; overflow: hidden; transition: all 0.3s; cursor: pointer; }}
.prof-card:hover {{ border-color: #38bdf8; }}
.prof-header {{ padding: 20px 24px; display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }}
.prof-name {{ font-size: 1.3em; font-weight: 600; color: #f8fafc; min-width: 200px; }}
.prof-stats {{ display: flex; gap: 16px; flex: 1; }}
.stat {{ background: #0f172a; padding: 6px 14px; border-radius: 8px; font-size: 0.9em; color: #94a3b8; }}
.stat b {{ color: #f8fafc; }}
.expand-hint {{ color: #64748b; font-size: 0.85em; }}
.prof-body {{ display: none; padding: 0 24px 24px; }}
.prof-card.expanded .prof-body {{ display: block; }}
.prof-card.expanded .expand-hint {{ display: none; }}
.tabs {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
.tab {{ background: #0f172a; border: 1px solid #334155; color: #94a3b8; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 0.85em; transition: all 0.2s; }}
.tab:hover, .tab.active {{ background: #38bdf8; color: #0f172a; border-color: #38bdf8; }}
.tab-content {{ background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 20px; line-height: 1.8; font-size: 0.95em; }}
.tab-content h1, .tab-content h2, .tab-content h3 {{ color: #38bdf8; margin: 16px 0 8px; }}
.tab-content ul, .tab-content ol {{ padding-left: 20px; }}
.tab-content li {{ margin: 4px 0; }}
.tab-content strong {{ color: #f8fafc; }}
.tab-content code {{ background: #1e293b; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
.tab-content table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
.tab-content th, .tab-content td {{ border: 1px solid #334155; padding: 8px 12px; text-align: left; }}
.tab-content th {{ background: #1e293b; color: #38bdf8; }}
.prof-actions {{ display: flex; gap: 12px; margin-top: 16px; }}
.btn {{ padding: 10px 24px; border-radius: 8px; border: none; cursor: pointer; font-size: 0.9em; font-weight: 500; transition: all 0.2s; }}
.btn-draft {{ background: #334155; color: #e2e8f0; }}
.btn-draft:hover {{ background: #475569; }}
.btn-send {{ background: #38bdf8; color: #0f172a; }}
.btn-send:hover {{ background: #7dd3fc; }}
.filter-bar {{ display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }}
.filter-bar input {{ background: #1e293b; border: 1px solid #334155; color: #e2e8f0; padding: 10px 16px; border-radius: 8px; font-size: 0.95em; flex: 1; min-width: 200px; }}
.filter-bar input:focus {{ outline: none; border-color: #38bdf8; }}
@media (max-width: 768px) {{
  .prof-header {{ flex-direction: column; align-items: flex-start; }}
  .prof-stats {{ flex-wrap: wrap; }}
}}
</style>
</head>
<body>
<div class="header">
  <h1>🎓 {school} {dept} 教授调研报告</h1>
  <div class="subtitle">自动化套磁系统 · 深度调研报告</div>
  <div class="meta">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} · 共 {len(professors_data)} 位教授</div>
</div>

<div class="stats-bar">
  <div class="stat-box"><div class="num">{len(professors_data)}</div><div class="label">调研教授</div></div>
  <div class="stat-box"><div class="num">{sum(1 for p in professors_data if p['parsed'].get('match_score','0') not in ('N/A','0') and int(p['parsed']['match_score'])>=7)}</div><div class="label">高匹配 (≥7)</div></div>
  <div class="stat-box"><div class="num">{sum(1 for p in professors_data if p['parsed'].get('h_index','0') not in ('N/A','0') and int(p['parsed']['h_index'])>=30)}</div><div class="label">h-index≥30</div></div>
</div>

<div class="filter-bar">
  <input type="text" placeholder="🔍 搜索教授姓名、研究方向..." oninput="filterCards(this.value)">
  <select onchange="sortBy(this.value)" style="background:#1e293b;border:1px solid #334155;color:#e2e8f0;padding:10px 16px;border-radius:8px;">
    <option value="match">按匹配度排序</option>
    <option value="hindex">按h-index排序</option>
    <option value="name">按姓名排序</option>
  </select>
</div>

<div id="cards">{cards_html}</div>

<script>
function showTab(btn, tabId) {{
  const card = btn.closest('.prof-card');
  card.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  card.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
  card.querySelector('#'+tabId).style.display = 'block';
}}

function filterCards(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('.prof-card').forEach(card => {{
    card.style.display = card.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}

function sortBy(key) {{
  const container = document.getElementById('cards');
  const cards = [...container.querySelectorAll('.prof-card')];
  cards.sort((a, b) => {{
    if (key === 'name') return a.querySelector('.prof-name').textContent.localeCompare(b.querySelector('.prof-name').textContent);
    const getVal = (card) => {{
      const stats = card.querySelector('.prof-stats').textContent;
      const m = key === 'match' ? stats.match(/匹配:\\s*(\\d+)/) : stats.match(/h-index:\\s*(\\d+)/);
      return m ? parseInt(m[1]) : 0;
    }};
    return getVal(b) - getVal(a);
  }});
  cards.forEach(c => container.appendChild(c));
}}
</script>
</body>
</html>"""


def _md_to_html(text: str) -> str:
    """简单 Markdown → HTML"""
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', text, flags=re.MULTILINE)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', text)
    text = text.replace("\n\n", "</p><p>")
    text = f"<p>{text}</p>"
    text = text.replace("<p></p>", "")
    return text


def outreach_generate_email(
    school: str,
    dept: str,
    professor: str,
    profile_name: str = None,
    path: str = None
) -> Dict[str, Any]:
    """
    为教授生成个性化套磁邮件

    Args:
        school: 学校名称
        dept: 院系
        professor: 教授姓名
        profile_name: 个人材料名称（可选，默认使用第一个）
        path: 项目根路径，任务文件将存储在 <path>/.outreach/

    Returns:
        邮件生成结果
    """
    init_dirs(path)

    prof_dir = SCHOOLS_DIR / f"{school}_{dept}" / professor.replace(" ", "_")
    research_file = prof_dir / "research.md"

    if not research_file.exists():
        return {
            "success": False,
            "error": f"未找到 {professor} 的调研报告，请先进行调研"
        }

    # 加载个人材料
    profile_content = ""
    if profile_name:
        profile_file = PROFILES_DIR / f"{profile_name}.md"
        if profile_file.exists():
            profile_content = profile_file.read_text("utf-8")
    else:
        # 使用第一个找到的材料
        for f in PROFILES_DIR.glob("*.md"):
            profile_content = f.read_text("utf-8")
            break

    if not profile_content:
        return {
            "success": False,
            "error": "未找到个人材料，请先上传CV/研究计划"
        }

    # 读取调研报告
    research = research_file.read_text("utf-8")

    # 生成邮件模板
    email_template = f"""SUBJECT: Prospective PhD Student - [你的姓名] - [研究方向]

Dear Professor {professor},

[第一段：提及教授的具体研究，说明为什么感兴趣]
I am writing to express my strong interest in your research on [具体研究方向/论文].
Your work on [具体项目/论文名] particularly caught my attention because [原因].

[第二段：介绍你的相关经历和技能]
I am currently a [学位] student at [学校], majoring in [专业].
My research experience includes [相关经历], where I [具体成果].
I have also [其他相关技能或经历].

[第三段：说明研究计划如何与教授方向契合]
I believe my background in [你的研究方向] aligns well with your current work on [教授方向].
Specifically, I am interested in exploring [具体研究想法] which could contribute to [教授的研究项目].

[第四段：询问招生名额，表达期待]
I would be grateful to know if you have any openings for PhD students in your group.
I have attached my CV and research statement for your reference.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
[你的姓名]
[你的学校/专业]
[你的邮箱]
"""

    # 保存邮件草稿
    email_file = prof_dir / "email_draft.md"
    email_file.write_text(email_template, "utf-8")

    return {
        "success": True,
        "professor": professor,
        "school": school,
        "dept": dept,
        "email_path": str(email_file),
        "template": email_template,
        "message": f"邮件模板已生成: {email_file}\n请根据以下调研报告个性化修改:\n{research[:500]}..."
    }


def outreach_list_professors(school: str = None, dept: str = None, path: str = None) -> Dict[str, Any]:
    """
    列出已调研的教授

    Args:
        school: 学校名称（可选）
        dept: 院系（可选）
        path: 项目根路径，任务文件将存储在 <path>/.outreach/

    Returns:
        教授列表
    """
    init_dirs(path)

    professors = []

    if school and dept:
        school_dir = SCHOOLS_DIR / f"{school}_{dept}"
        if school_dir.exists():
            for prof_dir in sorted(school_dir.iterdir()):
                if prof_dir.is_dir() and prof_dir.name != "__pycache__":
                    research_file = prof_dir / "research.md"
                    email_file = prof_dir / "email_draft.md"
                    professors.append({
                        "name": prof_dir.name.replace("_", " "),
                        "school": school,
                        "dept": dept,
                        "has_research": research_file.exists(),
                        "has_email": email_file.exists(),
                        "research_path": str(research_file) if research_file.exists() else None,
                        "email_path": str(email_file) if email_file.exists() else None
                    })
    else:
        # 列出所有学校
        for school_dir in sorted(SCHOOLS_DIR.iterdir()):
            if school_dir.is_dir():
                parts = school_dir.name.split("_", 1)
                if len(parts) == 2:
                    s, d = parts
                    for prof_dir in sorted(school_dir.iterdir()):
                        if prof_dir.is_dir() and prof_dir.name != "__pycache__":
                            research_file = prof_dir / "research.md"
                            email_file = prof_dir / "email_draft.md"
                            professors.append({
                                "name": prof_dir.name.replace("_", " "),
                                "school": s,
                                "dept": d,
                                "has_research": research_file.exists(),
                                "has_email": email_file.exists(),
                                "research_path": str(research_file) if research_file.exists() else None,
                                "email_path": str(email_file) if email_file.exists() else None
                            })

    return {
        "success": True,
        "count": len(professors),
        "professors": professors
    }
