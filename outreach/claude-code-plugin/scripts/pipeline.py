#!/usr/bin/env python3
"""
套磁全流程自动化
用法:
  python3 pipeline.py research --school MIT --dept CS
  python3 pipeline.py report --school MIT --dept CS
  python3 pipeline.py email --school MIT --dept CS --prof "Prof. Smith"
  python3 pipeline.py email --school MIT --dept CS --all --dry-run
  python3 pipeline.py full --school MIT --dept CS --dry-run
"""

import argparse
import json
import os
import sys
import re
import subprocess
import time
import csv
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
INBOX = BASE / "inbox"
PROFILES = BASE / "profiles"
SCHOOLS = BASE / "schools"
TEMPLATES = BASE / "templates"
LOGS = BASE / "logs"

def agent(prompt, timeout=180):
    """调用 OpenClaw agent"""
    try:
        r = subprocess.run(
            ["openclaw", "agent", "--to", "self", "--message", prompt],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()
    except:
        return None

def agent_with_file(prompt, file_path, timeout=180):
    """带文件上下文调用 agent"""
    content = Path(file_path).read_text(encoding="utf-8") if Path(file_path).exists() else ""
    full_prompt = f"""## 参考材料
{content}

---

{prompt}"""
    return agent(full_prompt, timeout)

# ============================================================
# 阶段1: 解析用户材料
# ============================================================
def parse_profile():
    """解析 inbox 里的用户材料，生成 profiles/"""
    print("📋 解析个人材料...")
    profile = {}

    for f in sorted(INBOX.glob("*")):
        if f.suffix in (".md", ".txt"):
            profile[f.stem] = f.read_text("utf-8")
        elif f.suffix == ".pdf":
            print(f"  📄 解析 PDF: {f.name}")
            result = agent(f"请提取这个PDF文件的全部文本内容，保留结构：\n\n{f.read_text('utf-8', errors='ignore')}", 60)
            if result:
                profile[f.stem] = result
        elif f.suffix in (".docx", ".doc"):
            print(f"  📝 解析 Word: {f.name}")
            try:
                import docx
                doc = docx.Document(str(f))
                profile[f.stem] = "\n".join(p.text for p in doc.paragraphs)
            except:
                result = agent(f"请提取这个文档的全部文本内容", 60)
                if result:
                    profile[f.stem] = result

    if not profile:
        print("⚠️  inbox/ 目录为空，请先上传你的材料")
        return None

    # 保存到 profiles
    for name, content in profile.items():
        (PROFILES / f"{name}.md").write_text(content, "utf-8")

    print(f"  ✅ 已解析 {len(profile)} 份材料: {', '.join(profile.keys())}")
    return profile

# ============================================================
# 阶段2: 教授调研
# ============================================================
RESEARCH_PROMPT = """你是一个学术调研专家。请对以下教授进行全面深度调研。

## 教授信息
- 姓名: {name}
- 学校: {school}
- 院系: {dept}
- 主页: {homepage}

## 调研任务

请通过 web 搜索和抓取，完成以下调研，以 Markdown 格式输出：

### 1. 基本信息
- 全名、职称、所属实验室/组
- 研究方向（详细列出）
- 联系方式

### 2. 发表统计
- 总发表论文数（Google Scholar 数据）
- h-index, i10-index
- 近5年每年发文数量
- 主要发表会议/期刊（列出 top 5）
- **CCF-A 会议论文数量**（特别是大模型/LLM 方向，按年份列出）
- 代表性论文（最近3-5篇，含标题、会议/期刊、年份）

### 3. 学生去向
- 该教授指导的毕业生去向（业界/学术界）
- 毕业生现在在哪些公司/学校
- 平均毕业年限

### 4. 研究组分析
- 当前组内学生/博后数量
- 组内研究氛围（如果能找到信息）
- 近年发文周期（平均多久发一篇顶会）
- 组内学生发文数量

### 5. 导师风格
- 指导风格（放养/严格/合作型）
- 对学生的要求
- 是否支持学生参加学术会议
- 学生评价（如果有 RateMyProfessor 等信息）

### 6. 匹配度分析
基于以下个人背景，分析与该教授的匹配程度：

{profile_summary}

- 研究方向匹配度（1-10分）
- 技能匹配度（1-10分）
- 申请成功率评估
- 建议的切入点（如何在邮件中突出相关性）

### 7. 申请建议
- 该教授是否在招生（如果能找到信息）
- 最佳联系时间
- 邮件中应重点强调的内容
- 需要避免的事项

请尽可能用具体数据支撑分析。搜索 Google Scholar、OpenReview、个人主页、实验室网站等多个来源。"""

def research_professor(name, school, dept, homepage, profile_summary):
    """调研单个教授"""
    school_dir = SCHOOLS / f"{school}_{dept}"
    prof_dir = school_dir / name.replace(" ", "_")
    prof_dir.mkdir(parents=True, exist_ok=True)

    research_file = prof_dir / "research.md"
    if research_file.exists():
        print(f"  ⏭️  已有调研结果，跳过")
        return research_file

    print(f"  🔍 调研中...")
    prompt = RESEARCH_PROMPT.format(
        name=name, school=school, dept=dept,
        homepage=homepage, profile_summary=profile_summary
    )
    result = agent(prompt, timeout=300)

    if result:
        research_file.write_text(result, "utf-8")
        print(f"  ✅ 调研完成: {research_file}")
    else:
        print(f"  ❌ 调研失败")
    return research_file

def research_school(school, dept, professor_list_csv=None):
    """调研整个学校/学院"""
    print(f"\n{'='*60}")
    print(f"🏫 调研 {school} {dept}")
    print(f"{'='*60}")

    # 加载个人材料
    profile_summary = ""
    for f in PROFILES.glob("*.md"):
        content = f.read_text("utf-8")
        profile_summary += f"\n### {f.stem}\n{content[:1000]}\n"

    if not profile_summary.strip():
        print("⚠️  请先上传个人材料到 inbox/ 目录")
        return

    # 加载教授列表
    if professor_list_csv:
        csv_path = Path(professor_list_csv)
    else:
        csv_path = SCHOOLS / f"{school}_{dept}" / "professors.csv"

    if not csv_path.exists():
        # 自动搜索该学院的教授
        print(f"📋 未找到教授列表，自动搜索 {school} {dept} 教授...")
        professors = discover_professors(school, dept, profile_summary)
    else:
        professors = []
        with open(csv_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                professors.append(row)

    print(f"📊 共 {len(professors)} 位教授\n")

    for i, prof in enumerate(professors, 1):
        print(f"[{i}/{len(professors)}] {prof['name']}")
        research_professor(
            prof["name"], school, dept,
            prof.get("homepage", ""), profile_summary
        )
        time.sleep(5)  # 避免请求过快

def discover_professors(school, dept, profile_summary):
    """自动发现教授"""
    prompt = f"""搜索 {school} 大学 {dept} 学院的教授列表。

请返回 CSV 格式（每行一个教授）：
name,school,email,homepage,department,research_keywords,notes

要求：
1. 列出该学院所有教授（至少10-20位）
2. 优先列出研究方向与以下背景相关的教授：
{profile_summary[:500]}
3. 包含教授的个人主页链接
4. 注明研究方向关键词

只输出 CSV，不要其他内容。"""

    result = agent(prompt, timeout=120)
    if not result:
        return []

    # 解析 CSV
    professors = []
    reader = csv.DictReader(result.strip().split("\n"))
    for row in reader:
        if "name" in row:
            professors.append(row)

    # 保存 CSV
    school_dir = SCHOOLS / f"{school}_{dept}"
    school_dir.mkdir(parents=True, exist_ok=True)
    csv_path = school_dir / "professors.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        if professors:
            writer = csv.DictWriter(f, fieldnames=professors[0].keys())
            writer.writeheader()
            writer.writerows(professors)
    print(f"  💾 教授列表已保存: {csv_path}")

    return professors

# ============================================================
# 阶段3: 生成 HTML 报告
# ============================================================
def generate_html_report(school, dept):
    """为整个学院生成可视化 HTML 报告"""
    school_dir = SCHOOLS / f"{school}_{dept}"
    if not school_dir.exists():
        print(f"❌ 未找到 {school}_{dept} 的调研数据")
        return

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
                    "parsed": parse_research(content)
                })

    if not professors_data:
        print("❌ 没有调研数据")
        return

    assets_dir = school_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    style_file = TEMPLATES / "style.css"
    if style_file.exists():
        (assets_dir / "style.css").write_text(style_file.read_text("utf-8"), "utf-8")

    for professor in professors_data:
        prof_dir = school_dir / professor["dir"]
        prof_report_path = prof_dir / "report.html"
        prof_report_path.write_text(render_professor_report_html(school, dept, professor), "utf-8")

    html = render_index_html(school, dept, professors_data)
    report_path = school_dir / "report.html"
    index_path = school_dir / "index.html"
    report_path.write_text(html, "utf-8")
    index_path.write_text(html, "utf-8")
    print(f"📊 HTML 报告已生成: {report_path}")
    return report_path

