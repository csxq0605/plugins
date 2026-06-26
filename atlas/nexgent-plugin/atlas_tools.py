"""Atlas Nexgent Plugin — Codebase knowledge atlas tools.

Multi-agent parallel exploration of codebases. Generates architecture docs,
data flow maps, dependency analysis, and living knowledge maps.
"""

import json
import os
import re
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
    ".atlas", ".claude", ".nexgent",
}

_LANG_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".py": "Python", ".rs": "Rust", ".go": "Go", ".java": "Java", ".rb": "Ruby",
    ".php": "PHP", ".c": "C", ".cpp": "C++", ".cs": "C#", ".swift": "Swift",
    ".kt": "Kotlin", ".scala": "Scala", ".lua": "Lua", ".sh": "Shell",
    ".sql": "SQL", ".proto": "Protobuf", ".graphql": "GraphQL",
}

_CONFIG_FILES = {
    "package.json": "Node.js", "pyproject.toml": "Python", "setup.py": "Python",
    "Cargo.toml": "Rust", "go.mod": "Go", "pom.xml": "Java/Maven",
    "build.gradle": "Java/Gradle", "Gemfile": "Ruby", "composer.json": "PHP",
}

_ENTRY_PATTERNS = {
    "main": ["main.py", "main.js", "main.ts", "index.py", "index.js", "index.ts",
             "app.py", "app.js", "app.ts", "server.py", "server.js", "server.ts",
             "cmd/main.go", "src/main.rs"],
    "cli": ["cli.py", "cli.js", "cli.ts", "__main__.py"],
    "config": ["settings.py", "config.py", "config.js", "config.ts", ".env.example"],
}


# ============================================================
# Helpers
# ============================================================

def _walk_project(root: Path, max_depth: int = 10):
    """Walk project directory, yielding (relative_path, is_dir, name)."""
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        # Calculate depth
        rel = Path(dirpath).relative_to(root)
        depth = len(rel.parts)
        if depth >= max_depth:
            dirnames.clear()
            continue

        # Filter excluded directories
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE]

        for d in dirnames:
            yield (str(rel / d), True, d)

        for f in filenames:
            yield (str(rel / f), False, f)


def _count_files_by_lang(root: Path) -> dict[str, int]:
    """Count files grouped by language."""
    counts = defaultdict(int)
    for rel_path, is_dir, name in _walk_project(root):
        if is_dir:
            continue
        ext = Path(name).suffix.lower()
        if ext in _LANG_EXT:
            counts[_LANG_EXT[ext]] += 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def _detect_project_type(root: Path) -> list[str]:
    """Detect project types from config files."""
    types = []
    for config, ptype in _CONFIG_FILES.items():
        if (root / config).exists():
            types.append(ptype)
    return types


def _find_entry_points(root: Path) -> dict[str, list[str]]:
    """Find likely entry points."""
    found = {}
    for category, patterns in _ENTRY_PATTERNS.items():
        matches = []
        for pattern in patterns:
            if (root / pattern).exists():
                matches.append(pattern)
        if matches:
            found[category] = matches
    return found


def _find_modules(root: Path, max_depth: int = 3) -> list[dict]:
    """Find top-level modules/packages."""
    modules = []
    root = root.resolve()

    # Look for src/ first
    src = root / "src"
    if src.is_dir():
        for item in sorted(src.iterdir()):
            if item.is_dir() and item.name not in _EXCLUDE:
                modules.append({
                    "name": item.name,
                    "path": f"src/{item.name}",
                    "type": "package",
                    "files": sum(1 for _ in item.rglob("*") if _.is_file()),
                })
    else:
        # Look at top-level directories
        for item in sorted(root.iterdir()):
            if item.is_dir() and item.name not in _EXCLUDE and not item.name.startswith("."):
                file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                if file_count > 0:
                    modules.append({
                        "name": item.name,
                        "path": item.name,
                        "type": "package",
                        "files": file_count,
                    })

    return modules


