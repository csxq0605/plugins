# Superpowers Implementer -- Reference Doc

> This doc defines the lifecycle of an implementer teammate in the superpowers workflow.
> Language convention: narrative in Chinese, all technical terms / commands in English.

---

## Preconditions

- `team-coord:teammate` skill is active.
- Spawn brief (provided by lead) contains:
  - `worktree_path` -- absolute path to the feature worktree.
  - Spec document (functional requirements).
  - Plan document (task breakdown, sequencing, dependencies).
  - Overview and vision docs for broader context.

If any precondition is missing, ask the lead before proceeding.

---

## Step 4 -- Startup

1. **Enter the worktree:**

   ```
   EnterWorktree(path=worktree_path)
   ```

   All subsequent file operations happen inside this worktree.

2. **Read docs in order:**

   | Order | Doc | Purpose |
   |-------|-----|---------|
   | 1 | Brief | Understand what the lead expects from you |
   | 2 | Overview | Grasp the project's high-level architecture |
   | 3 | Vision | Align with long-term design direction |
   | 4 | Spec | Know exactly what to build (functional requirements) |
   | 5 | Plan | Know the task sequence and dependencies |

3. **Populate the 16-item task list.**

   Before writing any code, create a task list in the plan doc (or your working notes):

   | # | Field | Description |
   |---|-------|-------------|
   | 1 | Task ID | Unique identifier (e.g. T-001) |
   | 2 | Title | Short descriptive name |
   | 3 | Spec section | Which spec requirement this fulfills |
   | 4 | Plan dependency | Tasks that must finish first |
   | 5 | Target files | Files to create or modify |
   | 6 | Acceptance criteria | How you know it is done |
   | 7 | Test strategy | Unit / integration / manual |
   | 8 | Estimated complexity | low / medium / high |
   | 9 | Status | pending / in-progress / review / done |
   | 10 | Subagent dispatched | yes / no |
   | 11 | Spec review result | pass / fail + notes |
   | 12 | Code review result | pass / fail + notes |
   | 13 | Commit SHA | Filled after commit |
   | 14 | Blockers | Anything blocking this task |
   | 15 | Notes | Freeform remarks |
   | 16 | Final sign-off | All reviews passed: yes / no |

   Mark every task as `pending` initially. Update statuses as you progress.

---

## Step 5 -- Implement

For each task in the list (respecting dependency order):

1. **Dispatch an implementer subagent:**

   ```
   Agent(
     description="Implement task T-XXX",
     prompt="<task spec + context + acceptance criteria>",
     isolation="worktree"
   )
   ```

   The subagent does the actual production code writing -- not you.

2. **Important: "实际写 production code 的是 subagent，不是你"**

   The teammate's role is orchestration:
   - You break down work and dispatch subagents.
   - You review their output.
   - You do NOT write production code directly.

3. After the subagent returns, update the task status to `review`.

---

## Step 6 -- Two-Stage Review

Every task must pass **two independent reviews** before marking as `done`.

### Stage A -- Spec Review

- Does the code match the spec requirements?
- Are all acceptance criteria satisfied?
- Are edge cases described in the spec handled?

Dispatch a reviewer subagent (or review inline if the task is small):

```
Agent(
  description="Spec review for T-XXX",
  prompt="Review whether the implementation matches the spec: <spec excerpt>. Code is in <files>.",
  isolation="worktree"
)
```

Record the result in the task list field `Spec review result`.

### Stage B -- Code Quality Review

- Is the code clean, readable, and well-structured?
- Are there adequate tests?
- Are there security, performance, or correctness concerns?
- Does it follow project conventions?

Dispatch a separate reviewer subagent:

```
Agent(
  description="Code quality review for T-XXX",
  prompt="Review code quality for <files>. Check: readability, test coverage, security, performance, conventions.",
  isolation="worktree"
)
```

Record the result in the task list field `Code review result`.

### Decision

| Spec Review | Code Review | Action |
|-------------|-------------|--------|
| pass | pass | Mark task `done`, proceed to next task |
| fail | any | Fix and re-dispatch implementer subagent |
| pass | fail | Fix and re-dispatch implementer subagent |

Both stages must return clean (pass) before the task is marked `done`.

---

## Step 7 -- Wrap-Up + PR

Once all tasks are `done`:

1. **Invoke finishing skill:**

   ```
   Skill(skill="finishing-a-development-branch")
   ```

   This handles branch hygiene, merge-base checks, etc.

2. **Write a progress doc** summarizing:
   - What was built (mapped to spec sections).
   - Key design decisions.
   - Test coverage summary.
   - Any known limitations or follow-ups.

3. **Commit, push, and open PR:**

   ```
   git add -A
   git commit -m "feat: <description>"
   git push origin <branch>
   gh pr create --title "..." --body "..."
   ```

4. **Send the PR URL to the lead** via the messaging mechanism specified in the brief.

5. **Leave the worktree on disk.** Do NOT remove it -- the lead or reviewer teammates may need it.

---

## Step 9 -- Fix Loop

After the PR is open, the lead may relay review feedback:

1. **Pull inline PR comments:**

   ```
   gh api repos/<owner>/<repo>/pulls/<pr_number>/comments --jq '.[] | {path, line, body}'
   ```

2. **Apply fixes via subagents.** For each comment or batch of related comments:

   ```
   Agent(
     description="Fix PR comment on <file>:<line>",
     prompt="Fix the issue described: <comment body>. File: <path>, line: <line>.",
     isolation="worktree"
   )
   ```

3. **Commit and push:**

   ```
   git add -A
   git commit -m "fix: address review comment on <file>"
   git push
   ```

4. **Notify the lead** that fixes have been pushed.

5. **Loop** -- repeat steps 1-4 until the lead reports that the review passes.

   Do NOT merge the PR yourself. The lead decides when to merge.

---

## Summary Flow

```
Startup (Step 4)
  -> Read docs -> Populate 16-item task list
Implement (Step 5)
  -> For each task: dispatch subagent -> subagent writes code
Review (Step 6)
  -> Spec review + Code quality review -> both pass -> mark done
Wrap-up (Step 7)
  -> finishing skill -> progress doc -> commit-push-pr -> send PR URL -> leave worktree
Fix Loop (Step 9)
  -> Pull PR comments -> fix via subagent -> push -> notify lead -> repeat until approved
```

---

## Key Reminders

- You are an orchestrator, not a coder. Dispatch subagents for implementation and review.
- Always enter the worktree first. All file operations happen inside it.
- Never skip the two-stage review. Both spec and code quality must pass.
- Never merge the PR yourself. That is the lead's decision.
- Never remove the worktree. Leave it on disk for the lead and reviewers.
