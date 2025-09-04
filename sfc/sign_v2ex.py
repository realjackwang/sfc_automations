import os
import re
import time
from datetime import date, datetime

import requests

def get_once(session, headers):
    """获取 once"""
    url = "https://www.v2ex.com/mission/daily"
    r = session.get(url, headers=headers)

    if "你要查看的页面需要先登录" in r.text:
        return "", False, "登录失败，Cookie 可能已经失效"
    elif "每日登录奖励已领取" in r.text:
        match = re.search(r"已连续登录 \d+ 天", r.text)
        days = match.group(0) if match else ""
        return "", True, f"每日登录奖励已领取，{days}"

    once_match = re.search(r"once=(\d+)", r.text)
    if once_match:
        once = once_match.group(1)
        return once, True, "登录成功"
    else:
        return "", False, "获取 once 失败"


def check_in(session, headers, once):
    """签到"""
    url = "https://www.v2ex.com/mission/daily/redeem?once=" + once
    session.get(url, headers=headers)


def query_balance(session, headers):
    """查询余额"""
    url = "https://www.v2ex.com/balance"
    r = session.get(url, headers=headers)
    
    # 签到结果
    checkin_day_match = re.search(r'<small class="gray">(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \+\d{4})</small>', r.text)
    if checkin_day_match:
        checkin_day_str = checkin_day_match.group(1)
        checkin_day = datetime.strptime(checkin_day_str, '%Y-%m-%d %H:%M:%S %z')
        if checkin_day.date() == date.today():
            # 签到奖励
            bonus_match = re.search(r'(\d+ 的每日登录奖励 \d+ 铜币)', r.text)
            bonus = bonus_match.group(1) if bonus_match else "签到奖励获取失败"

            # 余额
            balance_matches = re.findall(r'<div class="balance_area bigger">([^<]+)</div>', r.text)
            if len(balance_matches) == 2:
                balance_matches = ['0'] + balance_matches

            if len(balance_matches) >= 3:
                golden, silver, bronze = [s.strip() for s in balance_matches[:3]]
                balance_msg = f"{golden} 金币，{silver} 银币，{bronze} 铜币"
            else:
                balance_msg = "余额获取失败"
            
            return True, bonus, balance_msg
        else:
            return False, "签到失败", "获取失败"
    else:
        return False, "签到失败", "获取失败"


def main(config):
    """
    主函数，执行签到并返回结果
    """
    title = 'V2EX 签到'
    
    cookie = config.get('cookie')
    if not cookie:
        return {
            'title': title,
            'success': False,
            'message': 'Cookie 未设置'
        }
    
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6,da;q=0.5",
        "cache-control": "no-cache",
        "Cookie": cookie,
        "pragma": "no-cache",
        "Referer": "https://www.v2ex.com/",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "x-requested-with": "X",
    }
    
    session = requests.Session()
    
    # 获取 once
    for i in range(3):
        try:
            once, success, login_msg = get_once(session, headers)
            break
        except AttributeError:
            if i < 2:
                time.sleep(3)
            else:
                return {
                    'title': title,
                    'success': False,
                    'message': '获取 once 失败'
                }
    
    messages = [login_msg]
    
    if once:
        check_in(session, headers, once)
        # 重新检查状态
        _, _, updated_login_msg = get_once(session, headers)
        messages = [updated_login_msg]
    
    if success:
        balance_success, bonus_msg, balance_msg = query_balance(session, headers)
        messages.append(bonus_msg)
        messages.append(f"账户余额: {balance_msg}")
        success = balance_success
    
    message = "\n".join(messages)
    
    return {
        'title': title,
        'success': success,
        'message': message
    }


if __name__ == '__main__':
    from config import V2EX_CONFIG
    if V2EX_CONFIG:
        result = main(V2EX_CONFIG[0])
        print(f"脚本运行结果: {result}")
    else:
        print("No configuration found.")