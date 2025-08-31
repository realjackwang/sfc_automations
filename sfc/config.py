import os

# 消息推送配置
PUSH_METHOD = os.getenv("PUSH_METHOD")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WXPUSHER_SPT = os.getenv("WXPUSHER_SPT")
VERCEL_API_URL = os.getenv("VERCEL_API_URL")

# 脚本相关的配置
SMZDM_CONFIG = {
    'sk': os.getenv('smzdm_sk'),
    'token': os.getenv('smzdm_token'),
    'cookie': os.getenv('smzdm_cookie'),
    'key': 'apr1$AwP!wRRT$gJ/q.X24poeBInlUJC',
}
POJIE52_CONFIG = {
    'cookie': os.getenv('pojie_cookie'),
}
ALIYUNDRIVE_CONFIG = {
    'refresh_token': os.getenv('aliyundrive_refresh_token'),
}
NATPIERCE_CONFIG = {
    'username': os.getenv('natpierce_username'),
    'password': os.getenv('natpierce_password'),
}
V2EX_CONFIG = {
    'cookie': os.getenv('V2EX_COOKIES'),
} 
