# SubAgent
- spawn_subagent：给子Agent一个全新的messages列表，自己跑循环，只回传结论
- 关键设计：
    - 上下文隔离：全新的message[]
    - 只回传结论：extract_text（last_message）
    - 禁止递龟：子Agent无task工具
    - 安全策略不跳过：子Agent工具调用也走PreToolUse hook

## CC源码
### 不止一种模式，是三种
- Normal Subagent：全新 messages[]，只有 prompt
- Fork Subagent：共享 prompt cache
- General-Purpose：同 Normal