"""Migrator Nexgent Plugin — Framework migration assistant tools.

Analyze codebase, generate migration plans, execute step by step with verification.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from collections import defaultdict

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


# ============================================================
# Constants
# ============================================================

_EXCLUDE = {
    "node_modules", "__pycache__", ".git", "target", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "coverage", ".tox", ".mypy_cache",
    ".migrations", ".claude", ".nexgent",
}

# Known migration patterns for common frameworks
KNOWN_MIGRATIONS = {
    "react": {
        "17→18": {
            "breaking_changes": [
                "ReactDOM.render replaced with createRoot",
                "Automatic batching in all contexts",
                "Strict Mode behavior changes",
                "useEffect cleanup timing changes",
                "Suspense for data fetching",
            ],
            "deprecated_apis": [
                "ReactDOM.render",
                "ReactDOM.hydrate",
                "ReactDOM.unmountComponentAtNode",
                "ReactDOM.findDOMNode",
            ],
            "file_patterns": ["*.jsx", "*.tsx", "*.js", "*.ts"],
            "search_terms": ["ReactDOM.render", "ReactDOM.hydrate", "componentWillMount",
                            "componentWillReceiveProps", "componentWillUpdate"],
        },
    },
    "express": {
        "4→5": {
            "breaking_changes": [
                "Removed app.del() (use app.delete())",
                "Removed app.param(fn) (use app.param(name, fn))",
                "Changed req.host to exclude port",
                "Changed req.query to use qs module by default",
                "Removed res.json(obj, status) (use res.status(status).json(obj))",
            ],
            "deprecated_apis": [
                "app.del()",
                "app.param(fn)",
                "res.json(obj, status)",
                "res.send(status)",
            ],
            "file_patterns": ["*.js", "*.ts"],
            "search_terms": ["app.del(", "app.param(", "res.json(", "res.send("],
        },
    },
    "python": {
        "3.9→3.12": {
            "breaking_changes": [
                "Removed distutils module",
                "Changed typing.Dict, List, etc. to dict, list",
                "Removed imp module",
                "Changed asyncio.get_event_loop() behavior",
                "Removed deprecated unittest methods",
            ],
            "deprecated_apis": [
                "typing.Dict", "typing.List", "typing.Set", "typing.Tuple",
                "distutils",
                "imp",
                "asyncio.get_event_loop()",
            ],
            "file_patterns": ["*.py"],
            "search_terms": ["from typing import", "import distutils", "import imp",
                            "asyncio.get_event_loop()"],
        },
    },
    "lodash": {
        "4→odash": {
            "breaking_changes": [
                "Different module structure",
                "Some methods renamed",
                "Different chaining behavior",
            ],
            "deprecated_apis": [],
            "file_patterns": ["*.js", "*.ts", "*.jsx", "*.tsx"],
            "search_terms": ["from 'lodash'", "require('lodash')", "import _ from 'lodash'"],
        },
    },
}


# ============================================================
# Helpers
# ============================================================

def _get_migrations_dir(root: Path = None) -> Path:
    """Get the migrations directory relative to project root."""
    base = root if root else Path.cwd()
    return (base / ".migrations").resolve()


def _ensure_migrations_dir(root: Path = None) -> Path:
    """Ensure migrations directory exists."""
    migrations_dir = _get_migrations_dir(root)
    migrations_dir.mkdir(parents=True, exist_ok=True)
    return migrations_dir


def _load_index(migrations_dir: Path) -> dict:
    """Load the migration index."""
    index_file = migrations_dir / "index.json"
    if index_file.exists():
        try:
            return json.loads(index_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"migrations": [], "next_id": 1}


def _save_index(migrations_dir: Path, index: dict):
    """Save the migration index."""
    (migrations_dir / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def _now_iso() -> str:
    """Get current time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def _walk_project(root: Path, max_depth: int = 10):
    """Walk project directory, yielding (relative_path, is_dir, name)."""
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        depth = len(rel.parts)
        if depth >= max_depth:
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE]
        for d in dirnames:
            yield (str(rel / d), True, d)
        for f in filenames:
            yield (str(rel / f), False, f)


