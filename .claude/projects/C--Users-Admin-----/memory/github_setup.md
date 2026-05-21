---
name: github-setup
description: Conversation history is tracked in git and auto-pushed to GitHub
metadata: 
  node_type: memory
  type: project
  originSessionId: f9d68320-93d8-41da-bc32-51bd0188df1f
---

Conversation history and Claude Code sessions are automatically version-controlled.

**Git repo:** `C:\Users\Admin（无密码）` — initialized as git repo
**GitHub remote:** `886caigudong/caigudong-` on GitHub
**Trigger:** `SessionEnd` hook in `.claude/settings.json` auto-commits and pushes to GitHub when the session ends

**Tracked files:**
- `.claude/history.jsonl` — all conversation history
- `.claude/projects/*.jsonl` — per-project session logs
- `.claude/settings.json` — configuration
- `.claude/memory/` — memory files

**Why:** So conversations survive reboots, crashes, and can be viewed on GitHub at any time.
**How:** No manual action needed. When a Claude Code session ends, the hook runs `git add`, `git commit`, `git push` automatically.
