---
name: cloud-server-setup
description: JD Cloud server with mihomo proxy and Claude Code for 24h auto-backup
metadata:
  type: project
  originSessionId: 4c96c553-6fe0-4a1d-af99-f5b0b12dde08
---

有一台京东云服务器（Ubuntu 22.04 LTS, IP: 117.72.114.74），用于 24h 运行 Claude Code 和自动备份。

**已部署的服务：**
- **mihomo (Clash Meta) v1.19.25** — 代理服务，HTTP 代理 7890 / SOCKS5 7891 / Mixed 7892
- **Claude Code 2.1.150** — 通过 DeepSeek API（deepseek-chat）运行
- **自动备份脚本** `/usr/local/bin/claude-backup.sh` — 每 30 分钟 cron 自动 commit + push
- **claude 用户** — 运行用户，有 sudo 权限，home: `/home/claude/`

**代理状况：**
- HTTP 代理 (7890) 工作正常，可通过 curl 访问 Google/GitHub
- SOCKS5 代理 (7891) 连接有问题
- SSH 连接 GitHub 需通过 `ssh.github.com:443` + HTTP CONNECT 代理，直连 22 端口被 GFW 阻断
- SSH 公钥认证尚未成功（2026-05-23 状态）

**GitHub 仓库：** `886caigudong/caigudong-`
**服务器工作目录：** `/workspace/claude-history`
**API 后端：** `https://api.deepseek.com/anthropic` (deepseek-chat)

**飞书 Bot 项目（2026-05-24 新增）：**
- 代码位置：`/workspace/claude-history/feishu-bot/`
- 状态：代码已开发完成，待部署
- Python FastAPI + DeepSeek API 工具调用
- 6 个核心工具：bash, read, write, edit, grep, glob
- 记忆系统通过 git 双向同步
- **注意：SSH 密码认证失效，记录中的几组密码均无法连接，需要通过京东云控制台检查服务器**

**Why：** 用户在国内使用 Claude Code，需要服务器 24h 运行和自动备份对话历史。
**How to apply：** 处理代理相关问题时，优先尝试 HTTP 代理方案，SSH 需走 443 端口。
