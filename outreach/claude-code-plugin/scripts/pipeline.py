#!/usr/bin/env python3
"""

:
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

# 配置文件放在 ~/.outreach/ (用户级配置)
CONFIG_DIR = Path.home() / ".outreach"

# 任务文件默认放在当前目录/.outreach/ (项目级)
# 可通过 --path 参数指定其他位置
DEFAULT_TASK_DIR = Path.cwd() / ".outreach"

def get_task_dir(path=None):
    """获取任务目录，优先使用指定路径，否则用当前目录"""
    if path:
        return Path(path).resolve() / ".outreach"
    return DEFAULT_TASK_DIR

# 这些变量在 main() 中根据 --path 参数初始化
BASE = None
INBOX = None
PROFILES = None
SCHOOLS = None
LOGS = None

TEMPLATES = Path(__file__).parent.parent / "templates"

def agent(prompt, timeout=180):
    """ OpenClaw agent"""
    try:
        r = subprocess.run(
            ["openclaw", "agent", "--to", "self", "--message", prompt],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()
    except:
        return None

def agent_with_file(prompt, file_path, timeout=180):
    """ agent"""
    content = Path(file_path).read_text(encoding="utf-8") if Path(file_path).exists() else ""
    full_prompt = f"""## 
{content}

---

{prompt}"""
    return agent(full_prompt, timeout)

# ============================================================
# 1: 
# ============================================================
def parse_profile():
    """ inbox Generate profiles/"""
    print("[LIST] Personal materials...")
    profile = {}

    for f in sorted(INBOX.glob("*")):
        if f.suffix in (".md", ".txt"):
            profile[f.stem] = f.read_text("utf-8")
        elif f.suffix == ".pdf":
            print(f"  [DOC]  PDF: {f.name}")
            result = agent(f"PDF\n\n{f.read_text('utf-8', errors='ignore')}", 60)
            if result:
                profile[f.stem] = result
        elif f.suffix in (".docx", ".doc"):
            print(f"  [NOTE]  Word: {f.name}")
            try:
                import docx
                doc = docx.Document(str(f))
                profile[f.stem] = "\n".join(p.text for p in doc.paragraphs)
            except:
                result = agent(f"", 60)
                if result:
                    profile[f.stem] = result

    if not profile:
        print("[WARN]  inbox/ Directory is emptyPlease upload first")
        return None

    #  profiles
    for name, content in profile.items():
        (PROFILES / f"{name}.md").write_text(content, "utf-8")

    print(f"  [OK] Parsed {len(profile)} materials: {', '.join(profile.keys())}")
    return profile

# ============================================================
# 2: ProfessorResearch
# ============================================================
RESEARCH_PROMPT = """ResearchProfessorResearch

## Professor
- : {name}
- School: {school}
- : {dept}
- : {homepage}

## Research

 web SearchCompletedResearch Markdown 

### 1. 
- /
- 
- 

### 2. 
- Google Scholar 
- h-index, i10-index
- 5
- / top 5
- **CCF-A **/LLM 
- 3-5/

### 3. 
- Professor/
- /School
- 

### 4. 
- /
- 
- 
- 

### 5. 
- //
- 
- 
-  RateMyProfessor 

### 6. 
Professor

{profile_summary}

- 1-10
- 1-10
- Success
- Email

### 7. 
- Professor
- 
- Email
- 

