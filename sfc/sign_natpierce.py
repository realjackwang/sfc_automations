import os
import requests
import json

# 定义 URL
login_url = "https://www.natpierce.cn/pc/login/login.html"
sign_url = "https://www.natpierce.cn/pc/sign/qiandao.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.natpierce.cn/pc/login/login.html",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.natpierce.cn",
    "X-Requested-With": "XMLHttpRequest"
}


def login_and_sign(username, password):
    """登录并签到"""
    session = requests.Session()
    try:
        login_data = {"username": username, "password": password}
        login_response = session.post(login_url, json=login_data, headers=headers)
        login_response.raise_for_status()

        if login_response.status_code == 200:
            print(f"用户 {username} 登录成功！")
            sign_response = session.post(sign_url, headers=headers)
            sign_response.raise_for_status()

            if sign_response.status_code == 200:
                print(f"用户 {username} 签到成功！")
                return True, f"用户 {username} 签到成功！"
            else:
                print(f"用户 {username} 签到失败！")
                return False, f"用户 {username} 签到失败！"
        else:
            print(f"用户 {username} 登录失败！")
            return False, f"用户 {username} 登录失败！"

    except requests.exceptions.RequestException as e:
        print(f"用户 {username} 发生错误：{e}")
        return False, f"用户 {username} 发生错误：{e}"
    finally:
        session.close()


def main(config):
    """
    主函数，执行签到并返回结果
    """
    title = 'NatPierce 签到'
    
    username = config.get('username')
    password = config.get('password')
    
    if not username or not password:
        return {
            'title': title,
            'success': False,
            'message': '用户名或密码未设置'
        }
    
    success, message = login_and_sign(username, password)
    
    return {
        'title': title,
        'success': success,
        'message': message
    }


if __name__ == '__main__':
    from config import NATPIERCE_CONFIG
    if NATPIERCE_CONFIG:
        result = main(NATPIERCE_CONFIG[0])
        print(f"脚本运行结果: {result}")
    else:
        print("No configuration found.")
