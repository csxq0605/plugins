"""
adr-generator Nexgent Plugin — Architecture Decision Record tools.
Creates, manages, and indexes ADRs with multiple templates and status tracking.
"""

import json
import os
import re
from datetime import datetime, timezone
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


# --- Config ---

_ADR_DIR = "docs/adr"
_INDEX_FILE = "index.md"

_TEMPLATES = {
    "madr": "madr",
    "y-statement": "y-statement",
}

_STATUSES = ["proposed", "accepted", "deprecated", "superseded"]


# --- Helpers ---

def _get_adr_dir(project_path: str = ".") -> Path:
    """Get the ADR directory path."""
    return Path(project_path).resolve() / _ADR_DIR


def _ensure_dir(adr_dir: Path):
    """Ensure ADR directory exists."""
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / "templates").mkdir(exist_ok=True)


def _get_next_number(adr_dir: Path) -> int:
    """Get the next ADR number."""
    max_num = 0
    if adr_dir.exists():
        for f in adr_dir.glob("*.md"):
            if f.name == _INDEX_FILE:
                continue
            match = re.match(r'^(\d{4})-', f.name)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)
    return max_num + 1


def _parse_adr_header(content: str) -> dict:
    """Parse ADR header information."""
    info = {}

    # Title
    title_match = re.search(r'^#\s+(\d{4})\.\s+(.+)$', content, re.MULTILINE)
    if title_match:
        info["number"] = int(title_match.group(1))
        info["title"] = title_match.group(2).strip()

    # Date
    date_match = re.search(r'^Date:\s*(.+)$', content, re.MULTILINE)
    if date_match:
        info["date"] = date_match.group(1).strip()

    # Status
    status_match = re.search(r'^##\s*Status\s*\n\s*(.+)$', content, re.MULTILINE)
    if status_match:
        status_line = status_match.group(1).strip().lower()
        for s in _STATUSES:
            if s in status_line:
                info["status"] = s
                break
        if "status" not in info:
            info["status"] = status_line

    return info


def _generate_madr(number: int, title: str, context: str = "", decision: str = "",
                   alternatives: list[dict] = None, consequences: dict = None,
                   related: list[dict] = None) -> str:
    """Generate MADR format ADR."""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    num_str = f"{number:04d}"

    lines = []
    lines.append(f"# {num_str}. {title}")
    lines.append("")
    lines.append(f"Date: {date}")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("Proposed")
    lines.append("")
    lines.append("## Context")
    lines.append("")
    lines.append(context or "{描述促使决策的问题或机会}")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(decision or "{清晰地陈述做出的决策}")
    lines.append("")
    lines.append("## Considered Alternatives")
    lines.append("")

    if alternatives:
        for i, alt in enumerate(alternatives, 1):
            name = alt.get("name", f"Alternative {i}")
            desc = alt.get("description", "")
            pros = alt.get("pros", [])
            cons = alt.get("cons", [])
            lines.append(f"### Alternative {i}: {name}")
            lines.append("")
            lines.append(desc)
            lines.append("")
            if pros:
                lines.append("- Pros:")
                for p in pros:
                    lines.append(f"  - {p}")
            if cons:
                lines.append("- Cons:")
                for c in cons:
                    lines.append(f"  - {c}")
            lines.append("")
    else:
        lines.append("### Alternative A: {名称}")
        lines.append("")
        lines.append("{描述}")
        lines.append("")
        lines.append("- Pros: {列表}")
        lines.append("- Cons: {列表}")
        lines.append("")

    lines.append("## Consequences")
    lines.append("")

    if consequences:
        if consequences.get("positive"):
            lines.append("### Positive")
            lines.append("")
            for c in consequences["positive"]:
                lines.append(f"- {c}")
            lines.append("")
        if consequences.get("negative"):
            lines.append("### Negative")
            lines.append("")
            for c in consequences["negative"]:
                lines.append(f"- {c}")
            lines.append("")
        if consequences.get("risks"):
            lines.append("### Risks")
            lines.append("")
            for c in consequences["risks"]:
                lines.append(f"- {c}")
            lines.append("")
    else:
        lines.append("### Positive")
        lines.append("")
        lines.append("- {列表}")
        lines.append("")
        lines.append("### Negative")
        lines.append("")
        lines.append("- {列表}")
        lines.append("")

    if related:
        lines.append("## Related Decisions")
        lines.append("")
        for r in related:
            r_num = f"{r['number']:04d}"
            lines.append(f"- [ADR-{r_num}]({r_num}-{_slugify(r.get('title', ''))}.md) — {r.get('relation', '')}")
        lines.append("")

    return "\n".join(lines)


