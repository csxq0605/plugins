# adr-generator (Claude Code Plugin)

Architecture Decision Record generator — pure SKILL.md implementation, guides LLM to create and manage ADRs.

## Installation

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adr-generator/claude-code-plugin
```

## Usage

```
/adr new                                 # Interactive creation
/adr new --template madr                 # MADR template
/adr new --template y-statement          # Y-Statement template
/adr list                                # List all ADRs
/adr list --status accepted              # Filter by status
/adr show 0001                           # Show ADR details
/adr index                               # Generate index
/adr search "database"                   # Search ADRs
```

## Directory Structure

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # Plugin manifest
├── CLAUDE.md                        # Contributor guidelines
├── skills/adr/
│   ├── SKILL.md                     # Main skill (ADR creation + two templates)
│   └── references/
│       ├── adr-principles.md        # ADR best practices
│       └── team-coord-guide.md      # team-coord integration guide
└── README.md / README.en.md
```

## Dependencies

None. Pure SKILL.md instructions, reads/writes `docs/adr/` directory.

## License

MIT
