from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger(__name__)

class EmbeddingService:
    _instance = None
    
    @classmethod
    def get_embeddings(cls):
        """
        Singleton pattern to ensure we only load the embedding model into memory once.
        """
        if cls._instance is None:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL} into memory. This may take a moment...")
                cls._instance = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL,
                    model_kwargs={'device': 'cpu'}, 
                    encode_kwargs={'normalize_embeddings': True} 
                )
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.error("CRITICAL ERROR: Failed to load the embedding model.")
                logger.error(traceback.format_exc())
                raise e
        return cls._instance
