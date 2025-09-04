
import os
import re
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup
from config import POJIE52_CONFIG


# 常量
SLEEP_TIME_RANGE = [60, 180]
URL_BASE = "https://www.52pojie.cn/"
URL_HOME = URL_BASE
URL_TASK_PAGE = URL_BASE + "home.php?mod=task&do=apply&id=2&referer=%2F"
URL_WAF_VERIFY = URL_BASE + "waf_zw_verify"
URL_EXTERNAL_SIGN_API = "https://52pojie-sign-sever.zzboy.tk/api/52pojie"
COMMON_HEADERS = {
  "Connection": "keep-alive",
  "Pragma": "no-cache",
  "Cache-Control": "no-cache",
  "Upgrade-Insecure-Requests": "1",
  "User-Agent": (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
  ),
  "Accept": (
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
    "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
  ),
  "Sec-Fetch-Site": "same-origin",
  "Sec-Fetch-Mode": "navigate",
  "Sec-Fetch-User": "?1",
  "Sec-Fetch-Dest": "document",
  "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"Windows"',
  "Referer": URL_BASE,
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
REQUEST_TIMEOUT = 30


def parse_cookie_str(cookie_str):
  """解析原始 Cookie 字符串，返回适用于 requests 的 cookie dict。"""
  if not cookie_str:
    return None, "Cookie 字符串为空"

  try:
    decoded_cookie = urllib.parse.unquote(cookie_str)
  except Exception as e:
    return None, f"Cookie 解码失败: {e}"

  cookies_for_requests = {}
  required_keys = {"htVC_2132_saltkey", "htVC_2132_auth"}
  found_keys = set()

  for item in decoded_cookie.split(";"):
    parts = item.split("=", 1)
    if len(parts) == 2:
      key, value = parts[0].strip(), parts[1].strip()
      if key in required_keys:
        cookies_for_requests[key] = value
        found_keys.add(key)

  if not required_keys.issubset(found_keys):
    missing = ", ".join(sorted(list(required_keys - found_keys)))
    return None, f"Cookie 中缺失必需字段: {missing}"

  return cookies_for_requests, ""


def check_status_and_get_params(session, user_cookies):
  """访问首页判断登录/签到状态，若未签到则获取签到所需参数。"""
  try:
    response = session.get(
      URL_HOME, headers=COMMON_HEADERS, cookies=user_cookies, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 登录失效判断（页面有登录按钮）
    if soup.find("button", class_="pn vm") is not None:
      return "Cookie失效 (需要登录)", None

    # 通过页面图片判断是否已签到
    sign_images = soup.find_all("img", class_="qq_bind")
    qds_icon_found = False
    wbs_icon_found = False

    for img_node in sign_images:
      src = img_node.get("src", "")
      if src.endswith("qds.png"):
        qds_icon_found = True
        break
      if src.endswith("wbs.png"):
        wbs_icon_found = True
        break

    if wbs_icon_found:
      return "今日已签到 (图片状态wbs.png)", None
    if not qds_icon_found and not wbs_icon_found:
      return (
        "无法确定签到状态 (未找到签到相关图片，可能页面结构改变或 Cookie 问题)",
        None,
      )

    # 找到未签到图标，访问任务页面获取参数
    task_response = session.get(
      URL_TASK_PAGE, headers=COMMON_HEADERS, cookies=user_cookies, timeout=REQUEST_TIMEOUT
    )
    task_response.raise_for_status()
    task_text = task_response.text

    # 两种正则尝试：优先匹配 renversement(...) 形式，否则回退到通用数字匹配
    match_lz_lj = re.search(r"renversement\('\s*([0-9]{4,})\s*'\).*renversement\('\s*([0-9]{4,})\s*'\)", task_text, re.S)
    if not match_lz_lj:
      match_lz_lj = re.search(r".*='([0-9]{4,})'.*='([0-9]{4,})'.*", task_text, re.S)

    if not match_lz_lj:
      return "未查询到签到参数", None

    lz, lj = match_lz_lj.group(1), match_lz_lj.group(2)

    match_le = re.search(r".*='([a-zA-Z0-9/+]{40,})'.*", task_text, re.S)
    if not match_le:
      return "未查询到签到参数", None

    le = match_le.group(1)
    return "待签到 (参数已获取)", {"lz": lz, "lj": lj, "le": le}

  except requests.exceptions.RequestException as e:
    return f"网络请求失败: {e}", None
  except Exception as e:
    return f"解析页面或获取参数时发生未知错误: {e}", None

  return "未知初始状态", None


def execute_signin_flow(session, user_cookies, signin_params, global_token):
  """执行外部签名 API + 提交 WAF 验证并返回最终结果文本。"""
  try:
    external_api_payload = {
      "lz": signin_params["lz"],
      "lj": signin_params["lj"],
      "le": signin_params["le"],
      "token": global_token,
    }

    external_api_response = requests.post(
      URL_EXTERNAL_SIGN_API, json=external_api_payload, timeout=REQUEST_TIMEOUT
    )

    if external_api_response.status_code != 200:
      try:
        error_msg = external_api_response.json().get("msg", external_api_response.text)
      except Exception:
        error_msg = external_api_response.text
      return (
        f"外部签名API调用失败 ({external_api_response.status_code}): {error_msg}. "
        "请检查API状态: https://zhustatus.azurewebsites.net/"
      )

    waf_payload_data = external_api_response.text

    waf_response = session.post(
      URL_WAF_VERIFY, headers=COMMON_HEADERS, cookies=user_cookies, data=waf_payload_data, timeout=REQUEST_TIMEOUT
    )
    waf_response.raise_for_status()

    final_check_response = session.get(
      URL_TASK_PAGE, headers=COMMON_HEADERS, cookies=user_cookies, timeout=REQUEST_TIMEOUT
    )
    final_check_response.raise_for_status()

    soup = BeautifulSoup(final_check_response.text, "html.parser")
    message_div = soup.find("div", id="messagetext")
    if not message_div:
      return "签到结果未知 (未找到消息区域)"

    message_p = message_div.find("p")
    if not message_p:
      return "签到结果未知 (未找到消息段落)"

    result_text = message_p.text.strip()
    if "您需要先登录才能继续本操作" in result_text:
      return "Cookie失效 (签到后验证)"
    if "恭喜" in result_text:
      return "签到成功"
    if "不是进行中的任务" in result_text or "已完成" in result_text:
      return "今日已签到 (任务状态反馈)"

    return f"签到失败: {result_text}"

  except requests.exceptions.RequestException as e:
    return f"签到流程中网络请求失败: {e}"
  except Exception as e:
    return f"签到流程中发生未知错误: {e}"


def main(config):
  title = "吾爱破解签到"
  session = requests.Session()

  cookie = config.get("cookie", "")
  global_token = config.get("token", "")

  if not cookie:
    return {"title": title, "success": False, "message": "Cookie 未设置"}

  user_cookies_dict, error_msg = parse_cookie_str(cookie)
  if error_msg:
    return {"title": title, "success": False, "message": error_msg}

  print("Cookie 解析成功:", user_cookies_dict)

  status_message, sign_params = check_status_and_get_params(session, user_cookies_dict)
  if status_message == "待签到 (参数已获取)" and sign_params:
    status_message = execute_signin_flow(session, user_cookies_dict, sign_params, global_token)

  success = "签到成功" in status_message or "已签到" in status_message
  print(status_message)
  return {"title": title, "success": success, "message": status_message}


if __name__ == "__main__":
  if POJIE52_CONFIG:
    result = main(POJIE52_CONFIG[0])
    print(f"脚本运行结果: {result}")
  else:
    print("请在 .env 文件中配置 sign_52pojie")
 
