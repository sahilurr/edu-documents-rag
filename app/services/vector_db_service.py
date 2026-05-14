from langchain_community.vectorstores import Chroma
from app.services.embedding_service import EmbeddingService
from app.core.config import settings
from app.core.logger import setup_logger
import os
import traceback

logger = setup_logger(__name__)

class VectorDBService:
    def __init__(self):
        try:
            logger.info("Initializing VectorDBService...")
            self.embeddings = EmbeddingService.get_embeddings()
            self.persist_directory = settings.CHROMA_DB_DIR
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            logger.info(f"Connecting to ChromaDB at {self.persist_directory}")
            self.vector_store = Chroma(
                collection_name="edu_documents",
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            logger.info("Successfully connected to ChromaDB.")
        except Exception as e:
            logger.error("Failed to initialize VectorDBService.")
            logger.error(traceback.format_exc())
            raise e

    def store_chunks(self, chunks):
        if not chunks:
            logger.warning("No chunks provided for vector storage.")
            return
            
        try:
            logger.debug(f"Adding {len(chunks)} chunks to ChromaDB...")
            self.vector_store.add_documents(documents=chunks)
            logger.debug("Chunks successfully embedded and added to ChromaDB.")
        except Exception as e:
            logger.error("Failed to store chunks in ChromaDB.")
            logger.error(traceback.format_exc())
            raise e
            
    def get_vector_store(self):
        return self.vector_store
