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

def get_messages_rag( history):
    retry = 1
    model_name = 'deepseek-reasoner'
    while retry <= 1:
        try:
            messages = [
                {'role': 'system',
                 'content': '你是一个语义分析专家，专门从用户的多轮对话中提取出与当前问题相关的关键词，以便用于搜索产品资料。关键词应尽可能具体准确。'},
                {'role': 'user',
                 'content': f'以下是用户和助手的对话历史：\n\n{history}\n\n请你根据用户当前的问题，判断最相关的关键词（如产品名、功效成分、相关话题），用于搜索数据库。\n\n返回格式为：\n <关键词内容,关键词内容>"'}
            ]
            client = OpenAI(
                # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
                api_key='sk-08a1b5a3baf746128b2af77836c2ffd9',
                # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            completion = client.chat.completions.create(
                model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=messages
            )
            content_return = completion.choices[0].message.content
            return content_return

        except Exception as e:
            logger.error(traceback.format_exc())
            retry = retry + 1



def get_messages( history,rag_msg):
    # 构建系统消息（包含角色定义和规则）
    sys_countent = '''你是一个专业的大健康行业健康助手，具备以下能力：
                    1. 提供基础健康知识咨询（如饮食、运动、睡眠建议）
                    2.可以配用户正常聊天
                    3. 保持回复简洁易懂，避免专业术语,内容不要太长
                    '''
    if rag_msg:
        sys_countent=sys_countent+f' 并且基于以下检索的文本回答用户的问题，简介回答：{rag_msg}'

    system_message = {
        'role': 'system',
        'content': sys_countent
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
        'content': '''你的角色是顾客（customer），根据下面聊天记录模拟顾客（customer）与珍奥双迪公司的销售员（user）中文提问聊天 ，自然对话式的问答聊天'''
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
        'content': '''你的角色是大健康行业中珍奥双迪的销售专家，根据下面聊天记录中顾客（customer）与珍奥双迪的销售员（user）的对话，根据最后一句销售员（user）的回答进行分析，生成改进建议,不需要给出分析，直接给出改进建议和示例'''
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


def get_response_normal(user_input):
    # messages=[
    #     {'role': 'system', 'content': 'You are a helpful assistant.'},
    #     {'role': 'user', 'content': f'{user_input}'}
    # ]
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
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': f'{user_input}'}
            ]
            completion = client.chat.completions.create(
                model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=messages
            )
            content_return = completion.choices[0].message.content
            return content_return

        except Exception as e:
            logger.error(traceback.format_exc())
            retry = retry + 1

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