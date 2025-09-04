import os
import json
from dotenv import load_dotenv

load_dotenv()

# 消息推送配置
PUSH_METHOD = os.getenv("PUSH_METHOD")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WXPUSHER_SPT = os.getenv("WXPUSHER_SPT")
VERCEL_API_URL = os.getenv("VERCEL_API_URL")

# 脚本相关的配置
SMZDM_CONFIG = json.loads(os.getenv('sign_smzdm', '[{"cookie": ""}]'))
POJIE52_CONFIG = json.loads(os.getenv('sign_52pojie', '[{"cookie": "", "token": ""}]'))
ALIYUNDRIVE_CONFIG = json.loads(os.getenv('sign_aliyundrive', '[{"refresh_token": ""}]'))
NATPIERCE_CONFIG = json.loads(os.getenv('sign_natpierce', '[{"username": "", "password": ""}]'))
V2EX_CONFIG = json.loads(os.getenv('sign_v2ex', '[{"cookie": ""}]'))
HIFINI_CONFIG = json.loads(os.getenv('sign_hifini', '[{"cookie": ""}]'))
