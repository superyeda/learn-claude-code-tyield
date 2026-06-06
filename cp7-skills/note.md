# Skills

启动时把技能目录注入到SYSTEM prompt中，运行过程中需要时才加载skill完整内容，用到才花费token。
包含了两层设计
1. 启动时：目录SYSTEM prompt：启动时注入，每轮都带
2. 调用时：内容tool_result：Agent调用load_skill时，SKILL.md可用指引后续的工具调用，用于按需访问额外的资源。

## 下一节
上下文压缩