def _find_files_by_pattern(root: Path, patterns: list[str]) -> list[str]:
    """Find files matching glob patterns."""
    found = []
    for pattern in patterns:
        for f in root.rglob(pattern):
            if not any(ex in str(f) for ex in _EXCLUDE):
                found.append(str(f.relative_to(root)))
    return sorted(set(found))


def _search_in_files(root: Path, terms: list[str], file_patterns: list[str]) -> dict[str, list[dict]]:
    """Search for terms in files, returning matches with line numbers."""
    results = defaultdict(list)
    checked = 0

    for rel_path, is_dir, name in _walk_project(root, max_depth=8):
        if is_dir:
            continue

        # Check if file matches patterns
        ext = Path(name).suffix.lower()
        if not any(ext == p.replace("*", "") for p in file_patterns):
            continue

        checked += 1
        if checked > 500:  # Limit
            break

        try:
            filepath = root / rel_path
            content = filepath.read_text(encoding="utf-8", errors="ignore")

            for term in terms:
                if term in content:
                    # Find line numbers
                    for i, line in enumerate(content.split("\n"), 1):
                        if term in line:
                            results[term].append({
                                "file": rel_path,
                                "line": i,
                                "content": line.strip()[:200],
                            })
        except Exception:
            continue

    return dict(results)


def _detect_package_versions(root: Path) -> dict[str, str]:
    """Detect package versions from config files."""
    versions = {}

    # Node.js
    pkg_file = root / "package.json"
    if pkg_file.exists():
        try:
            pkg = json.loads(pkg_file.read_text(encoding="utf-8"))
            all_deps = {}
            all_deps.update(pkg.get("dependencies", {}))
            all_deps.update(pkg.get("devDependencies", {}))
            for name, version in all_deps.items():
                versions[name] = version
        except Exception:
            pass

    # Python
    for req_file in root.glob("requirements*.txt"):
        try:
            for line in req_file.read_text(encoding="utf-8").split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    match = re.match(r'^([\w-]+)\s*([>=<~!]+.*)?', line)
                    if match:
                        versions[match.group(1)] = match.group(2) or "any"
        except Exception:
            pass

    return versions


# ============================================================
# Tool: migrator_analyze
# ============================================================

_register(
    name="migrator_analyze",
    description="Analyze a codebase for migration targets. Identifies affected files, deprecated APIs, and breaking changes.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root.",
            },
            "source": {
                "type": "string",
                "description": "Source framework/library (e.g., react, express, python).",
            },
            "source_version": {
                "type": "string",
                "description": "Source version (e.g., 17, 4, 3.9).",
            },
            "target_version": {
                "type": "string",
                "description": "Target version (e.g., 18, 5, 3.12).",
            },
            "custom_terms": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Custom terms to search for in addition to known migration patterns.",
            },
        },
        "required": ["path", "source", "source_version", "target_version"],
    },
    permission_desc="Read project files to analyze migration targets.",
)


