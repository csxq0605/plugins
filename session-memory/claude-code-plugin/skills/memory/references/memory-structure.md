# Memory Structure Reference

## Memory Types

### Session Memory
Records what happened in a single conversation session.

**Fields**:
- `id`: Unique identifier (format: `session-YYYY-MM-DD-NNN`)
- `type`: Always "session"
- `timestamp`: ISO 8601 timestamp
- `tags`: Array of searchable tags
- `summary`: One-line summary of the session
- `context.files_modified`: List of files changed
- `context.decisions`: Key decisions made
- `context.blockers`: Issues encountered
- `context.next_steps`: Planned next actions
- `key_findings`: Important discoveries

### Decision Memory
Records a specific architectural or design decision.

**Fields**:
- `id`: Unique identifier (format: `decision-YYYY-MM-DD-NNN`)
- `type`: Always "decision"
- `timestamp`: ISO 8601 timestamp
- `tags`: Array of searchable tags
- `title`: Decision title
- `rationale`: Why this decision was made
- `alternatives_considered`: Other options that were evaluated
- `impact`: What changes as a result

### Finding Memory
Records an important discovery or insight.

**Fields**:
- `id`: Unique identifier (format: `finding-YYYY-MM-DD-NNN`)
- `type`: Always "finding"
- `timestamp`: ISO 8601 timestamp
- `tags`: Array of searchable tags
- `title`: Finding title
- `description`: Detailed description
- `evidence`: Supporting evidence
- `impact`: Why this matters

### Handoff Memory
Records a handoff between sessions or team members.

**Fields**:
- `id`: Unique identifier (format: `handoff-YYYY-MM-DD-NNN`)
- `type`: Always "handoff"
- `timestamp`: ISO 8601 timestamp
- `from_session`: Source session ID
- `to_role`: Target role or person
- `summary`: Handoff summary
- `completed`: List of completed tasks
- `remaining`: List of remaining tasks
- `context`: Additional context (API changes, error codes, etc.)

## Index Structure

The `.memory/index.json` file maintains a searchable index:

```json
{
  "version": "1.0",
  "last_updated": "2024-01-15T17:00:00Z",
  "memories": [
    {
      "id": "session-2024-01-15-001",
      "type": "session",
      "timestamp": "2024-01-15T10:30:00Z",
      "tags": ["auth", "api"],
      "summary": "修复了 JWT token 过期后不刷新的 bug",
      "path": "sessions/2024-01-15-001.json"
    }
  ],
  "tag_index": {
    "auth": ["session-2024-01-15-001", "decision-2024-01-15-001"],
    "api": ["session-2024-01-15-001"]
  }
}
```

## Expiry Policy

- **Session memories**: Expire after 30 days by default
- **Decision memories**: Never expire (manually managed)
- **Finding memories**: Expire after 90 days by default
- **Handoff memories**: Expire after 7 days by default

Override with `--expires` flag:
```
/memory save --expires 7d    # Expires in 7 days
/memory save --expires never # Never expires
```

## Search Algorithm

When searching memories:

1. **Exact match**: Check if query appears in summary, title, or description
2. **Tag match**: Check if query matches any tags
3. **Fuzzy match**: Use substring matching for partial matches
4. **Recency boost**: More recent memories rank higher
5. **Type boost**: Decision memories rank higher than session memories

## Privacy Considerations

- Memories are stored locally in `.memory/` directory
- `.memory/` should be added to `.gitignore` for private projects
- For shared projects, consider encrypting sensitive memories
- Never store credentials, tokens, or personal data in memories
