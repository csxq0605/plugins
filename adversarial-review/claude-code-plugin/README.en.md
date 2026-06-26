# adversarial-review (Claude Code Plugin)

Multi-perspective adversarial code review — pure SKILL.md implementation, no external dependencies.

## Installation

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adversarial-review/claude-code-plugin
```

## Usage

```
/adversarial-review                          # Quick mode: 6 perspectives sequentially
/adversarial-review --deep                   # Deep mode: detailed analysis + fix suggestions
/adversarial-review --fix                    # Fix mode: auto-fix + verify
/adversarial-review src/api                  # Specify path
/adversarial-review --perspective security   # Single perspective
```

## Directory Structure

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # Plugin manifest
├── CLAUDE.md                        # Contributor guidelines
├── skills/adversarial-review/
│   ├── SKILL.md                     # Main skill (6-perspective review flow)
│   └── references/
│       ├── patterns.md              # 200+ security detection regex patterns
│       ├── risk-dimensions.md       # 6 decay risk dimensions
│       └── team-coord-guide.md      # team-coord integration guide
└── README.md / README.en.md
```

## Dependencies

None. Pure SKILL.md instructions executed by Claude Code LLM.

## License

MIT
