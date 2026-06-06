---
name: agent-builder
description: Build AI coding agents with tool use, hooks, subagents, and skill systems
---

# Agent Builder Skill

You are an expert at building AI coding agents. When the user asks to build an agent, follow this structured approach.

## Architecture Overview

A production coding agent requires these layers:

```
┌─────────────────────────────────┐
│         System Prompt           │  ← persona + skill catalog
├─────────────────────────────────┤
│         Agent Loop              │  ← message → LLM → tool_use → repeat
├─────────────────────────────────┤
│         Tool Layer              │  ← bash, read, write, edit, glob, ...
├─────────────────────────────────┤
│         Hook System             │  ← permission, logging, context injection
├─────────────────────────────────┤
│         Subagent Layer          │  ← spawn isolated task workers
├─────────────────────────────────┤
│         Skill System            │  ← catalog scan + on-demand loading
└─────────────────────────────────┘
```

## Step-by-Step Build Process

### 1. Core Agent Loop

```python
def agent_loop(messages: list):
    while True:
        response = client.messages.create(
            model=MODEL, system=SYSTEM,
            messages=messages, tools=TOOLS, max_tokens=8000,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return  # final text response

        # Execute each tool_use block
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            handler = TOOL_HANDLERS.get(block.name)
            output = handler(**block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            })
        messages.append({"role": "user", "content": results})
```

### 2. Tool Definitions

Each tool needs:
- A JSON schema definition for `TOOLS` list
- A handler function in `TOOL_HANDLERS` dict

```python
TOOLS = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object",
         "properties": {"command": {"type": "string"}},
         "required": ["command"]}},
    # ... more tools
]

TOOL_HANDLERS = {
    "bash": run_bash,
    # ... more handlers
}
```

Essential tools to implement:
- `bash` — subprocess with timeout, capture stdout+stderr
- `read_file` — read with optional line limit
- `write_file` — write with auto mkdir
- `edit_file` — single old_text → new_text replacement
- `glob` — file pattern matching
- `todo_write` — task list management (print to terminal)

### 3. Hook System

Hooks let you intercept tool calls without hard-coding logic:

```python
HOOKS = {"UserPromptSubmit": [], "PreToolUse": [], "PostToolUse": [], "Stop": []}

def register_hook(event: str, callback):
    HOOKS[event].append(callback)

def trigger_hooks(event: str, *args):
    for callback in HOOKS[event]:
        result = callback(*args)
        if result is not None:
            return result  # block tool call
    return None
```

Standard hooks:
- **PreToolUse**: permission checks, logging
- **PostToolUse**: output size warnings
- **UserPromptSubmit**: context injection
- **Stop**: session summary

### 4. Subagent Spawning

Subagents run with a fresh message history and no task tool (prevents recursion):

```python
def spawn_subagent(description: str) -> str:
    messages = [{"role": "user", "content": description}]
    for _ in range(30):  # safety limit
        response = client.messages.create(
            model=MODEL, system=SUB_SYSTEM,
            messages=messages, tools=SUB_TOOLS, max_tokens=8000,
        )
        # ... same tool loop, but no "task" in SUB_TOOLS
    return extract_text(messages[-1]["content"])  # summary only
```

### 5. Skill System

Skills are directories under `skills/` with a `SKILL.md` manifest:

```
skills/
├── my-skill/
│   └── SKILL.md      ← YAML frontmatter + body
```

```yaml
---
name: my-skill
description: One-line summary
---

# Detailed instructions here...
```

- At startup: scan all `SKILL.md` files, build registry (name + description)
- In SYSTEM prompt: inject compact catalog
- At runtime: `load_skill(name)` returns full content

## Key Design Principles

1. **Workspace jail**: All file paths must resolve inside WORKDIR
2. **Timeout protection**: bash commands capped at 120s
3. **Output truncation**: cap at 50K chars to avoid token overflow
4. **Safety limits**: subagents max 30 turns
5. **Hooks over hard-coding**: permission logic in hooks, not in the loop

## Testing Checklist

After building, verify:
- [ ] Agent responds to text queries
- [ ] Tool use works (bash, file ops)
- [ ] Permission hooks block dangerous commands
- [ ] Subagent spawns and returns summary
- [ ] Skills load from catalog
