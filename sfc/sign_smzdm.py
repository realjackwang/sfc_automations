import hashlib
import random
import time
import requests
import json
import os
import re

def md5(m: str):
    """计算 MD5 值"""
    return hashlib.md5(m.encode()).hexdigest()

def robot_token(headers):
    """获取机器人 token"""
    ts = int(round(time.time() * 1000))
    url = "https://user-api.smzdm.com/robot/token"
    data = {
        "f": "android",
        "v": "10.4.1",
        "weixin": 1,
        "time": ts,
        "sign": md5(
            f"f=android&time={ts}&v=10.4.1&weixin=1&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC"
        ).upper(),
    }
    try:
        html = requests.post(url=url, headers=headers, data=data)
        result = html.json()
        token = result["data"]["token"]
        return token
    except:
        return None

def sign(headers, token):
    """执行签到"""
    Timestamp = int(round(time.time() * 1000))
    data = {
        "f": "android",
        "v": "10.4.1",
        "sk": "ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L",
        "weixin": 1,
        "time": Timestamp,
        "token": token,
        "sign": md5(
            f"f=android&sk=ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L&time={Timestamp}&token={token}&v=10.4.1&weixin=1&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC"
        ).upper(),
    }
    url = "https://user-api.smzdm.com/checkin"
    try:
        resp = requests.post(url=url, headers=headers, data=data)
        error_msg = resp.json()["error_msg"]
        return error_msg, data
    except:
        return "签到请求失败", data

def all_reward(headers, data):
    """领取所有奖励"""
    url2 = "https://user-api.smzdm.com/checkin/all_reward"
    try:
        resp = requests.post(url=url2, headers=headers, data=data)
        result = resp.json()
        msgs = []
        if normal_reward := result["data"]["normal_reward"]:
            try:
                msgs = [
                    f"签到奖励: {normal_reward['reward_add']['content']}",
                    f"连续签到: {normal_reward['sub_title']}",
                ]
            except:
                msgs = ["奖励信息解析失败"]
        return msgs
    except:
        return ["领取奖励失败"]

def active(cookie):
    """获取用户信息"""
    zdm_active_id = ["ljX8qVlEA7"]
    for active_id in zdm_active_id:
        url = f"https://zhiyou.smzdm.com/user/lottery/jsonp_draw?active_id={active_id}"
        rewardurl = f"https://zhiyou.smzdm.com/user/lottery/jsonp_get_active_info?active_id={active_id}"
        infourl = "https://zhiyou.smzdm.com/user/"
        headers = {
            "Host": "zhiyou.smzdm.com",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/smzdm 10.4.6 rv:130.1 (iPhone 13; iOS 15.6; zh_CN)/iphone_smzdmapp/10.4.6/wkwebview/jsbv_1.0.0",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Referer": "https://m.smzdm.com/",
            "Accept-Encoding": "gzip, deflate, br",
        }
        try:
            response = requests.post(url=url, headers=headers).json()
            response_info = requests.get(url=infourl, headers=headers).text
            _ = requests.get(url=rewardurl, headers=headers).json()
            name = (
                str(
                    re.findall(
                        '<a href="https://zhiyou.smzdm.com/user"> (.*?) </a>',
                        str(response_info),
                        re.S,
                    )
                )
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
            )
            level = (
                str(
                    re.findall(
                        r'<img src="https://res.smzdm.com/h5/h5_user/dist/assets/level/(.*?).png\?v=1">',
                        str(response_info),
                        re.S,
                    )
                )
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
            )
            gold = (
                str(
                    re.findall(
                        '<div class="assets-part assets-gold">\n                    (.*?)</span>',
                        str(response_info),
                        re.S,
                    )
                )
                .replace("[", "")
                .replace("]", "")
                .replace("'’", "")
                .replace('<span class="assets-part-element assets-num">', "")
                .replace("'", "")
            )
            silver = (
                str(
                    re.findall(
                        '<div class="assets-part assets-prestige">\n                    (.*?)</span>',
                        str(response_info),
                        re.S,
                    )
                )
                .replace("[", "")
                .replace("]", "")
                .replace("'’", "")
                .replace('<span class="assets-part-element assets-num">', "")
                .replace("'", "")
            )
            msg = [
                f"签到结果: {response['error_msg']}",
                f"等级: {level}",
                f"昵称: {name}",
                f"金币: {gold}",
                f"碎银: {silver}",
            ]
            return msg
        except:
            return ["获取用户信息失败"]
    return []

def main(config):
    """
    主函数，执行签到并返回结果
    """
    title = '什么值得买签到'
    
    cookie = config.get('cookie')
    if not cookie:
        return {
            'title': title,
            'success': False,
            'message': 'Cookie 未设置'
        }
    
    headers = {
        "Host": "user-api.smzdm.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookie,
        "User-Agent": "smzdm_android_V10.4.1 rv:841 (22021211RC;Android12;zh)smzdmapp",
    }
    
    # 获取用户信息
    user_info = active(cookie)
    
    # 获取 token
    token = robot_token(headers)
    if not token:
        return {
            'title': title,
            'success': False,
            'message': '获取 token 失败'
        }
    
    # 签到
    error_msg, data = sign(headers, token)
    
    # 领取奖励
    reward_msgs = all_reward(headers, data)
    
    # 组合消息
    all_msgs = user_info + [f"签到结果: {error_msg}"] + reward_msgs
    message = "\n".join(all_msgs)
    
    # 判断成功
    success = "成功" in error_msg or "已签到" in error_msg
    
    return {
        'title': title,
        'success': success,
        'message': message
    }

if __name__ == '__main__':
    from config import SMZDM_CONFIG
    result = main(SMZDM_CONFIG[0])
    print(f"脚本运行结果: {result}")
