# ADR Best Practices

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision together with its context and consequences. It's a lightweight way to document decisions that affect the structure, non-functional characteristics, dependencies, interfaces, or construction techniques of a system.

## When to Write an ADR

Write an ADR when:

- **The decision affects the system architecture** — database choice, API style, deployment strategy
- **The decision is hard to reverse** — adopting a framework, choosing a protocol
- **The team needs alignment** — different team members have different assumptions
- **Future developers need context** — why was this approach chosen over alternatives?
- **The decision might be questioned later** — provides justification

Don't write an ADR for:

- **Trivial decisions** — variable naming, code formatting (use linters)
- **Temporary decisions** — will be revisited in days, not months
- **Implementation details** — specific algorithm choice within a module

## ADR Principles

### 1. Immutable

Once accepted, an ADR should not be modified. If circumstances change, create a new ADR that supersedes the old one.

### 2. Lightweight

ADRs should be short (1-2 pages). They capture the essence of the decision, not a detailed design document.

### 3. Accessible

ADRs should be stored in the repository alongside the code. They should be easy to find and read.

### 4. Team-owned

Anyone on the team can propose an ADR. The team reviews and accepts/rejects together.

### 5. Living Documentation

ADRs form a decision log that evolves with the project. They help new team members understand why things are the way they are.

## Writing Tips

### Title

- Use imperative mood: "Use PostgreSQL" not "PostgreSQL was chosen"
- Be specific: "Use JWT for API Authentication" not "Authentication Decision"

### Context

- Describe the problem, not the solution
- Include constraints (technical, organizational, budget)
- Reference related decisions or requirements
- Keep it factual, not opinionated

### Decision

- Use active voice: "We will use…"
- Be specific and unambiguous
- State what AND why (briefly)

### Consequences

- Include both positive and negative consequences
- Be honest about trade-offs
- Identify risks and mitigation strategies

### Alternatives

- List at least 2 alternatives
- Explain why each was not chosen
- Be fair to all alternatives

## Template Comparison

| Template | Best For | Length | Sections |
|----------|----------|--------|----------|
| MADR | Important decisions | 2-3 pages | Context, Decision, Alternatives, Consequences |
| Y-Statement | Quick decisions | 0.5-1 page | One-sentence format, brief explanation |

## Numbering

- Use sequential numbers: 0001, 0002, 0003…
- Pad with zeros for sorting: 0001 not 1
- Include in filename: `0001-use-postgresql.md`

## Status Lifecycle

```
Proposed → Accepted → Deprecated
         ↘          ↗
          Superseded
```

- **Proposed**: Under discussion, not yet decided
- **Accepted**: Decision is active and should be followed
- **Deprecated**: No longer relevant (technology changed, requirements changed)
- **Superseded**: Replaced by a newer decision (link to new ADR)

## Tools

- **adr-tools**: CLI for managing ADRs (https://github.com/npryce/adr-tools)
- **Log4brains**: ADR management with web UI (https://github.com/thomvaill/log4brains)
- **adr-viewer**: Generate HTML view of ADRs (https://github.com/mrwilson/adr-viewer)

## References

- Michael Nygard, "Documenting Architecture Decisions" (2011)
- MADR: https://adr.github.io/
- GitHub ADR organization: https://adr.github.io/
