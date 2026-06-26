# dep-audit (Claude Code Plugin)

Dependency vulnerability audit — pure SKILL.md implementation, guides LLM to scan dependencies and query OSV vulnerability database.

## Installation

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/dep-audit/claude-code-plugin
```

## Usage

```
/audit                                   # Full audit
/audit --quick                           # Quick scan (direct deps only)
/audit --focus vulnerabilities          # Focus on vulnerabilities
/audit --focus outdated                 # Focus on outdated deps
/audit --focus licenses                 # Focus on licenses
/audit --severity critical              # Critical only
```

## Directory Structure

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # Plugin manifest
├── CLAUDE.md                        # Contributor guidelines
├── skills/audit/
│   ├── SKILL.md                     # Main skill (5-phase audit flow)
│   └── references/
│       ├── vuln-severity.md         # Vulnerability severity scoring
│       └── team-coord-guide.md      # team-coord integration guide
└── README.md / README.en.md
```

## Dependencies

None. Pure SKILL.md instructions, uses curl for OSV API calls.

## License

MIT
