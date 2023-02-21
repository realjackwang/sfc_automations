import requests
import json
import os
import sign_smzdm
import sign_52pojie
import sign_aliyundrive

xz_token = os.environ.get('xz_token')

func_list = {
    'sign_smzdm':sign_smzdm,
    'sign_52pojie':sign_52pojie,
    'sign_aliyundrive':sign_aliyundrive
    }

def xz_push(title, content):
    requests.get('https://xizhi.qqoq.net/%s.channel?title=%s&content=%s' % (xz_token, title, content))

def notion_push():
    pass

def sfc(fun_name):
    try:
        [title, success] = func_list[fun_name].main()

        print('-----------------\nsuccess: %s\n-----------------' % str(success))

        notion_push()

        if not success:
            xz_push(title, '执行失败')
    except:
        xz_push('%s 错误' % fun_name, '抛出异常，请及时查看日志')

def handler(event, context):
    if event['user_event'] in func_list.keys():
        sfc(event['user_event'])
    else:
        print('未找到该云函数')

if __name__ == '__main__':
  start()
 
