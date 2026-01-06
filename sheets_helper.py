"""
Google Sheets 辅助函数
提供简化的新闻数据保存接口
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .sheets_client import get_sheets_client, append_to_sheets


def save_news_to_sheets(
    articles: List[Dict[str, Any]],
    add_header: bool = False,
    add_timestamp: bool = True
) -> Dict[str, Any]:
    """
    保存新闻数据到 Google Sheets
    
    Args:
        articles: 新闻文章列表，每篇文章包含:
                 - title: 标题
                 - source: 来源
                 - published_at: 发布时间
                 - url: 链接
                 - raw_summary: 摘要
        add_header: 是否添加表头（默认 False）
        add_timestamp: 是否添加时间戳分隔行（默认 True）
        
    Returns:
        {
            "success": bool,
            "updated_cells": int,
            "updated_range": str,
            "sheet_url": str,
            "error": str  # 如果失败
        }
    """
    try:
        rows = []
        
        # 添加时间戳分隔行
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows.append([f"=== 批次: {timestamp} ===", "", "", "", ""])
        
        # 添加表头
        if add_header:
            rows.append(["发布时间", "标题", "来源", "链接", "摘要"])
        
        # 添加新闻数据
        for article in articles:
            rows.append([
                article.get('published_at', ''),
                article.get('title', ''),
                article.get('source', ''),
                article.get('url', ''),
                article.get('raw_summary', '')[:500]  # 限制摘要长度
            ])
        
        # 追加到 Google Sheets
        result = append_to_sheets(rows)
        
        # 获取表格 URL
        client = get_sheets_client()
        sheet_url = f"https://docs.google.com/spreadsheets/d/{client.spreadsheet_id}"
        
        return {
            "success": True,
            "updated_cells": result.get('updates', {}).get('updatedCells', 0),
            "updated_range": result.get('updates', {}).get('updatedRange', ''),
            "sheet_url": sheet_url
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def create_sheets_header() -> Dict[str, Any]:
    """
    在 Google Sheets 中创建表头
    只需要运行一次
    
    Returns:
        {
            "success": bool,
            "sheet_url": str,
            "error": str  # 如果失败
        }
    """
    try:
        from .sheets_client import write_to_sheets
        
        header = [["发布时间", "标题", "来源", "链接", "摘要"]]
        result = write_to_sheets(header)
        
        client = get_sheets_client()
        sheet_url = f"https://docs.google.com/spreadsheets/d/{client.spreadsheet_id}"
        
        return {
            "success": True,
            "sheet_url": sheet_url
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_sheet_url() -> Optional[str]:
    """
    获取 Google Sheets 的 URL
    
    Returns:
        表格 URL 或 None（如果失败）
    """
    try:
        client = get_sheets_client()
        return f"https://docs.google.com/spreadsheets/d/{client.spreadsheet_id}"
    except:
        return None
