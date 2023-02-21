import hashlib
import random
import time
import requests
import os
import json

sk = os.environ.get('smzdm_sk')
token = os.environ.get('smzdm_token')
cookie = os.environ.get('smzdm_cookie')
key = 'apr1$AwP!wRRT$gJ/q.X24poeBInlUJC'


# 状态地址
current_url = 'https://zhiyou.smzdm.com/user/info/jsonp_get_current'
# 签到地址
checkin_url = 'https://user-api.smzdm.com/checkin'

user_tuple = (
    {
        'sk': sk,
        'token': token,
        'cookie': cookie,
    },
)

def md5(m: str):
    return hashlib.md5(m.encode()).hexdigest()


def sign(url):
    global code
    url = url
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
            f'f=android&sk={sk}&time={timestamp*1000}&token={token}&v=10.4.20&weixin=1&key={key}'
        ).upper(),
        'touchstone_event': '',
        'time': timestamp * 1000,
        'token': token,
    }
    res = requests.post(url, headers=headers, data=data)
    if res.status_code == 200:
        data = json.loads(res.text)
        return data
    else:
        return None


def main():
    title = '什么值得买签到'
    success = False

    data = sign(checkin_url)
    if data:
        if data['error_msg']:
            success = True
        else:
            success = True
    return [title, success]


if __name__ == '__main__':
  main()
 
