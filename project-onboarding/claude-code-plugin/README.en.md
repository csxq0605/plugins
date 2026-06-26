# project-onboarding (Claude Code Plugin)

Automated project onboarding — pure SKILL.md implementation, guides LLM to scan projects and generate onboarding docs.

## Installation

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/project-onboarding/claude-code-plugin
```

## Usage

```
/onboarding                              # Full scan
/onboarding --quick                      # Quick overview
/onboarding --focus tech-stack           # Focus on tech stack
/onboarding --focus build                # Focus on build system
/onboarding --focus test                 # Focus on testing
/onboarding --focus ci                   # Focus on CI/CD
/onboarding --focus code-style           # Focus on code style
```

## Directory Structure

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # Plugin manifest
├── CLAUDE.md                        # Contributor guidelines
├── skills/onboarding/
│   ├── SKILL.md                     # Main skill (7-phase scan flow)
│   └── references/
│       ├── detection-patterns.md    # Language/framework/CI/style detection patterns
│       └── team-coord-guide.md      # team-coord integration guide
└── README.md / README.en.md
```

## Dependencies

None. Pure SKILL.md instructions.

## License

MIT