Search Google ScholarOpenReview"""

def research_professor(name, school, dept, homepage, profile_summary):
    """ResearchProfessor"""
    school_dir = SCHOOLS / f"{school}_{dept}"
    prof_dir = school_dir / name.replace(" ", "_")
    prof_dir.mkdir(parents=True, exist_ok=True)

    research_file = prof_dir / "research.md"
    if research_file.exists():
        print(f"  [SKIP]  ResearchSkip")
        return research_file

    print(f"  [SEARCH] Research...")
    prompt = RESEARCH_PROMPT.format(
        name=name, school=school, dept=dept,
        homepage=homepage, profile_summary=profile_summary
    )
    result = agent(prompt, timeout=300)

    if result:
        research_file.write_text(result, "utf-8")
        print(f"  [OK] ResearchCompleted: {research_file}")
    else:
        print(f"  [FAIL] ResearchFailed")
    return research_file

def research_school(school, dept, professor_list_csv=None):
    """ResearchSchool/Department"""
    print(f"\n{'='*60}")
    print(f"[SCHOOL] Research {school} {dept}")
    print(f"{'='*60}")

    # LoadPersonal materials
    profile_summary = ""
    for f in PROFILES.glob("*.md"):
        content = f.read_text("utf-8")
        profile_summary += f"\n### {f.stem}\n{content[:1000]}\n"

    if not profile_summary.strip():
        print("[WARN]  Please upload firstPersonal materials inbox/ ")
        return

    # LoadProfessor
    if professor_list_csv:
        csv_path = Path(professor_list_csv)
    else:
        csv_path = SCHOOLS / f"{school}_{dept}" / "professors.csv"

    if not csv_path.exists():
        # SearchDepartmentProfessor
        print(f"[LIST] Not foundProfessorSearch {school} {dept} Professor...")
        professors = discover_professors(school, dept, profile_summary)
    else:
        professors = []
        with open(csv_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                professors.append(row)

    print(f"[STATS] Total {len(professors)} Professor\n")

    for i, prof in enumerate(professors, 1):
        print(f"[{i}/{len(professors)}] {prof['name']}")
        research_professor(
            prof["name"], school, dept,
            prof.get("homepage", ""), profile_summary
        )
        time.sleep(5)  # 

def discover_professors(school, dept, profile_summary):
    """Professor"""
    prompt = f"""Search {school}  {dept} DepartmentProfessor

 CSV Professor
name,school,email,homepage,department,research_keywords,notes


1. DepartmentProfessor10-20
2. Professor
{profile_summary[:500]}
3. Professor
4. 

 CSV"""

    result = agent(prompt, timeout=120)
    if not result:
        return []

    #  CSV
    professors = []
    reader = csv.DictReader(result.strip().split("\n"))
    for row in reader:
        if "name" in row:
            professors.append(row)

    #  CSV
    school_dir = SCHOOLS / f"{school}_{dept}"
    school_dir.mkdir(parents=True, exist_ok=True)
    csv_path = school_dir / "professors.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        if professors:
            writer = csv.DictWriter(f, fieldnames=professors[0].keys())
            writer.writeheader()
            writer.writerows(professors)
    print(f"  [SAVE] Professor: {csv_path}")

    return professors

# ============================================================
# 3: Generate HTML Report
# ============================================================
def generate_html_report(school, dept):
    """DepartmentGenerate HTML Report"""
    school_dir = SCHOOLS / f"{school}_{dept}"
    if not school_dir.exists():
        print(f"[FAIL] Not found {school}_{dept} Research")
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
        print("[FAIL] Research")
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
    print(f"[STATS] HTML ReportGenerate: {report_path}")
    return report_path

def parse_research(content):
    """Research Markdown """
    data = {
        "h_index": extract_field(content, r"h-index[:\s]*(\d+)"),
        "total_pubs": extract_field(content, r"(?:total|Total)[:\s]*(\d+)"),
        "match_score": extract_field(content, r"(?:match|Match)[^\d]*(\d+)"),
        "sections": {}
    }

    #  ### 
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
    """ HTML Report"""
    cards_html = ""
    for p in professors_data:
        parsed = p["parsed"]
        sections = parsed.get("sections", {})

        # 
        basic = sections.get("1. ", "")
        pubs = sections.get("2. ", "")
        students = sections.get("3. ", "")
        group = sections.get("4. ", "")
        style = sections.get("5. ", "")
        match = sections.get("6. ", "")
        advice = sections.get("7. ", "")

        match_score = parsed.get("match_score", "N/A")
        h_index = parsed.get("h_index", "N/A")
        total_pubs = parsed.get("total_pubs", "N/A")

        match_color = "#22c55e" if match_score not in ("N/A",) and int(match_score) >= 7 else "#eab308" if match_score not in ("N/A",) and int(match_score) >= 4 else "#ef4444"

        cards_html += f"""