def _find_imports_in_file(filepath: Path) -> list[str]:
    """Extract import statements from a file."""
    imports = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        ext = filepath.suffix.lower()

        if ext in (".py",):
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    imports.append(line.split("#")[0].strip())

        elif ext in (".ts", ".tsx", ".js", ".jsx"):
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("import "):
                    imports.append(line.split("//")[0].strip())
                elif line.startswith("require("):
                    imports.append(line.split("//")[0].strip())

        elif ext in (".go",):
            in_import = False
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("import"):
                    in_import = True
                if in_import:
                    if '"' in line:
                        match = re.search(r'"([^"]+)"', line)
                        if match:
                            imports.append(match.group(1))
                    if line == ")":
                        in_import = False

    except Exception:
        pass

    return imports


def _analyze_dependencies(root: Path) -> dict[str, Any]:
    """Analyze project dependencies."""
    deps = {"external": [], "internal": [], "dev": []}

    # Node.js
    pkg_file = root / "package.json"
    if pkg_file.exists():
        try:
            pkg = json.loads(pkg_file.read_text(encoding="utf-8"))
            deps["external"].extend(pkg.get("dependencies", {}).keys())
            deps["dev"].extend(pkg.get("devDependencies", {}).keys())
        except Exception:
            pass

    # Python
    for req_file in root.glob("requirements*.txt"):
        try:
            for line in req_file.read_text(encoding="utf-8").split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    name = re.split(r"[>=<!\[]", line)[0].strip()
                    if name:
                        deps["external"].append(name)
        except Exception:
            pass

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            # Simple extraction of dependencies
            in_deps = False
            for line in content.split("\n"):
                if "dependencies" in line and "[" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith("]"):
                        break
                    match = re.search(r'"([^">=<]+)', line)
                    if match:
                        deps["external"].append(match.group(1).strip())
        except Exception:
            pass

    # Rust
    cargo = root / "Cargo.toml"
    if cargo.exists():
        try:
            content = cargo.read_text(encoding="utf-8")
            in_deps = False
            for line in content.split("\n"):
                if line.strip() in ("[dependencies]", "[dev-dependencies]"):
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith("["):
                        in_deps = False
                        continue
                    match = re.match(r'^(\w[\w-]*)\s*=', line)
                    if match:
                        deps["external"].append(match.group(1))
        except Exception:
            pass

    # Go
    go_mod = root / "go.mod"
    if go_mod.exists():
        try:
            content = go_mod.read_text(encoding="utf-8")
            in_require = False
            for line in content.split("\n"):
                if line.strip().startswith("require"):
                    in_require = True
                    continue
                if in_require:
                    if line.strip() == ")":
                        break
                    parts = line.strip().split()
                    if len(parts) >= 1 and parts[0] != "//":
                        deps["external"].append(parts[0])
        except Exception:
            pass

    # Deduplicate
    deps["external"] = sorted(set(deps["external"]))
    deps["dev"] = sorted(set(deps["dev"]))

    return deps


def _detect_patterns(root: Path) -> dict[str, Any]:
    """Detect coding patterns and conventions."""
    patterns = {
        "naming": [],
        "structure": [],
        "testing": [],
        "error_handling": [],
    }

    # Check for common patterns
    files_checked = 0
    for rel_path, is_dir, name in _walk_project(root, max_depth=4):
        if is_dir or files_checked > 200:
            continue
        files_checked += 1

        ext = Path(name).suffix.lower()
        if ext not in (".py", ".ts", ".js", ".go", ".rs"):
            continue

        try:
            filepath = root / rel_path
            content = filepath.read_text(encoding="utf-8", errors="ignore")[:5000]

            # Naming patterns
            if ext == ".py":
                if re.search(r"class\s+[A-Z]", content):
                    if "PascalCase classes" not in patterns["naming"]:
                        patterns["naming"].append("PascalCase classes")
                if re.search(r"def\s+[a-z_]", content):
                    if "snake_case functions" not in patterns["naming"]:
                        patterns["naming"].append("snake_case functions")

            elif ext in (".ts", ".js"):
                if re.search(r"class\s+[A-Z]", content):
                    if "PascalCase classes" not in patterns["naming"]:
                        patterns["naming"].append("PascalCase classes")
                if re.search(r"(const|let)\s+[a-z]", content):
                    if "camelCase variables" not in patterns["naming"]:
                        patterns["naming"].append("camelCase variables")

            # Error handling patterns
            if "try:" in content or "try {" in content or "try(" in content:
                if "try/catch blocks" not in patterns["error_handling"]:
                    patterns["error_handling"].append("try/catch blocks")

            # Testing patterns
            if "test" in name.lower() or "spec" in name.lower():
                if "test files present" not in patterns["testing"]:
                    patterns["testing"].append("test files present")

        except Exception:
            continue

    # Check for testing framework
    if (root / "jest.config.js").exists() or (root / "jest.config.ts").exists():
        patterns["testing"].append("Jest")
    if (root / "vitest.config.ts").exists():
        patterns["testing"].append("Vitest")
    if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists():
        if "pytest" in str(list(root.glob("pyproject.toml"))):
            patterns["testing"].append("pytest")

    return patterns


