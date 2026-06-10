"""Agent main loop: message processing and tool dispatch."""

import config
from config import client, MODEL, CONTEXT_LIMIT, MAX_REACTIVE_RETRIES
from skills import build_system
from tools import TOOLS, TOOL_HANDLERS
from hooks import trigger_hooks
from compact import estimate_size, snip_compact, micro_compact, tool_result_budget, compact_history, reactive_compact
from memory import load_memories, extract_memories, consolidate_memories


rounds_since_todo = 0

def agent_loop(messages: list):
    global rounds_since_todo

    # s09: inject relevant memory content into the current user turn
    memories_content = load_memories(messages)
    memory_turn = len(messages) - 1 if messages and isinstance(messages[-1].get("content"), str) else None
    # s09: build system each turn; memory index may update after extraction
    system = build_system()

    while True:
        # s09: save pre-compression snapshot for accurate memory extraction
        pre_compress = [m if isinstance(m, dict) else {"role": m.get("role", ""),
            "content": str(m.get("content", ""))} for m in messages]

        messages[:] = tool_result_budget(messages)  # L3: persist large outputs
        messages[:] = snip_compact(messages)  # L1: snip middle
        messages[:] = micro_compact(messages)  # L2: placeholder old results

        # Context still too large, trigger LLM summary
        if estimate_size(messages) > CONTEXT_LIMIT:
            print("[auto compact]")
            messages[:] = compact_history(messages)

        if rounds_since_todo >= 3 and messages:
            messages.append({"role": "user",
                             "content": "<reminder>Update your todos.</reminder>"})
            rounds_since_todo = 0

        try:
            # s09: inject memories into the user message for this request
            request_messages = messages
            if memories_content and memory_turn is not None and memory_turn < len(messages):
                request_messages = messages.copy()
                request_messages[memory_turn] = {
                    **messages[memory_turn],
                    "content": memories_content + "\n\n" + messages[memory_turn]["content"],
                }
            response = client.messages.create(model=MODEL, system=system, messages=request_messages, tools=TOOLS, max_tokens=8000)
            reactive_retries = 0  # reset on successful API call
        except Exception as e:
            if ("prompt_too_long" in str(e).lower() or "too many tokens" in str(e).lower()) and reactive_retries < MAX_REACTIVE_RETRIES:
                print("[reactive compact]")
                messages[:] = reactive_compact(messages)
                reactive_retries += 1
                continue
            raise

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            # s09: extract from pre-compression snapshot for full fidelity
            extract_memories(pre_compress)
            consolidate_memories()
            force = trigger_hooks("Stop", messages)
            if force:
                messages.append({"role": "user", "content": force})
                continue
            return

        rounds_since_todo += 1
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"\033[36m> {block.name}\033[0m")

            # compact tool triggers compact_history
            if block.name == "compact":
                messages[:] = compact_history(messages)
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": "[Compacted. Conversation history has been summarized.]"})
                messages.append({"role": "user", "content": results})
                break  # end current turn, start fresh with compacted context

            blocked = trigger_hooks("PreToolUse", block)
            if blocked:
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": str(blocked)})
                continue
            handler = TOOL_HANDLERS.get(block.name)
            output = handler(**block.input) if handler else f"Unknown: {block.name}"
            trigger_hooks("PostToolUse", block, output)
            if block.name == "todo_write":
                rounds_since_todo = 0
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": results})
