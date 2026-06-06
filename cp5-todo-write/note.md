# Todo write

- todo_write工具：接收带状态的列表，保存在当前进程的内存中，同时在状态显示进度
- Nag reminder：模型连续三轮没有调到todo_write时，自动注入一条提醒

## CC源码
CC中有两套任务系统并存
- TodoWrite：一个简单的列表工具，数据存在内存中，退出后清空
- Task System：文件持久化、依赖图、并发锁、ownership
Task System相比之下的核心增强包括
- 文件持久化（在claude配置文件tasks/{taskListId}/{taskId}.json）
- blockedBy：依赖图而非平铺列表
- proper-lockfile：并发安全而非无锁
- 四个独立工具：Create、Get、Update、List
- TaskCreated/TaskCompleted hooks供外部系统集成

## 下一节
如果任务太大，仅凭TODO列表不够用，放在同一个对话中会被上下文淹没
subAgent可用把大任务拆成子任务，每个子任务派一个独立的agent。
