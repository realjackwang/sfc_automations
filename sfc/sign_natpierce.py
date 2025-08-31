import os
import requests
import json

# 定义 URL 和登录信息
login_url = "https://www.natpierce.cn/pc/login/login.html"
sign_url = "https://www.natpierce.cn/pc/sign/qiandao.html"

# 获取多个账号和密码
usernames = json.loads(os.environ.get('natpierce_username', '[]'))
passwords = json.loads(os.environ.get('natpierce_password', '[]'))

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.natpierce.cn/pc/login/login.html",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.natpierce.cn",
    "X-Requested-With": "XMLHttpRequest"
}


def login_and_sign(username, password):
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
                return [f"{username} 签到", True]
            else:
                print(f"用户 {username} 签到失败！")
                return [f"{username} 签到", False]
        else:
            print(f"用户 {username} 登录失败！")
            return [f"{username} 登录失败", False]

    except requests.exceptions.RequestException as e:
        print(f"用户 {username} 发生错误：{e}")
        return [f"{username} 签到错误", False]
    finally:
        session.close()


def main():
    results = []
    if len(usernames) == len(passwords):
        for username, password in zip(usernames, passwords):
            result = login_and_sign(username, password)
            results.append(result)
    else:
        print("账号和密码数量不匹配，请检查环境变量！")

    return results


if __name__ == '__main__':
    main()