def parse_research(content):
    """解析调研 Markdown 为结构化数据"""
    data = {
        "h_index": extract_field(content, r"h-index[:\s]*(\d+)"),
        "total_pubs": extract_field(content, r"(?:总[发发表]*|total)[:\s]*(\d+)"),
        "match_score": extract_field(content, r"(?:匹配度|匹配)[^\d]*(\d+)"),
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

def extract_field(text, pattern):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1) if m else "N/A"

def render_html(school, dept, professors_data):
    """渲染 HTML 报告"""
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
    <div class="tab-content" id="basic">{md_to_html(basic)}</div>
    <div class="tab-content" id="pubs" style="display:none">{md_to_html(pubs)}</div>
    <div class="tab-content" id="students" style="display:none">{md_to_html(students)}</div>
    <div class="tab-content" id="group" style="display:none">{md_to_html(group)}</div>
    <div class="tab-content" id="style" style="display:none">{md_to_html(style)}</div>
    <div class="tab-content" id="match" style="display:none">{md_to_html(match)}</div>
    <div class="tab-content" id="advice" style="display:none">{md_to_html(advice)}</div>
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

def safe_int(value):
    try:
        return int(value)
    except Exception:
        return 0

def get_section(sections, prefix):
    for key, value in sections.items():
        if key.startswith(prefix):
            return value
    return "暂无"

