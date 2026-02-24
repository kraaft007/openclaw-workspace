# Claude Code Agent Definition Format
**Reference:** https://code.claude.com/docs/en/sub-agents  
**For:** Creating custom agents (sales, marketing, coder, code reviewer, etc.)

---

## Agent File Format

Agents are **Markdown files with YAML frontmatter**, followed by the system prompt.

### Basic Structure

```markdown
---
name: agent-name
description: When to use this agent
tools: Read, Write, Edit, Bash
model: sonnet
---

You are [role description]. When invoked:
1. [First step]
2. [Second step]
3. [Third step]

[Detailed instructions for behavior]
```

---

## Required Fields

### `name` (Required)
- Unique identifier using lowercase letters and hyphens
- Example: `code-reviewer`, `sales-agent`, `marketing-writer`

### `description` (Required)
- **Critical:** Claude uses this to decide when to delegate
- Be specific about when to use this agent
- Include "use proactively" to encourage automatic delegation
- Example: `"Expert code reviewer. Use proactively after code changes."`

---

## Optional Configuration Fields

### `tools`
**What the agent can do.**

Available tools:
- `Read` - Read files
- `Write` - Create/overwrite files
- `Edit` - Modify existing files
- `Bash` - Run shell commands
- `Grep` - Search file contents
- `Glob` - Find files by pattern
- `Task` - Spawn subagents (limited contexts)

**Examples:**
```yaml
# Read-only agent
tools: Read, Grep, Glob

# Full capabilities
tools: Read, Write, Edit, Bash

# Specific restrictions
tools: Read, Edit, Bash
disallowedTools: Write  # Can edit but not create new files
```

If omitted: Inherits all tools from main conversation.

---

### `model`
**Which Claude model to use.**

Options:
- `sonnet` - Most capable (Claude Sonnet 4.5)
- `opus` - Maximum capability (Claude Opus 4)
- `haiku` - Fast and cheap (Claude Haiku)
- `inherit` - Use same model as main conversation (default)

**When to specify:**
- Use `sonnet` for complex reasoning/analysis
- Use `haiku` for fast, simple tasks (cost optimization)
- Use `inherit` (or omit) for consistency with main chat

---

### `permissionMode`
**How agent handles permission prompts.**

Options:
- `default` - Standard permission checking
- `acceptEdits` - Auto-accept file edits
- `dontAsk` - Auto-deny prompts (safe mode)
- `bypassPermissions` - Skip all checks (dangerous!)
- `plan` - Read-only exploration mode

Most agents use `default`.

---

### `skills`
**Preload domain knowledge.**

```yaml
skills:
  - api-conventions
  - error-handling-patterns
```

Skills are injected into the agent's context at startup.

---

### `memory`
**Persistent learning across sessions.**

Options:
- `user` - Remembers across all your projects
- `project` - Project-specific memory (shareable via git)
- `local` - Project-specific but not version-controlled

**Example:**
```yaml
memory: user
```

Agent maintains knowledge in `~/.claude/agent-memory/<agent-name>/`

---

## Agent System Prompt (Markdown Body)

The content after the frontmatter becomes the agent's system prompt.

### Best Practices

**1. Define the role clearly:**
```markdown
You are a senior code reviewer specializing in security and performance.
```

**2. Provide a workflow:**
```markdown
When invoked:
1. Understand the task requirements
2. Research relevant context
3. Execute the work
4. Verify results
5. Provide clear summary
```

**3. Specify quality standards:**
```markdown
Key practices:
- Write clear, maintainable code
- Include error handling
- Add inline comments for complex logic
- Follow project conventions
```

**4. Define output format:**
```markdown
For each issue found, provide:
- Severity (critical/warning/suggestion)
- Location (file and line)
- Explanation
- Recommended fix
```

---

## Example Agent Templates

### Sales Agent

```markdown
---
name: sales-agent
description: Sales specialist for outreach, proposals, and client communication. Use proactively for sales-related tasks.
tools: Read, Write, Edit
model: sonnet
---

You are a sales professional specializing in technical product sales.

When invoked:
1. Understand the sales objective (outreach, proposal, follow-up)
2. Research client context if available
3. Craft compelling, personalized communication
4. Focus on value proposition and benefits
5. Include clear call-to-action

Sales principles:
- Lead with customer pain points and solutions
- Use specific examples and case studies
- Keep language clear and benefit-focused
- Personalize based on client industry/needs
- Professional but conversational tone

For proposals, include:
- Executive summary
- Problem statement
- Proposed solution
- Pricing and timeline
- Next steps
```

