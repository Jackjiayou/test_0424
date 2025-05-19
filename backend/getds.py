# coding=utf-8

from openai import OpenAI
import  logging
import  traceback
from datetime import datetime
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
DP_URL = 'https://api.deepseek.com/v1'
DP_KEY ='sk-083524dfc0b747d69bfcf3fd5b19c9ca'

def get_messages( history):
    # 构建系统消息（包含角色定义和规则）
    system_message = {
        'role': 'system',
        'content': '''你是一个专业的大健康行业健康助手，具备以下能力：
                    1. 提供基础健康知识咨询（如饮食、运动、睡眠建议）
                    2.可以配用户正常聊天
                    3.提供情绪价值
                    4. 严格遵守医疗合规要求，避免提供诊断或治疗建议
                    5. 对于症状描述类问题，需提示用户"建议及时就医"的免责声明
                    6. 涉及用药/治疗方案的问题，必须强调"请遵医嘱"
                    7. 保持回复简洁易懂，避免专业术语
                    '''
    }
    # 构建用户历史消息（聊天记录）
    messages = [system_message]
    for history_item in history:
        messages.append({'role': history_item['type'], 'content': history_item['content']})

    # # 添加用户当前输入
    # messages.append({'role': 'user', 'content': user_input})

    return messages

import  json
def get_messages_ai( history):
    # 构建系统消息（包含角色定义和规则） 下面是一段顾客（customer）和用户(user)的聊天记录，顾客提问，用户回答，聊天记录中，
    system_message = {
        'role': 'system',
        'content': '''你的角色是顾客（customer），根据下面聊天记录模拟顾客（customer）与用户（user）中文提问聊天 ，自然对话式的问答聊天'''
    }
    data1 = json.loads(history)
    # 构建用户历史消息（聊天记录）
    messages = [system_message]
    for history_item in data1:
        messages.append({'role': 'assistant' if history_item['from']=='customer' else 'user', 'content': history_item['text']})


    return messages

def get_messages_analyze( history):
    # 构建系统消息（包含角色定义和规则） 下面是一段顾客（customer）和用户(user)的聊天记录，顾客提问，用户回答，聊天记录中，
    system_message = {
        'role': 'system',
        'content': '''你的角色是大健康行业的销售专家，根据下面聊天记录顾客（customer）与用户（user）根据最后一句 用户（user）的话进行分析，生成改进建议,不需要给出分析，直接给出改进建议和示例'''
    }
    data1 = json.loads(history)
    # 构建用户历史消息（聊天记录）
    messages = [system_message]
    for history_item in data1:
        messages.append({'role': 'assistant' if history_item['from']=='customer' else 'user', 'content': history_item['text']})


    return messages
def get_response_qwen(user_input):

    retry = 1
    model_name = 'deepseek-reasoner'
    while retry <= 1:
        try:

            client = OpenAI(
                # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
                api_key='sk-08a1b5a3baf746128b2af77836c2ffd9',
                # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            completion = client.chat.completions.create(
                model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=user_input
            )
            content_return = completion.choices[0].message.content
            return content_return

        except Exception as e:
            logger.error(traceback.format_exc())
            retry = retry+1

def get_response(user_input):

    retry = 1
    model_name = 'deepseek-reasoner'
    while retry <= 1:
        try:

            client = OpenAI(
                # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
                api_key='sk-08a1b5a3baf746128b2af77836c2ffd9',
                # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            completion = client.chat.completions.create(
                model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=user_input
                # messages=[
                #     {'role': 'system', 'content': 'You are a helpful assistant.'},
                #     {'role': 'user', 'content': f'{user_input}'}
                # ]
            )

            content_return = completion.choices[0].message.content
            # client = OpenAI(api_key=DP_KEY, base_url="https://api.deepseek.com")
            # response = client.chat.completions.create(
            #     model="deepseek-chat",
            #     messages=[
            #         {"role": "system", "content": "你是一名文本解析助手"},
            #         {"role": "user", "content": f"{user_input}"},
            #     ],
            #     stream=False
            # )
            # content_return = response.choices[0].message.content

            return content_return

        except Exception as e:
            logger.error(traceback.format_exc())
            retry = retry+1

if __name__ == "__main__":
    # 执行评测
    start_time = datetime.now()

    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key='sk-08a1b5a3baf746128b2af77836c2ffd9', # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-plus", # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': '你是谁？'}
            ]
    )
    print(completion.choices[0].message.content)
    end_time = datetime.now()
    print(f"qwen评测耗时： {end_time - start_time}")

    start_time = datetime.now()
    client = OpenAI(api_key=DP_KEY, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一名文本解析助手"},
            {"role": "user", "content": f"{'你是谁？'}"},
        ],
        stream=False
    )
    content_return = response.choices[0].message.content
    print(content_return)
    end_time = datetime.now()
    print(f"ds评测耗时： {end_time - start_time}")