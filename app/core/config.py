from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Edu-RAG-Backend"
    API_V1_STR: str = "/api/v1"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "edu_rag"
    UPLOAD_DIR: str = "data/uploads"
    CHROMA_DB_DIR: str = "data/chromadb"

    # RAG Pipeline Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Hybrid Retrieval Configuration
    RETRIEVAL_K_VECTOR: int = 10
    RETRIEVAL_K_BM25: int = 10
    RETRIEVAL_FETCH_K: int = 20
    HYBRID_BM25_WEIGHT: float = 0.4
    HYBRID_VECTOR_WEIGHT: float = 0.6

    # Reranker Configuration
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RERANK_TOP_K: int = 4

    # Ollama LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "mistral"

    # Security Settings
    SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week

    class Config:
        env_file = ".env"

settings = Settings()