<div class="prof-card" onclick="this.classList.toggle('expanded')">
  <div class="prof-header">
    <div class="prof-name">{p['name']}</div>
    <div class="prof-stats">
      <span class="stat">[STATS] h-index: <b>{h_index}</b></span>
      <span class="stat">[DOC] : <b>{total_pubs}</b></span>
      <span class="stat" style="color:{match_color}"> : <b>{match_score}/10</b></span>
    </div>
    <div class="expand-hint"> </div>
  </div>
  <div class="prof-body">
    <div class="tabs">
      <button class="tab active" onclick="event.stopPropagation();showTab(this,'basic')"></button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'pubs')"></button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'students')"></button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'group')"></button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'style')"></button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'match')"></button>
      <button class="tab" onclick="event.stopPropagation();showTab(this,'advice')"></button>
    </div>
    <div class="tab-content" id="basic">{md_to_html(basic)}</div>
    <div class="tab-content" id="pubs" style="display:none">{md_to_html(pubs)}</div>
    <div class="tab-content" id="students" style="display:none">{md_to_html(students)}</div>
    <div class="tab-content" id="group" style="display:none">{md_to_html(group)}</div>
    <div class="tab-content" id="style" style="display:none">{md_to_html(style)}</div>
    <div class="tab-content" id="match" style="display:none">{md_to_html(match)}</div>
    <div class="tab-content" id="advice" style="display:none">{md_to_html(advice)}</div>
    <div class="prof-actions">
      <button class="btn btn-draft" onclick="event.stopPropagation();">GenerateEmailDraft</button>
      <button class="btn btn-send" onclick="event.stopPropagation();">SendEmail</button>
    </div>
  </div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{school} {dept} ProfessorResearchReport</title>
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
  <h1> {school} {dept} ProfessorResearchReport</h1>
  <div class="subtitle">  ResearchReport</div>
  <div class="meta">Generate: {datetime.now().strftime('%Y-%m-%d %H:%M')}  Total {len(professors_data)} Professor</div>
</div>

<div class="stats-bar">
  <div class="stat-box"><div class="num">{len(professors_data)}</div><div class="label">ResearchProfessor</div></div>
  <div class="stat-box"><div class="num">{sum(1 for p in professors_data if p['parsed'].get('match_score','0') not in ('N/A','0') and int(p['parsed']['match_score'])>=7)}</div><div class="label"> (7)</div></div>
  <div class="stat-box"><div class="num">{sum(1 for p in professors_data if p['parsed'].get('h_index','0') not in ('N/A','0') and int(p['parsed']['h_index'])>=30)}</div><div class="label">h-index30</div></div>
</div>