def strip_markdown(text):
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'^[#\-\*\d\.\s]+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def short_text(text, limit=180):
    plain = strip_markdown(text)
    return plain if len(plain) <= limit else plain[:limit].rstrip() + "..."

def render_index_html(school, dept, professors_data):
    cards = []
    ordered = sorted(
        professors_data,
        key=lambda x: (-safe_int(x["parsed"].get("match_score")), -safe_int(x["parsed"].get("h_index")), x["name"])
    )
    for p in ordered:
        parsed = p["parsed"]
        sections = parsed.get("sections", {})
        match_score = parsed.get("match_score", "N/A")
        h_index = parsed.get("h_index", "N/A")
        total_pubs = parsed.get("total_pubs", "N/A")
        summary = short_text(get_section(sections, "6."), 130)
        cards.append(f"""
  <a class="card" href="{p['dir']}/report.html">
    <span class="tag">{school} · {dept}</span>
    <h3>{p['name']}</h3>
    <p>{summary}</p>
    <div class="mini-stats">
      <span>🎯 匹配 {match_score}/10</span>
      <span>📊 h-index {h_index}</span>
      <span>📄 论文 {total_pubs}</span>
    </div>
    <div class="venue">点击进入完整调研报告</div>
  </a>""")

    high_match = sum(1 for p in professors_data if safe_int(p["parsed"].get("match_score")) >= 7)
    high_hindex = sum(1 for p in professors_data if safe_int(p["parsed"].get("h_index")) >= 30)
    html = (TEMPLATES / "index.html").read_text("utf-8")
    return (
        html.replace("{{TOPIC}}", f"{school} {dept}")
        .replace("{{TOPIC_DISPLAY_NAME}}", f"{school} {dept} 教授调研索引")
        .replace("{{TOPIC_SUBTITLE}}", "基于主页、Scholar、OpenReview、学生去向、导师风格与个人背景匹配的自动化套磁调研")
        .replace("{{TOPIC_SUMMARY}}", "先浏览全局卡片，再进入每位教授的独立长文报告。")
        .replace("{{META_LINE}}", f"共 {len(professors_data)} 位教授 · 高匹配 {high_match} 位 · h-index≥30 {high_hindex} 位 · 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        .replace("{{CARDS}}", "\n".join(cards))
    )

def render_professor_report_html(school, dept, professor):
    parsed = professor["parsed"]
    sections = parsed.get("sections", {})
    basic = get_section(sections, "1.")
    pubs = get_section(sections, "2.")
    students = get_section(sections, "3.")
    group = get_section(sections, "4.")
    style = get_section(sections, "5.")
    match = get_section(sections, "6.")
    advice = get_section(sections, "7.")
    match_score = parsed.get("match_score", "N/A")
    h_index = parsed.get("h_index", "N/A")
    total_pubs = parsed.get("total_pubs", "N/A")
    summary = short_text(match if match != "暂无" else advice if advice != "暂无" else basic, 220)

    draft_exists = (SCHOOLS / f"{school}_{dept}" / professor["dir"] / "email_draft.md").exists()
    draft_href = "email_draft.md" if draft_exists else "#"
    draft_cls = "" if draft_exists else "disabled"
    score_class = "good" if safe_int(match_score) >= 7 else "warn" if safe_int(match_score) >= 4 else "bad"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{professor['name']} — 调研报告</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>

<header class="meta-bar">
  <h1>{professor['name']} — 教授调研报告</h1>
  <div class="authors">{school} · {dept} · 自动化套磁调研</div>
  <nav class="meta-links">
    <a href="../report.html">📚 返回学院索引</a>
    <a href="research.md">📝 原始调研 Markdown</a>
    <a href="{draft_href}" class="{draft_cls}">✉️ 邮件草稿</a>
  </nav>
</header>

<nav class="toc-float">
  <strong>目录</strong>
  <ol>
    <li><a href="#speedread">5 分钟速读</a></li>
    <li><a href="#tldr">TL;DR</a></li>
    <li><a href="#basic">基本信息</a></li>
    <li><a href="#pubs">发表统计</a></li>
    <li><a href="#students">学生去向</a></li>
    <li><a href="#group">研究组分析</a></li>
    <li><a href="#style">导师风格</a></li>
    <li><a href="#match">匹配度分析</a></li>
    <li><a href="#advice">申请建议</a></li>
  </ol>
</nav>

<main class="wrap">
  <section id="speedread">
    <div class="callout good">
      <div class="label">⏱️ 如果你只有 5 分钟</div>
      <ul class="list-clean">
        <li><strong>对象：</strong>{professor['name']}，{school} {dept}</li>
        <li><strong>一句话判断：</strong>{summary}</li>
        <li><strong>核心看点：</strong>优先判断方向是否重合、近年产出是否稳定、训练风格是否适合你。</li>
      </ul>
    </div>
    <div class="keynum-row">
      <div class="keynum"><div class="n">{match_score}</div><div class="cap">匹配度 / 10</div></div>
      <div class="keynum"><div class="n">{h_index}</div><div class="cap">Google Scholar h-index</div></div>
      <div class="keynum"><div class="n">{total_pubs}</div><div class="cap">总发文数</div></div>
    </div>
  </section>

  <section id="tldr">
    <div class="tldr">
      <div class="label">TL;DR</div>
      {summary}
    </div>
  </section>

  <section id="basic">
    <h2>1. 基本信息</h2>
    <div class="intuition"><div class="label">先看这部分</div><p>先判断老师所属组、研究主线和基本身份，再决定值不值得深挖后续章节。</p></div>
    {md_to_html(basic)}
    <div class="takeaway">如果这里和你的大方向已经不对齐，通常不建议投入大量时间写深度个性化邮件。</div>
  </section>

  <section id="pubs">
    <h2>2. 发表统计</h2>
    <div class="intuition"><div class="label">怎么看</div><p>不要只看总量，更要看近几年发文节奏、顶会密度，以及大模型相关工作是否持续输出。</p></div>
    {md_to_html(pubs)}
  </section>

  <section id="students">
    <h2>3. 学生去向</h2>
    <div class="bridge">这部分回答的是“跟了这个老师以后，常见出口是什么”。</div>
    {md_to_html(students)}
  </section>

  <section id="group">
    <h2>4. 研究组分析</h2>
    <div class="callout warn"><div class="label">关注点</div>组内规模、协作结构和发文周期，往往直接影响你的日常体验和成长路径。</div>
    {md_to_html(group)}
  </section>

  <section id="style">
    <h2>5. 导师风格</h2>
    <div class="intuition"><div class="label">为什么重要</div><p>同样强的导师，指导方式可能完全不同。和你工作方式匹配，比单纯“名气大”更重要。</p></div>
    {md_to_html(style)}
  </section>

  <section id="match">
    <h2>6. 匹配度分析</h2>
    <div class="callout {score_class}"><div class="label">决策建议</div>当前自动评估匹配度为 <strong>{match_score}/10</strong>。这是后续生成套磁邮件时最该依赖的章节。</div>
    {md_to_html(match)}
  </section>

  <section id="advice">
    <h2>7. 申请建议</h2>
    {md_to_html(advice)}
    <details class="dig"><summary>深入（可跳过）：后续动作建议</summary><p>如果你决定继续联系这位老师，下一步应基于本页“匹配度分析”和“申请建议”生成个性化邮件，再进行人工审核后发送。</p></details>
  </section>
</main>

</body>
</html>"""

def md_to_html(text):
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

# ============================================================
# 阶段4: 生成邮件
# ============================================================
EMAIL_PROMPT = """你是一个学术套磁邮件写作专家。请根据以下调研报告和个人材料，写一封个性化套磁邮件。

## 教授调研报告
{research}

## 我的个人材料
{profile}

## 写作要求
1. 标题格式: Prospective PhD Student - [你的名字] - [具体研究方向]
2. 正文 200-300 词
3. 开头提及教授的具体研究（引用调研报告中的具体论文或项目）
4. 基于匹配度分析，突出最相关的经历
5. 语气专业真诚，不要模板化
6. 结尾询问招生名额

直接输出：
SUBJECT: 邮件标题
BODY:
邮件正文"""

def generate_email(prof_name, school, dept):
    """为单个教授生成邮件"""
    prof_dir = SCHOOLS / f"{school}_{dept}" / prof_name.replace(" ", "_")
    research_file = prof_dir / "research.md"
    if not research_file.exists():
        print(f"❌ 未找到 {prof_name} 的调研数据")
        return None

    # 加载个人材料
    profile = ""
    for f in PROFILES.glob("*.md"):
        profile += f"\n### {f.stem}\n{f.read_text('utf-8')}\n"

    research = research_file.read_text("utf-8")
    prompt = EMAIL_PROMPT.format(research=research, profile=profile)
    result = agent(prompt, timeout=120)

    if not result:
        return None

    # 解析
    subject, body = "", ""
    lines = result.split("\n")
    body_lines = []
    in_body = False
    for line in lines:
        if line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()
        elif line.strip() == "BODY:":
            in_body = True
        elif in_body:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()

    # 保存
    email_file = prof_dir / "email_draft.md"
    email_file.write_text(f"# {subject}\n\n{body}", "utf-8")
    print(f"  📧 邮件草稿已生成: {email_file}")
    return {"subject": subject, "body": body, "file": email_file}

def generate_emails(school, dept, prof_name=None, all_profs=False):
    """批量生成邮件"""
    school_dir = SCHOOLS / f"{school}_{dept}"
    if prof_name:
        return generate_email(prof_name, school, dept)
    elif all_profs:
        results = []
        for prof_dir in sorted(school_dir.iterdir()):
            if prof_dir.is_dir() and (prof_dir / "research.md").exists():
                name = prof_dir.name.replace("_", " ")
                print(f"\n📧 为 {name} 生成邮件...")
                r = generate_email(name, school, dept)
                if r:
                    results.append(r)
                time.sleep(5)
        return results

# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="套磁全流程自动化")
    sub = parser.add_subparsers(dest="command")

    # setup: 解析材料
    sub.add_parser("setup", help="解析 inbox/ 中的个人材料")

    # research: 调研教授
    p_r = sub.add_parser("research", help="调研教授")
    p_r.add_argument("--school", required=True)
    p_r.add_argument("--dept", required=True)
    p_r.add_argument("--csv", help="教授列表CSV（可选，不提供则自动搜索）")

    # report: 生成报告
    p_rp = sub.add_parser("report", help="生成HTML报告")
    p_rp.add_argument("--school", required=True)
    p_rp.add_argument("--dept", required=True)

    # email: 生成邮件
    p_e = sub.add_parser("email", help="生成邮件")
    p_e.add_argument("--school", required=True)
    p_e.add_argument("--dept", required=True)
    p_e.add_argument("--prof", help="指定教授姓名")
    p_e.add_argument("--all", action="store_true", help="所有教授")
    p_e.add_argument("--dry-run", action="store_true")

    # send: 发送邮件
    p_s = sub.add_parser("send", help="发送邮件")
    p_s.add_argument("--school", required=True)
    p_s.add_argument("--dept", required=True)
    p_s.add_argument("--prof", required=True)
    p_s.add_argument("--confirm", action="store_true")

    # full: 全流程
    p_f = sub.add_parser("full", help="全流程: 调研→报告→邮件")
    p_f.add_argument("--school", required=True)
    p_f.add_argument("--dept", required=True)
    p_f.add_argument("--csv", help="教授列表CSV（可选）")
    p_f.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "setup":
        parse_profile()
    elif args.command == "research":
        research_school(args.school, args.dept, args.csv)
    elif args.command == "report":
        generate_html_report(args.school, args.dept)
    elif args.command == "email":
        generate_emails(args.school, args.dept, args.prof, args.all)
    elif args.command == "send":
        # 读取邮件草稿并发送
        prof_dir = SCHOOLS / f"{args.school}_{args.dept}" / args.prof.replace(" ", "_")
        email_file = prof_dir / "email_draft.md"
        if not email_file.exists():
            print("❌ 请先生成邮件草稿")
            return
        content = email_file.read_text("utf-8")
        lines = content.split("\n")
        subject = lines[0].replace("# ", "").strip()
        body = "\n".join(lines[2:]).strip()
        if args.confirm:
            print(f"📧 正在发送...\n标题: {subject}\n")
            r = agent(f"请用 email_send 发送邮件给 {args.prof}，标题: {subject}，正文如下:\n{body}", 60)
            print(r)
        else:
            print(f"⚠️  请加 --confirm 确认发送\n标题: {subject}\n正文:\n{body}")
    elif args.command == "full":
        print("🚀 全流程启动\n")
        parse_profile()
        print()
        research_school(args.school, args.dept, args.csv)
        print()
        generate_html_report(args.school, args.dept)
        print()
        generate_emails(args.school, args.dept, all_profs=True)
        print(f"\n✅ 全流程完成！报告: {SCHOOLS / f'{args.school}_{args.dept}' / 'report.html'}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
