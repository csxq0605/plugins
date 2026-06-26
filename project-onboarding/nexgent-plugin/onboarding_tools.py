"""
project-onboarding Nexgent Plugin — Project analysis and onboarding tools.
Scans project structure, tech stack, build system, test framework, CI/CD, code style.
"""

import json
import os
import re
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

_LANG_EXTENSIONS = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".py": "Python", ".rs": "Rust", ".go": "Go", ".java": "Java", ".kt": "Kotlin",
    ".rb": "Ruby", ".php": "PHP", ".c": "C", ".h": "C", ".cpp": "C++", ".hpp": "C++",
    ".cs": "C#", ".swift": "Swift", ".dart": "Dart", ".lua": "Lua", ".zig": "Zig",
    ".ex": "Elixir", ".erl": "Erlang", ".hs": "Haskell", ".scala": "Scala",
    ".clj": "Clojure", ".ml": "OCaml",
}

_FRAMEWORK_DEPS = {
    # JS/TS Frontend
    "react": "React", "vue": "Vue", "@angular/core": "Angular", "svelte": "Svelte",
    "solid-js": "Solid.js", "next": "Next.js", "nuxt": "Nuxt", "gatsby": "Gatsby",
    "@sveltejs/kit": "SvelteKit", "remix": "Remix", "astro": "Astro",
    # JS/TS Backend
    "express": "Express", "fastify": "Fastify", "koa": "Koa", "hono": "Hono",
    "@nestjs/core": "NestJS", "hapi": "Hapi",
    # Python
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI", "tornado": "Tornado",
    "torch": "PyTorch", "tensorflow": "TensorFlow", "transformers": "HF Transformers",
    # Rust
    "actix-web": "Actix Web", "axum": "Axum", "rocket": "Rocket", "tokio": "Tokio",
    "serde": "Serde", "tauri": "Tauri",
    # Go
    "github.com/gin-gonic/gin": "Gin", "github.com/labstack/echo": "Echo",
}

_TEST_DEPS = {
    "jest": "Jest", "vitest": "Vitest", "mocha": "Mocha", "ava": "AVA",
    "@playwright/test": "Playwright", "cypress": "Cypress",
    "@testing-library/react": "React Testing Library",
    "pytest": "pytest", "nose2": "nose2", "behave": "behave",
}

_CI_FILES = {
    ".github/workflows": "GitHub Actions",
    ".gitlab-ci.yml": "GitLab CI",
    ".circleci/config.yml": "CircleCI",
    "Jenkinsfile": "Jenkins",
    ".travis.yml": "Travis CI",
    ".drone.yml": "Drone CI",
    "azure-pipelines.yml": "Azure Pipelines",
    "bitbucket-pipelines.yml": "Bitbucket Pipelines",
    "cloudbuild.yaml": "Google Cloud Build",
}

_LINTER_FILES = {
    ".eslintrc.js": "ESLint", ".eslintrc.json": "ESLint", ".eslintrc.yml": "ESLint",
    "eslint.config.js": "ESLint", "eslint.config.mjs": "ESLint",
    ".flake8": "flake8", ".pylintrc": "Pylint",
    "rustfmt.toml": "rustfmt", ".rustfmt.toml": "rustfmt",
    ".clang-format": "clang-format", ".golangci.yml": "golangci-lint",
    ".rubocop.yml": "RuboCop",
}

_FORMATTER_FILES = {
    ".prettierrc": "Prettier", "prettier.config.js": "Prettier",
    ".editorconfig": "EditorConfig", ".stylelintrc": "Stylelint",
}

_HOOK_FILES = {
    ".husky/pre-commit": "Husky", ".pre-commit-config.yaml": "pre-commit",
    ".lefthook.yml": "Lefthook",
}

_LOCK_FILES = {
    "package-lock.json": "npm", "yarn.lock": "yarn", "pnpm-lock.yaml": "pnpm",
    "bun.lockb": "bun", "Pipfile.lock": "pipenv", "poetry.lock": "poetry",
    "uv.lock": "uv", "Cargo.lock": "cargo", "go.sum": "go modules",
    "Gemfile.lock": "bundler", "composer.lock": "composer",
}

_MONOREPO_FILES = {
    "lerna.json": "Lerna", "pnpm-workspace.yaml": "pnpm workspaces",
    "nx.json": "Nx", "turbo.json": "Turborepo", "rush.json": "Rush",
}

