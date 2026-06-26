"""
dev-flow Nexgent Plugin — Unified development workflow tools.
One plugin for the entire dev lifecycle: onboard, audit, review, changelog, adr, memory.
"""

import json
import os
import re
import ssl
import subprocess
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Tool definitions
TOOL_DEFS = []
PERMISSIONS = {}

def _register(name, description, parameters, permission_desc):
    TOOL_DEFS.append({
        "name": name,
        "description": description,
        "parameters": parameters,
    })
    PERMISSIONS[name] = permission_desc


# --- SSL Context ---
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


# ============================================================
# Onboard — project scanning
# ============================================================

_LANG_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".py": "Python", ".rs": "Rust", ".go": "Go", ".java": "Java", ".rb": "Ruby",
    ".php": "PHP", ".c": "C", ".cpp": "C++", ".cs": "C#", ".swift": "Swift",
}

_FW_DEPS = {
    "react": "React", "vue": "Vue", "next": "Next.js", "express": "Express",
    "fastify": "Fastify", "@nestjs/core": "NestJS", "svelte": "Svelte",
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
    "torch": "PyTorch", "tensorflow": "TensorFlow",
    "actix-web": "Actix Web", "axum": "Axum", "tokio": "Tokio",
}

_TEST_DEPS = {
    "jest": "Jest", "vitest": "Vitest", "@playwright/test": "Playwright",
    "cypress": "Cypress", "pytest": "pytest",
}

_CI_FILES = {
    ".github/workflows": "GitHub Actions", ".gitlab-ci.yml": "GitLab CI",
    ".circleci/config.yml": "CircleCI", "Jenkinsfile": "Jenkins",
}

_LINTER_FILES = {
    ".eslintrc.js": "ESLint", ".eslintrc.json": "ESLint", "eslint.config.js": "ESLint",
    ".flake8": "flake8", "rustfmt.toml": "rustfmt", ".golangci.yml": "golangci-lint",
}

_LOCK_FILES = {
    "package-lock.json": "npm", "yarn.lock": "yarn", "pnpm-lock.yaml": "pnpm",
    "poetry.lock": "poetry", "Cargo.lock": "cargo", "go.sum": "go modules",
}

_EXCLUDE = {"node_modules", "__pycache__", ".git", "target", ".venv", "venv", "dist", "build"}


def _count_files(root: Path, exts: list[str]) -> int:
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE]
        for f in filenames:
            if any(f.endswith(ext) for ext in exts):
                count += 1
    return count


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _detect_languages(root: Path) -> dict[str, int]:
    ext_groups = {}
    for ext, lang in _LANG_EXT.items():
        ext_groups.setdefault(lang, []).append(ext)
    result = {}
    for lang, exts in ext_groups.items():
        count = _count_files(root, exts)
        if count > 0:
            result[lang] = count
    return dict(sorted(result.items(), key=lambda x: -x[1]))


def _detect_frameworks(root: Path) -> list[str]:
    frameworks = []
    pkg = _read_json(root / "package.json")
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))
    for dep, name in _FW_DEPS.items():
        if dep in all_deps:
            frameworks.append(name)
    for req_file in root.glob("requirements*.txt"):
        try:
            content = req_file.read_text(encoding="utf-8").lower()
            for dep, name in _FW_DEPS.items():
                if dep in content and name not in frameworks:
                    frameworks.append(name)
        except Exception:
            pass
    return frameworks


def _detect_tests(root: Path) -> list[str]:
    tests = []
    pkg = _read_json(root / "package.json")
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))
    for dep, name in _TEST_DEPS.items():
        if dep in all_deps:
            tests.append(name)
    return tests


def _detect_ci(root: Path) -> list[str]:
    ci = []
    for path, platform in _CI_FILES.items():
        if (root / path).exists():
            ci.append(platform)
    return ci


