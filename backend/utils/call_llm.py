from langchain_openai import ChatOpenAI
import os
import time

#导入环境变量
from dotenv import load_dotenv
load_dotenv()


def get_response(user_input,model_name="gpt-4o-mini"):
    retry = 0
    while retry <= 3:
        try:
            llm = ChatOpenAI(
                openai_api_key=os.getenv("OPENAI_KEY"),
                base_url=os.getenv("BASE_URL"),
                temperature=0,
                model_name=model_name)
            return llm.invoke(user_input).content
        except Exception as e:
            print(f"""Function parse Error:{e}""")
            time.sleep(2)


if __name__ == "__main__":
    text = "what happen"
    print(get_response([
                         {"role":"user","content":f"nihao"}]))