def _generate_y_statement(number: int, title: str, context: str = "", problem: str = "",
                          decision: str = "", supplement: str = "",
                          positive: str = "", negative: str = "") -> str:
    """Generate Y-Statement format ADR."""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    num_str = f"{number:04d}"

    lines = []
    lines.append(f"# {num_str}. {title}")
    lines.append("")
    lines.append(f"Date: {date}")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("Proposed")
    lines.append("")
    lines.append("## Y-Statement")
    lines.append("")
    lines.append(f"In the context of {context or '{上下文}'},")
    lines.append(f"facing {problem or '{问题}'},")
    lines.append(f"we decided {decision or '{决策}'},")
    if supplement:
        lines.append(f"and {supplement},")
    lines.append(f"to achieve {positive or '{期望后果}'},")
    lines.append(f"accepting {negative or '{负面后果}'}.")
    lines.append("")
    lines.append("## Details")
    lines.append("")
    lines.append("{扩展说明，包含技术细节}")
    lines.append("")
    lines.append("## Considered Alternatives")
    lines.append("")
    lines.append("- {替代方案 1}: {为什么不选}")
    lines.append("- {替代方案 2}: {为什么不选}")
    lines.append("")

    return "\n".join(lines)


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:50].strip('-')


def _generate_index(adr_dir: Path) -> str:
    """Generate ADR index."""
    lines = []
    lines.append("# Architecture Decision Records")
    lines.append("")
    lines.append("| # | Title | Date | Status |")
    lines.append("|---|-------|------|--------|")

    adrs = []
    if adr_dir.exists():
        for f in sorted(adr_dir.glob("*.md")):
            if f.name == _INDEX_FILE:
                continue
            try:
                content = f.read_text(encoding="utf-8")
                info = _parse_adr_header(content)
                if info.get("number"):
                    adrs.append({
                        "file": f.name,
                        "number": info["number"],
                        "title": info.get("title", f.stem),
                        "date": info.get("date", ""),
                        "status": info.get("status", "unknown"),
                    })
            except Exception:
                pass

    adrs.sort(key=lambda x: x["number"])

    for adr in adrs:
        num = f"{adr['number']:04d}"
        lines.append(f"| {num} | [{adr['title']}]({adr['file']}) | {adr['date']} | {adr['status']} |")

    if not adrs:
        lines.append("| - | No ADRs yet | - | - |")

    lines.append("")
    return "\n".join(lines)


# --- Tool Implementations ---

def _tool_create_adr(args: dict) -> dict:
    """Create a new ADR."""
    project_path = args.get("path", ".")
    adr_dir = _get_adr_dir(project_path)
    _ensure_dir(adr_dir)

    template = args.get("template", "madr")
    title = args.get("title", "Untitled Decision")
    number = args.get("number") or _get_next_number(adr_dir)

    if template == "y-statement":
        content = _generate_y_statement(
            number=number,
            title=title,
            context=args.get("context", ""),
            problem=args.get("problem", ""),
            decision=args.get("decision", ""),
            supplement=args.get("supplement", ""),
            positive=args.get("positive", ""),
            negative=args.get("negative", ""),
        )
    else:  # madr
        content = _generate_madr(
            number=number,
            title=title,
            context=args.get("context", ""),
            decision=args.get("decision", ""),
            alternatives=args.get("alternatives"),
            consequences=args.get("consequences"),
            related=args.get("related"),
        )

    slug = _slugify(title)
    filename = f"{number:04d}-{slug}.md"
    file_path = adr_dir / filename
    file_path.write_text(content, encoding="utf-8")

    return {
        "number": number,
        "title": title,
        "file": str(file_path),
        "filename": filename,
        "template": template,
    }


def _tool_list_adrs(args: dict) -> list[dict]:
    """List all ADRs."""
    project_path = args.get("path", ".")
    adr_dir = _get_adr_dir(project_path)

    if not adr_dir.exists():
        return []

    status_filter = args.get("status")
    adrs = []

    for f in sorted(adr_dir.glob("*.md")):
        if f.name == _INDEX_FILE:
            continue
        try:
            content = f.read_text(encoding="utf-8")
            info = _parse_adr_header(content)
            if info.get("number"):
                if status_filter and info.get("status") != status_filter:
                    continue
                adrs.append({
                    "file": f.name,
                    "number": info["number"],
                    "title": info.get("title", f.stem),
                    "date": info.get("date", ""),
                    "status": info.get("status", "unknown"),
                })
        except Exception:
            pass

    adrs.sort(key=lambda x: x["number"])
    return adrs