def _scan_exports(filepath: Path) -> list[str]:
    """Extract exported symbols from a file."""
    exports = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        ext = filepath.suffix.lower()

        if ext in (".ts", ".js", ".tsx", ".jsx"):
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("export "):
                    # export function/class/const/interface/type
                    match = re.search(r'export\s+(?:default\s+)?(?:function|class|const|let|var|interface|type|enum)\s+(\w+)', line)
                    if match:
                        exports.append(match.group(1))
                    elif "export default" in line:
                        exports.append("default")

        elif ext == ".py":
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("def ") and not line.startswith("def _"):
                    match = re.search(r'def\s+(\w+)', line)
                    if match:
                        exports.append(match.group(1))
                elif line.startswith("class "):
                    match = re.search(r'class\s+(\w+)', line)
                    if match:
                        exports.append(match.group(1))

    except Exception:
        pass

    return exports


# ============================================================
# Tool: atlas_explore
# ============================================================

_register(
    name="atlas_explore",
    description="Explore a codebase and generate raw findings across 5 dimensions: architecture, dependencies, data flows, entry points, and patterns.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root. Defaults to current directory.",
            },
            "depth": {
                "type": "string",
                "enum": ["quick", "normal", "deep"],
                "description": "Exploration depth. Default: normal.",
            },
            "dimensions": {
                "type": "array",
                "items": {"type": "string", "enum": ["architecture", "dependencies", "data_flow", "entry_points", "patterns"]},
                "description": "Specific dimensions to explore. Default: all.",
            },
        },
        "required": [],
    },
    permission_desc="Read project files to analyze codebase structure.",
)


def _explore_architecture(root: Path, depth: str) -> dict:
    """Explore architecture: modules, layers, abstractions."""
    modules = _find_modules(root)
    project_types = _detect_project_type(root)
    languages = _count_files_by_lang(root)

    # Detect layering
    layers = []
    common_layers = {
        "controllers": "Controller/API layer",
        "routes": "Routing layer",
        "services": "Service layer",
        "models": "Data/Model layer",
        "middleware": "Middleware layer",
        "utils": "Utility layer",
        "lib": "Library layer",
        "core": "Core layer",
        "handlers": "Handler layer",
        "repositories": "Repository layer",
        "dto": "Data Transfer Objects",
        "schemas": "Schema definitions",
    }
    for dir_name, layer_desc in common_layers.items():
        if (root / dir_name).is_dir() or (root / "src" / dir_name).is_dir():
            layers.append(layer_desc)

    # Count total files
    total_files = sum(1 for _, is_dir, _ in _walk_project(root) if not is_dir)

    return {
        "project_types": project_types,
        "languages": languages,
        "modules": modules,
        "layers": layers,
        "total_files": total_files,
    }


def _explore_dependencies(root: Path, depth: str) -> dict:
    """Explore dependencies: external, internal graph."""
    deps = _analyze_dependencies(root)

    # Find internal import patterns (sample a few files)
    internal_imports = defaultdict(set)
    files_checked = 0
    max_files = 50 if depth == "quick" else 200 if depth == "normal" else 500

    for rel_path, is_dir, name in _walk_project(root, max_depth=6):
        if is_dir or files_checked >= max_files:
            continue
        ext = Path(name).suffix.lower()
        if ext not in (".py", ".ts", ".js", ".tsx", ".jsx", ".go"):
            continue
        files_checked += 1

        filepath = root / rel_path
        imports = _find_imports_in_file(filepath)
        for imp in imports:
            if imp.startswith(".") or imp.startswith("@/"):
                module = imp.split("/")[0] if not imp.startswith("@") else "/".join(imp.split("/")[:2])
                internal_imports[module].add(rel_path)

    return {
        "external_deps": deps["external"],
        "dev_deps": deps["dev"],
        "internal_graph": {k: sorted(v) for k, v in internal_imports.items()},
    }


