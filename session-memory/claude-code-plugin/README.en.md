# session-memory (Claude Code Plugin)

Persistent cross-session memory — pure SKILL.md implementation, guides LLM to manage `.memory/` directory.

## Installation

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/session-memory/claude-code-plugin
```

## Usage

```
/memory save                             # Save current session summary
/memory save --tags "auth,refactor"      # Save with tags
/memory recall                           # Show recent memories
/memory recall --query "auth"            # Search memories
/memory list                             # List all memories
/memory delete <id>                      # Delete memory
/memory handoff                          # Generate handoff document
/memory resume                           # Resume last session context
```

## Directory Structure

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # Plugin manifest
├── CLAUDE.md                        # Contributor guidelines
├── skills/memory/
│   ├── SKILL.md                     # Main skill (memory management workflow)
│   └── references/
│       ├── memory-structure.md      # Memory structure details
│       └── team-coord-guide.md      # team-coord integration guide
└── README.md / README.en.md
```

## Dependencies

None. Pure SKILL.md instructions, reads/writes `.memory/` directory.

## License

MIT
