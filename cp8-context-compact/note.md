# Context Compact
每轮LLM调用前都会有三层预处理器（0API），如果处理后的数据还是超过阈值时触发LLM摘要（1API）,API报错时还一层应急裁剪

## 工作原理
### L1：snip_compact
裁剪掉无关旧对话，比如消息数超过50条->保留前三条和后47条，裁掉中间的。
剩下的消息里tool_result内容在累计
### L2：micro_compact
旧工具结果占位，Agent读了10个文件，前几次的都还在上下文中，占着大量空间。可以只保留最近的3条tool_result完整内容，旧的用一行占位符。
但单条新结果就可能过大
### L3：tool_result_budget
大结果落盘，模型以下读五个文件，最后导致单挑user消息过大，对于过大的消息落盘，上下文只保留内容位置和前2000字摘要。需要的时候再去磁盘读。

前三层都是纯文本/结构操作，0API调用，但也无法理解对话内容，上下文可能依然太大
### L4：compact_history
LLM全量摘要
1. 保存 transcript：完整对话写入 .transcripts/，JSONL 格式。transcript 保留了可恢复记录，但模型的活跃上下文里只剩摘要。对模型当下推理来说，细节已经不在上下文中了。
2. LLM 生成摘要：把对话历史发给 LLM，要求保留当前目标、重要发现、已改文件、剩余工作、用户约束等关键信息。
3. 替换消息列表：所有旧消息被替换为一条摘要。

### 兜底：reactive_compact
有时候 API 还是返回 prompt_too_long（413），上下文增长速度快于压缩触发速度时。
这时触发 reactive_compact：比 compact_history 更激进，从尾部回退，以字节级精度裁剪到 API 可接受的大小，只保留最后 5 条消息 + 摘要。
reactive compact 有重试上限（默认 1 次）。再失败就抛出异常，不无限循环。

L3->L1->L2->L4->reactiveCompact


