import os
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

try:
    # 使用绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_name = os.path.join(current_dir, "models", "bge-small-zh-v1.5")
    
    if not os.path.exists(model_name):
        raise FileNotFoundError(f"Model directory not found at {model_name}")
        
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}
    
    hf = HuggingFaceBgeEmbeddings(
        model_name=model_name, 
        model_kwargs=model_kwargs, 
        encode_kwargs=encode_kwargs
    )
except ImportError as e:
    print("Error: Required dependencies not installed. Please install them using:")
    print("pip install langchain-community sentence-transformers")
    raise e
except Exception as e:
    print(f"Error initializing embedding model: {str(e)}")
    raise e