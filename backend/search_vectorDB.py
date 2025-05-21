import os
import sys
# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 只需要上一级目录，因为已经在src目录下了
sys.path.append(project_root)

from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from utils.get_embedding_model import hf


def vector_search(query, filter_query=None, db_path="./db/fund_production_chunk", k=1):
    # 使用绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, db_path)
    print('vector_search1')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Vector database not found at {db_path}")
        
    fund_names_db = FAISS.load_local(db_path,
                                     hf,
                                     allow_dangerous_deserialization=True)
    print('vector_search2')
    if filter_query:
        result = fund_names_db.similarity_search(query, filter=filter_query, k=k)
    else:
        result = fund_names_db.similarity_search(query, k=k)
    print('vector_search3')
    return result


if __name__ == "__main__":
    print(vector_search(query="29、珍奥维生素D维生素K片", filter_query={"name": "production"}))

    # print(vector_search(query="浦银", db_path="FUND_NAME_VECTOR", k=1))