def _detect_style(root: Path) -> list[str]:
    style = []
    for f, tool in _LINTER_FILES.items():
        if (root / f).exists():
            style.append(tool)
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "[tool.ruff]" in content:
                style.append("Ruff")
            if "[tool.black]" in content:
                style.append("Black")
        except Exception:
            pass
    return style


def _detect_package_manager(root: Path) -> str:
    for lock, pm in _LOCK_FILES.items():
        if (root / lock).exists():
            return pm
    return "unknown"


def _get_tree(root: Path, max_depth: int = 3) -> str:
    lines = []
    def _walk(path: Path, prefix: str, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return
        entries = [e for e in entries if e.name not in _EXCLUDE]
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                _walk(entry, child_prefix, depth + 1)
            else:
                lines.append(f"{prefix}{connector}{entry.name}")
    lines.append(f"{root.name}/")
    _walk(root, "", 1)
    return "\n".join(lines)


# ============================================================
# Audit — dependency vulnerability scanning
# ============================================================

_ECOSYSTEM_MAP = {
    "package.json": "npm", "requirements.txt": "PyPI", "pyproject.toml": "PyPI",
    "Cargo.toml": "crates.io", "go.mod": "Go", "Gemfile": "RubyGems",
    "composer.json": "Packagist", "pom.xml": "Maven",
}


def _parse_deps_package_json(root: Path) -> list[dict]:
    pkg = _read_json(root / "package.json")
    deps = []
    for section in ["dependencies", "devDependencies"]:
        for name, version in pkg.get(section, {}).items():
            clean = re.sub(r'^[^0-9]*', '', version)
            deps.append({"name": name, "version": clean, "ecosystem": "npm"})
    return deps


def _parse_deps_requirements(root: Path) -> list[dict]:
    deps = []
    for req_file in root.glob("requirements*.txt"):
        try:
            for line in req_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                match = re.match(r'^([a-zA-Z0-9_.-]+)\s*([><=!~]*)\s*([0-9a-zA-Z.]*)', line)
                if match:
                    deps.append({"name": match.group(1), "version": match.group(3) or "*", "ecosystem": "PyPI"})
        except Exception:
            pass
    return deps


def _parse_all_deps(root: Path) -> list[dict]:
    deps = []
    deps.extend(_parse_deps_package_json(root))
    deps.extend(_parse_deps_requirements(root))
    cargo = root / "Cargo.toml"
    if cargo.exists():
        try:
            for line in cargo.read_text(encoding="utf-8").splitlines():
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*"([^"]+)"', line.strip())
                if match:
                    deps.append({"name": match.group(1), "version": match.group(2), "ecosystem": "crates.io"})
        except Exception:
            pass
    go_mod = root / "go.mod"
    if go_mod.exists():
        try:
            in_require = False
            for line in go_mod.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("require ("):
                    in_require = True
                    continue
                if line == ")" and in_require:
                    in_require = False
                    continue
                if in_require:
                    parts = line.split()
                    if len(parts) >= 2:
                        deps.append({"name": parts[0], "version": parts[1].lstrip("v"), "ecosystem": "Go"})
        except Exception:
            pass
    return deps


def _query_osv(package_name: str, ecosystem: str, version: str = None) -> list[dict]:
    url = "https://api.osv.dev/v1/query"
    payload = {"package": {"name": package_name, "ecosystem": ecosystem}}
    if version and version != "*":
        payload["version"] = version
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, context=_ctx, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8")).get("vulns", [])
    except Exception:
        return []


def _extract_severity(vuln: dict) -> str:
    _norm = {"MODERATE": "MEDIUM", "INFO": "LOW"}
    db = vuln.get("database_specific", {})
    sev = db.get("severity", "")
    if sev:
        return _norm.get(sev.upper(), sev.upper())
    eco = vuln.get("ecosystem_specific", {})
    sev = eco.get("severity", "")
    if sev:
        return _norm.get(sev.upper(), sev.upper())
    return "UNKNOWN"


