# Claude Code & Nexgent Plugins

A collection of independent plugins for Claude Code and Nexgent, designed for multi-agent workflows and enhanced developer productivity.

## Plugins

### team-coord
Two subskills for agent team coordination — lead orchestrates (pure coordinator), teammate guides each worker. Covers inbox sync, WHAT vs HOW spawn, unified reports.

- **Claude Code**: `claude-code-plugin/`
- **Nexgent**: `nexgent-plugin/`

### adversarial-review
Multi-perspective code review with 6 analysis lenses (security, performance, architecture, code quality, test quality, API design), unified findings format, health scoring (0-100), and iterative fix loop.

- **Claude Code**: `claude-code-plugin/`
- **Nexgent**: `nexgent-plugin/`

### lit-review
Systematic literature review pipeline — multi-source academic search (arXiv, Semantic Scholar), citation network analysis, subtopic decomposition, and structured review synthesis.

- **Claude Code**: `claude-code-plugin/`
- **Nexgent**: `nexgent-plugin/`

### project-onboarding
Automated project onboarding — scans structure, tech stack, build system, test framework, CI/CD, code style, and generates structured onboarding docs. 7 detection tools for comprehensive project analysis.

- **Claude Code**: `claude-code-plugin/`
- **Nexgent**: `nexgent-plugin/`

### dep-audit
Dependency vulnerability audit — scans dependency files (npm, PyPI, crates.io, Go, Maven), queries OSV vulnerability database, detects outdated packages, flags license risks, and generates structured audit reports with health scoring.

- **Claude Code**: `claude-code-plugin/`
- **Nexgent**: `nexgent-plugin/`

### session-memory
Persistent cross-session memory — saves and restores conversation context, key decisions, findings, and progress. Supports tagging, search, auto-expiry, and team-coord handoff. 9 memory tools for comprehensive context management.

- **Claude Code**: `claude-code-plugin/`
- **Nexgent**: `nexgent-plugin/`

### adr-generator
Architecture Decision Record generator — creates, manages, and indexes ADRs with multiple templates (MADR, Y-Statement), status tracking, and cross-referencing. 6 ADR tools for decision documentation.

- **Claude Code**: `claude-code-plugin/`
- **Nexgent**: `nexgent-plugin/`

## Installation

### Claude Code

```bash
# Install from GitHub
claude install-plugin github:csxq0605/plugins
```

### Nexgent

```bash
# Clone and install
git clone https://github.com/csxq0605/plugins.git
cd plugins

# Install plugin by copying to Nexgent plugins directory
cp -r adversarial-review/nexgent-plugin ~/.nexgent/plugins/adversarial-review
cp -r lit-review/nexgent-plugin ~/.nexgent/plugins/lit-review
cp -r project-onboarding/nexgent-plugin ~/.nexgent/plugins/project-onboarding
cp -r dep-audit/nexgent-plugin ~/.nexgent/plugins/dep-audit
cp -r session-memory/nexgent-plugin ~/.nexgent/plugins/session-memory
cp -r adr-generator/nexgent-plugin ~/.nexgent/plugins/adr-generator
```

## Semantic Scholar API

The lit-review plugin supports Semantic Scholar for enhanced paper search and citation analysis.

### Claude Code Version

Configure via:
```bash
python bin/lit-search.py set-key YOUR_API_KEY
```

### Nexgent Version

Configure via environment variable or config file:
```bash
export SEMANTIC_SCHOLAR_API_KEY=YOUR_API_KEY
```

Config is stored at `~/.lit-review/config.json` and shared between both versions.

## Development

Each plugin follows the dual-version structure:
- `plugin-name/claude-code-plugin/` — Pure SKILL.md files for Claude Code
- `plugin-name/nexgent-plugin/` — Python tools + SKILL.md for Nexgent
