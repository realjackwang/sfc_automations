import os
import requests
import logging
from utils import HW

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

refresh_token = os.environ.get('aliyundrive_refresh_token')
update_access_token_url = 'https://auth.aliyundrive.com/v2/account/token'
sign_url = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
data = {
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token
}


def update_access_token():
    headers = {'Content-Type': 'application/json'}
    res = requests.post(update_access_token_url, headers=headers, json=data)
    print('update_res:\n' + str(res.json()))
    if res.status_code == 200:
        access_token = res.json()['access_token']
        refresh_token = res.json()['refresh_token']
        hw = HW()
        hw.update_user_data('aliyundrive_refresh_token', refresh_token)
    else:
        access_token = None
        logging.error('access_token 获取失败.')
    return access_token


def get_reward_all(access_token, max_day):
    url = 'https://member.aliyundrive.com/v1/activity/sign_in_reward'
    params = {'_rx-s': 'mobile'}
    headers = {'Authorization': f'Bearer {access_token}'}
    for day in range(1, max_day + 1):
        try:
            requests.post(
                url,
                params=params,
                headers=headers,
                json={'signInDay': day},
            )
        except requests.RequestException as e:
            logging.error(f'兑换请求失败: {e}')
            return False
    logging.info('已自动领取本月全部奖励.')
    return True


def sign(access_token):
    success = False
    if access_token:
        headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
        res = requests.post(sign_url, headers=headers, json=data)
        print('sign_res:\n' + str(res.json()))
        success = res.json()['success']
        if not success:
            logging.error('签到失败.')
            return False
        signin_count = res.json()['result']['signInCount']
        logging.info(f'签到成功, 本月累计签到 {signin_count} 天.')
        success = get_reward_all(access_token, len(res.json()['result']['signInLogs']))
    return success


def main():
    title = '阿里云盘签到'

    access_token = update_access_token()
    success = sign(access_token)

    return [title, success]


if __name__ == '__main__':
    main()
