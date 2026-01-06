"""
Gmail 客户端工具模块
提供发送邮件的封装函数
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64


SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    """
    获取 Gmail API 服务
    自动处理认证和 token 刷新
    """
    # 加载环境变量
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path)
    
    creds = None
    token_file = os.getenv("GMAIL_TOKEN_FILE", "./gmail_token.pickle")
    credentials_file = os.getenv("GMAIL_CREDENTIALS_FILE", "./gmail_credentials.json")
    
    # 检查是否有保存的 token
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # 如果没有有效凭据，让用户登录
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 保存凭据供下次使用
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)


def send_news_email(
    articles: List[Dict[str, Any]],
    to_email: Optional[str] = None,
    subject: Optional[str] = None,
    time_window: Optional[str] = None,
    sheet_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    发送新闻汇总邮件
    
    Args:
        articles: 新闻文章列表，每篇文章包含 title, source, url, published_at, raw_summary
        to_email: 收件人邮箱（可选，默认从环境变量读取）
        subject: 邮件主题（可选，默认自动生成）
        time_window: 时间窗口描述（可选）
        sheet_url: Google Sheets 链接（可选）
        
    Returns:
        {
            "success": bool,
            "message_id": str,  # 如果成功
            "error": str        # 如果失败
        }
    """
    # 加载环境变量
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # 获取收件人
    if not to_email:
        to_email = os.getenv("GMAIL_TO")
    
    if not to_email:
        return {
            "success": False,
            "error": "未设置收件人邮箱（GMAIL_TO）"
        }
    
    # 生成主题
    if not subject:
        subject = f"📰 新闻日报 - {len(articles)} 条新闻"
    
    try:
        service = get_gmail_service()
        
        # 构建邮件
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['To'] = to_email
        message['From'] = 'me'
        
        # 构建 HTML 正文
        html_body = _build_html_body(articles, time_window, sheet_url)
        
        # 构建纯文本正文
        text_body = _build_text_body(articles, time_window, sheet_url)
        
        # 添加到邮件
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        message.attach(part1)
        message.attach(part2)
        
        # 发送
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return {
            "success": True,
            "message_id": sent_message['id']
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _build_html_body(
    articles: List[Dict[str, Any]], 
    time_window: Optional[str] = None,
    sheet_url: Optional[str] = None
) -> str:
    """构建 HTML 邮件正文"""
    
    html = """
    <html>
      <head>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
          h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
          .summary { background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #3498db; }
          .article { margin: 20px 0; padding: 15px; border-left: 3px solid #3498db; background-color: #f9f9f9; }
          .article h3 { margin: 0 0 8px 0; color: #2c3e50; }
          .meta { color: #7f8c8d; font-size: 0.9em; margin: 5px 0; }
          .summary-text { color: #555; margin: 10px 0; }
          a { color: #3498db; text-decoration: none; }
          a:hover { text-decoration: underline; }
          .button { display: inline-block; padding: 10px 20px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        </style>
      </head>
      <body>
        <h1>📰 新闻日报</h1>
        
        <div class="summary">
          <strong>📊 本期摘要</strong><br>
    """
    
    html += f"          • 新闻总数: <strong>{len(articles)}</strong><br>\n"
    
    if time_window:
        html += f"          • 时间范围: {time_window}<br>\n"
    
    html += "        </div>\n"
    
    # 添加 Google Sheets 链接
    if sheet_url:
        html += f'        <p><a href="{sheet_url}" class="button">📊 查看完整报告（Google Sheets）</a></p>\n'
    
    html += "        <h2>📑 今日头条</h2>\n"
    
    # 添加新闻文章（最多显示 10 条）
    for i, article in enumerate(articles[:10], 1):
        title = article.get('title', '无标题')
        source = article.get('source', '未知来源')
        published_at = article.get('published_at', 'N/A')
        url = article.get('url', '#')
        summary = article.get('raw_summary', '暂无摘要')
        
        html += f"""
        <div class="article">
          <h3>{i}. {title}</h3>
          <div class="meta">
            📍 来源: <strong>{source}</strong> | 🕐 发布时间: {published_at}
          </div>
          <div class="summary-text">{summary}</div>
          <a href="{url}">阅读全文 →</a>
        </div>
        """
    
    # 如果新闻超过 10 条，添加提示
    if len(articles) > 10:
        html += f"""
        <div class="summary">
          <strong>📌 注意:</strong> 为了邮件简洁，仅显示前 10 条新闻。
          完整的 {len(articles)} 条新闻请查看 Google Sheets。
        </div>
        """
    
    html += """
      </body>
    </html>
    """
    
    return html


def _build_text_body(
    articles: List[Dict[str, Any]], 
    time_window: Optional[str] = None,
    sheet_url: Optional[str] = None
) -> str:
    """构建纯文本邮件正文"""
    
    text = "=" * 60 + "\n"
    text += "📰 新闻日报\n"
    text += "=" * 60 + "\n\n"
    
    text += f"新闻总数: {len(articles)}\n"
    
    if time_window:
        text += f"时间范围: {time_window}\n"
    
    if sheet_url:
        text += f"\n📊 查看完整报告: {sheet_url}\n"
    
    text += "\n" + "=" * 60 + "\n"
    text += "📑 今日头条\n"
    text += "=" * 60 + "\n\n"
    
    # 添加新闻文章（最多显示 10 条）
    for i, article in enumerate(articles[:10], 1):
        title = article.get('title', '无标题')
        source = article.get('source', '未知来源')
        published_at = article.get('published_at', 'N/A')
        url = article.get('url', '#')
        summary = article.get('raw_summary', '暂无摘要')
        
        text += f"{i}. {title}\n"
        text += f"   来源: {source}\n"
        text += f"   时间: {published_at}\n"
        text += f"   摘要: {summary}\n"
        text += f"   链接: {url}\n"
        text += "\n"
    
    if len(articles) > 10:
        text += f"\n注意: 仅显示前 10 条新闻，完整的 {len(articles)} 条新闻请查看 Google Sheets。\n"
    
    text += "=" * 60 + "\n"
    
    return text


# ============ 便捷函数 ============

def send_email(
    articles: List[Dict[str, Any]],
    to_email: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    发送新闻邮件的简化接口
    
    Args:
        articles: 新闻列表
        to_email: 收件人（可选）
        **kwargs: 其他参数（subject, time_window, sheet_url）
        
    Returns:
        包含 success 和 message_id 或 error 的字典
    """
    return send_news_email(articles, to_email, **kwargs)
