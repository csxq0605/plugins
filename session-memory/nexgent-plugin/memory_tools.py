"""
session-memory Nexgent Plugin — Persistent cross-session memory tools.
Saves and restores conversation context, key decisions, findings, and progress.
"""

import json
import os
import re
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


# --- Config ---

_MEMORY_DIR = ".memory"
_INDEX_FILE = "index.json"
_DEFAULT_EXPIRY = {
    "session": 30,  # days
    "decision": None,  # never
    "finding": 90,
    "handoff": 7,
}


# --- Helpers ---

def _get_memory_dir(project_path: str = ".") -> Path:
    """Get the memory directory path."""
    return Path(project_path).resolve() / _MEMORY_DIR


def _ensure_dirs(mem_dir: Path):
    """Ensure memory directories exist."""
    (mem_dir / "sessions").mkdir(parents=True, exist_ok=True)
    (mem_dir / "decisions").mkdir(parents=True, exist_ok=True)
    (mem_dir / "findings").mkdir(parents=True, exist_ok=True)
    (mem_dir / "handoffs").mkdir(parents=True, exist_ok=True)


def _load_index(mem_dir: Path) -> dict:
    """Load the memory index."""
    index_path = mem_dir / _INDEX_FILE
    if index_path.exists():
        try:
            return json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "version": "1.0",
        "last_updated": None,
        "memories": [],
        "tag_index": {},
    }


def _save_index(mem_dir: Path, index: dict):
    """Save the memory index."""
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    (mem_dir / _INDEX_FILE).write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _generate_id(mem_type: str) -> str:
    """Generate a unique memory ID."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H%M%S")
    return f"{mem_type}-{date_str}-{timestamp}"


def _save_memory(mem_dir: Path, index: dict, memory: dict) -> str:
    """Save a memory to disk and update index."""
    _ensure_dirs(mem_dir)

    mem_type = memory["type"]
    mem_id = memory["id"]

    # Determine subdirectory
    subdir = {
        "session": "sessions",
        "decision": "decisions",
        "finding": "findings",
        "handoff": "handoffs",
    }.get(mem_type, "sessions")

    # Save memory file
    file_path = mem_dir / subdir / f"{mem_id}.json"
    file_path.write_text(
        json.dumps(memory, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Update index
    index_entry = {
        "id": mem_id,
        "type": mem_type,
        "timestamp": memory.get("timestamp"),
        "tags": memory.get("tags", []),
        "summary": memory.get("summary", memory.get("title", "")),
        "path": f"{subdir}/{mem_id}.json",
    }

    index["memories"].append(index_entry)

    # Update tag index
    for tag in memory.get("tags", []):
        if tag not in index["tag_index"]:
            index["tag_index"][tag] = []
        index["tag_index"][tag].append(mem_id)

    _save_index(mem_dir, index)
    return mem_id


def _load_memory(mem_dir: Path, memory_path: str) -> dict | None:
    """Load a memory from disk."""
    full_path = mem_dir / memory_path
    if full_path.exists():
        try:
            return json.loads(full_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def _search_memories(index: dict, query: str = None, tags: list[str] = None,
                      mem_type: str = None, limit: int = 10) -> list[dict]:
    """Search memories by query, tags, and type."""
    results = []

    for entry in index.get("memories", []):
        # Filter by type
        if mem_type and entry.get("type") != mem_type:
            continue

        # Filter by tags
        if tags:
            entry_tags = set(entry.get("tags", []))
            if not any(t in entry_tags for t in tags):
                continue

        # Filter by query (search in summary)
        if query:
            summary = entry.get("summary", "").lower()
            if query.lower() not in summary:
                # Also check tags
                tag_match = any(query.lower() in t.lower() for t in entry.get("tags", []))
                if not tag_match:
                    continue

        results.append(entry)

    # Sort by timestamp (most recent first)
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return results[:limit]


def _cleanup_expired(mem_dir: Path, index: dict) -> int:
    """Remove expired memories."""
    now = datetime.now(timezone.utc)
    removed = 0

    active_memories = []
    for entry in index.get("memories", []):
        mem_type = entry.get("type", "session")
        expiry_days = _DEFAULT_EXPIRY.get(mem_type)

        if expiry_days is None:
            # Never expires
            active_memories.append(entry)
            continue

        timestamp = entry.get("timestamp")
        if timestamp:
            try:
                mem_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if now - mem_time > timedelta(days=expiry_days):
                    # Remove file
                    file_path = mem_dir / entry.get("path", "")
                    if file_path.exists():
                        file_path.unlink()
                    removed += 1
                    continue
            except Exception:
                pass

        active_memories.append(entry)

    if removed > 0:
        index["memories"] = active_memories
        # Rebuild tag index
        tag_index = {}
        for entry in active_memories:
            for tag in entry.get("tags", []):
                if tag not in tag_index:
                    tag_index[tag] = []
                tag_index[tag].append(entry["id"])
        index["tag_index"] = tag_index
        _save_index(mem_dir, index)

    return removed


# --- Tool Implementations ---

def _tool_save_session(args: dict) -> dict:
    """Save a session memory."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    memory = {
        "id": _generate_id("session"),
        "type": "session",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tags": args.get("tags", []),
        "summary": args.get("summary", ""),
        "context": {
            "files_modified": args.get("files_modified", []),
            "decisions": args.get("decisions", []),
            "blockers": args.get("blockers", []),
            "next_steps": args.get("next_steps", []),
        },
        "key_findings": args.get("key_findings", []),
    }

    # Set expiry
    expires = args.get("expires")
    if expires:
        memory["expires"] = expires

    mem_id = _save_memory(mem_dir, index, memory)
    return {"id": mem_id, "status": "saved"}


