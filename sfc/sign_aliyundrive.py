import os
import requests
from utils import HW

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
    return access_token


def sign(access_token):
    if access_token:
        headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
        res = requests.post(sign_url, headers=headers, json=data)
        print('sign_res:\n' + str(res.json()))
        return res.json()['success']
    else:
        return False


def main():
    title = '阿里云盘签到'
    success = False

    access_token = update_access_token()
    success = sign(access_token)

    return [title, success]


if __name__ == '__main__':
    main()
