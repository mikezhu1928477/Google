"""
Google 工具模块
提供 Google API 相关的工具和客户端
"""

from .sheets_client import (
    SheetsClient,
    get_sheets_client,
    write_to_sheets,
    append_to_sheets,
    read_from_sheets
)

from .sheets_helper import (
    save_news_to_sheets,
    create_sheets_header,
    get_sheet_url
)

from .gmail_client import (
    send_email,
    send_news_email,
    get_gmail_service
)

__all__ = [
    # Sheets 客户端（低级 API）
    'SheetsClient',
    'get_sheets_client',
    'write_to_sheets',
    'append_to_sheets',
    'read_from_sheets',
    
    # Sheets 辅助函数（高级 API）
    'save_news_to_sheets',
    'create_sheets_header',
    'get_sheet_url',
    
    # Gmail 客户端
    'send_email',
    'send_news_email',
    'get_gmail_service'
]
