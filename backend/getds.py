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
                 'content': '你是一个语义分析专家，专门从用户的多轮对话中提取出与当前问题相关的关键词，生成的关键词是与我的资料库相关的，我目前提供的资料库如下三类【公司具体产品信息、产品名称列表信息、珍奥双迪健康产业集团发展历程】，以便用于搜索产品资料。关键词应尽可能具体准确。如果用户的问题与产品、健康等需要查资料的内容无关（如闲聊、问你是谁等），请返回关键词：无。'},
                {'role': 'user',
                 'content': f'以下是用户和助手的对话历史：\n\n{history}\n\n根据最新一轮用户的问题（最后用户user的话）基于我提供的资料库判断是否需要提取关键词用于查询资料，如果不需要则返回<无>，需要的话判断最相关的关键词（如产品名、功效成分、相关话题，产品种类），比如我提供了产品名称列表信息，用户问都有什么产品，那关键词是产品名称列表，问具体产品信息时关键词是产品名称，问公司信息时关键词是珍奥双迪健康产业集团发展，用于搜索数据库。\n\n仅返回格式如下：\n关键词：<关键词内容>\n\n如果没有相关关键词，请返回：\n关键词：无'}
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

def get_messages_aill( history):
    retry = 1
    model_name = 'deepseek-reasoner'
    while retry <= 1:
        try:
            messages = [
                {'role': 'system',
                 'content': '你是一个语义分析专家，专门从用户的多轮对话中提取出与当前问题相关的关键词，生成的关键词是与我的资料库相关的，我目前提供的资料库如下三类【核苷酸资料】，以便用于搜索产品资料。关键词应尽可能具体准确。如果用户的问题与产品、健康等需要查资料的内容无关（如闲聊、问你是谁等），请返回关键词：无。'},
                {'role': 'user',
                 'content': f'以下是用户和助手的对话历史：\n\n{history}\n\n根据最新一轮用户的问题（最后用户user的话）基于我提供的资料库判断是否需要提取关键词用于查询资料，如果不需要则返回<无>，需要的话判断最相关的关键词（如产品名、功效成分、相关话题，产品种类），比如我提供了产品名称列表信息，用户问都有什么产品，那关键词是产品名称列表，问具体产品信息时关键词是产品名称，问公司信息时关键词是珍奥双迪健康产业集团发展，用于搜索数据库。\n\n仅返回格式如下：\n关键词：<关键词内容>\n\n如果没有相关关键词，请返回：\n关键词：无'}
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
                    3. 保持回复简洁易懂，避免专业术语,内容不要太长,根据提供的检索的文本回答用户的问题，如果没有给检索文本，当用户问到的是公司信息或者公司产品信息则真实回答，不要说不确定的信息，其他性质的问题可以自由合理恰当简介的回答。
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
        'content': '''你是一位潜在顾客，正在与一位珍奥双迪公司的销售员对话。回答有如下要求：
        1.请以顾客的身份回复，一定要用顾客的什么回复，自然、对话式的回答，如果销售回复的离谱，可以不用客气。
        2.不要以AI的身份回复，不要承认自己是程序。请根据上下文保持对话连贯，语气自然贴近生活，用中文回复'''
    }
    data1 = json.loads(history)
    # 构建用户历史消息（聊天记录）
    messages = [system_message]
    for history_item in data1:
        messages.append({'role': 'assistant' if history_item['from']=='customer' else 'user', 'content': history_item['text']})


    return messages

def get_messages_analyze( history,rag_msg,sence):
    # 构建系统消息（包含角色定义和规则） 下面是一段顾客（customer）和用户(user)的聊天记录，顾客提问，用户回答，聊天记录中，
    content = f'''{sence}，根据下面聊天记录中顾客（assistant）与珍奥双迪的销售员（user）的对话，根据历史对话给出改进建议和示例。
                改进建议生成要求如下:
                1.根据销售员（user）最后一句的回答进行分析，生成改进建议.
                
                示例生成要求如下：
                1.根据顾客（assistant）最后一句话并且结合以下给的资料 “{rag_msg}” 给出示例,示例字数不用过多 简洁明了,
                2.生成的示例要根据给的资料的内容，但不能虚构案例和数据，尤其想一些指标、详细信息、配料表、案例等信息不可以虚构
                3.如果示例中设计公司产品的数据案例等信息一定要基于给的资料'''


    system_message = {
        'role': 'system',
        'content': content
    }
    data1 = json.loads(history)
    # 构建用户历史消息（聊天记录）
    messages = [system_message]
    for history_item in data1:
        messages.append({'role': 'assistant' if history_item['from']=='customer' else 'user', 'content': history_item['text']})


    return messages

def get_response_qwen(user_input):

    retry = 1
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
                messages=user_input,
                temperature=0.0
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

            # client = OpenAI(
            #     # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            #     api_key='sk-08a1b5a3baf746128b2af77836c2ffd9',
            #     # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
            #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            # )
            #
            # completion = client.chat.completions.create(
            #     model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            #     messages=user_input
            #     # messages=[
            #     #     {'role': 'system', 'content': 'You are a helpful assistant.'},
            #     #     {'role': 'user', 'content': f'{user_input}'}
            #     # ]
            # )
            #
            # content_return = completion.choices[0].message.content

            #-----------------------------
            client = OpenAI(api_key=DP_KEY, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一名文本解析助手"},
                    {"role": "user", "content": f"{user_input}"},
                ],
                stream=False,
                temperature=0.0
            )
            content_return = response.choices[0].message.content
            #---------------------------------------------------------------
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