def _migrator_analyze(args: dict) -> dict:
    """Analyze codebase for migration targets."""
    root = Path(args["path"]).resolve()
    if not root.is_dir():
        return {"error": f"Path not found: {args['path']}"}

    source = args["source"].lower()
    source_version = args["source_version"]
    target_version = args["target_version"]
    migration_key = f"{source_version}→{target_version}"

    # Get known migration info
    migration_info = KNOWN_MIGRATIONS.get(source, {}).get(migration_key, {})

    # Detect current package versions
    versions = _detect_package_versions(root)

    # Find affected files
    file_patterns = migration_info.get("file_patterns", ["*.js", "*.ts", "*.py", "*.jsx", "*.tsx"])
    affected_files = _find_files_by_pattern(root, file_patterns)

    # Search for deprecated APIs
    search_terms = migration_info.get("search_terms", [])
    if "custom_terms" in args:
        search_terms.extend(args["custom_terms"])

    matches = _search_in_files(root, search_terms, file_patterns) if search_terms else {}

    # Calculate effort
    total_matches = sum(len(v) for v in matches.values())
    if total_matches < 10:
        effort = "low"
        effort_hours = "1-4"
    elif total_matches < 50:
        effort = "medium"
        effort_hours = "4-16"
    else:
        effort = "high"
        effort_hours = "16+"

    # Risk assessment
    breaking_changes = migration_info.get("breaking_changes", [])
    if len(breaking_changes) > 5:
        risk = "high"
    elif len(breaking_changes) > 2:
        risk = "medium"
    else:
        risk = "low"

    analysis = {
        "source": source,
        "migration": migration_key,
        "current_versions": {k: v for k, v in versions.items()
                           if source in k.lower()},
        "affected_files_count": len(affected_files),
        "affected_files_sample": affected_files[:20],
        "deprecated_usage": {
            term: {
                "count": len(occurrences),
                "files": list(set(o["file"] for o in occurrences))[:5],
            }
            for term, occurrences in matches.items()
        },
        "breaking_changes": breaking_changes,
        "deprecated_apis": migration_info.get("deprecated_apis", []),
        "effort": effort,
        "effort_hours": effort_hours,
        "risk": risk,
        "total_matches": total_matches,
    }

    # Save analysis to .migrations directory
    migrations_dir = _ensure_migrations_dir(root)
    index = _load_index(migrations_dir)
    migration_id = f"{source}-{source_version}-to-{target_version}"
    migration_dir = migrations_dir / migration_id
    migration_dir.mkdir(parents=True, exist_ok=True)

    (migration_dir / "analysis.json").write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Update index
    index["migrations"].append({
        "id": migration_id,
        "source": source,
        "migration": migration_key,
        "status": "analyzed",
        "created_at": _now_iso(),
    })
    _save_index(migrations_dir, index)

    return analysis


# ============================================================
# Tool: migrator_plan
# ============================================================

_register(
    name="migrator_plan",
    description="Generate a step-by-step migration plan from analysis results.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root.",
            },
            "strategy": {
                "type": "string",
                "enum": ["incremental", "big-bang"],
                "description": "Migration strategy. Default: incremental.",
            },
            "custom_steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "files": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name", "description"],
                },
                "description": "Custom migration steps to include.",
            },
        },
        "required": ["path"],
    },
    permission_desc="Generate migration plan in .migrations/ directory.",
)