def _explore_data_flow(root: Path, depth: str) -> dict:
    """Explore data flows: how data moves through the system."""
    flows = {
        "input_points": [],
        "output_points": [],
        "storage": [],
        "transforms": [],
    }

    for rel_path, is_dir, name in _walk_project(root, max_depth=4):
        if is_dir:
            continue

        ext = Path(name).suffix.lower()
        if ext not in (".py", ".ts", ".js", ".go", ".rs"):
            continue

        try:
            filepath = root / rel_path
            content = filepath.read_text(encoding="utf-8", errors="ignore")[:8000]

            # Input points
            if any(kw in content for kw in ["req.body", "req.params", "req.query", "request.body",
                                              "request.args", "request.form", "sys.argv", "argparse",
                                              "click.", "@app.route", "router.get", "router.post",
                                              "fastapi", "Flask"]):
                flows["input_points"].append(rel_path)

            # Output points
            if any(kw in content for kw in ["res.json", "res.send", "response.json", "return jsonify",
                                              "Response(", "render_template", "redirect("]):
                flows["output_points"].append(rel_path)

            # Storage
            if any(kw in content for kw in ["sqlite", "postgres", "mysql", "mongodb", "redis",
                                              "SQLAlchemy", "Prisma", "Mongoose", "sequelize",
                                              ".save()", ".create(", ".update(", ".delete("]):
                flows["storage"].append(rel_path)

            # Transforms
            if any(kw in content for kw in ["transform(", "map(", "filter(", "reduce(",
                                              "serialize", "deserialize", "validate",
                                              "Schema", "pydantic", "zod", "joi"]):
                flows["transforms"].append(rel_path)

        except Exception:
            continue

    return flows


def _explore_entry_points(root: Path, depth: str) -> dict:
    """Explore entry points: main paths, CLI, API endpoints."""
    entries = _find_entry_points(root)

    # Find API routes
    api_routes = []
    for rel_path, is_dir, name in _walk_project(root, max_depth=5):
        if is_dir:
            continue
        ext = Path(name).suffix.lower()
        if ext not in (".py", ".ts", ".js"):
            continue
        if "route" in name.lower() or "api" in rel_path.lower() or "endpoint" in rel_path.lower():
            api_routes.append(rel_path)

    # Find CLI commands
    cli_commands = []
    for rel_path, is_dir, name in _walk_project(root, max_depth=4):
        if is_dir:
            continue
        if name in ("cli.py", "cli.ts", "cli.js", "__main__.py", "commands"):
            cli_commands.append(rel_path)

    return {
        "entry_points": entries,
        "api_routes": api_routes[:20],  # Limit
        "cli_commands": cli_commands[:20],
    }


def _explore_patterns(root: Path, depth: str) -> dict:
    """Explore coding patterns and conventions."""
    return _detect_patterns(root)


# ============================================================
# Tool: atlas_map
# ============================================================

_register(
    name="atlas_map",
    description="Generate structured architecture documentation from exploration results. Creates docs in .atlas/docs/.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root. Defaults to current directory.",
            },
            "format": {
                "type": "string",
                "enum": ["markdown", "json"],
                "description": "Output format. Default: markdown.",
            },
        },
        "required": [],
    },
    permission_desc="Write documentation files to .atlas/ directory.",
)


def _generate_architecture_doc(exploration: dict) -> str:
    """Generate architecture.md from exploration results."""
    arch = exploration.get("architecture", {})
    lines = [
        "# Architecture",
        "",
        f"**Project type:** {', '.join(arch.get('project_types', ['Unknown']))}",
        f"**Total files:** {arch.get('total_files', 0)}",
        "",
        "## Languages",
        "",
    ]
    for lang, count in arch.get("languages", {}).items():
        lines.append(f"- {lang}: {count} files")

    lines.extend(["", "## Modules", ""])
    for mod in arch.get("modules", []):
        lines.append(f"- **{mod['name']}** (`{mod['path']}`) — {mod['files']} files")

    if arch.get("layers"):
        lines.extend(["", "## Layers", ""])
        for layer in arch["layers"]:
            lines.append(f"- {layer}")

    return "\n".join(lines)