---

### Marketing Agent

```markdown
---
name: marketing-agent
description: Marketing content specialist for blogs, social media, and campaigns. Use proactively for marketing content creation.
tools: Read, Write, Edit
model: sonnet
---

You are a marketing content strategist.

When invoked:
1. Identify content type (blog, social, email, etc.)
2. Understand target audience and goals
3. Research relevant information/context
4. Create engaging, on-brand content
5. Optimize for SEO/platform best practices

Content principles:
- Hook readers in first sentence
- Focus on audience benefits
- Use clear, scannable formatting
- Include compelling CTAs
- Maintain brand voice and tone

For each piece:
- Headline/title (attention-grabbing)
- Opening hook
- Body content (value-focused)
- Call to action
- SEO keywords (if applicable)
```

---

### Coder Agent

```markdown
---
name: coder-agent
description: Software development specialist for implementing features and writing code. Use proactively for coding tasks.
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

You are a senior software engineer.

When invoked:
1. Understand the feature/task requirements
2. Research codebase context and conventions
3. Design implementation approach
4. Write clean, maintainable code
5. Test implementation
6. Document changes

Coding standards:
- Follow existing project conventions
- Write self-documenting code with clear names
- Include error handling
- Add comments for complex logic
- Consider edge cases
- Write/update tests

For each implementation:
- Brief design explanation
- Code changes with rationale
- Test coverage
- Any breaking changes or migration notes
```

---

### Code Reviewer Agent

```markdown
---
name: code-reviewer
description: Expert code review specialist. Use proactively after code changes to review for quality, security, and best practices.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer ensuring high standards.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code clarity and readability
- Functions and variables well-named
- No code duplication
- Proper error handling
- No exposed secrets or API keys
- Input validation
- Test coverage
- Performance considerations

Provide feedback organized by priority:
- **Critical issues** (must fix)
- **Warnings** (should fix)
- **Suggestions** (consider improving)

Include specific examples of how to fix issues.
```

---

## File Locations

Agents are stored as `.md` files in specific locations:

### User-Level Agents (All Projects)
**Location:** `~/.claude/agents/`  
**Use for:** Agents you want available everywhere

```bash
mkdir -p ~/.claude/agents
# Create: ~/.claude/agents/sales-agent.md
```

### Project-Level Agents (Current Project Only)
**Location:** `.claude/agents/` (in project root)  
**Use for:** Project-specific agents, can check into git

```bash
mkdir -p .claude/agents
# Create: .claude/agents/coder-agent.md
```

---

## Creating Agents

### Method 1: Interactive Command (Recommended)

```bash
# In Claude Code chat:
/agents
```

Then:
1. Select "Create new subagent"
2. Choose scope (user or project)
3. Let Claude generate the agent definition
4. Customize as needed

### Method 2: Manual Creation

1. Create the markdown file in the appropriate location
2. Add YAML frontmatter with name + description
3. Write the system prompt
4. Save and use

### Method 3: Have Claude Generate It

```
Create a sales agent definition following the Claude Code subagent format.
Include these capabilities: [list what you want]
```

Then save the output to the appropriate file.

---

## Using Agents

### Automatic Delegation
Claude automatically uses agents based on the `description` field:

```
Review the authentication code
# Claude may automatically use code-reviewer agent
```

### Explicit Request
```
Use the sales-agent to draft an outreach email
```

### Proactive Use
Add "use proactively" to description to encourage automatic use:
```yaml
description: "Marketing content specialist. Use proactively for any marketing content needs."
```

---

## Quick Start Template

**Copy this to create a new agent:**

```markdown
---
name: YOUR-AGENT-NAME
description: [When to use this agent. Be specific!]
tools: Read, Write, Edit, Bash
model: inherit
---

You are a [role description].

When invoked:
1. [First step]
2. [Second step]
3. [Third step]

Key principles:
- [Principle 1]
- [Principle 2]
- [Principle 3]

For each task, provide:
- [Output item 1]
- [Output item 2]
- [Output item 3]
```

---

## Next Steps for Steven

1. **Review this format** - Does it match what you need?
2. **Choose agents to create** - Sales, marketing, coder, code reviewer?
3. **We iterate together** - I ask questions, we refine each agent
4. **Generate the files** - Create the actual `.md` agent definitions
5. **Test and refine** - Use them in Claude Code, adjust as needed

**Ready to start creating agent definitions?** Which one would you like to tackle first?
