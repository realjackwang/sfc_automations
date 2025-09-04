import json
import requests
from datetime import datetime

def set_cookies(session, cookies_str):
    """设置cookies"""
    try:
        cookies = {}
        for c in cookies_str.split(';'):
            if '=' in c:
                key, value = c.strip().split('=', 1)
                cookies[key.strip()] = value.strip()
        session.cookies.update(cookies)
        return True
    except Exception as e:
        return False

def do_sign(session, sign_url):
    """执行签到"""
    try:
        response = session.post(sign_url, timeout=10)
        
        if response.status_code == 200:
            rsp_text = response.text.strip()
            if "今天已经签过啦！" in rsp_text:
                return True, '已经签到过了，不再重复签到!'
            elif "成功" in rsp_text:
                try:
                    rsp_json = json.loads(rsp_text)
                    return True, rsp_json.get('message', '签到成功')
                except:
                    return True, '签到成功'
            elif "请登录后再签到!" in rsp_text:
                return False, "Cookie没有正确设置！"
            else:
                return False, f"未知异常: {rsp_text}"
        else:
            return False, f"请求失败，状态码: {response.status_code}"
    except Exception as e:
        return False, f"签到过程发生错误: {str(e)}"

def main(config):
    title = 'HiFiNi 签到'
    cookie = config.get('cookie', '')
    domain = config.get('domain', 'www.hifini.com')
    
    if not cookie:
        return {'success': False, 'title': title, 'message': 'Cookie 未设置'}
    
    base_url = f"https://{domain}"
    sign_url = f"{base_url}/sg_sign.htm"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'text/plain, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': base_url,
        'Referer': base_url,
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    if not set_cookies(session, cookie):
        return {'success': False, 'title': title, 'message': '设置 Cookies 失败'}
    
    success, message = do_sign(session, sign_url)
    return {'success': success, 'title': title, 'message': message}


if __name__ == "__main__":
    from config import HIFINI_CONFIG
    result = main(HIFINI_CONFIG[0])
    print(f"脚本运行结果: {result}")