def _migrator_plan(args: dict) -> dict:
    """Generate a migration plan."""
    root = Path(args["path"]).resolve()
    if not root.is_dir():
        return {"error": f"Path not found: {args['path']}"}

    migrations_dir = _ensure_migrations_dir(root)

    # Find the latest analysis
    index = _load_index(migrations_dir)
    if not index["migrations"]:
        return {"error": "No analysis found. Run migrator_analyze first."}

    latest = index["migrations"][-1]
    migration_id = latest["id"]
    migration_dir = migrations_dir / migration_id

    # Load analysis
    analysis_file = migration_dir / "analysis.json"
    if not analysis_file.exists():
        return {"error": "Analysis file not found."}
    analysis = json.loads(analysis_file.read_text(encoding="utf-8"))

    strategy = args.get("strategy", "incremental")

    # Generate steps based on analysis
    steps = []
    step_id = 1

    # Group deprecated usage by type
    deprecated = analysis.get("deprecated_usage", {})

    if strategy == "incremental":
        # Step 1: Update imports/requires
        if any("import" in term.lower() or "require" in term.lower() for term in deprecated):
            steps.append({
                "id": step_id,
                "name": "Update imports and requires",
                "description": f"Update import statements for {analysis['migration']}",
                "files": [],
                "verification": "Run linting and type checks",
                "rollback": "git checkout -- .",
            })
            step_id += 1

        # Step 2-N: Address each deprecated API
        for term, info in deprecated.items():
            steps.append({
                "id": step_id,
                "name": f"Migrate {term}",
                "description": f"Replace {term} with its modern equivalent",
                "files": info.get("files", []),
                "count": info.get("count", 0),
                "verification": f"Run tests that use {term}",
                "rollback": f"git checkout -- {' '.join(info.get('files', [])[:3])}",
            })
            step_id += 1

        # Final step: Full verification
        steps.append({
            "id": step_id,
            "name": "Full verification",
            "description": "Run complete test suite and verify all changes",
            "files": [],
            "verification": "npm test / pytest / full test suite",
            "rollback": "git checkout -- .",
        })

    else:  # big-bang
        steps.append({
            "id": 1,
            "name": "Apply all migration changes",
            "description": f"Apply all changes for {analysis['migration']} at once",
            "files": analysis.get("affected_files_sample", []),
            "verification": "Full test suite",
            "rollback": "git checkout -- .",
        })

    # Add custom steps if provided
    if "custom_steps" in args:
        for custom in args["custom_steps"]:
            steps.append({
                "id": step_id,
                "name": custom["name"],
                "description": custom["description"],
                "files": custom.get("files", []),
                "verification": "Manual verification",
                "rollback": "Manual rollback",
            })
            step_id += 1

    # Save plan
    plan = {
        "migration_id": migration_id,
        "source": analysis["source"],
        "migration": analysis["migration"],
        "strategy": strategy,
        "total_steps": len(steps),
        "steps": steps,
        "created_at": _now_iso(),
    }

    plan_file = migration_dir / "plan.json"
    plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    # Initialize progress
    progress = {
        "migration_id": migration_id,
        "current_step": 0,
        "completed_steps": [],
        "failed_steps": [],
        "status": "planned",
        "started_at": None,
        "updated_at": _now_iso(),
    }
    (migration_dir / "progress.json").write_text(
        json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Update index
    for mig in index["migrations"]:
        if mig["id"] == migration_id:
            mig["status"] = "planned"
            mig["total_steps"] = len(steps)
            break
    _save_index(migrations_dir, index)

    # Save step details
    steps_dir = migration_dir / "steps"
    steps_dir.mkdir(exist_ok=True)
    for step in steps:
        step_md = [
            f"# Step {step['id']}: {step['name']}",
            "",
            f"**Description:** {step['description']}",
            "",
            f"**Verification:** {step['verification']}",
            f"**Rollback:** {step['rollback']}",
            "",
        ]
        if step.get("files"):
            step_md.extend(["## Affected Files", ""])
            for f in step["files"]:
                step_md.append(f"- `{f}`")

        (steps_dir / f"step-{step['id']}.md").write_text("\n".join(step_md), encoding="utf-8")

    return {
        "migration_id": migration_id,
        "strategy": strategy,
        "total_steps": len(steps),
        "steps": [{"id": s["id"], "name": s["name"]} for s in steps],
    }


# ============================================================
# Tool: migrator_execute
# ============================================================

_register(
    name="migrator_execute",
    description="Execute a migration step and track progress.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root.",
            },
            "step_id": {
                "type": "integer",
                "description": "Step ID to execute. If not provided, executes the next pending step.",
            },
            "action": {
                "type": "string",
                "enum": ["execute", "continue", "retry"],
                "description": "Action to take. Default: execute.",
            },
        },
        "required": ["path"],
    },
    permission_desc="Execute migration step and update progress.",
)


def _migrator_execute(args: dict) -> dict:
    """Execute a migration step."""
    root = Path(args.get("path", ".")).resolve()
    migrations_dir = _ensure_migrations_dir(root)
    index = _load_index(migrations_dir)

    if not index["migrations"]:
        return {"error": "No migration found. Run migrator_analyze and migrator_plan first."}

    latest = index["migrations"][-1]
    migration_id = latest["id"]
    migration_dir = migrations_dir / migration_id

    # Load plan and progress
    plan_file = migration_dir / "plan.json"
    progress_file = migration_dir / "progress.json"

    if not plan_file.exists():
        return {"error": "No plan found. Run migrator_plan first."}

    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    progress = json.loads(progress_file.read_text(encoding="utf-8"))

    # Determine which step to execute
    action = args.get("action", "execute")
    if action == "continue":
        step_id = progress["current_step"] + 1
    elif action == "retry":
        if progress["failed_steps"]:
            step_id = progress["failed_steps"][-1]
        else:
            step_id = progress["current_step"]
    else:
        step_id = args.get("step_id", progress["current_step"] + 1)

    # Find the step
    step = None
    for s in plan["steps"]:
        if s["id"] == step_id:
            step = s
            break

    if not step:
        return {"error": f"Step {step_id} not found in plan."}

    # Update progress
    progress["current_step"] = step_id
    progress["status"] = "in_progress"
    if not progress["started_at"]:
        progress["started_at"] = _now_iso()
    progress["updated_at"] = _now_iso()

    if step_id not in progress["completed_steps"]:
        progress["completed_steps"].append(step_id)
    if step_id in progress["failed_steps"]:
        progress["failed_steps"].remove(step_id)

    (migration_dir / "progress.json").write_text(
        json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Update index
    for mig in index["migrations"]:
        if mig["id"] == migration_id:
            mig["status"] = "in_progress"
            mig["current_step"] = step_id
            mig["completed_steps"] = len(progress["completed_steps"])
            break
    _save_index(migrations_dir, index)

    return {
        "migration_id": migration_id,
        "step_id": step_id,
        "step_name": step["name"],
        "status": "executed",
        "verification": step.get("verification", "Manual verification needed"),
        "rollback": step.get("rollback", "Manual rollback"),
        "progress": f"{len(progress['completed_steps'])}/{plan['total_steps']}",
    }


# ============================================================
# Tool: migrator_verify
# ============================================================

_register(
    name="migrator_verify",
    description="Verify that a migration step was successful.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root.",
            },
            "step_id": {
                "type": "integer",
                "description": "Step ID to verify. If not provided, verifies the current step.",
            },
            "result": {
                "type": "string",
                "enum": ["pass", "fail", "partial"],
                "description": "Verification result. Default: pass.",
            },
            "notes": {
                "type": "string",
                "description": "Verification notes.",
            },
        },
        "required": ["path"],
    },
    permission_desc="Record verification result in migration progress.",
)