<div class="filter-bar">
  <input type="text" placeholder="[SEARCH] SearchProfessor..." oninput="filterCards(this.value)">
  <select onchange="sortBy(this.value)" style="background:#1e293b;border:1px solid #334155;color:#e2e8f0;padding:10px 16px;border-radius:8px;">
    <option value="match"></option>
    <option value="hindex">h-index</option>
    <option value="name"></option>
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
      const m = key === 'match' ? stats.match(/:\\s*(\\d+)/) : stats.match(/h-index:\\s*(\\d+)/);
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
    return ""

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
    <span class="tag">{school}  {dept}</span>
    <h3>{p['name']}</h3>
    <p>{summary}</p>
    <div class="mini-stats">
      <span>  {match_score}/10</span>
      <span>[STATS] h-index {h_index}</span>
      <span>[DOC]  {total_pubs}</span>
    </div>
    <div class="venue">ResearchReport</div>
  </a>""")

    high_match = sum(1 for p in professors_data if safe_int(p["parsed"].get("match_score")) >= 7)
    high_hindex = sum(1 for p in professors_data if safe_int(p["parsed"].get("h_index")) >= 30)
    html = (TEMPLATES / "index.html").read_text("utf-8")
    return (
        html.replace("{{TOPIC}}", f"{school} {dept}")
        .replace("{{TOPIC_DISPLAY_NAME}}", f"{school} {dept} ProfessorResearch")
        .replace("{{TOPIC_SUBTITLE}}", "ScholarOpenReviewResearch")
        .replace("{{TOPIC_SUMMARY}}", "ProfessorReport")
        .replace("{{META_LINE}}", f"Total {len(professors_data)} Professor   {high_match}   h-index30 {high_hindex}   Generate {datetime.now().strftime('%Y-%m-%d %H:%M')}")
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
    summary = short_text(match if match != "" else advice if advice != "" else basic, 220)

    draft_exists = (SCHOOLS / f"{school}_{dept}" / professor["dir"] / "email_draft.md").exists()
    draft_href = "email_draft.md" if draft_exists else "#"
    draft_cls = "" if draft_exists else "disabled"
    score_class = "good" if safe_int(match_score) >= 7 else "warn" if safe_int(match_score) >= 4 else "bad"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{professor['name']}  ResearchReport</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>

<header class="meta-bar">
  <h1>{professor['name']}  ProfessorResearchReport</h1>
  <div class="authors">{school}  {dept}  Research</div>
  <nav class="meta-links">
    <a href="../report.html"> Department</a>
    <a href="research.md">[NOTE] Research Markdown</a>
    <a href="{draft_href}" class="{draft_cls}"> EmailDraft</a>
  </nav>
</header>

<nav class="toc-float">
  <strong></strong>
  <ol>
    <li><a href="#speedread">5 </a></li>
    <li><a href="#tldr">TL;DR</a></li>
    <li><a href="#basic"></a></li>
    <li><a href="#pubs"></a></li>
    <li><a href="#students"></a></li>
    <li><a href="#group"></a></li>
    <li><a href="#style"></a></li>
    <li><a href="#match"></a></li>
    <li><a href="#advice"></a></li>
  </ol>
</nav>

<main class="wrap">
  <section id="speedread">
    <div class="callout good">
      <div class="label">  5 </div>
      <ul class="list-clean">
        <li><strong></strong>{professor['name']}{school} {dept}</li>
        <li><strong></strong>{summary}</li>
        <li><strong></strong></li>
      </ul>
    </div>
    <div class="keynum-row">
      <div class="keynum"><div class="n">{match_score}</div><div class="cap"> / 10</div></div>
      <div class="keynum"><div class="n">{h_index}</div><div class="cap">Google Scholar h-index</div></div>
      <div class="keynum"><div class="n">{total_pubs}</div><div class="cap"></div></div>
    </div>
  </section>

  <section id="tldr">
    <div class="tldr">
      <div class="label">TL;DR</div>
      {summary}
    </div>
  </section>

  <section id="basic">
    <h2>1. </h2>
    <div class="intuition"><div class="label"></div><p></p></div>
    {md_to_html(basic)}
    <div class="takeaway">Email</div>
  </section>

  <section id="pubs">
    <h2>2. </h2>
    <div class="intuition"><div class="label"></div><p></p></div>
    {md_to_html(pubs)}
  </section>

  <section id="students">
    <h2>3. </h2>
    <div class="bridge"></div>
    {md_to_html(students)}
  </section>

  <section id="group">
    <h2>4. </h2>
    <div class="callout warn"><div class="label"></div></div>
    {md_to_html(group)}
  </section>

  <section id="style">
    <h2>5. </h2>
    <div class="intuition"><div class="label"></div><p></p></div>
    {md_to_html(style)}
  </section>

  <section id="match">
    <h2>6. </h2>
    <div class="callout {score_class}"><div class="label"></div> <strong>{match_score}/10</strong>GenerateEmail</div>
    {md_to_html(match)}
  </section>

  <section id="advice">
    <h2>7. </h2>
    {md_to_html(advice)}
    <details class="dig"><summary>Skip</summary><p>GenerateEmailSend</p></details>
  </section>
</main>

</body>
</html>"""

def md_to_html(text):
    """ Markdown  HTML"""
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
# 4: GenerateEmail
# ============================================================
EMAIL_PROMPT = """EmailResearchReportPersonal materialsEmail

## ProfessorResearchReport
{research}

## Personal materials
{profile}

## 
1. : Prospective PhD Student - [] - []
2.  200-300 
3. ProfessorResearchReport
4. 
5. 
6. 


SUBJECT: Email
BODY:
Email"""

def generate_email(prof_name, school, dept):
    """ProfessorGenerateEmail"""
    prof_dir = SCHOOLS / f"{school}_{dept}" / prof_name.replace(" ", "_")
    research_file = prof_dir / "research.md"
    if not research_file.exists():
        print(f"[FAIL] Not found {prof_name} Research")
        return None

    # LoadPersonal materials
    profile = ""
    for f in PROFILES.glob("*.md"):
        profile += f"\n### {f.stem}\n{f.read_text('utf-8')}\n"

    research = research_file.read_text("utf-8")
    prompt = EMAIL_PROMPT.format(research=research, profile=profile)
    result = agent(prompt, timeout=120)

    if not result:
        return None

    # 
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

    # 
    email_file = prof_dir / "email_draft.md"
    email_file.write_text(f"# {subject}\n\n{body}", "utf-8")
    print(f"  [EMAIL] EmailDraftGenerate: {email_file}")
    return {"subject": subject, "body": body, "file": email_file}

