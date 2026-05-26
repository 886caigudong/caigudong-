"""
工具定义 - JSON Schema 列表

每个工具包含 name, description, input_schema 三个字段，
直接作为 tools 参数传入 DeepSeek API。
"""

TOOLS = [
    # ========== 系统工具 ==========
    {
        "name": "bash",
        "description": "执行 bash 命令。可用于运行脚本、安装包、操作文件系统等。命令会在工作目录下执行，并注入 HTTP_PROXY 环境变量。",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "要执行的 bash 命令"},
                "timeout": {
                    "type": "integer",
                    "description": "超时时间（毫秒），默认 30000",
                    "default": 30000,
                },
                "description": {
                    "type": "string",
                    "description": "命令的简要说明，用于日志记录",
                    "default": "",
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "read",
        "description": "读取文件内容。支持设置偏移行数和限制行数，返回内容带行号。",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件的绝对路径",
                },
                "offset": {
                    "type": "integer",
                    "description": "起始行号（从 0 开始，默认 0）",
                    "default": 0,
                },
                "limit": {
                    "type": "integer",
                    "description": "读取行数上限",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "write",
        "description": "写入文件。如果文件不存在则创建，如果存在则覆盖。会自动创建父目录。",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件的绝对路径",
                },
                "content": {
                    "type": "string",
                    "description": "要写入的文件内容",
                },
            },
            "required": ["file_path", "content"],
        },
    },
    {
        "name": "edit",
        "description": "编辑文件。查找 old_string 并替换为 new_string（替换第一个匹配）。如果 old_string 有多个匹配会报错。",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件的绝对路径",
                },
                "old_string": {
                    "type": "string",
                    "description": "要被替换的文本（必须唯一匹配）",
                },
                "new_string": {
                    "type": "string",
                    "description": "替换后的新文本",
                },
            },
            "required": ["file_path", "old_string", "new_string"],
        },
    },
    {
        "name": "grep",
        "description": "在文件中搜索文本模式。支持正则表达式，可通过 glob 过滤文件类型。",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "要搜索的正则表达式模式",
                },
                "path": {
                    "type": "string",
                    "description": "搜索路径（默认当前目录）",
                },
                "glob": {
                    "type": "string",
                    "description": "文件 glob 模式过滤，如 *.py",
                },
                "output_mode": {
                    "type": "string",
                    "description": "输出模式: content（内容）, files_with_matches（仅文件名）, count（计数）",
                    "default": "content",
                    "enum": ["content", "files_with_matches", "count"],
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "glob",
        "description": "查找文件路径。支持 glob 模式匹配，如 **/*.py。",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "glob 模式，如 **/*.txt",
                },
                "path": {
                    "type": "string",
                    "description": "搜索路径（默认当前目录）",
                },
            },
            "required": ["pattern"],
        },
    },
    # ========== 飞书工具 ==========
    {
        "name": "feishu_send_message",
        "description": "向飞书用户或群聊发送消息。支持文本消息。需要知道接收者的 open_id（用户）或 chat_id（群聊）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "receive_id": {
                    "type": "string",
                    "description": "接收者 ID（open_id 表示用户，chat_id 表示群聊）",
                },
                "content": {
                    "type": "string",
                    "description": "消息文本内容",
                },
                "receive_id_type": {
                    "type": "string",
                    "description": "ID 类型: open_id（默认）/ chat_id / user_id / email",
                    "default": "open_id",
                    "enum": ["open_id", "chat_id", "user_id", "email"],
                },
            },
            "required": ["receive_id", "content"],
        },
    },
    {
        "name": "feishu_read_messages",
        "description": "读取指定飞书群聊的最近消息列表。需要提供群聊的 chat_id。",
        "input_schema": {
            "type": "object",
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "群聊 ID (chat_id)",
                },
                "page_size": {
                    "type": "integer",
                    "description": "返回消息数量，默认 20，最大 50",
                    "default": 20,
                },
            },
            "required": ["container_id"],
        },
    },
    {
        "name": "feishu_search_contact",
        "description": "搜索飞书联系人。通过关键词匹配姓名、邮箱或手机号查找用户。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词（姓名/邮箱/手机号）",
                },
                "page_size": {
                    "type": "integer",
                    "description": "返回数量，默认 20，最大 50",
                    "default": 20,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "feishu_create_doc",
        "description": "在飞书中创建新文档。返回文档 ID 和访问链接。",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "文档标题",
                },
                "folder_token": {
                    "type": "string",
                    "description": "目标文件夹 token（可选，不填则创建在根目录）",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "feishu_append_doc_content",
        "description": "向已存在的飞书文档追加文本内容。需要提供文档 ID。",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "飞书文档 ID",
                },
                "content": {
                    "type": "string",
                    "description": "要追加的文本内容",
                },
            },
            "required": ["document_id", "content"],
        },
    },
    {
        "name": "feishu_list_calendar_events",
        "description": "查询飞书日历事件列表。可以指定时间范围筛选。",
        "input_schema": {
            "type": "object",
            "properties": {
                "calendar_id": {
                    "type": "string",
                    "description": "日历 ID（可选，不填则查询主日历）",
                },
                "page_size": {
                    "type": "integer",
                    "description": "返回数量，默认 20，最大 50",
                    "default": 20,
                },
                "start_time": {
                    "type": "string",
                    "description": "开始时间（Unix 毫秒时间戳，可选）",
                },
                "end_time": {
                    "type": "string",
                    "description": "结束时间（Unix 毫秒时间戳，可选）",
                },
            },
        },
    },
    {
        "name": "feishu_create_calendar_event",
        "description": "在飞书日历中创建新事件/日程。需要标题、开始和结束时间。",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "事件标题",
                },
                "start_datetime": {
                    "type": "string",
                    "description": "开始时间，格式如 2026-05-26T10:00:00",
                },
                "end_datetime": {
                    "type": "string",
                    "description": "结束时间，格式如 2026-05-26T11:00:00",
                },
                "description": {
                    "type": "string",
                    "description": "事件描述（可选）",
                },
                "calendar_id": {
                    "type": "string",
                    "description": "日历 ID（可选，不填则创建在主日历）",
                },
                "participants": {
                    "type": "string",
                    "description": "参与人 open_id，多个用逗号分隔（可选）",
                },
            },
            "required": ["summary", "start_datetime", "end_datetime"],
        },
    },
    {
        "name": "feishu_get_my_info",
        "description": "获取当前飞书用户/机器人的基本信息，包括名称、open_id、邮箱等。无需参数。",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "feishu_get_group_info",
        "description": "获取飞书群聊的详细信息，包括名称、描述、成员数量等。",
        "input_schema": {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "string",
                    "description": "群聊 ID",
                },
            },
            "required": ["chat_id"],
        },
    },
    {
        "name": "feishu_list_groups",
        "description": "列出当前用户加入的所有飞书群聊。",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_size": {
                    "type": "integer",
                    "description": "返回数量，默认 20，最大 50",
                    "default": 20,
                },
            },
        },
    },
    {
        "name": "feishu_approval_list",
        "description": "列出飞书审批实例。可按状态筛选。",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_size": {
                    "type": "integer",
                    "description": "返回数量，默认 20，最大 100",
                    "default": 20,
                },
                "status": {
                    "type": "string",
                    "description": "审批状态过滤: pending / approved / rejected / canceled（可选）",
                    "enum": ["", "pending", "approved", "rejected", "canceled"],
                },
            },
        },
    },
]


# 工具名称 -> 友好中文名映射，用于 system prompt 引用
TOOL_NAMES_CN = {
    "bash": "Bash 命令执行",
    "read": "读取文件",
    "write": "写入文件",
    "edit": "编辑文件",
    "grep": "搜索文件内容",
    "glob": "查找文件路径",
    "feishu_send_message": "飞书发送消息",
    "feishu_read_messages": "飞书读取消息",
    "feishu_search_contact": "飞书搜索联系人",
    "feishu_create_doc": "飞书创建文档",
    "feishu_append_doc_content": "飞书编辑文档",
    "feishu_list_calendar_events": "飞书查看日历",
    "feishu_create_calendar_event": "飞书创建日程",
    "feishu_get_my_info": "飞书查看个人信息",
    "feishu_get_group_info": "飞书查看群聊信息",
    "feishu_list_groups": "飞书列出群聊",
    "feishu_approval_list": "飞书查看审批",
}
