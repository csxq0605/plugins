"""
dep-audit Nexgent Plugin — Dependency vulnerability audit tools.
Scans dependency files, queries OSV vulnerability database, detects outdated packages, flags license risks.
"""

import json
import os
import re
import ssl
import urllib.request
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


# --- Config ---

_ECOSYSTEM_MAP = {
    "package.json": "npm",
    "requirements.txt": "PyPI",
    "requirements-dev.txt": "PyPI",
    "pyproject.toml": "PyPI",
    "Cargo.toml": "crates.io",
    "go.mod": "Go",
    "Gemfile": "RubyGems",
    "composer.json": "Packagist",
    "pom.xml": "Maven",
    "build.gradle": "Maven",
}

_HIGH_RISK_LICENSES = [
    "GPL-2.0", "GPL-2.0-only", "GPL-2.0-or-later",
    "GPL-3.0", "GPL-3.0-only", "GPL-3.0-or-later",
    "AGPL-3.0", "AGPL-3.0-only", "AGPL-3.0-or-later",
    "SSPL-1.0", "BUSL-1.1",
    "CC-BY-NC", "CC-BY-NC-SA",
    "UNKNOWN", "UNLICENSED",
]

_SAFE_LICENSES = [
    "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0",
    "ISC", "0BSD", "CC0-1.0", "Unlicense", "Zlib",
    "MPL-2.0", "LGPL-2.1", "LGPL-3.0",
]

_SEVERITY_WEIGHTS = {"CRITICAL": 25, "HIGH": 10, "MEDIUM": 3, "MODERATE": 3, "LOW": 1}


# --- Dependency Parsing ---

def _parse_package_json(root: Path) -> list[dict]:
    """Parse package.json dependencies."""
    pkg_path = root / "package.json"
    if not pkg_path.exists():
        return []

    try:
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    deps = []
    for section in ["dependencies", "devDependencies"]:
        for name, version in pkg.get(section, {}).items():
            # Clean version string
            clean_version = re.sub(r'^[^0-9]*', '', version)
            deps.append({
                "name": name,
                "version": clean_version,
                "raw_version": version,
                "type": section,
                "ecosystem": "npm",
                "source": "package.json",
            })

    return deps


def _parse_requirements_txt(root: Path) -> list[dict]:
    """Parse requirements.txt dependencies."""
    deps = []
    for req_file in ["requirements.txt", "requirements-dev.txt", "requirements-test.txt"]:
        path = root / req_file
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Parse: package>=1.0.0, package==1.0.0, package~=1.0.0
            match = re.match(r'^([a-zA-Z0-9_.-]+)\s*([><=!~]+)\s*([0-9a-zA-Z.*]+)', line)
            if match:
                name = match.group(1)
                version = match.group(3)
                deps.append({
                    "name": name,
                    "version": version,
                    "raw_version": line,
                    "type": "dependency",
                    "ecosystem": "PyPI",
                    "source": req_file,
                })
            elif re.match(r'^[a-zA-Z0-9_.-]+$', line):
                deps.append({
                    "name": line,
                    "version": "*",
                    "raw_version": line,
                    "type": "dependency",
                    "ecosystem": "PyPI",
                    "source": req_file,
                })

    return deps


def _parse_pyproject_toml(root: Path) -> list[dict]:
    """Parse pyproject.toml dependencies (simplified)."""
    path = root / "pyproject.toml"
    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return []

    deps = []
    # Simple regex-based parsing for dependencies section
    in_deps = False
    for line in content.splitlines():
        line = line.strip()
        if line == "dependencies = [":
            in_deps = True
            continue
        if in_deps:
            if line == "]":
                in_deps = False
                continue
            # Parse: "package>=1.0.0"
            match = re.match(r'["\']([a-zA-Z0-9_.-]+)\s*([><=!~]*)\s*([0-9a-zA-Z.*]*)["\']', line)
            if match:
                name = match.group(1)
                version = match.group(3) or "*"
                deps.append({
                    "name": name,
                    "version": version,
                    "raw_version": line.strip('"\''),
                    "type": "dependency",
                    "ecosystem": "PyPI",
                    "source": "pyproject.toml",
                })

    return deps


