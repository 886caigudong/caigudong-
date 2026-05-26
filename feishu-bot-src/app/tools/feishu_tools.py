"""
飞书 Open API 工具模块

提供一系列工具函数，让 Claude 能够通过飞书 API 操控飞书。
所有函数遵循统一模式：
  - async def tool_name(params...) -> str
  - 返回纯文本字符串，错误以 [错误] 前缀标记

需要飞书应用拥有以下权限（需在开发者后台添加并审批）：
  - im:message                      (已有) 发送消息
  - im:message:readonly                   读取消息
  - contact:contact:readonly              搜索联系人/查看组织架构
  - docx:document                         创建/编辑文档
  - calendar:calendar                     管理日历
  - im:chat:readonly                      查看群聊信息
  - approval:approval                     审批管理
"""

import time
import json
import httpx
from urllib.parse import quote

# 飞书 Open API 基础 URL
FEISHU_OPEN_API = "https://open.feishu.cn/open-apis"

# Token 缓存（与 app/bot/auth.py 独立，避免循环导入）
_tenant_access_token: str = ""
_token_expire_time: float = 0

# ---------- 认证 ----------

def get_tenant_access_token() -> str:
    """
    获取 tenant_access_token，带缓存。
    如果 app.bot.auth 已导入则复用其 token，否则自行获取。
    """
    global _tenant_access_token, _token_expire_time

    # 优先尝试复用 bot.auth 中的 token
    try:
        from app.bot.auth import get_tenant_access_token as _bot_auth_token
        return _bot_auth_token()
    except (ImportError, Exception):
        pass

    # 缓存有效则直接返回
    if _tenant_access_token and time.time() < _token_expire_time - 60:
        return _tenant_access_token

    # 从 config 获取凭证
    try:
        from app.config import settings
        app_id = settings.feishu_app_id
        app_secret = settings.feishu_app_secret
    except Exception:
        import os
        app_id = os.getenv("FEISHU_APP_ID", "")
        app_secret = os.getenv("FEISHU_APP_SECRET", "")

    if not app_id or not app_secret:
        return "[错误] 未配置 FEISHU_APP_ID 或 FEISHU_APP_SECRET"

    url = f"{FEISHU_OPEN_API}/auth/v3/tenant_access_token/internal"
    try:
        resp = httpx.post(url, json={
            "app_id": app_id,
            "app_secret": app_secret,
        }, timeout=10)
        result = resp.json()
        if result.get("code") == 0:
            _tenant_access_token = result["tenant_access_token"]
            _token_expire_time = time.time() + result.get("expire", 7200)
            return _tenant_access_token
        else:
            return f"[错误] 获取 tenant_access_token 失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 获取 tenant_access_token 超时"
    except Exception as e:
        return f"[错误] 获取 tenant_access_token 异常: {e}"


def _headers() -> dict:
    """构建带认证的请求头。"""
    token = get_tenant_access_token()
    if token.startswith("[错误]"):
        raise RuntimeError(token)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }


# ---------- 工具函数 ----------

