import os
import requests
import importlib
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

from config import PUSH_METHOD, VERCEL_API_URL, SMZDM_CONFIG, POJIE52_CONFIG, ALIYUNDRIVE_CONFIG, NATPIERCE_CONFIG, V2EX_CONFIG


# 统一的推送模块
def push_notification(content, method, task_name, status, source="华为云"):
    """
    一个统一的推送接口，用于向各种渠道发送通知。
    """
    print(f"[{method}] 推送通知 - 任务: {task_name}, 状态: {status}, 消息: {content}")
    
    # 更改为直接使用 Vercel API
    if method == "vercel_api":
        if not VERCEL_API_URL:
            print("❌ Vercel API URL未设置，无法推送任务状态。")
            return
        
        payload = {
            "source": source,
            "task_name": task_name,
            "status": status,
            "message": content,
        }
        try:
            requests.post(VERCEL_API_URL, json=payload, timeout=10)
            print("✅ Vercel API 推送成功")
        except requests.exceptions.RequestException as e:
            print(f"❌ Vercel API 推送失败: {e}")


# 将所有子脚本集中管理
# 字典的值为元组，包含 (脚本模块, 脚本配置字典)
# 注意: 这里不再直接导入模块，只保留配置
func_list = {
    'sign_smzdm': SMZDM_CONFIG,
    'sign_52pojie': POJIE52_CONFIG,
    'sign_aliyundrive': ALIYUNDRIVE_CONFIG,
    'sign_natpierce': NATPIERCE_CONFIG,
    'sign_v2ex': V2EX_CONFIG,
}


def run_script(fun_name):
    """
    执行指定的子脚本并处理结果。
    """
    try:
        # 使用动态导入，根据名称加载模块
        script_module = importlib.import_module(fun_name)

        # 获取对应的配置
        config = func_list[fun_name]

        # 调用脚本的 main 函数，并传入配置
        result = script_module.main(config)

        # 检查返回结果的格式
        if not isinstance(result, dict) or 'success' not in result or 'title' not in result:
            raise ValueError(f"脚本 '{fun_name}' 返回的结果格式不正确。")

        # 打印运行结果
        print('-----------------')
        print(f"脚本: {result['title']}")
        print(f"状态: {'成功' if result['success'] else '失败'}")
        if 'message' in result:
            print(f"消息: {result['message']}")
        print('-----------------')
        
        # 根据结果进行通知
        if not result['success']:
            push_notification(
                content=result.get('message', '函数运行失败，请查看日志'),
                method=PUSH_METHOD,
                task_name=result['title'],
                status="failure"
            )
        else:
            push_notification(
                content=result.get('message', '函数运行成功'),
                method=PUSH_METHOD,
                task_name=result['title'],
                status="success"
            )
            
    except KeyError:
        # 如果找不到对应的云函数
        error_message = f"未找到名为 '{fun_name}' 的云函数。"
        print(error_message)
        push_notification(
            content=error_message,
            method=PUSH_METHOD,
            task_name=fun_name,
            status="failure"
        )
    except Exception as e:
        # 捕获所有其他异常
        error_message = f"脚本 '{fun_name}' 运行异常: {e}"
        print(error_message)
        push_notification(
            content=error_message,
            method=PUSH_METHOD,
            task_name=fun_name,
            status="failure"
        )


def handler(event, context):
    """
    华为云函数入口
    """
    # 确保 event 中有 'user_event'
    if 'user_event' in event:
        run_script(event['user_event'])
    else:
        print("未在事件中找到 'user_event' 参数。")


if __name__ == '__main__':
    # 在本地运行时，手动指定要运行的函数名
    # 请根据需要修改为你想测试的脚本
    run_script('sign_smzdm')