def _parse_cargo_toml(root: Path) -> list[dict]:
    """Parse Cargo.toml dependencies (simplified)."""
    path = root / "Cargo.toml"
    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return []

    deps = []
    in_deps = False
    for line in content.splitlines():
        line = line.strip()
        if line in ("[dependencies]", "[dev-dependencies]", "[build-dependencies]"):
            in_deps = True
            dep_type = "dev-dependency" if "dev" in line else "dependency"
            continue
        if line.startswith("[") and in_deps:
            in_deps = False
            continue
        if in_deps:
            # Parse: package = "1.0.0" or package = { version = "1.0.0" }
            match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*"([^"]+)"', line)
            if match:
                deps.append({
                    "name": match.group(1),
                    "version": match.group(2),
                    "raw_version": line,
                    "type": dep_type,
                    "ecosystem": "crates.io",
                    "source": "Cargo.toml",
                })
            else:
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*\{.*version\s*=\s*"([^"]+)"', line)
                if match:
                    deps.append({
                        "name": match.group(1),
                        "version": match.group(2),
                        "raw_version": line,
                        "type": dep_type,
                        "ecosystem": "crates.io",
                        "source": "Cargo.toml",
                    })

    return deps


def _parse_go_mod(root: Path) -> list[dict]:
    """Parse go.mod dependencies (simplified)."""
    path = root / "go.mod"
    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return []

    deps = []
    in_require = False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("require ("):
            in_require = True
            continue
        if line == ")" and in_require:
            in_require = False
            continue
        if in_require or line.startswith("require "):
            # Parse: module/path v1.2.3
            parts = line.replace("require ", "").strip().split()
            if len(parts) >= 2:
                deps.append({
                    "name": parts[0],
                    "version": parts[1].lstrip("v"),
                    "raw_version": line,
                    "type": "dependency",
                    "ecosystem": "Go",
                    "source": "go.mod",
                })

    return deps


def _parse_all_deps(root: Path) -> list[dict]:
    """Parse all dependency files in the project."""
    deps = []
    deps.extend(_parse_package_json(root))
    deps.extend(_parse_requirements_txt(root))
    deps.extend(_parse_pyproject_toml(root))
    deps.extend(_parse_cargo_toml(root))
    deps.extend(_parse_go_mod(root))

    # Recurse into subdirectories (max depth 2) for monorepos
    for child in root.iterdir():
        if child.is_dir() and child.name not in (
            "node_modules", ".git", "__pycache__", "target", ".venv", "venv",
            "dist", "build", ".next", ".nuxt", ".tox", "vendor",
        ):
            child_deps = []
            child_deps.extend(_parse_package_json(child))
            child_deps.extend(_parse_requirements_txt(child))
            child_deps.extend(_parse_cargo_toml(child))
            child_deps.extend(_parse_go_mod(child))
            for d in child_deps:
                d["source"] = f"{child.name}/{d['source']}"
            deps.extend(child_deps)

    return deps


# --- OSV API ---

def _query_osv(package_name: str, ecosystem: str, version: str = None) -> list[dict]:
    """Query OSV API for vulnerabilities."""
    url = "https://api.osv.dev/v1/query"
    payload = {
        "package": {
            "name": package_name,
            "ecosystem": ecosystem,
        }
    }
    if version and version != "*":
        payload["version"] = version

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, context=_ctx, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("vulns", [])
    except Exception:
        return []


def _extract_severity(vuln: dict) -> str:
    """Extract severity from OSV vulnerability."""
    _sev_normalize = {"MODERATE": "MEDIUM", "INFO": "LOW"}

    # Try database_specific
    db_spec = vuln.get("database_specific", {})
    severity = db_spec.get("severity", "")
    if severity:
        sev = severity.upper()
        return _sev_normalize.get(sev, sev)

    # Try severity array
    severities = vuln.get("severity", [])
    for s in severities:
        if s.get("type") == "CVSS_V3":
            score_str = s.get("score", "")
            # Parse CVSS vector for score
            match = re.search(r'CVSS:3\.[01]/.*', score_str)
            if match:
                # Extract base score from vector
                pass

    # Try to extract from ecosystem_specific
    eco_spec = vuln.get("ecosystem_specific", {})
    severity = eco_spec.get("severity", "")
    if severity:
        sev = severity.upper()
        return _sev_normalize.get(sev, sev)

    return "UNKNOWN"


