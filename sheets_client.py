"""
Google Sheets 客户端工具模块
提供与 Google Sheets 交互的封装函数
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build


class SheetsClient:
    """Google Sheets 客户端类"""
    
    def __init__(self, spreadsheet_id: Optional[str] = None, service_account_file: Optional[str] = None):
        """
        初始化 Google Sheets 客户端
        
        Args:
            spreadsheet_id: Google Spreadsheet ID，如果不提供则从环境变量读取
            service_account_file: 服务账号 JSON 文件路径，如果不提供则从环境变量读取
        """
        # 加载环境变量
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(dotenv_path=env_path)
        
        # 获取配置
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SPREADSHEET_ID")
        self.service_account_file = service_account_file or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        
        if not self.spreadsheet_id:
            raise ValueError("未找到 GOOGLE_SPREADSHEET_ID，请在 .env 文件中配置或传入参数")
        if not self.service_account_file:
            raise ValueError("未找到 GOOGLE_SERVICE_ACCOUNT_FILE，请在 .env 文件中配置或传入参数")
        
        # 认证和连接
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.scopes
        )
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheet = self.service.spreadsheets()
        
        # 缓存工作表信息
        self._sheets_cache = None
    
    def get_sheets(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """获取所有工作表信息"""
        if self._sheets_cache is None or force_refresh:
            spreadsheet = self.sheet.get(spreadsheetId=self.spreadsheet_id).execute()
            self._sheets_cache = spreadsheet.get('sheets', [])
        return self._sheets_cache
    
    def get_first_sheet_title(self) -> str:
        """获取第一个工作表的标题"""
        sheets = self.get_sheets()
        if not sheets:
            raise RuntimeError("未找到任何工作表")
        return sheets[0]['properties']['title']
    
    def write_data(self, data: List[List[Any]], range_notation: str, value_input_option: str = 'RAW') -> Dict[str, Any]:
        """写入数据到指定范围（会覆盖现有数据）"""
        result = self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_notation,
            valueInputOption=value_input_option,
            body={'values': data}
        ).execute()
        return result
    
    def append_data(self, data: List[List[Any]], range_notation: str, value_input_option: str = 'RAW') -> Dict[str, Any]:
        """追加数据到指定范围（不覆盖现有数据，追加到末尾）"""
        result = self.sheet.values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_notation,
            valueInputOption=value_input_option,
            insertDataOption='INSERT_ROWS',
            body={'values': data}
        ).execute()
        return result
    
    def read_data(self, range_notation: str) -> List[List[Any]]:
        """从指定范围读取数据"""
        result = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_notation
        ).execute()
        return result.get('values', [])


# ============ 便捷函数 ============

def get_sheets_client(spreadsheet_id: Optional[str] = None, service_account_file: Optional[str] = None) -> SheetsClient:
    """获取 Google Sheets 客户端实例"""
    return SheetsClient(spreadsheet_id, service_account_file)


def write_to_sheets(data: List[List[Any]], range_notation: Optional[str] = None, sheet_title: Optional[str] = None, spreadsheet_id: Optional[str] = None) -> Dict[str, Any]:
    """快速写入数据到 Google Sheets"""
    client = get_sheets_client(spreadsheet_id)
    
    if range_notation is None:
        sheet_name = sheet_title or client.get_first_sheet_title()
        range_notation = f"{sheet_name}!A1"
    
    return client.write_data(data, range_notation)


def append_to_sheets(data: List[List[Any]], range_notation: Optional[str] = None, sheet_title: Optional[str] = None, spreadsheet_id: Optional[str] = None) -> Dict[str, Any]:
    """快速追加数据到 Google Sheets"""
    client = get_sheets_client(spreadsheet_id)
    
    if range_notation is None:
        sheet_name = sheet_title or client.get_first_sheet_title()
        range_notation = f"{sheet_name}!A:Z"
    
    return client.append_data(data, range_notation)


def read_from_sheets(range_notation: str, spreadsheet_id: Optional[str] = None) -> List[List[Any]]:
    """快速从 Google Sheets 读取数据"""
    client = get_sheets_client(spreadsheet_id)
    return client.read_data(range_notation)