def _tool_save_decision(args: dict) -> dict:
    """Save a decision memory."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    memory = {
        "id": _generate_id("decision"),
        "type": "decision",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tags": args.get("tags", []),
        "title": args.get("title", ""),
        "rationale": args.get("rationale", ""),
        "alternatives_considered": args.get("alternatives", []),
        "impact": args.get("impact", []),
    }

    mem_id = _save_memory(mem_dir, index, memory)
    return {"id": mem_id, "status": "saved"}


def _tool_save_finding(args: dict) -> dict:
    """Save a finding memory."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    memory = {
        "id": _generate_id("finding"),
        "type": "finding",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tags": args.get("tags", []),
        "title": args.get("title", ""),
        "description": args.get("description", ""),
        "evidence": args.get("evidence", ""),
        "impact": args.get("impact", ""),
    }

    mem_id = _save_memory(mem_dir, index, memory)
    return {"id": mem_id, "status": "saved"}


def _tool_save_handoff(args: dict) -> dict:
    """Save a handoff memory."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    memory = {
        "id": _generate_id("handoff"),
        "type": "handoff",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "from_session": args.get("from_session", ""),
        "to_role": args.get("to_role", ""),
        "summary": args.get("summary", ""),
        "completed": args.get("completed", []),
        "remaining": args.get("remaining", []),
        "context": args.get("context", {}),
    }

    mem_id = _save_memory(mem_dir, index, memory)
    return {"id": mem_id, "status": "saved"}


def _tool_recall(args: dict) -> list[dict]:
    """Search and recall memories."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    query = args.get("query")
    tags = args.get("tags")
    mem_type = args.get("type")
    limit = args.get("limit", 10)

    entries = _search_memories(index, query, tags, mem_type, limit)

    # Load full memories
    results = []
    for entry in entries:
        full = _load_memory(mem_dir, entry.get("path", ""))
        if full:
            results.append(full)
        else:
            results.append(entry)

    return results


def _tool_list_memories(args: dict) -> list[dict]:
    """List all memories."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    mem_type = args.get("type")
    memories = index.get("memories", [])

    if mem_type:
        memories = [m for m in memories if m.get("type") == mem_type]

    # Sort by timestamp
    memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return memories


def _tool_delete_memory(args: dict) -> dict:
    """Delete a memory by ID."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    memory_id = args.get("id")
    if not memory_id:
        return {"error": "Memory ID is required"}

    # Find and remove from index
    removed = None
    remaining = []
    for entry in index.get("memories", []):
        if entry["id"] == memory_id:
            removed = entry
            # Remove file
            file_path = mem_dir / entry.get("path", "")
            if file_path.exists():
                file_path.unlink()
        else:
            remaining.append(entry)

    if not removed:
        return {"error": f"Memory not found: {memory_id}"}

    index["memories"] = remaining

    # Rebuild tag index
    tag_index = {}
    for entry in remaining:
        for tag in entry.get("tags", []):
            if tag not in tag_index:
                tag_index[tag] = []
            tag_index[tag].append(entry["id"])
    index["tag_index"] = tag_index

    _save_index(mem_dir, index)
    return {"deleted": memory_id}


