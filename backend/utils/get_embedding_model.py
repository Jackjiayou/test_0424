import os
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from threading import Lock

class EmbeddingModel:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingModel, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            # 使用绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_name = os.path.join(current_dir, "models", "bge-small-zh-v1.5")
            
            if not os.path.exists(model_name):
                raise FileNotFoundError(f"Model directory not found at {model_name}")
                
            model_kwargs = {"device": "cpu"}
            encode_kwargs = {"normalize_embeddings": True}
            
            self.model = HuggingFaceBgeEmbeddings(
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
    
    def get_embedding(self, text):
        """获取单个文本的embedding"""
        return self.model.embed_query(text)
    
    def get_embeddings(self, texts):
        """批量获取多个文本的embeddings"""
        return self.model.embed_documents(texts)

# 创建单例实例
embedding_model = EmbeddingModel()

# 导出模型实例，保持与原有代码兼容
hf = embedding_model.model