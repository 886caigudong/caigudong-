---
name: feishu-bot
description: Feishu Bot for Claude Code - full tool capability via mobile phone
metadata:
  type: project
  originSessionId: cf27dd37-3384-441e-ad3a-4169df524299
---

## 飞书 Bot 项目

将 Claude Code 完整能力通过飞书 Bot 平移到手机端，包括对话、工具执行、记忆系统。

**状态：** 代码已部署到服务器，服务运行中（端口 8080）
**部署时间：** 2026-05-24

**技术栈：**
- Python FastAPI（服务端）
- DeepSeek API Anthropic 兼容端点（对话引擎）
- 飞书开放平台（消息入口）
- Cloudflare Tunnel（HTTPS 暴露，待配置）

**核心模块：**
- `app/bot/` — 飞书消息收发（handler, sender, auth）
- `app/engine/` — DeepSeek API 工具调用循环（anthropic_client）
- `app/tools/` — 6 个工具（bash, read, write, edit, grep, glob）
- `app/memory/` — 记忆加载/同步（manager, git_sync）
- `app/session/` — 会话管理（内存存储，24h 过期）

**当前服务器状态：**
- Python 3.10.12
- FastAPI 服务运行中，健康检查 OK
- 端口 8080（feishu-bot API）
- 端口 8081（storyboard 静态页面）
- mihomo 代理 7890

**待办：**
- 飞书开放平台创建应用 → 获取 App ID / App Secret → 填入 .env
- Cloudflare Tunnel 配置 HTTPS
- 上述完成后，飞书发消息即可用手机与 Claude Code 对话

**Why：** 用户希望在手机端也能使用 Claude Code 的全部能力，不受电脑开关机限制。
**How to apply：** 部署后所有记忆通过 GitHub 双向同步，手机端和电脑端共享同一套上下文。