def _tool_cleanup(args: dict) -> dict:
    """Clean up expired memories."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    removed = _cleanup_expired(mem_dir, index)
    return {"removed": removed, "remaining": len(index.get("memories", []))}


def _tool_generate_handoff(args: dict) -> str:
    """Generate a handoff document from recent memories."""
    project_path = args.get("path", ".")
    mem_dir = _get_memory_dir(project_path)
    index = _load_index(mem_dir)

    # Get recent memories
    to_role = args.get("to_role", "next developer")
    limit = args.get("limit", 5)

    recent = _search_memories(index, limit=limit)

    lines = []
    lines.append(f"# Handoff Document")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"To: {to_role}")
    lines.append("")

    # Recent sessions
    sessions = [m for m in recent if m.get("type") == "session"]
    if sessions:
        lines.append("## Recent Sessions")
        for s in sessions:
            lines.append(f"- **{s.get('summary', 'No summary')}** ({s.get('timestamp', '')[:10]})")
            if s.get("context", {}).get("next_steps"):
                for step in s["context"]["next_steps"]:
                    lines.append(f"  - Next: {step}")
        lines.append("")

    # Recent decisions
    decisions = [m for m in recent if m.get("type") == "decision"]
    if decisions:
        lines.append("## Key Decisions")
        for d in decisions:
            lines.append(f"- **{d.get('title', 'No title')}**: {d.get('rationale', '')}")
        lines.append("")

    # Blockers
    blockers = []
    for s in sessions:
        blockers.extend(s.get("context", {}).get("blockers", []))
    if blockers:
        lines.append("## Blockers")
        for b in blockers:
            lines.append(f"- {b}")
        lines.append("")

    # Remaining work
    remaining = []
    for s in sessions:
        remaining.extend(s.get("context", {}).get("next_steps", []))
    if remaining:
        lines.append("## Remaining Work")
        for r in remaining:
            lines.append(f"- {r}")
        lines.append("")

    return "\n".join(lines)


# --- Register Tools ---

_register(
    "memory_save_session",
    "Save a session memory — records what happened in a conversation session.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "summary": {"type": "string", "description": "One-line summary of the session"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Searchable tags"},
            "files_modified": {"type": "array", "items": {"type": "string"}, "description": "Files that were modified"},
            "decisions": {"type": "array", "items": {"type": "string"}, "description": "Key decisions made"},
            "blockers": {"type": "array", "items": {"type": "string"}, "description": "Issues encountered"},
            "next_steps": {"type": "array", "items": {"type": "string"}, "description": "Planned next actions"},
            "key_findings": {"type": "array", "items": {"type": "string"}, "description": "Important discoveries"},
        },
        "required": ["summary"],
    },
    "Write session memory to .memory/ directory",
)

_register(
    "memory_save_decision",
    "Save a decision memory — records a specific architectural or design decision.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "title": {"type": "string", "description": "Decision title"},
            "rationale": {"type": "string", "description": "Why this decision was made"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Searchable tags"},
            "alternatives": {"type": "array", "items": {"type": "string"}, "description": "Other options considered"},
            "impact": {"type": "array", "items": {"type": "string"}, "description": "What changes as a result"},
        },
        "required": ["title", "rationale"],
    },
    "Write decision memory to .memory/ directory",
)

_register(
    "memory_save_finding",
    "Save a finding memory — records an important discovery or insight.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "title": {"type": "string", "description": "Finding title"},
            "description": {"type": "string", "description": "Detailed description"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Searchable tags"},
            "evidence": {"type": "string", "description": "Supporting evidence"},
            "impact": {"type": "string", "description": "Why this matters"},
        },
        "required": ["title", "description"],
    },
    "Write finding memory to .memory/ directory",
)

_register(
    "memory_save_handoff",
    "Save a handoff memory — records a handoff between sessions or team members.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "to_role": {"type": "string", "description": "Target role or person"},
            "summary": {"type": "string", "description": "Handoff summary"},
            "from_session": {"type": "string", "description": "Source session ID"},
            "completed": {"type": "array", "items": {"type": "string"}, "description": "Completed tasks"},
            "remaining": {"type": "array", "items": {"type": "string"}, "description": "Remaining tasks"},
            "context": {"type": "object", "description": "Additional context"},
        },
        "required": ["summary"],
    },
    "Write handoff memory to .memory/ directory",
)

_register(
    "memory_recall",
    "Search and recall memories by query, tags, or type.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "query": {"type": "string", "description": "Search query"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
            "type": {"type": "string", "description": "Filter by type (session, decision, finding, handoff)"},
            "limit": {"type": "integer", "description": "Maximum results (default: 10)"},
        },
    },
    "Read memories from .memory/ directory",
)

_register(
    "memory_list",
    "List all memories, optionally filtered by type.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "type": {"type": "string", "description": "Filter by type (session, decision, finding, handoff)"},
        },
    },
    "Read memory index from .memory/ directory",
)

_register(
    "memory_delete",
    "Delete a memory by ID.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "id": {"type": "string", "description": "Memory ID to delete"},
        },
        "required": ["id"],
    },
    "Delete memory file from .memory/ directory",
)

_register(
    "memory_cleanup",
    "Clean up expired memories based on default expiry policies.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Delete expired memory files from .memory/ directory",
)

_register(
    "memory_generate_handoff",
    "Generate a handoff document from recent memories.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "to_role": {"type": "string", "description": "Target role (default: 'next developer')"},
            "limit": {"type": "integer", "description": "Number of recent memories to include (default: 5)"},
        },
    },
    "Read memories and generate handoff document",
)


# --- Tool Dispatch ---

_TOOL_MAP = {
    "memory_save_session": _tool_save_session,
    "memory_save_decision": _tool_save_decision,
    "memory_save_finding": _tool_save_finding,
    "memory_save_handoff": _tool_save_handoff,
    "memory_recall": _tool_recall,
    "memory_list": _tool_list_memories,
    "memory_delete": _tool_delete_memory,
    "memory_cleanup": _tool_cleanup,
    "memory_generate_handoff": _tool_generate_handoff,
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
