#!/usr/bin/env python3
"""
s09: Memory — persistent cross-session knowledge.

Refactored into modules:
  - config.py:   paths, client, constants
  - tools.py:    tool implementations + registry
  - hooks.py:    hook system + implementations
  - skills.py:   skill system + system prompts
  - subagent.py: subagent spawning
  - compact.py:  context compaction pipeline (L1-L4)
  - memory.py:   memory system (load/extract/consolidate)
  - loop.py:     agent main loop
"""

from hooks import register_all_hooks, trigger_hooks
from tools import TOOLS, TOOL_HANDLERS
from skills import load_skill
from subagent import spawn_subagent
from compact import compact_history
from loop import agent_loop


# ═══════════════════════════════════════════════════════════
#  Register tools and hooks
# ═══════════════════════════════════════════════════════════

# Add compact tool
TOOLS.append({"name": "compact", "description": "Summarize earlier conversation to free context space.",
     "input_schema": {"type": "object", "properties": {"focus": {"type": "string"}}}})

# Add skill tool (catalog is already in SYSTEM prompt, this loads full content)
TOOLS.append(
    {"name": "load_skill", "description": "Load the full content of a skill by name.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}})
TOOL_HANDLERS["load_skill"] = load_skill

# Add task tool (subagent)
TOOLS.append({
    "name": "task",
    "description": "Launch a subagent to handle a complex subtask. Returns only the final conclusion.",
    "input_schema": {"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"]},
})
TOOL_HANDLERS["task"] = spawn_subagent

# Register all hooks
register_all_hooks()


# ═══════════════════════════════════════════════════════════
#  Main Entry
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("s09: Memory — persistent cross-session knowledge")
    print("输入问题，回车发送。输入 q 退出。\n")

    history = []
    while True:
        try:
            query = input("\033[36ms09 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        trigger_hooks("UserPromptSubmit", query)
        history.append({"role": "user", "content": query})
        agent_loop(history)
        for block in history[-1]["content"]:
            if getattr(block, "type", None) == "text":
                print(block.text)
        print()
