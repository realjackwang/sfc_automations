import os
import requests
import json
import logging
from utils import HW
from config import ALIYUNDRIVE_CONFIG
from typing import Tuple


UPDATE_ACCESS_TOKEN_URL = 'https://auth.aliyundrive.com/v2/account/token'
SIGN_URL = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
REWARD_URL = 'https://member.aliyundrive.com/v1/activity/sign_in_reward'

REQUEST_TIMEOUT = 30


def update_access_token(refresh_token: str):
    headers = {'Content-Type': 'application/json'}
    payload = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    try:
        res = requests.post(UPDATE_ACCESS_TOKEN_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        logging.info('update_res: %s', res.text)
        if res.status_code == 200:
            j = res.json()
            access_token = j.get('access_token')
            new_refresh_token = j.get('refresh_token')
            if new_refresh_token:
                try:
                    hw = HW()
                    # 尝试读取已有的 user_data 中的 sign_aliyundrive 配置（优先更新数组），兼容旧的 aliyundrive_refresh_token
                    user_data = hw.get_user_data() or {}
                    updated = False
                    if isinstance(user_data, dict) and 'sign_aliyundrive' in user_data:
                        sval = user_data.get('sign_aliyundrive')
                        # 支持存为 JSON 字符串或直接为列表
                        parsed = None
                        if isinstance(sval, str):
                            try:
                                parsed = json.loads(sval)
                            except Exception:
                                parsed = None
                        elif isinstance(sval, list):
                            parsed = sval

                        if isinstance(parsed, list) and len(parsed) > 0:
                            # 仅按传入的旧 refresh_token 精确匹配更新对应账号，支持多账号
                            for entry in parsed:
                                if isinstance(entry, dict) and entry.get('refresh_token') == refresh_token:
                                    entry['refresh_token'] = new_refresh_token
                                    updated = True
                                    break

                            if updated:
                                # 将修改写回列表
                                try:
                                    hw.update_user_data('sign_aliyundrive', parsed)
                                except Exception:
                                    try:
                                        hw.update_user_data('sign_aliyundrive', json.dumps(parsed, ensure_ascii=False))
                                    except Exception:
                                        logging.exception('写回 sign_aliyundrive 列表失败')
                            else:
                                logging.info('未在 sign_aliyundrive 列表中匹配到旧 refresh_token，未修改配置')

                    if not updated:
                        logging.info('未更新任何 sign_aliyundrive 条目（未匹配旧 refresh_token）')
                except Exception:
                    logging.exception('更新本地 refresh_token 失败')
            return access_token, new_refresh_token
        else:
            logging.error('access_token 获取失败: %s', res.text)
            return None, None
    except requests.RequestException as e:
        logging.error('请求获取 access_token 失败: %s', e)
        return None, None


def get_reward_all(access_token: str, max_day: int) -> bool:
    params = {'_rx-s': 'mobile'}
    headers = {'Authorization': f'Bearer {access_token}'}
    for day in range(1, max_day + 1):
        try:
            requests.post(REWARD_URL, params=params, headers=headers, json={'signInDay': day}, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            logging.error('兑换请求失败: %s', e)
            return False
    logging.info('已自动领取本月全部奖励.')
    return True


def sign(access_token: str) -> Tuple[bool, str]:
    """返回 (success, message)"""
    if not access_token:
        return False, 'access_token 为空'
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    try:
        res = requests.post(SIGN_URL, headers=headers, json={}, timeout=REQUEST_TIMEOUT)
        logging.info('sign_res: %s', res.text)
        j = res.json()
    except requests.RequestException as e:
        logging.error('签到请求失败: %s', e)
        return False, f'签到请求失败: {e}'
    except ValueError:
        return False, '签到返回解析失败'

    success = j.get('success', False)
    if not success:
        msg = j.get('message') or str(j)
        logging.error('签到失败: %s', msg)
        return False, f'签到失败: {msg}'

    signin_count = j.get('result', {}).get('signInCount')
    logging.info('签到成功, 本月累计签到 %s 天.', signin_count)
    max_day = len(j.get('result', {}).get('signInLogs', []))
    got_all = get_reward_all(access_token, max_day)
    if not got_all:
        return False, '签到成功但领取奖励失败'
    return True, f'签到成功, 本月累计签到 {signin_count} 天, 并已领取奖励'


def main(config):
    title = '阿里云盘签到'
    refresh_token = config.get('refresh_token')
    if not refresh_token:
        msg = '未提供 refresh_token'
        logging.error(msg)
        return {'title': title, 'success': False, 'message': msg}

    #access_token, new_refresh = update_access_token(refresh_token)
    access_token = config.get('access_token')
    if not access_token:
        msg = '更新 access_token 失败'
        logging.error(msg)
        return {'title': title, 'success': False, 'message': msg}

    success, message = sign(access_token)
    return {'title': title, 'success': success, 'message': message}


if __name__ == '__main__':
    result = main(ALIYUNDRIVE_CONFIG[0])
    print(f"脚本运行结果: {result}")