async def feishu_send_message(
    receive_id_type: str = "open_id",
    receive_id: str = "",
    content: str = "",
    msg_type: str = "text",
) -> str:
    """
    发送消息到飞书用户或群聊。

    参数:
        receive_id_type: 接收者 ID 类型，可选 open_id / user_id / chat_id / email
        receive_id:     接收者 ID 值
        content:         消息内容（纯文本或 JSON 字符串）
        msg_type:        消息类型，可选 text / post / interactive / image

    返回格式示例:
        "消息已发送，message_id=om_xxxxx"
    """
    if not receive_id:
        return "[错误] 请提供 receive_id（接收者ID）"
    if not content:
        return "[错误] 请提供消息内容"

    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    # 根据 msg_type 构建 content 字段
    if msg_type == "text":
        content_json = json.dumps({"text": content}, ensure_ascii=False)
    elif msg_type in ("post", "interactive"):
        # post / interactive 需要传入已经是 JSON 字符串的内容
        content_json = content
    else:
        content_json = json.dumps({"text": content}, ensure_ascii=False)

    url = f"{FEISHU_OPEN_API}/im/v1/messages?receive_id_type={receive_id_type}"
    body = {
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": content_json,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, json=body)
            result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            msg_id = data.get("message_id", "")
            return f"消息已发送，message_id={msg_id}"
        else:
            return f"[错误] 发送消息失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 发送消息超时"
    except Exception as e:
        return f"[错误] 发送消息异常: {e}"


async def feishu_read_messages(
    container_id_type: str = "chat",
    container_id: str = "",
    page_size: int = 20,
) -> str:
    """
    读取指定会话的最近消息列表。

    参数:
        container_id_type: 容器类型，固定为 "chat"
        container_id:      群聊 ID (chat_id)
        page_size:         返回消息数量，最大 50

    返回:
        消息列表 JSON，包含消息 ID、发送者、内容、发送时间等
    """
    if not container_id:
        return "[错误] 请提供 container_id（群聊ID）"

    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    page_size = min(max(1, page_size), 50)

    url = f"{FEISHU_OPEN_API}/im/v1/messages"
    params = {
        "container_id_type": container_id_type,
        "container_id": container_id,
        "page_size": page_size,
        "sort_type": "ByCreateTimeDesc",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers, params=params)
            result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            items = data.get("items", [])
            if not items:
                return "该会话暂无消息记录"

            output_lines = [f"共 {len(items)} 条消息："]
            for msg in items:
                msg_id = msg.get("message_id", "")
                sender = msg.get("sender", {}).get("id", "")
                msg_type = msg.get("msg_type", "")
                body_str = json.dumps(msg.get("body", {}), ensure_ascii=False)
                create_time = msg.get("create_time", "")
                output_lines.append(
                    f"  [{create_time}] {sender} ({msg_type}): {body_str[:200]}"
                )
            return "\n".join(output_lines)
        else:
            return f"[错误] 读取消息失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 读取消息超时"
    except Exception as e:
        return f"[错误] 读取消息异常: {e}"


async def feishu_search_contact(
    query: str = "",
    page_size: int = 20,
) -> str:
    """
    搜索飞书联系人/用户。

    参数:
        query:    搜索关键词（姓名、邮箱、手机号等）
        page_size: 返回数量，最大 50

    返回:
        用户列表，包含姓名、邮箱、手机号、部门等
    """
    if not query:
        return "[错误] 请提供搜索关键词"

    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    page_size = min(max(1, page_size), 50)

    url = f"{FEISHU_OPEN_API}/contact/v3/users"
    params = {
        "page_size": page_size,
        "user_id_type": "open_id",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers, params=params)
            result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            items = data.get("items", [])
            if not items:
                return f"未找到匹配 '{query}' 的联系人"

            # 本地过滤（飞书搜索 API 需要特定权限，先用本地过滤）
            matched = []
            for user in items:
                name = user.get("name", "") or ""
                email = user.get("email", "") or ""
                mobile = user.get("mobile", "") or ""
                if (query.lower() in name.lower()
                        or query.lower() in email.lower()
                        or query in mobile):
                    matched.append(user)

            if not matched:
                return f"未找到匹配 '{query}' 的联系人"

            output_lines = [f"找到 {len(matched)} 个匹配联系人："]
            for user in matched:
                output_lines.append(
                    f"  - {user.get('name', '未知')} "
                    f"(open_id: {user.get('open_id', '')}, "
                    f"邮箱: {user.get('email', '无')}, "
                    f"手机: {user.get('mobile', '无')})"
                )
            return "\n".join(output_lines)
        else:
            return f"[错误] 搜索联系人失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 搜索联系人超时"
    except Exception as e:
        return f"[错误] 搜索联系人异常: {e}"


async def feishu_create_doc(
    title: str = "",
    folder_token: str = "",
) -> str:
    """
    创建飞书文档。

    参数:
        title:        文档标题
        folder_token: 文件夹 token（可选，不填则创建在根目录）

    返回:
        文档链接和基本信息
    """
    if not title:
        return "[错误] 请提供文档标题"

    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    url = f"{FEISHU_OPEN_API}/docx/v1/documents"
    body: dict = {"title": title}
    if folder_token:
        body["folder_token"] = folder_token

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, json=body)
            result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            doc_id = data.get("document", {}).get("document_id", "")
            doc_url = f"https://bytedance.feishu.cn/docx/{doc_id}"
            return (
                f"文档创建成功！\n"
                f"  标题: {title}\n"
                f"  文档ID: {doc_id}\n"
                f"  链接: {doc_url}"
            )
        else:
            return f"[错误] 创建文档失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 创建文档超时"
    except Exception as e:
        return f"[错误] 创建文档异常: {e}"