def _generate_deps_doc(exploration: dict) -> str:
    """Generate dependencies.md from exploration results."""
    deps = exploration.get("dependencies", {})
    lines = [
        "# Dependencies",
        "",
        "## External Dependencies",
        "",
    ]
    for dep in deps.get("external_deps", []):
        lines.append(f"- {dep}")

    if deps.get("dev_deps"):
        lines.extend(["", "## Dev Dependencies", ""])
        for dep in deps["dev_deps"]:
            lines.append(f"- {dep}")

    if deps.get("internal_graph"):
        lines.extend(["", "## Internal Module Graph", ""])
        for module, importers in deps["internal_graph"].items():
            lines.append(f"- **{module}** imported by {len(importers)} file(s)")

    return "\n".join(lines)


def _generate_data_flow_doc(exploration: dict) -> str:
    """Generate data-flow.md from exploration results."""
    flows = exploration.get("data_flow", {})
    lines = ["# Data Flow", ""]

    sections = {
        "input_points": "Input Points",
        "output_points": "Output Points",
        "storage": "Storage",
        "transforms": "Transforms",
    }
    for key, title in sections.items():
        items = flows.get(key, [])
        if items:
            lines.extend([f"## {title}", ""])
            for item in items:
                lines.append(f"- `{item}`")
            lines.append("")

    return "\n".join(lines)


def _generate_entry_points_doc(exploration: dict) -> str:
    """Generate entry-points.md from exploration results."""
    entries = exploration.get("entry_points", {})
    lines = ["# Entry Points", ""]

    ep = entries.get("entry_points", {})
    for category, paths in ep.items():
        lines.extend([f"## {category.title()}", ""])
        for p in paths:
            lines.append(f"- `{p}`")
        lines.append("")

    if entries.get("api_routes"):
        lines.extend(["## API Routes", ""])
        for route in entries["api_routes"]:
            lines.append(f"- `{route}`")
        lines.append("")

    if entries.get("cli_commands"):
        lines.extend(["## CLI Commands", ""])
        for cmd in entries["cli_commands"]:
            lines.append(f"- `{cmd}`")
        lines.append("")

    return "\n".join(lines)


def _generate_patterns_doc(exploration: dict) -> str:
    """Generate patterns.md from exploration results."""
    patterns = exploration.get("patterns", {})
    lines = ["# Patterns & Conventions", ""]

    for category, items in patterns.items():
        if items:
            lines.extend([f"## {category.replace('_', ' ').title()}", ""])
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    return "\n".join(lines)


def _generate_summary(exploration: dict) -> str:
    """Generate SUMMARY.md from all exploration results."""
    arch = exploration.get("architecture", {})
    deps = exploration.get("dependencies", {})
    flows = exploration.get("data_flow", {})
    entries = exploration.get("entry_points", {})
    patterns = exploration.get("patterns", {})

    lines = [
        "# Codebase Atlas — Summary",
        "",
        f"**Project type:** {', '.join(arch.get('project_types', ['Unknown']))}",
        f"**Languages:** {', '.join(arch.get('languages', {}).keys())}",
        f"**Total files:** {arch.get('total_files', 0)}",
        f"**External deps:** {len(deps.get('external_deps', []))}",
        "",
        "## Quick Overview",
        "",
        "### Architecture",
        "",
    ]

    if arch.get("modules"):
        lines.append(f"**{len(arch['modules'])} modules** found:")
        for mod in arch["modules"][:5]:
            lines.append(f"- {mod['name']} ({mod['files']} files)")
        if len(arch["modules"]) > 5:
            lines.append(f"- ... and {len(arch['modules']) - 5} more")
        lines.append("")

    if arch.get("layers"):
        lines.extend([f"**Layers:** {', '.join(arch['layers'])}", ""])

    lines.extend([
        "### Data Flow",
        "",
        f"- Input points: {len(flows.get('input_points', []))}",
        f"- Output points: {len(flows.get('output_points', []))}",
        f"- Storage modules: {len(flows.get('storage', []))}",
        "",
        "### Entry Points",
        "",
    ])

    ep = entries.get("entry_points", {})
    for category, paths in ep.items():
        lines.append(f"- {category}: {len(paths)}")

    lines.extend([
        "",
        "### Patterns",
        "",
    ])
    for category, items in patterns.items():
        if items:
            lines.append(f"- {category}: {', '.join(items[:3])}")

    lines.extend(["", "---", "", "See `docs/` for detailed documentation."])

    return "\n".join(lines)


