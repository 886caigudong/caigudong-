# 飞书 Claude 操控飞书 · 部署指南

## 文件清单

以下文件需要上传到服务器 `/workspace/claude-history/feishu-bot/app/` 目录：

| 本地文件 | 服务器路径 | 操作 |
|---------|-----------|------|
| `app/tools/feishu_tools.py` | `app/tools/feishu_tools.py` | **新建** |
| `app/engine/tool_definitions.py` | `app/engine/tool_definitions.py` | **替换** |
| `app/tools/executor.py` | `app/tools/executor.py` | **替换** |
| `app/engine/system_prompt.py` | `app/engine/system_prompt.py` | **替换** |

## 部署步骤

### 方式一：SCP 直传（推荐，最快）

在 **本地电脑** 的 PowerShell 或 CMD 中执行：

```bash
# 将 feishu-bot-src 下的文件上传到服务器
scp -P 22222 -r feishu-bot-src/app/tools/feishu_tools.py root@117.72.114.74:/workspace/claude-history/feishu-bot/app/tools/
scp -P 22222 feishu-bot-src/app/engine/tool_definitions.py root@117.72.114.74:/workspace/claude-history/feishu-bot/app/engine/
scp -P 22222 feishu-bot-src/app/tools/executor.py root@117.72.114.74:/workspace/claude-history/feishu-bot/app/tools/
scp -P 22222 feishu-bot-src/app/engine/system_prompt.py root@117.72.114.74:/workspace/claude-history/feishu-bot/app/engine/
```

### 方式二：服务器直接 git 拉取（如果文件已 push）

```bash
# 在服务器上执行
cd /workspace/claude-history
git pull
```

### 方式三：从 GitHub Release 下载

访问 https://github.com/886caigudong/caigudong-/releases 下载最新包，
解压后覆盖到 `/workspace/claude-history/feishu-bot/`。

### 重启服务

```bash
# 在服务器上执行
sudo systemctl restart feishu-bot
sudo systemctl status feishu-bot
```

## 飞书开发者后台配置

需要为飞书应用添加以下权限（在 https://open.feishu.cn/app 中操作）：

1. 登录飞书开发者后台
2. 找到你的应用（APP_ID: cli_aa98c07314389cc5）
3. 进入「权限管理」页面
4. 添加以下权限：

| 权限 | 对应工具 | 说明 |
|------|---------|------|
| `im:message` | feishu_send_message | ✅ 已有，发送消息 |
| `im:message:readonly` | feishu_read_messages | 读取消息记录 |
| `contact:contact:readonly` | feishu_search_contact / feishu_get_my_info | 搜索联系人 |
| `docx:document` | feishu_create_doc / feishu_append_doc_content | 创建/编辑文档 |
| `calendar:calendar:readonly` | feishu_list_calendar_events | 查询日历 |
| `calendar:calendar` | feishu_create_calendar_event | 创建日程 |
| `im:chat:readonly` | feishu_get_group_info / feishu_list_groups | 查看群聊 |
| `approval:approval` | feishu_approval_list | 查看审批 |

> **注意：** 添加权限后需要重新发布应用，并由飞书管理员审批通过。

## 验证部署

### 1. 检查服务状态
```bash
curl http://localhost:8080/health
```
预期返回：`{"status":"ok",...}`

### 2. 在飞书上测试
给 Bot 发送以下消息测试各功能：

```
帮我查一下我的飞书信息
列出我的群聊
创建一个文档，标题叫"测试文档"
搜索联系人"张三"
```

## 快速部署脚本

如果服务器可以 SSH 直连，运行以下命令一键部署：

```bash
# 保存为 deploy.sh 并执行
#!/bin/bash
SERVER="root@117.72.114.74"
PORT="22222"
BOT_DIR="/workspace/claude-history/feishu-bot"

# 上传新文件
scp -P $PORT app/tools/feishu_tools.py $SERVER:$BOT_DIR/app/tools/
scp -P $PORT app/engine/tool_definitions.py $SERVER:$BOT_DIR/app/engine/
scp -P $PORT app/tools/executor.py $SERVER:$BOT_DIR/app/tools/
scp -P $PORT app/engine/system_prompt.py $SERVER:$BOT_DIR/app/engine/

# 重启服务
ssh -p $PORT $SERVER "sudo systemctl restart feishu-bot && sleep 2 && sudo systemctl status feishu-bot --no-pager"
```

## 回滚方案

如果新功能有问题，可以使用 git 回滚：

```bash
cd /workspace/claude-history
git checkout -- feishu-bot/app/engine/tool_definitions.py
git checkout -- feishu-bot/app/tools/executor.py
git checkout -- feishu-bot/app/engine/system_prompt.py
sudo systemctl restart feishu-bot
```
