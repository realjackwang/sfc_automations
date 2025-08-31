import hashlib
import random
import time
import requests
import json
import os

# 状态地址
current_url = 'https://zhiyou.smzdm.com/user/info/jsonp_get_current'
# 签到地址
checkin_url = 'https://user-api.smzdm.com/checkin'


def md5(m: str):
    """计算 MD5 值"""
    return hashlib.md5(m.encode()).hexdigest()


def sign_request(url, config):
    """发送签到请求并返回响应数据"""
    sk = config.get('sk')
    token = config.get('token')
    cookie = config.get('cookie')
    key = config.get('key')
    
    if not (sk and token and cookie):
        return {'error_msg': '配置信息不完整', 'success': False}

    timestamp = int(time.time())
    headers = {
        'user-agent': 'smzdm_android_V10.4.20 rv:860 (Redmi Note 3;Android10;zh)smzdmapp',
        'request_key': str(
            random.randint(10000000, 100000000) * 10000000000 + timestamp
        ),
        'cookie': cookie,
        'content-type': 'application/x-www-form-urlencoded',
    }
    timestamp = timestamp - random.randint(0, 10)
    data = {
        'weixin': '1',
        'captcha': '',
        'f': 'android',
        'v': '10.4.20',
        'sk': sk,
        'sign': md5(
            f'f=android&sk={sk}&time={timestamp * 1000}&token={token}&v=10.4.20&weixin=1&key={key}'
        ).upper(),
        'touchstone_event': '',
        'time': timestamp * 1000,
        'token': token,
    }
    try:
        res = requests.post(url, headers=headers, data=data)
        res.raise_for_status()
        return json.loads(res.text)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def main(config):
    """
    主函数，执行签到并返回结果
    """
    title = '什么值得买签到'
    
    data = sign_request(checkin_url, config)
    
    if data:
        if data.get('error_code') == 0:
            # 签到成功
            message = data.get('data', {}).get('checkin_reward', '')
            return {
                'title': title,
                'success': True,
                'message': f"签到成功，获得：{message}"
            }
        else:
            # 签到失败
            return {
                'title': title,
                'success': False,
                'message': data.get('error_msg', '未知错误')
            }
    else:
        # 请求失败
        return {
            'title': title,
            'success': False,
            'message': '请求失败，请检查网络或配置'
        }

if __name__ == '__main__':
    # 仅用于本地测试，从环境变量获取配置
    from config import SMZDM_CONFIG
    result = main(SMZDM_CONFIG)
    print(f"脚本运行结果: {result}")