# ============================================================
# Tool: atlas_query
# ============================================================

_register(
    name="atlas_query",
    description="Query the codebase knowledge base to answer questions about architecture, dependencies, data flows, etc.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the codebase root (must have .atlas/ from previous explore/map).",
            },
            "question": {
                "type": "string",
                "description": "Question about the codebase.",
            },
        },
        "required": ["path", "question"],
    },
    permission_desc="Read .atlas/ directory to answer questions.",
)


def _query_atlas(root: Path, question: str) -> dict:
    """Query the atlas knowledge base."""
    atlas_dir = root / ".atlas"
    if not atlas_dir.exists():
        return {"error": "No .atlas/ directory found. Run atlas_explore and atlas_map first."}

    question_lower = question.lower()
    results = []

    # Search through docs
    docs_dir = atlas_dir / "docs"
    if docs_dir.exists():
        for doc_file in docs_dir.glob("*.md"):
            try:
                content = doc_file.read_text(encoding="utf-8")
                # Simple keyword matching
                score = 0
                words = question_lower.split()
                for word in words:
                    if len(word) > 2 and word in content.lower():
                        score += 1

                if score > 0:
                    # Extract relevant sections
                    sections = content.split("\n## ")
                    relevant = []
                    for section in sections:
                        section_lower = section.lower()
                        if any(word in section_lower for word in words if len(word) > 2):
                            relevant.append(section.strip()[:500])

                    if relevant:
                        results.append({
                            "file": doc_file.name,
                            "score": score,
                            "sections": relevant[:3],
                        })
            except Exception:
                continue

    # Also search raw findings
    raw_dir = atlas_dir / "raw"
    if raw_dir.exists():
        for raw_file in raw_dir.glob("*.md"):
            try:
                content = raw_file.read_text(encoding="utf-8")
                words = question_lower.split()
                score = sum(1 for word in words if len(word) > 2 and word in content.lower())

                if score > 0:
                    results.append({
                        "file": f"raw/{raw_file.name}",
                        "score": score,
                        "sections": [content[:500]],
                    })
            except Exception:
                continue

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "question": question,
        "results": results[:5],
        "total_matches": len(results),
    }


# ============================================================
# Tool: atlas_diff
# ============================================================

_register(
    name="atlas_diff",
    description="Compare two codebases or codebase snapshots and identify structural differences.",
    parameters={
        "type": "object",
        "properties": {
            "path1": {
                "type": "string",
                "description": "Path to the first codebase.",
            },
            "path2": {
                "type": "string",
                "description": "Path to the second codebase.",
            },
        },
        "required": ["path1", "path2"],
    },
    permission_desc="Read both codebase directories to compare structure.",
)


