---
name: memory-retention
description: "User wants me to proactively build and maintain memory so each session doesn't feel like starting over"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4c96c553-6fe0-4a1d-af99-f5b0b12dde08
---

每次对话时主动记录关键信息到 memory，不要等用户提醒。

**Why：** 用户不希望每次对话都像重新开始。之前曾多次问过"还记得我们之前的对话吗"，说明对记忆连续性很在意。

**How to apply：**
- 每次会话中主动记录：代理配置、项目决策、用户偏好、bug/问题
- 及时更新 MEMORY.md 索引，新记忆文件必须添加索引条目
- 会话结束时检查是否有新信息需要记忆
- 当用户提出新的工作方向时，先查记忆再响应
- 与代码无关但与用户相关的 meta 信息（环境、工具链、偏好）也要记录