def _migrator_verify(args: dict) -> dict:
    """Verify a migration step."""
    root = Path(args.get("path", ".")).resolve()
    migrations_dir = _ensure_migrations_dir(root)
    index = _load_index(migrations_dir)

    if not index["migrations"]:
        return {"error": "No migration found."}

    latest = index["migrations"][-1]
    migration_id = latest["id"]
    migration_dir = migrations_dir / migration_id

    # Load progress
    progress_file = migration_dir / "progress.json"
    progress = json.loads(progress_file.read_text(encoding="utf-8"))

    step_id = args.get("step_id", progress["current_step"])
    result = args.get("result", "pass")

    # Load verification results
    verification_file = migration_dir / "verification.json"
    if verification_file.exists():
        verification = json.loads(verification_file.read_text(encoding="utf-8"))
    else:
        verification = {"steps": {}}

    verification["steps"][str(step_id)] = {
        "result": result,
        "notes": args.get("notes", ""),
        "verified_at": _now_iso(),
    }

    verification_file.write_text(
        json.dumps(verification, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Update progress if failed
    if result == "fail":
        if step_id not in progress["failed_steps"]:
            progress["failed_steps"].append(step_id)
        if step_id in progress["completed_steps"]:
            progress["completed_steps"].remove(step_id)
        progress["status"] = "failed"
    elif result == "pass":
        if step_id in progress["failed_steps"]:
            progress["failed_steps"].remove(step_id)

    progress["updated_at"] = _now_iso()
    (migration_dir / "progress.json").write_text(
        json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return {
        "migration_id": migration_id,
        "step_id": step_id,
        "result": result,
        "status": progress["status"],
    }


# ============================================================
# Tool: migrator_status
# ============================================================

_register(
    name="migrator_status",
    description="Check migration progress.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root.",
            },
            "detailed": {
                "type": "boolean",
                "description": "Show detailed per-step status. Default: false.",
            },
        },
        "required": [],
    },
    permission_desc="Read migration progress from .migrations/ directory.",
)


