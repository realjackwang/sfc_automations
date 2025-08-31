import os
import requests
import sign_smzdm
import sign_52pojie
import sign_aliyundrive
import sign_natpierce

xz_token = os.environ.get('xz_token')

func_list = {
    'sign_smzdm': sign_smzdm,
    'sign_52pojie': sign_52pojie,
    'sign_aliyundrive': sign_aliyundrive,
    'sign_natpierce': sign_natpierce
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
            xz_push('%s 失败' % title, '函数运行失败，请查看日志')
    except:
        xz_push('%s 错误' % fun_name, '抛出异常，请及时查看日志')


def handler(event, context):
    if event['user_event'] in func_list.keys():
        sfc(event['user_event'])
    else:
        print('未找到该云函数')


if __name__ == '__main__':
    sfc('sign_smzdm')