def _extract_fixed(vuln: dict, pkg_name: str) -> str | None:
    for affected in vuln.get("affected", []):
        if affected.get("package", {}).get("name") == pkg_name:
            for r in affected.get("ranges", []):
                for event in r.get("events", []):
                    if "fixed" in event:
                        return event["fixed"]
    return None


# ============================================================
# Review — code review
# ============================================================

_REVIEW_SESSIONS = {}


class ReviewSession:
    def __init__(self, session_id: str, target: str, perspectives: list[str]):
        self.session_id = session_id
        self.target = target
        self.perspectives = perspectives
        self.findings = []
        self.created_at = datetime.now(timezone.utc).isoformat()

    def add_finding(self, finding: dict) -> bool:
        required = ["id", "perspective", "severity", "title", "file", "risk", "fix"]
        if not all(k in finding for k in required):
            return False
        if finding.get("confidence", 0) < 70:
            return False
        self.findings.append(finding)
        return True

    def get_health_score(self) -> dict:
        weights = {"critical": 15, "warning": 5, "suggestion": 1}
        perspective_scores = {}
        for p in self.perspectives:
            p_findings = [f for f in self.findings if f.get("perspective") == p]
            deduction = sum(weights.get(f.get("severity", ""), 0) for f in p_findings)
            perspective_scores[p] = max(0, 100 - deduction)
        overall = sum(perspective_scores.values()) / len(perspective_scores) if perspective_scores else 100
        return {
            "overall": round(overall, 1),
            "perspective_scores": perspective_scores,
            "findings_count": {
                "critical": sum(1 for f in self.findings if f.get("severity") == "critical"),
                "warning": sum(1 for f in self.findings if f.get("severity") == "warning"),
                "suggestion": sum(1 for f in self.findings if f.get("severity") == "suggestion"),
            },
        }


# ============================================================
# Changelog — git log parsing
# ============================================================

_COMMIT_TYPES = {
    "feat": "✨ Features", "fix": "🐛 Bug Fixes", "perf": "⚡ Performance",
    "docs": "📝 Documentation", "refactor": "🔨 Refactoring", "test": "✅ Tests",
    "chore": "🔧 Chores", "ci": "👷 CI/CD", "build": "📦 Build",
}

_COMMIT_RE = re.compile(
    r'^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<desc>.+)$'
)


def _run_git(args: list[str], cwd: str = ".") -> str:
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, cwd=cwd, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def _parse_commit_line(line: str) -> dict | None:
    parts = line.split("|", 4)
    if len(parts) < 5:
        return None
    hash_val, subject, body, author, date = parts
    m = _COMMIT_RE.match(subject)
    if m:
        ctype = m.group("type")
        scope = m.group("scope")
        breaking = m.group("breaking") is not None
        desc = m.group("desc")
    else:
        ctype, scope, breaking, desc = "other", None, False, subject
    if body and "BREAKING CHANGE:" in body:
        breaking = True
    return {
        "hash": hash_val[:8], "type": ctype, "scope": scope,
        "breaking": breaking, "description": desc, "subject": subject,
        "author": author, "date": date,
    }


def _suggest_bump(commits: list[dict]) -> str:
    if any(c["breaking"] for c in commits):
        return "major"
    if any(c["type"] == "feat" for c in commits):
        return "minor"
    if any(c["type"] in ("fix", "perf") for c in commits):
        return "patch"
    return "none"


# ============================================================
# ADR — architecture decision records
# ============================================================

_ADR_DIR = "docs/adr"


def _get_adr_dir(project_path: str) -> Path:
    return Path(project_path).resolve() / _ADR_DIR


def _next_adr_number(adr_dir: Path) -> int:
    max_n = 0
    if adr_dir.exists():
        for f in adr_dir.glob("*.md"):
            m = re.match(r'^(\d{4})-', f.name)
            if m:
                max_n = max(max_n, int(m.group(1)))
    return max_n + 1


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return re.sub(r'-+', '-', text)[:50].strip('-')


# ============================================================
# Memory — cross-session persistence
# ============================================================

