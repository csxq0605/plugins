# lit-review (Claude Code Plugin)

Systematic literature review — 3 skills (search/analyze/synthesize) + CLI search tool.

## Installation

```bash
claude install-plugin github:csxq0605/plugins
```

## Skills

| Skill | Purpose |
|-------|---------|
| `/lit-review:search` | Search arXiv + Semantic Scholar |
| `/lit-review:analyze` | Deep analysis of a single paper |
| `/lit-review:synthesize` | Generate literature review |

## Semantic Scholar API Configuration

```bash
python bin/lit-search.py set-key YOUR_API_KEY
```

Config is stored at `~/.lit-review/config.json`, shared between both versions.

## Directory Structure

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # Plugin manifest (3 skills)
├── CLAUDE.md                        # Contributor guidelines
├── bin/lit-search.py                # CLI search tool (arXiv + Semantic Scholar)
├── skills/
│   ├── search/SKILL.md              # Search skill
│   ├── analyze/SKILL.md             # Analysis skill
│   └── synthesize/SKILL.md          # Synthesis skill
└── README.md / README.en.md
```

## Dependencies

None. `lit-search.py` uses Python standard library (urllib, json, xml).

## License

MIT
