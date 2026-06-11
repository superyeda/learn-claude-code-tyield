"""Dynamic system prompt: section-based assembly with caching."""

import json
from config import WORKDIR, MEMORY_INDEX
from tools import TOOL_HANDLERS
from skills import list_skills


# ═══════════════════════════════════════════════════════════
#  Prompt Sections — modular pieces of the system prompt
# ═══════════════════════════════════════════════════════════

PROMPT_SECTIONS = {
    "identity": "You are a coding agent. Act, don't explain.",
    "tools": f"Available tools: {', '.join(TOOL_HANDLERS.keys())}.",
    "workspace": f"Working directory: {WORKDIR}",
    "memory": "Relevant memories are injected below when available.\n"
              "When the user says 'remember' or expresses a clear preference, extract it as a memory.",
}


# ═══════════════════════════════════════════════════════════
#  Assembly — select and join sections based on context
# ═══════════════════════════════════════════════════════════

def assemble_system_prompt(context: dict) -> str:
    """Assemble system prompt from sections based on current context."""
    sections = []

    # Always loaded
    sections.append(PROMPT_SECTIONS["identity"])
    sections.append(PROMPT_SECTIONS["tools"])
    sections.append(PROMPT_SECTIONS["workspace"])

    # Skills catalog
    catalog = list_skills()
    if catalog and catalog != "(no skills found)":
        sections.append(f"Skills available:\n{catalog}\nUse load_skill to get full details when needed.")

    # Conditional — memory loaded when MEMORY.md has content
    memories = context.get("memories", "")
    if memories:
        sections.append(f"Memories available:\n{memories}")
        sections.append(PROMPT_SECTIONS["memory"])

    return "\n\n".join(sections)


# ═══════════════════════════════════════════════════════════
#  Cache — avoid redundant assembly when context unchanged
# ═══════════════════════════════════════════════════════════

_last_context_key = None
_last_prompt = None

def get_system_prompt(context: dict) -> str:
    """Get system prompt with caching. Rebuilds only when context changes."""
    global _last_context_key, _last_prompt
    key = json.dumps(context, sort_keys=True, ensure_ascii=False, default=str)
    if key == _last_context_key and _last_prompt:
        print("  \033[90m[cache hit] system prompt unchanged\033[0m")
        return _last_prompt
    _last_context_key = key
    _last_prompt = assemble_system_prompt(context)

    loaded = ["identity", "tools", "workspace", "skills"]
    if context.get("memories"):
        loaded.append("memory")
    print(f"  \033[32m[assembled] sections: {', '.join(loaded)}\033[0m")
    return _last_prompt


# ═══════════════════════════════════════════════════════════
#  Context — derive from real state
# ═══════════════════════════════════════════════════════════

def update_context(context: dict, messages: list) -> dict:
    """Derive context from real state: tools, workspace, memory files."""
    memories = ""
    if MEMORY_INDEX.exists():
        content = MEMORY_INDEX.read_text().strip()
        if content:
            memories = content
    return {
        "enabled_tools": list(TOOL_HANDLERS.keys()),
        "workspace": str(WORKDIR),
        "memories": memories,
    }