async def feishu_append_doc_content(
    document_id: str = "",
    content: str = "",
) -> str:
    """
    向飞书文档追加内容（支持纯文本）。

    参数:
        document_id: 文档 ID
        content:     要追加的文本内容

    返回:
        操作结果
    """
    if not document_id:
        return "[错误] 请提供 document_id"
    if not content:
        return "[错误] 请提供要追加的内容"

    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    url = f"{FEISHU_OPEN_API}/docx/v1/documents/{document_id}/content"
    body = {
        "content": content,
        "content_type": "text",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=body)
            result = resp.json()

        if result.get("code") == 0:
            return f"文档内容已更新（追加 {len(content)} 字符）"
        else:
            return f"[错误] 更新文档失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 更新文档超时"
    except Exception as e:
        return f"[错误] 更新文档异常: {e}"


async def feishu_list_calendar_events(
    calendar_id: str = "",
    page_size: int = 20,
    start_time: str = "",
    end_time: str = "",
) -> str:
    """
    查询日历事件列表。

    参数:
        calendar_id: 日历 ID（不填则查询主日历）
        page_size:   返回数量，最大 50
        start_time:  开始时间（Unix 毫秒时间戳）
        end_time:    结束时间（Unix 毫秒时间戳）

    返回:
        事件列表
    """
    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    # 如果没有指定 calendar_id，先获取主日历
    if not calendar_id:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                cal_resp = await client.get(
                    f"{FEISHU_OPEN_API}/calendar/v4/calendars",
                    headers=headers,
                    params={"page_size": 1},
                )
                cal_result = cal_resp.json()
                if cal_result.get("code") == 0:
                    items = cal_result.get("data", {}).get("items", [])
                    if items:
                        calendar_id = items[0].get("calendar_id", "")
        except Exception:
            pass

        if not calendar_id:
            return "[错误] 无法获取默认日历，请提供 calendar_id"

    page_size = min(max(1, page_size), 50)
    url = f"{FEISHU_OPEN_API}/calendar/v4/calendars/{calendar_id}/events"
    params: dict = {"page_size": page_size}
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers, params=params)
            result = resp.json()

        if result.get("code") == 0:
            items = result.get("data", {}).get("items", [])
            if not items:
                return "该日历暂无事件"

            output_lines = [f"共 {len(items)} 个事件："]
            for ev in items:
                summary = ev.get("summary", "无标题")
                start = ev.get("start", {}).get("date", "") or ev.get("start", {}).get("datetime", "")
                end = ev.get("end", {}).get("date", "") or ev.get("end", {}).get("datetime", "")
                status = ev.get("status", "")
                output_lines.append(f"  - {summary} ({start} ~ {end}) [{status}]")
            return "\n".join(output_lines)
        else:
            return f"[错误] 查询日历失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 查询日历超时"
    except Exception as e:
        return f"[错误] 查询日历异常: {e}"


async def feishu_create_calendar_event(
    calendar_id: str = "",
    summary: str = "",
    description: str = "",
    start_datetime: str = "",
    end_datetime: str = "",
    participants: str = "",
) -> str:
    """
    创建日历事件。

    参数:
        calendar_id:    日历 ID（不填则创建在主日历）
        summary:        事件标题
        description:    事件描述
        start_datetime: 开始时间，格式 "2026-05-26T10:00:00"
        end_datetime:   结束时间，格式 "2026-05-26T11:00:00"
        participants:   参与人 open_id，多个用逗号分隔

    返回:
        创建结果和事件链接
    """
    if not summary:
        return "[错误] 请提供事件标题 (summary)"
    if not start_datetime or not end_datetime:
        return "[错误] 请提供 start_datetime 和 end_datetime"

    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    # 获取默认日历
    if not calendar_id:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                cal_resp = await client.get(
                    f"{FEISHU_OPEN_API}/calendar/v4/calendars",
                    headers=headers,
                    params={"page_size": 1},
                )
                cal_result = cal_resp.json()
                if cal_result.get("code") == 0:
                    items = cal_result.get("data", {}).get("items", [])
                    if items:
                        calendar_id = items[0].get("calendar_id", "")
        except Exception:
            pass

        if not calendar_id:
            return "[错误] 无法获取默认日历"

    url = f"{FEISHU_OPEN_API}/calendar/v4/calendars/{calendar_id}/events"
    body: dict = {
        "summary": summary,
        "start": {"datetime": start_datetime, "timezone": "Asia/Shanghai"},
        "end": {"datetime": end_datetime, "timezone": "Asia/Shanghai"},
    }
    if description:
        body["description"] = description

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, json=body)
            result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            event_id = data.get("event_id", "")
            return (
                f"日程创建成功！\n"
                f"  标题: {summary}\n"
                f"  时间: {start_datetime} ~ {end_datetime}\n"
                f"  事件ID: {event_id}"
            )
        else:
            return f"[错误] 创建日程失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 创建日程超时"
    except Exception as e:
        return f"[错误] 创建日程异常: {e}"