_DEPLOY_FILES = {
    "Dockerfile": "Docker", "docker-compose.yml": "Docker Compose",
    "kustomization.yaml": "Kustomize", "serverless.yml": "Serverless Framework",
    "fly.toml": "Fly.io", "vercel.json": "Vercel", "netlify.toml": "Netlify",
    "render.yaml": "Render", "railway.json": "Railway",
    "Pulumi.yaml": "Pulumi",
}


# --- Scanning Functions ---

def _count_files(root: Path, exts: list[str], exclude: list[str] = None) -> int:
    """Count files with given extensions, excluding certain directories."""
    exclude = exclude or ["node_modules", "__pycache__", ".git", "target", ".venv", "venv", "dist", "build", ".next"]
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for f in filenames:
            if any(f.endswith(ext) for ext in exts):
                count += 1
    return count


def _detect_languages(root: Path) -> dict[str, int]:
    """Detect languages by file extension and count."""
    ext_groups = {}
    for ext, lang in _LANG_EXTENSIONS.items():
        ext_groups.setdefault(lang, []).append(ext)

    result = {}
    for lang, exts in ext_groups.items():
        count = _count_files(root, exts)
        if count > 0:
            result[lang] = count

    return dict(sorted(result.items(), key=lambda x: -x[1]))