def _tool_show_adr(args: dict) -> dict | str:
    """Show ADR details."""
    project_path = args.get("path", ".")
    adr_dir = _get_adr_dir(project_path)

    number = args.get("number")
    if not number:
        return {"error": "ADR number is required"}

    num_str = f"{int(number):04d}"

    for f in adr_dir.glob(f"{num_str}-*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            info = _parse_adr_header(content)
            return {
                "number": info.get("number"),
                "title": info.get("title"),
                "date": info.get("date"),
                "status": info.get("status"),
                "file": str(f),
                "content": content,
            }
        except Exception:
            pass

    return {"error": f"ADR {num_str} not found"}


def _tool_update_status(args: dict) -> dict:
    """Update ADR status."""
    project_path = args.get("path", ".")
    adr_dir = _get_adr_dir(project_path)

    number = args.get("number")
    new_status = args.get("status")

    if not number or not new_status:
        return {"error": "Number and status are required"}

    if new_status not in _STATUSES:
        return {"error": f"Invalid status: {new_status}. Must be one of: {', '.join(_STATUSES)}"}

    num_str = f"{int(number):04d}"

    for f in adr_dir.glob(f"{num_str}-*.md"):
        try:
            content = f.read_text(encoding="utf-8")

            # Replace status
            status_pattern = r'(## Status\s*\n\s*)(\S.+)'
            replacement = f'\\1{new_status.capitalize()}'
            new_content = re.sub(status_pattern, replacement, content, flags=re.MULTILINE)

            # If superseded, add reference
            superseded_by = args.get("superseded_by")
            if new_status == "superseded" and superseded_by:
                sup_num = f"{int(superseded_by):04d}"
                replacement = f'\\1Superseded by ADR-{sup_num}'
                new_content = re.sub(status_pattern, replacement, new_content, flags=re.MULTILINE)

            f.write_text(new_content, encoding="utf-8")

            return {
                "number": int(number),
                "status": new_status,
                "file": str(f),
            }
        except Exception as e:
            return {"error": str(e)}

    return {"error": f"ADR {num_str} not found"}


def _tool_generate_index(args: dict) -> str:
    """Generate ADR index."""
    project_path = args.get("path", ".")
    adr_dir = _get_adr_dir(project_path)

    index_content = _generate_index(adr_dir)

    # Save index
    _ensure_dir(adr_dir)
    index_path = adr_dir / _INDEX_FILE
    index_path.write_text(index_content, encoding="utf-8")

    return index_content


def _tool_search_adrs(args: dict) -> list[dict]:
    """Search ADRs by keyword."""
    project_path = args.get("path", ".")
    adr_dir = _get_adr_dir(project_path)

    query = args.get("query", "").lower()
    if not query:
        return []

    results = []
    if adr_dir.exists():
        for f in adr_dir.glob("*.md"):
            if f.name == _INDEX_FILE:
                continue
            try:
                content = f.read_text(encoding="utf-8")
                if query in content.lower():
                    info = _parse_adr_header(content)
                    if info.get("number"):
                        results.append({
                            "file": f.name,
                            "number": info["number"],
                            "title": info.get("title", f.stem),
                            "date": info.get("date", ""),
                            "status": info.get("status", "unknown"),
                        })
            except Exception:
                pass

    results.sort(key=lambda x: x["number"])
    return results


# --- Register Tools ---

_register(
    "adr_create",
    "Create a new Architecture Decision Record.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "title": {"type": "string", "description": "ADR title"},
            "template": {"type": "string", "description": "Template: 'madr' or 'y-statement' (default: madr)"},
            "number": {"type": "integer", "description": "ADR number (auto-assigned if omitted)"},
            "context": {"type": "string", "description": "Context description"},
            "decision": {"type": "string", "description": "Decision description"},
            "alternatives": {"type": "array", "items": {"type": "object"}, "description": "Alternative solutions"},
            "consequences": {"type": "object", "description": "Decision consequences"},
            "related": {"type": "array", "items": {"type": "object"}, "description": "Related ADRs"},
            "problem": {"type": "string", "description": "Problem statement (Y-Statement)"},
            "supplement": {"type": "string", "description": "Supplement (Y-Statement)"},
            "positive": {"type": "string", "description": "Positive outcome (Y-Statement)"},
            "negative": {"type": "string", "description": "Negative outcome (Y-Statement)"},
        },
        "required": ["title"],
    },
    "Write ADR file to docs/adr/ directory",
)

_register(
    "adr_list",
    "List all Architecture Decision Records, optionally filtered by status.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "status": {"type": "string", "description": "Filter by status (proposed, accepted, deprecated, superseded)"},
        },
    },
    "Read ADR files from docs/adr/ directory",
)

_register(
    "adr_show",
    "Show details of a specific ADR.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "number": {"type": "integer", "description": "ADR number"},
        },
        "required": ["number"],
    },
    "Read specific ADR file from docs/adr/ directory",
)

_register(
    "adr_update_status",
    "Update the status of an ADR (accepted, deprecated, superseded).",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "number": {"type": "integer", "description": "ADR number"},
            "status": {"type": "string", "description": "New status (accepted, deprecated, superseded)"},
            "superseded_by": {"type": "integer", "description": "ADR number that supersedes this one"},
        },
        "required": ["number", "status"],
    },
    "Modify ADR file status in docs/adr/ directory",
)

_register(
    "adr_index",
    "Generate the ADR index file.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Read all ADR files and write index.md to docs/adr/",
)

_register(
    "adr_search",
    "Search ADRs by keyword.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "query": {"type": "string", "description": "Search keyword"},
        },
        "required": ["query"],
    },
    "Search ADR files in docs/adr/ directory",
)


# --- Tool Dispatch ---

_TOOL_MAP = {
    "adr_create": _tool_create_adr,
    "adr_list": _tool_list_adrs,
    "adr_show": _tool_show_adr,
    "adr_update_status": _tool_update_status,
    "adr_index": _tool_generate_index,
    "adr_search": _tool_search_adrs,
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
