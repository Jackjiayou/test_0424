from sentence_transformers import SentenceTransformer
import os

def download_model():
    # 创建模型保存目录
    model_dir = "./models/bge-small-zh-v1.5"
    os.makedirs(model_dir, exist_ok=True)
    
    # 下载模型
    print("正在下载模型...")
    model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    
    # 保存模型到本地
    print(f"正在保存模型到 {model_dir}...")
    model.save(model_dir)
    print("模型下载完成！")

if __name__ == "__main__":
    download_model() 