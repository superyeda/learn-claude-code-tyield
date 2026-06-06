"""Agent main loop: message processing and tool dispatch."""

import config
from config import client, MODEL, CONTEXT_LIMIT, MAX_REACTIVE_RETRIES
from skills import SYSTEM
from tools import TOOLS, TOOL_HANDLERS
from hooks import trigger_hooks
from compact import estimate_size, snip_compact, micro_compact, tool_result_budget, compact_history, reactive_compact


rounds_since_todo = 0

def agent_loop(messages: list):
    global rounds_since_todo
    while True:
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
            response = client.messages.create(model=MODEL, system=SYSTEM, messages=messages, tools=TOOLS, max_tokens=8000)
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