async def feishu_get_my_info() -> str:
    """
    获取当前登录用户/机器人的基本信息。

    返回:
        用户信息（姓名、open_id、邮箱等）
    """
    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    url = f"{FEISHU_OPEN_API}/contact/v3/users/me"
    params = {"user_id_type": "open_id"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers, params=params)
            result = resp.json()

        if result.get("code") == 0:
            user = result.get("data", {}).get("user", {})
            return (
                f"用户信息：\n"
                f"  名称: {user.get('name', '未知')}\n"
                f"  open_id: {user.get('open_id', '')}\n"
                f"  邮箱: {user.get('email', '无')}\n"
                f"  手机: {user.get('mobile', '无')}"
            )
        else:
            return f"[错误] 获取用户信息失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 获取用户信息超时"
    except Exception as e:
        return f"[错误] 获取用户信息异常: {e}"


async def feishu_get_group_info(
    chat_id: str = "",
) -> str:
    """
    获取群聊信息。

    参数:
        chat_id: 群聊 ID

    返回:
        群聊名称、描述、成员数量等
    """
    if not chat_id:
        return "[错误] 请提供 chat_id（群聊ID）"

    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    url = f"{FEISHU_OPEN_API}/im/v1/chats/{chat_id}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            return (
                f"群聊信息：\n"
                f"  名称: {data.get('name', '未知')}\n"
                f"  群聊ID: {data.get('chat_id', '')}\n"
                f"  描述: {data.get('description', '无')}\n"
                f"  成员数: {data.get('member_count', '未知')}\n"
                f"  群主: {data.get('owner_id', '未知')}\n"
                f"  类型: {'群组' if data.get('chat_type') == 'group' else '会话'}"
            )
        else:
            return f"[错误] 获取群聊信息失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 获取群聊信息超时"
    except Exception as e:
        return f"[错误] 获取群聊信息异常: {e}"


async def feishu_list_groups(
    page_size: int = 20,
) -> str:
    """
    列出用户加入的群聊列表。

    参数:
        page_size: 返回数量，最大 50

    返回:
        群聊列表
    """
    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    page_size = min(max(1, page_size), 50)
    url = f"{FEISHU_OPEN_API}/im/v1/chats"
    params = {"page_size": page_size}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers, params=params)
            result = resp.json()

        if result.get("code") == 0:
            items = result.get("data", {}).get("items", [])
            if not items:
                return "未找到群聊"

            output_lines = [f"共 {len(items)} 个群聊："]
            for chat in items:
                output_lines.append(
                    f"  - {chat.get('name', '未命名')} "
                    f"(chat_id: {chat.get('chat_id', '')}, "
                    f"成员: {chat.get('member_count', '?')})"
                )
            return "\n".join(output_lines)
        else:
            return f"[错误] 获取群聊列表失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 获取群聊列表超时"
    except Exception as e:
        return f"[错误] 获取群聊列表异常: {e}"


async def feishu_approval_list(
    page_size: int = 20,
    status: str = "",
) -> str:
    """
    列出审批实例列表。

    参数:
        page_size: 返回数量，最大 100
        status:    审批状态过滤，可选 pending / approved / rejected / canceled

    返回:
        审批列表
    """
    try:
        headers = _headers()
    except RuntimeError as e:
        return str(e)

    page_size = min(max(1, page_size), 100)
    url = f"{FEISHU_OPEN_API}/approval/v4/instances"
    params: dict = {
        "page_size": page_size,
        "user_id_type": "open_id",
    }
    if status:
        params["status"] = status

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers, params=params)
            result = resp.json()

        if result.get("code") == 0:
            items = result.get("data", {}).get("items", [])
            if not items:
                return "暂无审批记录"

            output_lines = [f"共 {len(items)} 条审批："]
            for inst in items:
                output_lines.append(
                    f"  - {inst.get('name', '未命名')} "
                    f"(状态: {inst.get('status', '?')}, "
                    f"发起人: {inst.get('applicant', {}).get('name', '?')})"
                )
            return "\n".join(output_lines)
        else:
            return f"[错误] 获取审批列表失败: {result.get('msg', '未知错误')}"
    except httpx.TimeoutException:
        return "[错误] 获取审批列表超时"
    except Exception as e:
        return f"[错误] 获取审批列表异常: {e}"
