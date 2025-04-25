# coding=utf-8

from openai import OpenAI
DP_URL = 'https://api.deepseek.com/v1'
DP_KEY ='sk-083524dfc0b747d69bfcf3fd5b19c9ca'
def get_response(user_input):

    retry = 1
    model_name = 'deepseek-reasoner'
    while retry <= 1:
        try:
            client = OpenAI(api_key=DP_KEY, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一名文本解析助手"},
                    {"role": "user", "content": f"{user_input}"},
                ],
                stream=False
            )
            content_return = response.choices[0].message.content

            return content_return

        except Exception as e:
            retry = retry+1



