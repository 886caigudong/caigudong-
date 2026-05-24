---
name: github-setup
description: Conversation history is tracked in git and auto-pushed to GitHub via proxy
metadata: 
  node_type: memory
  type: project
  originSessionId: 4c96c553-6fe0-4a1d-af99-f5b0b12dde08
---

对话历史通过 git 版本控制，会话结束时自动推送到 GitHub。

**Git 仓库：** `C:\Users\Admin（无密码）`
**GitHub 远程：** `https://github.com/886caigudong/caigudong-.git`
**触发方式：** `SessionEnd` hook 在 `.claude/settings.json` 中配置，会话结束时自动 commit + push

**代理配置（国内环境必需）：**
- 地址：`http://127.0.0.1:7897`
- 写入 git 全局配置（`git config --global http.proxy` / `https.proxy`）
- 仅支持 GitHub 访问（Google/YouTube 等其他外网不可达）
- 若代理失效，git push 会超时失败（约 21s）

**追踪的文件：**
- `.claude/history.jsonl` — 所有对话历史
- `.claude/projects/*.jsonl` — 项目级会话日志
- `.claude/settings.json` — 配置文件
- `.claude/memory/` — 记忆文件
