# Hooks

将非核心功能从循环内移到hook上，循环不在直接调用如何函数，而是改为trigger_hooks(),有注册表决定跑什么。不用再将很多功能硬编码到循环里

四个事件覆盖一个完整的Agent cycle
- UserPromptSubmit：用户输入提交后，进入LLM前（输入验证、注入上下文）
- PreToolUse：工具执行前（权限检查、日志记录）
- PostToolUse：工具执行后（副作用，输出检查）
- STOP：循环即将退出时（收尾清理，或强制继续跑）
拓展通过register_hook()添加，循环只调用trigger_hooks()

## CC源码
### Hook事件不止4个，而是27个
- 工具相关：PreToolUse, PostToolUse, PostToolUseFailure
- 会话相关：SessionStart, SessionEnd, Stop, StopFailure, Setup
- 用户交互：UserPromptSubmit, Notification, PermissionRequest, PermissionDenied
- 子 Agent：SubagentStart, SubagentStop
- 压缩相关：PreCompact, PostCompact
- 团队相关：TeammateIdle, TaskCreated, TaskCompleted
- 其他：Elicitation, ElicitationResult, ConfigChange, WorktreeCreate, WorktreeRemove, InstructionsLoaded, CwdChanged, FileChanged

### HookResult实际是14个字段，而不是简单的是否NONE
- message	Message	可选 UI 消息
- blockingError	HookBlockingError	阻塞错误 → 注入对话让模型自纠
- outcome	success/blocking/non_blocking_error/cancelled	执行结果
- preventContinuation	boolean	阻止后续执行
- stopReason	string	停止原因描述
- permissionBehavior	allow/deny/ask/passthrough	hook 返回权限决策
- updatedInput	Record	修改工具输入
- additionalContext	string	附加上下文
- updatedMCPToolOutput	unknown	MCP 工具输出修改
### Hook 'allow' 不能绕过 deny/ask 规则
hook 返回 allow 时，仍然要检查 settings.json 的 deny/ask 规则。即使用户的 hook 脚本说"允许"，如果在 settings.json 中禁用了这个工具，操作仍然会被阻止。
教学版没有这个层次，只把 PreToolUse 的非 None 返回值解释为阻止本次工具执行。这在教学场景中够了，但在生产环境中会形成安全漏洞。

### StopHookActive机制
stopHookActive 状态字段。当 stop hooks 产生 blockingError 时，循环带 stopHookActive: true 重入下一轮。后续迭代中 stop hooks 看到这个标志就不会再次触发。这防止了一个永不停机的 bug：模型自纠后 stop hook 再次报错 → 模型再自纠 → stop hook 再报错...

## 下一节
给Agent一个计划工具，先列清单，再做
