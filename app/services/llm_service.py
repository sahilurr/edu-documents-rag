from langchain_community.llms import Ollama
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger(__name__)

class LLMService:
    _instance = None
    
    @classmethod
    def get_llm(cls):
        """
        Singleton pattern to ensure the Ollama connection is reused efficiently.
        """
        if cls._instance is None:
            try:
                logger.info(f"Initializing connection to Ollama ({settings.OLLAMA_BASE_URL}) for model: {settings.LLM_MODEL}")
                cls._instance = Ollama(
                    base_url=settings.OLLAMA_BASE_URL,
                    model=settings.LLM_MODEL,
                    # VERY IMPORTANT FOR HALLUCINATION PREVENTION:
                    # Temperature 0.0 forces the model to be deterministic and strict.
                    # It will prefer facts in the prompt over its own creative internal weights.
                    temperature=0.0 
                )
                logger.info("Ollama LLM connection established.")
            except Exception as e:
                logger.error("CRITICAL ERROR: Failed to initialize Ollama LLM.")
                logger.error(traceback.format_exc())
                raise e
        return cls._instance
