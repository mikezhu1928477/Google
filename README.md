
Gmail配置
第一步：
访问 https://console.cloud.google.com/apis/library/gmail.googleapis.com  点击使用此api。

第二步：
访问：https://console.cloud.google.com/apis/credentials 
如果有显示黄色箭头《请务必使用关于您的应用的信息配置 OAuth 权限请求页面。》需要配置Google Auth Platform
全部选择自己邮箱，

第三步：
创建 OAuth 客户端 ID，桌面应用
显示OAuth客户端已创建之后 点击左下角下载Json

第四步：
把下载好的   {OAuth客户端凭证}    改名成gmail_credentials.json，放到本地文件夹

---------------------------------------------------------------------------------------------
Google sheets配置
第一步：
访问：https://console.cloud.google.com/ 点击顶部项目名 → "新建项目" 点"创建"

第二步：
访问：https://console.cloud.google.com/apis/library 搜索：Google Sheets API 点"启用"

第三步：
访问：https://console.cloud.google.com/iam-admin/serviceaccounts
点 "新创项目" 创建， 名字设为news-bot

第四步：
点击刚创建的 news-bot 点"密钥"标签 点"添加密钥" → "创建新密钥"
选"JSON" → 点"创建"

第五步：
把下载好   {服务账号密钥（机器人账号）}  改名成gmail_credentials.json，放到本地文件夹

第六步：
5️⃣ 创建 Google Sheet 并共享
访问：https://sheets.google.com/ 创建新表格 点右上角"共享"
粘贴机器人邮箱（在 JSON 文件里找 client_email），权限选"编辑者"，点"共享"

-------------------------------------------------
.env配置

# 需要改的
GOOGLE_SPREADSHEET_ID= 复制google spreadsheet的url
    比如：
    https://docs.google.com/spreadsheets/d/1yRqPIl6HqMTX3QUejQB0_wojW3EkVVp3HGaJOabglj0/edit?gid=0#gid=0
    这里的GOOGLE_SPREADSHEET_ID就是1yRqPIl6HqMTX3QUejQB0_wojW3EkVVp3HGaJOabglj0

GMAIL_TO=自己的邮箱

# 原封不动
GOOGLE_SERVICE_ACCOUNT_FILE=./service-account.json 
GMAIL_CREDENTIALS_FILE=./gmail_credentials.json