def _read_json(path: Path) -> dict:
    """Read a JSON file safely."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _detect_frameworks_from_package_json(root: Path) -> list[dict]:
    """Detect frameworks from package.json."""
    pkg_path = root / "package.json"
    if not pkg_path.exists():
        return []

    pkg = _read_json(pkg_path)
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))

    frameworks = []
    for dep, name in _FRAMEWORK_DEPS.items():
        if dep in all_deps:
            frameworks.append({"name": name, "version": all_deps[dep], "type": "dependency"})

    return frameworks


def _detect_frameworks_from_requirements(root: Path) -> list[dict]:
    """Detect frameworks from requirements.txt or pyproject.toml."""
    frameworks = []

    # requirements.txt
    for req_file in root.glob("requirements*.txt"):
        try:
            content = req_file.read_text(encoding="utf-8").lower()
            for dep, name in _FRAMEWORK_DEPS.items():
                if dep in content:
                    frameworks.append({"name": name, "version": "*", "type": "dependency"})
        except Exception:
            pass

    # pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8").lower()
            for dep, name in _FRAMEWORK_DEPS.items():
                if dep in content:
                    frameworks.append({"name": name, "version": "*", "type": "dependency"})
        except Exception:
            pass

    return frameworks


def _detect_frameworks_from_cargo(root: Path) -> list[dict]:
    """Detect frameworks from Cargo.toml."""
    cargo = root / "Cargo.toml"
    if not cargo.exists():
        return []

    try:
        content = cargo.read_text(encoding="utf-8").lower()
        frameworks = []
        for dep, name in _FRAMEWORK_DEPS.items():
            if dep in content:
                frameworks.append({"name": name, "version": "*", "type": "dependency"})
        return frameworks
    except Exception:
        return []


def _detect_frameworks(root: Path) -> list[dict]:
    """Detect all frameworks."""
    frameworks = []
    frameworks.extend(_detect_frameworks_from_package_json(root))
    frameworks.extend(_detect_frameworks_from_requirements(root))
    frameworks.extend(_detect_frameworks_from_cargo(root))
    # Deduplicate
    seen = set()
    unique = []
    for f in frameworks:
        if f["name"] not in seen:
            seen.add(f["name"])
            unique.append(f)
    return unique


def _detect_test_frameworks(root: Path) -> list[str]:
    """Detect test frameworks."""
    frameworks = []

    # From package.json
    pkg = _read_json(root / "package.json")
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))
    for dep, name in _TEST_DEPS.items():
        if dep in all_deps:
            frameworks.append(name)

    # From requirements
    for req_file in root.glob("requirements*.txt"):
        try:
            content = req_file.read_text(encoding="utf-8").lower()
            for dep, name in _TEST_DEPS.items():
                if dep in content and name not in frameworks:
                    frameworks.append(name)
        except Exception:
            pass

    return frameworks


def _detect_package_manager(root: Path) -> str:
    """Detect package manager from lock files."""
    for lock_file, manager in _LOCK_FILES.items():
        if (root / lock_file).exists():
            return manager
    return "unknown"


def _detect_scripts(root: Path) -> dict[str, str]:
    """Detect scripts from package.json."""
    pkg = _read_json(root / "package.json")
    return pkg.get("scripts", {})


def _detect_ci(root: Path) -> list[dict]:
    """Detect CI/CD configurations."""
    ci_configs = []

    # GitHub Actions (special case - directory)
    gh_workflows = root / ".github" / "workflows"
    if gh_workflows.exists():
        workflows = []
        for f in gh_workflows.glob("*.yml"):
            try:
                content = f.read_text(encoding="utf-8")
                name_match = re.search(r"name:\s*(.+)", content)
                workflows.append({
                    "file": f.name,
                    "name": name_match.group(1).strip() if name_match else f.stem,
                })
            except Exception:
                workflows.append({"file": f.name, "name": f.stem})
        ci_configs.append({"platform": "GitHub Actions", "workflows": workflows})

    # Other CI files
    for ci_file, platform in _CI_FILES.items():
        if ci_file == ".github/workflows":
            continue
        if (root / ci_file).exists():
            ci_configs.append({"platform": platform, "file": ci_file})

    return ci_configs


def _detect_code_style(root: Path) -> dict:
    """Detect code style tools."""
    style = {"linters": [], "formatters": [], "hooks": [], "commit_conventions": []}

    for f, tool in _LINTER_FILES.items():
        if (root / f).exists():
            style["linters"].append(tool)

    # Check pyproject.toml for ruff/pylint
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "[tool.ruff]" in content:
                style["linters"].append("Ruff")
            if "[tool.pylint]" in content:
                style["linters"].append("Pylint")
            if "[tool.black]" in content:
                style["formatters"].append("Black")
            if "[tool.isort]" in content:
                style["formatters"].append("isort")
        except Exception:
            pass

    for f, tool in _FORMATTER_FILES.items():
        if (root / f).exists():
            style["formatters"].append(tool)

    for f, tool in _HOOK_FILES.items():
        if (root / f).exists():
            style["hooks"].append(tool)

    # Commit conventions
    pkg = _read_json(root / "package.json")
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))

    commit_tools = {
        "@commitlint/cli": "Commitlint",
        "standard-version": "Standard Version",
        "semantic-release": "Semantic Release",
        "@release-it/release-it": "Release It",
    }
    for dep, name in commit_tools.items():
        if dep in all_deps:
            style["commit_conventions"].append(name)

    if (root / "commitlint.config.js").exists() or (root / ".commitlintrc").exists():
        if "Commitlint" not in style["commit_conventions"]:
            style["commit_conventions"].append("Commitlint")

    # Deduplicate
    for key in style:
        style[key] = list(dict.fromkeys(style[key]))

    return style


def _detect_deploy(root: Path) -> list[str]:
    """Detect deployment configurations."""
    platforms = []
    for f, platform in _DEPLOY_FILES.items():
        if (root / f).exists():
            platforms.append(platform)

    # Check k8s directory
    k8s_dir = root / "k8s"
    if k8s_dir.exists():
        platforms.append("Kubernetes")

    # Check helm directory
    helm_dir = root / "helm"
    if helm_dir.exists():
        platforms.append("Helm")

    # Check terraform
    tf_dir = root / "terraform"
    if tf_dir.exists() and list(tf_dir.glob("*.tf")):
        platforms.append("Terraform")

    return platforms


def _detect_monorepo(root: Path) -> dict | None:
    """Detect monorepo setup."""
    for f, tool in _MONOREPO_FILES.items():
        if (root / f).exists():
            return {"tool": tool, "config": f}

    # Check for workspaces in package.json
    pkg = _read_json(root / "package.json")
    if "workspaces" in pkg:
        return {"tool": "npm/yarn workspaces", "config": "package.json"}

    return None


def _read_env_example(root: Path) -> list[dict]:
    """Read .env.example or .env.template."""
    for env_file in [".env.example", ".env.template", ".env.local.example"]:
        path = root / env_file
        if path.exists():
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
                vars = []
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, _, value = line.partition("=")
                        vars.append({
                            "name": key.strip(),
                            "default": value.strip().strip('"').strip("'"),
                            "required": value.strip() == "" or value.strip() in ('""', "''"),
                        })
                return vars
            except Exception:
                pass
    return []


def _get_directory_tree(root: Path, max_depth: int = 3) -> str:
    """Get a directory tree string."""
    exclude = {"node_modules", "__pycache__", ".git", "target", ".venv", "venv",
               "dist", "build", ".next", ".nuxt", ".tox", ".mypy_cache", ".pytest_cache"}
    lines = []

    def _walk(path: Path, prefix: str, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return

        entries = [e for e in entries if e.name not in exclude]
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


def _get_readme_summary(root: Path) -> str:
    """Extract description from README."""
    for readme in ["README.md", "README.rst", "README"]:
        path = root / readme
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                # Get first non-empty, non-heading line
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        return line[:200]
            except Exception:
                pass
    return ""


# --- Tool Implementations ---

def _tool_scan_project(args: dict) -> dict:
    """Full project scan."""
    root = Path(args.get("path", ".")).resolve()
    if not root.exists():
        return {"error": f"Path does not exist: {root}"}

    depth = args.get("depth", 3)

    # Phase 1: Identity
    pkg = _read_json(root / "package.json")
    project_name = pkg.get("name", root.name)
    readme_summary = _get_readme_summary(root)

    # Phase 2: Languages
    languages = _detect_languages(root)

    # Phase 3: Frameworks
    frameworks = _detect_frameworks(root)

    # Phase 4: Build/Run
    scripts = _detect_scripts(root)
    package_manager = _detect_package_manager(root)

    # Phase 5: Test
    test_frameworks = _detect_test_frameworks(root)

    # Phase 6: CI/CD
    ci_configs = _detect_ci(root)

    # Phase 7: Code Style
    code_style = _detect_code_style(root)

    # Extras
    deploy = _detect_deploy(root)
    monorepo = _detect_monorepo(root)
    env_vars = _read_env_example(root)
    tree = _get_directory_tree(root, depth)

    return {
        "name": project_name,
        "description": readme_summary,
        "path": str(root),
        "languages": languages,
        "frameworks": frameworks,
        "package_manager": package_manager,
        "scripts": scripts,
        "test_frameworks": test_frameworks,
        "ci": ci_configs,
        "code_style": code_style,
        "deploy": deploy,
        "monorepo": monorepo,
        "env_vars": env_vars,
        "tree": tree,
    }


def _tool_detect_languages(args: dict) -> dict:
    """Detect programming languages in the project."""
    root = Path(args.get("path", ".")).resolve()
    return {"languages": _detect_languages(root)}


def _tool_detect_frameworks(args: dict) -> dict:
    """Detect frameworks and libraries."""
    root = Path(args.get("path", ".")).resolve()
    return {"frameworks": _detect_frameworks(root)}


def _tool_detect_ci(args: dict) -> dict:
    """Detect CI/CD configurations."""
    root = Path(args.get("path", ".")).resolve()
    return {"ci": _detect_ci(root)}


def _tool_detect_code_style(args: dict) -> dict:
    """Detect code style tools (linters, formatters, hooks)."""
    root = Path(args.get("path", ".")).resolve()
    return {"code_style": _detect_code_style(root)}


def _tool_get_tree(args: dict) -> dict:
    """Get directory tree structure."""
    root = Path(args.get("path", ".")).resolve()
    depth = args.get("depth", 3)
    return {"tree": _get_directory_tree(root, depth)}


def _tool_generate_onboarding(args: dict) -> str:
    """Generate onboarding markdown document."""
    scan = _tool_scan_project(args)
    if "error" in scan:
        return scan["error"]

    lines = []
    lines.append(f"# Project Onboarding: {scan['name']}")
    lines.append("")

    if scan["description"]:
        lines.append(f"> {scan['description']}")
        lines.append("")

    # Languages
    if scan["languages"]:
        lines.append("## Languages")
        for lang, count in list(scan["languages"].items())[:5]:
            lines.append(f"- **{lang}**: {count} files")
        lines.append("")

    # Frameworks
    if scan["frameworks"]:
        lines.append("## Frameworks & Libraries")
        for f in scan["frameworks"]:
            ver = f.get("version", "*")
            lines.append(f"- {f['name']} `{ver}`")
        lines.append("")

    # Package Manager
    if scan["package_manager"] != "unknown":
        lines.append(f"## Package Manager\n- {scan['package_manager']}\n")

    # Scripts
    if scan["scripts"]:
        lines.append("## Key Commands")
        lines.append("| Command | Purpose |")
        lines.append("|---------|---------|")
        important = ["install", "dev", "start", "build", "test", "lint", "format", "check"]
        for cmd, script in scan["scripts"].items():
            if any(k in cmd.lower() for k in important):
                lines.append(f"| `{cmd}` | `{script}` |")
        lines.append("")

    # Test
    if scan["test_frameworks"]:
        lines.append(f"## Test Frameworks\n")
        for tf in scan["test_frameworks"]:
            lines.append(f"- {tf}")
        lines.append("")

    # CI
    if scan["ci"]:
        lines.append("## CI/CD")
        for ci in scan["ci"]:
            lines.append(f"- {ci['platform']}")
            if "workflows" in ci:
                for wf in ci["workflows"]:
                    lines.append(f"  - {wf['name']} (`{wf['file']}`)")
        lines.append("")

    # Code Style
    style = scan.get("code_style", {})
    if any(style.values()):
        lines.append("## Code Style")
        if style.get("linters"):
            lines.append(f"- **Linters**: {', '.join(style['linters'])}")
        if style.get("formatters"):
            lines.append(f"- **Formatters**: {', '.join(style['formatters'])}")
        if style.get("hooks"):
            lines.append(f"- **Git Hooks**: {', '.join(style['hooks'])}")
        if style.get("commit_conventions"):
            lines.append(f"- **Commit Conventions**: {', '.join(style['commit_conventions'])}")
        lines.append("")

    # Deploy
    if scan["deploy"]:
        lines.append(f"## Deployment\n- {', '.join(scan['deploy'])}\n")

    # Monorepo
    if scan["monorepo"]:
        lines.append(f"## Monorepo\n- {scan['monorepo']['tool']} (`{scan['monorepo']['config']}`)\n")

    # Env vars
    if scan["env_vars"]:
        lines.append("## Environment Variables")
        lines.append("| Variable | Required | Default |")
        lines.append("|----------|----------|---------|")
        for v in scan["env_vars"][:20]:
            req = "Yes" if v["required"] else "No"
            lines.append(f"| `{v['name']}` | {req} | `{v['default']}` |")
        lines.append("")

    # Tree
    lines.append("## Directory Structure")
    lines.append(f"```\n{scan['tree']}\n```")
    lines.append("")

    return "\n".join(lines)


# --- Register Tools ---

_register(
    "onboarding_scan",
    "Full project scan — detects languages, frameworks, build system, test framework, CI/CD, code style, and generates structured report.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "depth": {"type": "integer", "description": "Directory tree depth (default: 3)"},
        },
    },
    "Scan project structure and configuration files",
)

_register(
    "onboarding_detect_languages",
    "Detect programming languages by file extension and count.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Count source files by language",
)

_register(
    "onboarding_detect_frameworks",
    "Detect frameworks and libraries from dependency files.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Read package.json, requirements.txt, Cargo.toml for framework detection",
)

_register(
    "onboarding_detect_ci",
    "Detect CI/CD platform and workflow configurations.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Read CI configuration files",
)

_register(
    "onboarding_detect_code_style",
    "Detect code style tools — linters, formatters, git hooks, commit conventions.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
        },
    },
    "Read linter and formatter configuration files",
)

_register(
    "onboarding_get_tree",
    "Get directory tree structure.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "depth": {"type": "integer", "description": "Maximum depth (default: 3)"},
        },
    },
    "List directory structure",
)

_register(
    "onboarding_generate",
    "Generate a complete onboarding markdown document.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Project root path (default: current directory)"},
            "depth": {"type": "integer", "description": "Directory tree depth (default: 3)"},
        },
    },
    "Full project scan and onboarding document generation",
)


# --- Tool Dispatch ---

_TOOL_MAP = {
    "onboarding_scan": _tool_scan_project,
    "onboarding_detect_languages": _tool_detect_languages,
    "onboarding_detect_frameworks": _tool_detect_frameworks,
    "onboarding_detect_ci": _tool_detect_ci,
    "onboarding_detect_code_style": _tool_detect_code_style,
    "onboarding_get_tree": _tool_get_tree,
    "onboarding_generate": _tool_generate_onboarding,
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
