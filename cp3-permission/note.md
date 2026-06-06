# Permission

## 三道闸门
1. 拒接列表：永远禁止的操作rm -rf / 、sudo等
2. 规则匹配：取决于上下文的操作（写工作区外、rm等），交给3
3. 用户审批：2命中后，暂停等待用户确认。

## 实际CC
### CC的验证阶段
1. Zod schema 验证（toolExecution.ts:614-680）— 参数类型检查
2. validateInput()（toolExecution.ts:682-733）— 工具级语义验证
3. backfillObservableInput()（toolExecution.ts:784）— 补全遗留字段
4. PreToolUse hooks（toolExecution.ts:800-862）— 钩子可以返回 allow/deny/ask
5. resolveHookPermissionDecision()（toolExecution.ts:921-931）— 协调钩子+管线决策
6. hasPermissionsToUseToolInner()（permissions.ts:1158-1310）— 多层规则检查：
### 拒绝列表
不是单一文件，是八个来源。多个来源的规则合并，高优先级来源覆盖低优先级（从低到高：user < project < local < flag < policy，加上 cliArg、command、session）。
- userSettings：~/.claude/settings.json
- projectSettings：.claude/settings.json
- localSettings：settings.local.json
- flagSettings：Feature flags
- policySettings：企业管理策略
- cliArg：--allowedTools / --deniedTools
- command：内联命令
- session：会话内临时授权

### CC的auto
CC 的 auto 模式下，不会每次都弹对话框。CC会把工具调用 + 对话上下文发给一个分类器 LLM 判断是否安全。先尝试 acceptEdits 模式模拟（如果 acceptEdits 允许 → 直接批准），再查安全工具白名单，最后才调分类器。分类器连续拒绝太多次 → 回退到人工审批。

## 下一章：Hooks给循环加钩子
如果想在工具调用前后加日志或者在某些操作后自动触发git commit，这些拓展逻辑如何拓展
