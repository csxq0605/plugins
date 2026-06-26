# dev-flow — Claude Code Plugin

One plugin for the entire dev lifecycle: project onboarding → dependency audit → code review (6 perspectives) → changelog → architecture decision records → cross-session memory.

## Installation

```bash
claude install-plugin github:csxq0605/plugins
```

## Usage

```
/dev-flow                                # Show project status and next steps
/dev-flow onboard                        # Project onboarding scan
/dev-flow audit                          # Dependency security audit
/dev-flow review                         # Code review (6 perspectives)
/dev-flow review --fix                   # Code review + auto-fix
/dev-flow changelog                      # Generate changelog
/dev-flow changelog --suggest-bump       # Suggest version bump
/dev-flow adr                            # Record architecture decision
/dev-flow adr list                       # List all decisions
/dev-flow recall                         # View memories
/dev-flow recall --query "auth"          # Search memories
/dev-flow save                           # Save current work state
/dev-flow resume                         # Resume last work state
```

## Why 1 plugin instead of 6?

Real dev workflow: you need audit + review + changelog + ADR in a single PR flow. Fragmented plugins create pseudo-needs, not real value.

## License

MIT