_MEMORY_DIR = ".dev-flow"
_MEMORY_TYPES = {"session": 30, "decision": None, "finding": 90, "handoff": 7}


def _get_memory_dir(project_path: str) -> Path:
    return Path(project_path).resolve() / _MEMORY_DIR


def _load_memory_index(mem_dir: Path) -> dict:
    idx_path = mem_dir / "index.json"
    if idx_path.exists():
        try:
            return json.loads(idx_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": "1.0", "last_updated": None, "memories": [], "tag_index": {}}


def _save_memory_index(mem_dir: Path, index: dict):
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    (mem_dir / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")


def _gen_mem_id(mem_type: str) -> str:
    return f"{mem_type}-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')}"


def _save_memory(mem_dir: Path, index: dict, memory: dict) -> str:
    for d in ["sessions", "decisions", "findings", "handoffs"]:
        (mem_dir / d).mkdir(parents=True, exist_ok=True)
    mem_type = memory["type"]
    mem_id = memory["id"]
    subdir = {"session": "sessions", "decision": "decisions", "finding": "findings", "handoff": "handoffs"}.get(mem_type, "sessions")
    (mem_dir / subdir / f"{mem_id}.json").write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")
    index["memories"].append({
        "id": mem_id, "type": mem_type, "timestamp": memory.get("timestamp"),
        "tags": memory.get("tags", []), "summary": memory.get("summary", memory.get("title", "")),
        "path": f"{subdir}/{mem_id}.json",
    })
    for tag in memory.get("tags", []):
        index.setdefault("tag_index", {}).setdefault(tag, []).append(mem_id)
    _save_memory_index(mem_dir, index)
    return mem_id


# ============================================================
# Tool Implementations
# ============================================================

def _tool_onboard(args: dict) -> dict:
    """Full project onboarding scan."""
    root = Path(args.get("path", ".")).resolve()
    if not root.exists():
        return {"error": f"Path does not exist: {root}"}
    pkg = _read_json(root / "package.json")
    readme = ""
    for r in ["README.md", "README"]:
        p = root / r
        if p.exists():
            try:
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        readme = line[:200]
                        break
            except Exception:
                pass
    return {
        "name": pkg.get("name", root.name),
        "description": readme,
        "languages": _detect_languages(root),
        "frameworks": _detect_frameworks(root),
        "package_manager": _detect_package_manager(root),
        "test_frameworks": _detect_tests(root),
        "ci": _detect_ci(root),
        "code_style": _detect_style(root),
        "scripts": _read_json(root / "package.json").get("scripts", {}),
        "tree": _get_tree(root, args.get("depth", 3)),
    }


def _tool_audit(args: dict) -> dict:
    """Dependency vulnerability audit."""
    root = Path(args.get("path", ".")).resolve()
    if not root.exists():
        return {"error": f"Path does not exist: {root}"}
    deps = _parse_all_deps(root)
    vulns = []
    for dep in deps:
        osv_vulns = _query_osv(dep["name"], dep["ecosystem"], dep.get("version"))
        for v in osv_vulns:
            vulns.append({
                "id": v.get("id", "UNKNOWN"),
                "package": dep["name"],
                "ecosystem": dep["ecosystem"],
                "installed_version": dep.get("version", "unknown"),
                "fixed_version": _extract_fixed(v, dep["name"]),
                "severity": _extract_severity(v),
                "summary": v.get("summary", "")[:200],
            })
    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for v in vulns:
        sev_counts[v["severity"]] = sev_counts.get(v["severity"], 0) + 1
    score = max(0, 100 - sev_counts["CRITICAL"] * 25 - sev_counts["HIGH"] * 10 - sev_counts["MEDIUM"] * 3 - sev_counts["LOW"])
    return {"total_deps": len(deps), "vulnerabilities": vulns, "severity_counts": sev_counts, "health_score": score}


def _tool_review_start(args: dict) -> dict:
    """Start a review session."""
    sid = f"review-{len(_REVIEW_SESSIONS) + 1:04d}"
    perspectives = args.get("perspectives", "security,performance,architecture,quality,test,api").split(",")
    perspectives = [p.strip() for p in perspectives]
    session = ReviewSession(sid, args.get("target", "."), perspectives)
    _REVIEW_SESSIONS[sid] = session
    return {"session_id": sid, "target": session.target, "perspectives": perspectives}


def _tool_review_add_finding(args: dict) -> dict:
    """Add a finding to a review session."""
    sid = args.get("session_id", "")
    session = _REVIEW_SESSIONS.get(sid)
    if not session:
        return {"error": f"Session not found: {sid}"}
    finding = {k: args.get(k) for k in ["id", "perspective", "severity", "title", "file", "line", "evidence", "risk", "fix", "confidence", "ref"]}
    if session.add_finding(finding):
        return {"status": "added", "finding_id": finding["id"], "total": len(session.findings)}
    return {"error": "Finding rejected (missing fields or confidence < 70)"}


def _tool_review_score(args: dict) -> dict:
    """Get health score for a review session."""
    sid = args.get("session_id", "")
    session = _REVIEW_SESSIONS.get(sid)
    if not session:
        return {"error": f"Session not found: {sid}"}
    return session.get_health_score()


def _tool_review_export(args: dict) -> str:
    """Export review as markdown."""
    sid = args.get("session_id", "")
    session = _REVIEW_SESSIONS.get(sid)
    if not session:
        return f"Error: Session not found: {sid}"
    score = session.get_health_score()
    lines = [f"# Review Report — {sid}", "", f"**Target**: {session.target}", f"**Health Score**: {score['overall']}/100", ""]
    lines.append("| Perspective | Score | Critical | Warning | Suggestion |")
    lines.append("|------------|-------|----------|---------|------------|")
    for p in session.perspectives:
        ps = score["perspective_scores"].get(p, 100)
        pf = [f for f in session.findings if f.get("perspective") == p]
        c = sum(1 for f in pf if f.get("severity") == "critical")
        w = sum(1 for f in pf if f.get("severity") == "warning")
        s = sum(1 for f in pf if f.get("severity") == "suggestion")
        lines.append(f"| {p} | {ps} | {c} | {w} | {s} |")
    lines.append("")
    for sev in ["critical", "warning", "suggestion"]:
        sev_findings = [f for f in session.findings if f.get("severity") == sev]
        if sev_findings:
            lines.append(f"### {sev.upper()}")
            for f in sev_findings:
                lines.append(f"- **{f.get('id', '?')}**: {f.get('title', '?')} (`{f.get('file', '?')}:{f.get('line', '?')}`)")
                lines.append(f"  - Risk: {f.get('risk', '')}")
                lines.append(f"  - Fix: {f.get('fix', '')}")
            lines.append("")
    return "\n".join(lines)


def _tool_changelog(args: dict) -> str:
    """Generate changelog from git history."""
    repo_path = args.get("path", ".")
    from_ref = args.get("from", "")
    to_ref = args.get("to", "HEAD")
    version = args.get("version", "Unreleased")

    if from_ref:
        ref_range = f"{from_ref}..{to_ref}"
    else:
        last_tag = _run_git(["describe", "--tags", "--abbrev=0"], cwd=repo_path)
        ref_range = f"{last_tag}..{to_ref}" if last_tag else to_ref

    raw = _run_git(["log", ref_range, "--pretty=format:%H|%s|%b|%an|%aI", "--no-merges"], cwd=repo_path)
    if not raw:
        return f"## [{version}]\n\nNo changes found.\n"

    commits = []
    for line in raw.split("\n"):
        c = _parse_commit_line(line)
        if c:
            commits.append(c)

    groups = {}
    for c in commits:
        groups.setdefault(c["type"], []).append(c)

    bump = _suggest_bump(commits)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [f"## [{version}] - {date}", ""]
    breaking = [c for c in commits if c["breaking"]]
    if breaking:
        lines.append("### ⚠️ Breaking Changes")
        for c in breaking:
            scope = f"**{c['scope']}**: " if c["scope"] else ""
            lines.append(f"- {scope}{c['description']}")
        lines.append("")

    for type_key in ["feat", "fix", "perf", "docs", "refactor", "test", "chore"]:
        type_commits = groups.get(type_key, [])
        if not type_commits:
            continue
        label = _COMMIT_TYPES.get(type_key, type_key)
        lines.append(f"### {label}")
        for c in type_commits:
            if c["breaking"]:
                continue
            scope = f"**{c['scope']}**: " if c["scope"] else ""
            lines.append(f"- {scope}{c['description']} (`{c['hash']}`)")
        lines.append("")

    return "\n".join(lines)


def _tool_adr_create(args: dict) -> dict:
    """Create an ADR."""
    adr_dir = _get_adr_dir(args.get("path", "."))
    adr_dir.mkdir(parents=True, exist_ok=True)
    title = args.get("title", "Untitled Decision")
    number = args.get("number") or _next_adr_number(adr_dir)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    num_str = f"{number:04d}"

    content = f"# {num_str}. {title}\n\nDate: {date}\n\n## Status\n\nProposed\n\n"
    content += f"## Context\n\n{args.get('context', '{背景描述}')}\n\n"
    content += f"## Decision\n\n{args.get('decision', '{决策内容}')}\n\n"
    content += f"## Consequences\n\n### Positive\n\n- {args.get('positive', '{正面后果}')}\n\n### Negative\n\n- {args.get('negative', '{负面后果}')}\n"

    filename = f"{num_str}-{_slugify(title)}.md"
    (adr_dir / filename).write_text(content, encoding="utf-8")
    return {"number": number, "title": title, "file": filename}


def _tool_adr_list(args: dict) -> list[dict]:
    """List all ADRs."""
    adr_dir = _get_adr_dir(args.get("path", "."))
    if not adr_dir.exists():
        return []
    adrs = []
    for f in sorted(adr_dir.glob("*.md")):
        if f.name == "index.md":
            continue
        try:
            content = f.read_text(encoding="utf-8")
            title_m = re.search(r'^#\s+\d{4}\.\s+(.+)$', content, re.MULTILINE)
            status_m = re.search(r'^##\s*Status\s*\n\s*(.+)$', content, re.MULTILINE)
            adrs.append({
                "number": int(f.name[:4]),
                "title": title_m.group(1).strip() if title_m else f.stem,
                "status": status_m.group(1).strip().lower() if status_m else "unknown",
                "file": f.name,
            })
        except Exception:
            pass
    return adrs


def _tool_memory_save(args: dict) -> dict:
    """Save a memory."""
    mem_dir = _get_memory_dir(args.get("path", "."))
    mem_dir.mkdir(parents=True, exist_ok=True)
    index = _load_memory_index(mem_dir)
    mem_type = args.get("type", "session")
    memory = {
        "id": _gen_mem_id(mem_type),
        "type": mem_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tags": args.get("tags", []),
        "summary": args.get("summary", ""),
        "title": args.get("title", ""),
        "context": args.get("context", {}),
    }
    mem_id = _save_memory(mem_dir, index, memory)
    return {"id": mem_id, "status": "saved"}


def _tool_memory_recall(args: dict) -> list[dict]:
    """Search memories."""
    mem_dir = _get_memory_dir(args.get("path", "."))
    if not mem_dir.exists():
        return []
    index = _load_memory_index(mem_dir)
    query = args.get("query", "").lower()
    tags = args.get("tags", [])
    mem_type = args.get("type")
    results = []
    for entry in index.get("memories", []):
        if mem_type and entry.get("type") != mem_type:
            continue
        if tags and not any(t in entry.get("tags", []) for t in tags):
            continue
        if query and query not in entry.get("summary", "").lower() and not any(query in t.lower() for t in entry.get("tags", [])):
            continue
        full_path = mem_dir / entry.get("path", "")
        if full_path.exists():
            try:
                results.append(json.loads(full_path.read_text(encoding="utf-8")))
            except Exception:
                results.append(entry)
        else:
            results.append(entry)
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return results[:args.get("limit", 10)]


# ============================================================
# Register Tools
# ============================================================

_register("devflow_onboard", "Scan project: languages, frameworks, build system, test, CI/CD, code style.",
    {"type": "object", "properties": {"path": {"type": "string"}, "depth": {"type": "integer"}}}, "Read project config files")

_register("devflow_audit", "Audit dependencies for vulnerabilities via OSV database.",
    {"type": "object", "properties": {"path": {"type": "string"}}}, "Query OSV API and read dependency files")

_register("devflow_review_start", "Start a multi-perspective code review session.",
    {"type": "object", "properties": {"target": {"type": "string"}, "perspectives": {"type": "string"}}, "required": ["target"]}, "Initialize review session")

_register("devflow_review_add_finding", "Add a finding to a review session.",
    {"type": "object", "properties": {
        "session_id": {"type": "string"}, "id": {"type": "string"}, "perspective": {"type": "string"},
        "severity": {"type": "string"}, "title": {"type": "string"}, "file": {"type": "string"},
        "line": {"type": "integer"}, "evidence": {"type": "string"}, "risk": {"type": "string"},
        "fix": {"type": "string"}, "confidence": {"type": "integer"}, "ref": {"type": "string"},
    }, "required": ["session_id", "id", "perspective", "severity", "title", "file", "risk", "fix"]}, "Add finding to review")

_register("devflow_review_score", "Get health score for a review session.",
    {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]}, "Calculate review health score")

_register("devflow_review_export", "Export review as markdown report.",
    {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]}, "Generate review report")

