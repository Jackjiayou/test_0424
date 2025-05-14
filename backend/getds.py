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
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': f'{user_input}'}
                ]
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