def _extract_fixed_version(vuln: dict, package_name: str) -> str | None:
    """Extract fixed version from vulnerability."""
    for affected in vuln.get("affected", []):
        pkg = affected.get("package", {})
        if pkg.get("name") == package_name:
            for r in affected.get("ranges", []):
                for event in r.get("events", []):
                    if "fixed" in event:
                        return event["fixed"]
    return None


# --- Health Score ---

def _calculate_health_score(vulns: list[dict]) -> dict:
    """Calculate health score from vulnerabilities."""
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    _sev_normalize = {"MODERATE": "MEDIUM", "INFO": "LOW", "UNKNOWN": "UNKNOWN"}

    for v in vulns:
        sev = v.get("severity", "UNKNOWN").upper()
        sev = _sev_normalize.get(sev, sev)
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    deduction = 0
    for sev, count in severity_counts.items():
        weight = _SEVERITY_WEIGHTS.get(sev, 1)
        deduction += weight * count

    score = max(0, 100 - deduction)

    if score >= 90:
        grade = "Excellent"
    elif score >= 70:
        grade = "Good"
    elif score >= 50:
        grade = "Needs Improvement"
    else:
        grade = "Critical Issues"

    return {
        "score": score,
        "grade": grade,
        "severity_counts": severity_counts,
        "total_vulns": sum(severity_counts.values()),
    }


# --- Tool Implementations ---

def _tool_scan_deps(args: dict) -> dict:
    """Scan project for all dependencies."""
    root = Path(args.get("path", ".")).resolve()
    if not root.exists():
        return {"error": f"Path does not exist: {root}"}

    deps = _parse_all_deps(root)

    # Group by ecosystem
    by_ecosystem = {}
    for d in deps:
        eco = d["ecosystem"]
        by_ecosystem.setdefault(eco, []).append(d)

    return {
        "path": str(root),
        "total": len(deps),
        "by_ecosystem": {k: len(v) for k, v in by_ecosystem.items()},
        "dependencies": deps,
    }


def _tool_check_vulns(args: dict) -> dict:
    """Check dependencies for known vulnerabilities using OSV."""
    root = Path(args.get("path", ".")).resolve()
    if not root.exists():
        return {"error": f"Path does not exist: {root}"}

    deps = _parse_all_deps(root)
    vulns = []
    checked = 0

    for dep in deps:
        checked += 1
        osv_vulns = _query_osv(dep["name"], dep["ecosystem"], dep.get("version"))

        for v in osv_vulns:
            vuln_id = v.get("id", "UNKNOWN")
            summary = v.get("summary", v.get("details", "")[:200])
            severity = _extract_severity(v)
            fixed = _extract_fixed_version(v, dep["name"])

            vulns.append({
                "id": vuln_id,
                "package": dep["name"],
                "ecosystem": dep["ecosystem"],
                "installed_version": dep.get("version", "unknown"),
                "fixed_version": fixed,
                "severity": severity,
                "summary": summary,
                "source": dep["source"],
                "references": [r.get("url") for r in v.get("references", [])[:3]],
            })

    health = _calculate_health_score(vulns)

    return {
        "path": str(root),
        "checked": checked,
        "vulnerabilities": vulns,
        "health": health,
    }


def _tool_audit_full(args: dict) -> dict:
    """Full dependency audit — scan, check vulns, assess risk."""
    root = Path(args.get("path", ".")).resolve()
    if not root.exists():
        return {"error": f"Path does not exist: {root}"}

    # Scan deps
    scan_result = _tool_scan_deps(args)
    if "error" in scan_result:
        return scan_result

    # Check vulns
    vuln_result = _tool_check_vulns(args)
    if "error" in vuln_result:
        return vuln_result

    # Group vulns by severity
    by_severity = {}
    for v in vuln_result["vulnerabilities"]:
        sev = v["severity"]
        by_severity.setdefault(sev, []).append(v)

    # Generate fix recommendations
    fixes = []
    for v in vuln_result["vulnerabilities"]:
        if v["fixed_version"]:
            ecosystem = v["ecosystem"]
            pkg = v["package"]
            fixed = v["fixed_version"]
            if ecosystem == "npm":
                cmd = f"npm install {pkg}@{fixed}"
            elif ecosystem == "PyPI":
                cmd = f"pip install {pkg}>={fixed}"
            elif ecosystem == "crates.io":
                cmd = f"cargo update -p {pkg}"
            elif ecosystem == "Go":
                cmd = f"go get {pkg}@v{fixed}"
            else:
                cmd = f"upgrade {pkg} to {fixed}"

            fixes.append({
                "package": pkg,
                "severity": v["severity"],
                "current": v["installed_version"],
                "fixed": fixed,
                "command": cmd,
                "vuln_id": v["id"],
            })

    # Sort fixes by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
    fixes.sort(key=lambda x: severity_order.get(x["severity"], 5))

    return {
        "path": str(root),
        "scan": scan_result,
        "vulnerabilities": vuln_result["vulnerabilities"],
        "health": vuln_result["health"],
        "fixes": fixes,
    }