def _diff_codebases(path1: Path, path2: Path) -> dict:
    """Compare two codebases structurally."""
    # Explore both
    arch1 = _explore_architecture(path1, "quick")
    arch2 = _explore_architecture(path2, "quick")

    deps1 = _analyze_dependencies(path1)
    deps2 = _analyze_dependencies(path2)

    # Compare languages
    langs1 = set(arch1.get("languages", {}).keys())
    langs2 = set(arch2.get("languages", {}).keys())

    # Compare modules
    mods1 = {m["name"] for m in arch1.get("modules", [])}
    mods2 = {m["name"] for m in arch2.get("modules", [])}

    # Compare deps
    ext1 = set(deps1.get("external", []))
    ext2 = set(deps2.get("external", []))

    return {
        "path1": str(path1),
        "path2": str(path2),
        "languages": {
            "only_in_1": sorted(langs1 - langs2),
            "only_in_2": sorted(langs2 - langs1),
            "common": sorted(langs1 & langs2),
        },
        "modules": {
            "only_in_1": sorted(mods1 - mods2),
            "only_in_2": sorted(mods2 - mods1),
            "common": sorted(mods1 & mods2),
        },
        "dependencies": {
            "only_in_1": sorted(ext1 - ext2),
            "only_in_2": sorted(ext2 - ext1),
            "common": sorted(ext1 & ext2),
        },
        "file_count": {
            "path1": arch1.get("total_files", 0),
            "path2": arch2.get("total_files", 0),
        },
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
    path = args.get("path", ".")

    if name == "atlas_explore":
        root = Path(path).resolve()
        if not root.is_dir():
            return {"error": f"Path not found: {path}"}

        depth = args.get("depth", "normal")
        dimensions = args.get("dimensions", ["architecture", "dependencies", "data_flow", "entry_points", "patterns"])

        result = {"path": str(root), "depth": depth, "dimensions": {}}

        dim_funcs = {
            "architecture": _explore_architecture,
            "dependencies": _explore_dependencies,
            "data_flow": _explore_data_flow,
            "entry_points": _explore_entry_points,
            "patterns": _explore_patterns,
        }

        for dim in dimensions:
            if dim in dim_funcs:
                result["dimensions"][dim] = dim_funcs[dim](root, depth)

        return result

    elif name == "atlas_map":
        root = Path(path).resolve()
        if not root.is_dir():
            return {"error": f"Path not found: {path}"}

        # Run exploration first
        exploration = {}
        for dim_name, dim_func in [
            ("architecture", _explore_architecture),
            ("dependencies", _explore_dependencies),
            ("data_flow", _explore_data_flow),
            ("entry_points", _explore_entry_points),
            ("patterns", _explore_patterns),
        ]:
            exploration[dim_name] = dim_func(root, "normal")

        # Create .atlas directory
        atlas_dir = root / ".atlas"
        raw_dir = atlas_dir / "raw"
        docs_dir = atlas_dir / "docs"
        raw_dir.mkdir(parents=True, exist_ok=True)
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Write raw findings
        for dim, data in exploration.items():
            (raw_dir / f"{dim}.md").write_text(
                f"# {dim.title()}\n\n```json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```\n",
                encoding="utf-8"
            )

        # Generate docs
        docs = {
            "architecture.md": _generate_architecture_doc(exploration),
            "dependencies.md": _generate_deps_doc(exploration),
            "data-flow.md": _generate_data_flow_doc(exploration),
            "entry-points.md": _generate_entry_points_doc(exploration),
            "patterns.md": _generate_patterns_doc(exploration),
        }

        for filename, content in docs.items():
            (docs_dir / filename).write_text(content, encoding="utf-8")

        # Generate summary
        summary = _generate_summary(exploration)
        (atlas_dir / "SUMMARY.md").write_text(summary, encoding="utf-8")

        # Generate index
        index_lines = [
            "# Codebase Atlas",
            "",
            "## Summary",
            "",
            "See [SUMMARY.md](SUMMARY.md) for an overview.",
            "",
            "## Documentation",
            "",
        ]
        for filename in docs:
            name = filename.replace(".md", "").replace("-", " ").title()
            index_lines.append(f"- [{name}](docs/{filename})")

        index_lines.extend(["", "## Raw Findings", ""])
        for dim in exploration:
            index_lines.append(f"- [{dim.title()}](raw/{dim}.md)")

        (atlas_dir / "index.md").write_text("\n".join(index_lines), encoding="utf-8")

        return {
            "status": "success",
            "output_dir": str(atlas_dir),
            "docs_generated": list(docs.keys()),
            "summary": summary[:500],
        }

    elif name == "atlas_query":
        root = Path(path).resolve()
        question = args.get("question", "")
        if not question:
            return {"error": "Question is required."}
        return _query_atlas(root, question)

    elif name == "atlas_diff":
        path1 = Path(args.get("path1", "")).resolve()
        path2 = Path(args.get("path2", "")).resolve()
        if not path1.is_dir():
            return {"error": f"Path1 not found: {path1}"}
        if not path2.is_dir():
            return {"error": f"Path2 not found: {path2}"}
        return _diff_codebases(path1, path2)

    else:
        return {"error": f"Unknown tool: {name}"}