def generate_emails(school, dept, prof_name=None, all_profs=False):
    """GenerateEmail"""
    school_dir = SCHOOLS / f"{school}_{dept}"
    if prof_name:
        return generate_email(prof_name, school, dept)
    elif all_profs:
        results = []
        for prof_dir in sorted(school_dir.iterdir()):
            if prof_dir.is_dir() and (prof_dir / "research.md").exists():
                name = prof_dir.name.replace("_", " ")
                print(f"\n[EMAIL]  {name} GenerateEmail...")
                r = generate_email(name, school, dept)
                if r:
                    results.append(r)
                time.sleep(5)
        return results

# ============================================================
# CLI
# ============================================================
def main():
    global BASE, INBOX, PROFILES, SCHOOLS, LOGS

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--path", help="Project root path. Task files will be stored in <path>/.outreach/")
    sub = parser.add_subparsers(dest="command")

    # setup: 
    sub.add_parser("setup", help=" inbox/ Personal materials")

    # research: ResearchProfessor
    p_r = sub.add_parser("research", help="ResearchProfessor")
    p_r.add_argument("--school", required=True)
    p_r.add_argument("--dept", required=True)
    p_r.add_argument("--csv", help="ProfessorCSVSearch")

    # report: GenerateReport
    p_rp = sub.add_parser("report", help="GenerateHTMLReport")
    p_rp.add_argument("--school", required=True)
    p_rp.add_argument("--dept", required=True)

    # email: GenerateEmail
    p_e = sub.add_parser("email", help="GenerateEmail")
    p_e.add_argument("--school", required=True)
    p_e.add_argument("--dept", required=True)
    p_e.add_argument("--prof", help="Professor")
    p_e.add_argument("--all", action="store_true", help="Professor")
    p_e.add_argument("--dry-run", action="store_true")

    # send: SendEmail
    p_s = sub.add_parser("send", help="SendEmail")
    p_s.add_argument("--school", required=True)
    p_s.add_argument("--dept", required=True)
    p_s.add_argument("--prof", required=True)
    p_s.add_argument("--confirm", action="store_true")

    # full: 
    p_f = sub.add_parser("full", help=": ResearchReportEmail")
    p_f.add_argument("--school", required=True)
    p_f.add_argument("--dept", required=True)
    p_f.add_argument("--csv", help="ProfessorCSV")
    p_f.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    # 初始化任务目录
    task_dir = get_task_dir(args.path)
    BASE = task_dir
    INBOX = task_dir / "inbox"
    PROFILES = task_dir / "profiles"
    SCHOOLS = task_dir / "schools"
    LOGS = task_dir / "logs"

    # 确保目录存在
    for d in [INBOX, PROFILES, SCHOOLS, LOGS]:
        d.mkdir(parents=True, exist_ok=True)

    if args.command == "setup":
        parse_profile()
    elif args.command == "research":
        research_school(args.school, args.dept, args.csv)
    elif args.command == "report":
        generate_html_report(args.school, args.dept)
    elif args.command == "email":
        generate_emails(args.school, args.dept, args.prof, args.all)
    elif args.command == "send":
        # EmailDraftSend
        prof_dir = SCHOOLS / f"{args.school}_{args.dept}" / args.prof.replace(" ", "_")
        email_file = prof_dir / "email_draft.md"
        if not email_file.exists():
            print("[FAIL] GenerateEmailDraft")
            return
        content = email_file.read_text("utf-8")
        lines = content.split("\n")
        subject = lines[0].replace("# ", "").strip()
        body = "\n".join(lines[2:]).strip()
        if args.confirm:
            print(f"[EMAIL] Send...\n: {subject}\n")
            r = agent(f" email_send SendEmail {args.prof}: {subject}:\n{body}", 60)
            print(r)
        else:
            print(f"[WARN]   --confirm Send\n: {subject}\n:\n{body}")
    elif args.command == "full":
        print("[START] \n")
        parse_profile()
        print()
        research_school(args.school, args.dept, args.csv)
        print()
        generate_html_report(args.school, args.dept)
        print()
        generate_emails(args.school, args.dept, all_profs=True)
        print(f"\n[OK] CompletedReport: {SCHOOLS / f'{args.school}_{args.dept}' / 'report.html'}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
