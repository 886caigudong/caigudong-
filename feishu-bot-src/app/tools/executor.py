"""
工具执行调度器

根据工具名称将调用分发到对应的工具函数。
"""

import traceback

from app.tools.bash_tool import execute_bash
from app.tools.file_tools import read_file, write_file, edit_file
from app.tools.search_tools import grep_search, glob_search
from app.tools.feishu_tools import (
    feishu_send_message,
    feishu_read_messages,
    feishu_search_contact,
    feishu_create_doc,
    feishu_append_doc_content,
    feishu_list_calendar_events,
    feishu_create_calendar_event,
    feishu_get_my_info,
    feishu_get_group_info,
    feishu_list_groups,
    feishu_approval_list,
)


async def execute_tool(tool_name: str, tool_input: dict) -> str:
    """执行工具调用，返回文本结果。"""

    try:
        # ---- 系统工具 ----
        if tool_name == "bash":
            return await execute_bash(
                command=tool_input["command"],
                timeout=tool_input.get("timeout", 30000),
                description=tool_input.get("description", ""),
            )

        elif tool_name == "read":
            return await read_file(
                file_path=tool_input["file_path"],
                offset=tool_input.get("offset"),
                limit=tool_input.get("limit"),
            )

        elif tool_name == "write":
            return await write_file(
                file_path=tool_input["file_path"],
                content=tool_input["content"],
            )

        elif tool_name == "edit":
            return await edit_file(
                file_path=tool_input["file_path"],
                old_string=tool_input["old_string"],
                new_string=tool_input["new_string"],
            )

        elif tool_name == "grep":
            return await grep_search(
                pattern=tool_input["pattern"],
                path=tool_input.get("path"),
                glob=tool_input.get("glob"),
                output_mode=tool_input.get("output_mode", "content"),
            )

        elif tool_name == "glob":
            return await glob_search(
                pattern=tool_input["pattern"],
                path=tool_input.get("path"),
            )

        # ---- 飞书工具 ----
        elif tool_name == "feishu_send_message":
            return await feishu_send_message(
                receive_id=tool_input.get("receive_id", ""),
                content=tool_input.get("content", ""),
                receive_id_type=tool_input.get("receive_id_type", "open_id"),
            )

        elif tool_name == "feishu_read_messages":
            return await feishu_read_messages(
                container_id=tool_input.get("container_id", ""),
                page_size=tool_input.get("page_size", 20),
            )

        elif tool_name == "feishu_search_contact":
            return await feishu_search_contact(
                query=tool_input.get("query", ""),
                page_size=tool_input.get("page_size", 20),
            )

        elif tool_name == "feishu_create_doc":
            return await feishu_create_doc(
                title=tool_input.get("title", ""),
                folder_token=tool_input.get("folder_token", ""),
            )

        elif tool_name == "feishu_append_doc_content":
            return await feishu_append_doc_content(
                document_id=tool_input.get("document_id", ""),
                content=tool_input.get("content", ""),
            )

        elif tool_name == "feishu_list_calendar_events":
            return await feishu_list_calendar_events(
                calendar_id=tool_input.get("calendar_id", ""),
                page_size=tool_input.get("page_size", 20),
                start_time=tool_input.get("start_time", ""),
                end_time=tool_input.get("end_time", ""),
            )

        elif tool_name == "feishu_create_calendar_event":
            return await feishu_create_calendar_event(
                calendar_id=tool_input.get("calendar_id", ""),
                summary=tool_input.get("summary", ""),
                description=tool_input.get("description", ""),
                start_datetime=tool_input.get("start_datetime", ""),
                end_datetime=tool_input.get("end_datetime", ""),
                participants=tool_input.get("participants", ""),
            )

        elif tool_name == "feishu_get_my_info":
            return await feishu_get_my_info()

        elif tool_name == "feishu_get_group_info":
            return await feishu_get_group_info(
                chat_id=tool_input.get("chat_id", ""),
            )

        elif tool_name == "feishu_list_groups":
            return await feishu_list_groups(
                page_size=tool_input.get("page_size", 20),
            )

        elif tool_name == "feishu_approval_list":
            return await feishu_approval_list(
                page_size=tool_input.get("page_size", 20),
                status=tool_input.get("status", ""),
            )

        else:
            return f"[错误] 未知工具: {tool_name}"

    except PermissionError as e:
        return f"[安全拒绝] {e}"
    except Exception as e:
        tb = traceback.format_exc()
        return f"[执行错误] {tool_name}: {e}\n{tb[:500]}"