def _migrator_status(args: dict) -> dict:
    """Check migration status."""
    root = Path(args.get("path", ".")).resolve()
    migrations_dir = _ensure_migrations_dir(root)
    index = _load_index(migrations_dir)

    if not index["migrations"]:
        return {"error": "No migrations found."}

    latest = index["migrations"][-1]
    migration_id = latest["id"]
    migration_dir = migrations_dir / migration_id

    # Load plan and progress
    plan_file = migration_dir / "plan.json"
    progress_file = migration_dir / "progress.json"

    if not plan_file.exists() or not progress_file.exists():
        return {
            "migration_id": migration_id,
            "status": "analyzed",
            "message": "Analysis complete. Run migrator_plan to generate a plan.",
        }

    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    progress = json.loads(progress_file.read_text(encoding="utf-8"))

    # Calculate progress
    total = plan["total_steps"]
    completed = len(progress["completed_steps"])
    failed = len(progress["failed_steps"])
    percentage = round((completed / total) * 100) if total > 0 else 0

    result = {
        "migration_id": migration_id,
        "source": latest.get("source", "unknown"),
        "migration": latest.get("migration", "unknown"),
        "status": progress["status"],
        "progress": f"{completed}/{total} ({percentage}%)",
        "current_step": progress["current_step"],
        "completed_steps": completed,
        "failed_steps": failed,
        "started_at": progress.get("started_at"),
        "updated_at": progress.get("updated_at"),
    }

    if args.get("detailed"):
        result["steps"] = []
        for step in plan["steps"]:
            step_status = "pending"
            if step["id"] in progress["completed_steps"]:
                step_status = "completed"
            elif step["id"] in progress["failed_steps"]:
                step_status = "failed"
            elif step["id"] == progress["current_step"]:
                step_status = "in_progress"

            result["steps"].append({
                "id": step["id"],
                "name": step["name"],
                "status": step_status,
            })

    return result


# ============================================================
# Tool: migrator_rollback
# ============================================================

_register(
    name="migrator_rollback",
    description="Rollback a migration step.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root.",
            },
            "step_id": {
                "type": "integer",
                "description": "Step ID to rollback. If not provided, rolls back the last completed step.",
            },
            "action": {
                "type": "string",
                "enum": ["step", "all"],
                "description": "Rollback single step or all steps. Default: step.",
            },
        },
        "required": ["path"],
    },
    permission_desc="Rollback migration step and update progress.",
)


def _migrator_rollback(args: dict) -> dict:
    """Rollback a migration step."""
    root = Path(args.get("path", ".")).resolve()
    migrations_dir = _ensure_migrations_dir(root)
    index = _load_index(migrations_dir)

    if not index["migrations"]:
        return {"error": "No migration found."}

    latest = index["migrations"][-1]
    migration_id = latest["id"]
    migration_dir = migrations_dir / migration_id

    # Load plan and progress
    plan_file = migration_dir / "plan.json"
    progress_file = migration_dir / "progress.json"

    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    progress = json.loads(progress_file.read_text(encoding="utf-8"))

    action = args.get("action", "step")

    if action == "all":
        # Rollback all steps
        rolled_back = list(progress["completed_steps"])
        progress["completed_steps"] = []
        progress["failed_steps"] = []
        progress["current_step"] = 0
        progress["status"] = "rolled_back"
    else:
        step_id = args.get("step_id")
        if not step_id:
            # Rollback last completed step
            if progress["completed_steps"]:
                step_id = progress["completed_steps"][-1]
            else:
                return {"error": "No completed steps to rollback."}

        rolled_back = [step_id]
        if step_id in progress["completed_steps"]:
            progress["completed_steps"].remove(step_id)
        progress["status"] = "rolled_back"

    progress["updated_at"] = _now_iso()
    (migration_dir / "progress.json").write_text(
        json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Update index
    for mig in index["migrations"]:
        if mig["id"] == migration_id:
            mig["status"] = "rolled_back"
            break
    _save_index(migrations_dir, index)

    return {
        "migration_id": migration_id,
        "rolled_back_steps": rolled_back,
        "status": "rolled_back",
        "remaining_completed": len(progress["completed_steps"]),
    }


# ============================================================
# Tool dispatch
# ============================================================

def get_tools() -> list[dict]:
    """Return all registered tool definitions."""
    return TOOL_DEFS


def get_permissions() -> dict:
    """Return tool permission descriptions."""
    return PERMISSIONS


def call_tool(name: str, args: dict) -> Any:
    """Dispatch a tool call."""
    dispatch = {
        "migrator_analyze": _migrator_analyze,
        "migrator_plan": _migrator_plan,
        "migrator_execute": _migrator_execute,
        "migrator_verify": _migrator_verify,
        "migrator_status": _migrator_status,
        "migrator_rollback": _migrator_rollback,
    }

    if name in dispatch:
        return dispatch[name](args)
    else:
        return {"error": f"Unknown tool: {name}"}