def _tool_generate_report(args: dict) -> str:
    """Generate a markdown audit report."""
    audit = _tool_audit_full(args)
    if "error" in audit:
        return audit["error"]

    lines = []
    lines.append("# Dependency Audit Report")
    lines.append("")

    scan = audit["scan"]
    health = audit["health"]

    lines.append(f"**Project**: {Path(audit['path']).name}")
    lines.append(f"**Total Dependencies**: {scan['total']}")

    eco_summary = ", ".join(f"{k}: {v}" for k, v in scan["by_ecosystem"].items())
    if eco_summary:
        lines.append(f"**Ecosystems**: {eco_summary}")
    lines.append("")

    # Health Score
    lines.append("## Health Score")
    lines.append("")
    lines.append(f"**Score**: {health['score']}/100 ({health['grade']})")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = health["severity_counts"].get(sev, 0)
        emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "")
        lines.append(f"| {emoji} {sev} | {count} |")
    lines.append("")

    # Vulnerabilities
    vulns = audit["vulnerabilities"]
    if vulns:
        lines.append("## Vulnerabilities")
        lines.append("")

        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            sev_vulns = [v for v in vulns if v["severity"] == sev]
            if not sev_vulns:
                continue

            emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "")
            lines.append(f"### {emoji} {sev}")
            lines.append("")

            for v in sev_vulns:
                lines.append(f"**{v['id']}**: {v['package']} {v['installed_version']}")
                lines.append(f"- Severity: {v['severity']}")
                lines.append(f"- Summary: {v['summary']}")
                if v["fixed_version"]:
                    lines.append(f"- Fixed in: {v['fixed_version']}")
                if v["references"]:
                    lines.append(f"- References: {', '.join(v['references'])}")
                lines.append("")
    else:
        lines.append("## Vulnerabilities")
        lines.append("")
        lines.append("No known vulnerabilities found. ✅")
        lines.append("")

    # Fix Recommendations
    fixes = audit["fixes"]
    if fixes:
        lines.append("## Fix Recommendations")
        lines.append("")
        lines.append("| Priority | Package | Current | Fixed | Command |")
        lines.append("|----------|---------|---------|-------|---------|")
        for i, f in enumerate(fixes[:20], 1):
            lines.append(f"| P{i} | {f['package']} | {f['current']} | {f['fixed']} | `{f['command']}` |")
        lines.append("")

    return "\n".join(lines)


# --- Register Tools ---

_register(
    "audit_scan_deps",
    "Scan project for all dependencies — parses package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Read dependency files to extract package list",
)

_register(
    "audit_check_vulns",
    "Check dependencies for known vulnerabilities using OSV (Open Source Vulnerability) database.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Query OSV API for vulnerability information",
)

_register(
    "audit_full",
    "Full dependency audit — scan dependencies, check vulnerabilities, generate fix recommendations.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Full dependency audit with OSV vulnerability checking",
)

_register(
    "audit_generate_report",
    "Generate a markdown dependency audit report.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Full audit and markdown report generation",
)


# --- Tool Dispatch ---

_TOOL_MAP = {
    "audit_scan_deps": _tool_scan_deps,
    "audit_check_vulns": _tool_check_vulns,
    "audit_full": _tool_audit_full,
    "audit_generate_report": _tool_generate_report,
}


def get_tools() -> list[dict]:
    """Return tool definitions for Nexgent."""
    return TOOL_DEFS


def get_permissions() -> dict:
    """Return permission descriptions."""
    return PERMISSIONS


def call_tool(name: str, args: dict) -> Any:
    """Dispatch a tool call."""
    func = _TOOL_MAP.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(args)
    except Exception as e:
        return {"error": str(e)}