_register("devflow_changelog", "Generate changelog from git history with conventional commits.",
    {"type": "object", "properties": {"path": {"type": "string"}, "from": {"type": "string"}, "to": {"type": "string"}, "version": {"type": "string"}}}, "Read git log")

_register("devflow_adr_create", "Create an Architecture Decision Record.",
    {"type": "object", "properties": {"path": {"type": "string"}, "title": {"type": "string"}, "context": {"type": "string"}, "decision": {"type": "string"}, "positive": {"type": "string"}, "negative": {"type": "string"}}, "required": ["title"]}, "Write ADR file")

_register("devflow_adr_list", "List all Architecture Decision Records.",
    {"type": "object", "properties": {"path": {"type": "string"}}}, "Read ADR files")

_register("devflow_memory_save", "Save a memory (session, decision, finding, handoff).",
    {"type": "object", "properties": {"path": {"type": "string"}, "type": {"type": "string"}, "summary": {"type": "string"}, "title": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}, "context": {"type": "object"}}, "required": ["summary"]}, "Write memory to .dev-flow/")

_register("devflow_memory_recall", "Search and recall memories.",
    {"type": "object", "properties": {"path": {"type": "string"}, "query": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}, "type": {"type": "string"}, "limit": {"type": "integer"}}}, "Read memory files")


# ============================================================
# Tool Dispatch
# ============================================================

_TOOL_MAP = {
    "devflow_onboard": _tool_onboard,
    "devflow_audit": _tool_audit,
    "devflow_review_start": _tool_review_start,
    "devflow_review_add_finding": _tool_review_add_finding,
    "devflow_review_score": _tool_review_score,
    "devflow_review_export": _tool_review_export,
    "devflow_changelog": _tool_changelog,
    "devflow_adr_create": _tool_adr_create,
    "devflow_adr_list": _tool_adr_list,
    "devflow_memory_save": _tool_memory_save,
    "devflow_memory_recall": _tool_memory_recall,
}


def get_tools() -> list[dict]:
    return TOOL_DEFS


def get_permissions() -> dict:
    return PERMISSIONS


def call_tool(name: str, args: dict) -> Any:
    func = _TOOL_MAP.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(args)
    except Exception as e:
        return {"error": str(e)}
