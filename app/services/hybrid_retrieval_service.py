from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from app.services.vector_db_service import VectorDBService
from app.core.config import settings
from app.core.logger import setup_logger
import traceback


logger = setup_logger(__name__)


class HybridRetrievalService:
    """Singleton hybrid retriever combining BM25 (keyword) and vector similarity (MMR).

    BM25 is rebuilt in-memory from the Chroma collection at startup and after each
    document upload, so we never duplicate persisted state.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        try:
            logger.info("Initializing HybridRetrievalService...")
            self.vector_db = VectorDBService()
            self.vector_retriever = self.vector_db.get_vector_store().as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": settings.RETRIEVAL_K_VECTOR,
                    "fetch_k": settings.RETRIEVAL_FETCH_K,
                },
            )
            self.bm25_retriever = None
            self.ensemble = None
            self._rebuild_bm25()
            self._initialized = True
            logger.info("HybridRetrievalService initialized.")
        except Exception as e:
            logger.error("Failed to initialize HybridRetrievalService.")
            logger.error(traceback.format_exc())
            raise e

    def _rebuild_bm25(self):
        try:
            store = self.vector_db.get_vector_store()
            data = store.get()
            ids = data.get("ids", []) or []
            if not ids:
                logger.warning("Vector store is empty; BM25 retriever not built.")
                self.bm25_retriever = None
                self.ensemble = None
                return

            texts = data.get("documents", []) or []
            metas = data.get("metadatas", []) or [{}] * len(texts)
            docs = [
                Document(page_content=t, metadata=m or {})
                for t, m in zip(texts, metas)
            ]
            self.bm25_retriever = BM25Retriever.from_documents(docs)
            self.bm25_retriever.k = settings.RETRIEVAL_K_BM25
            self.ensemble = EnsembleRetriever(
                retrievers=[self.bm25_retriever, self.vector_retriever],
                weights=[settings.HYBRID_BM25_WEIGHT, settings.HYBRID_VECTOR_WEIGHT],
            )
            logger.info(f"BM25 retriever rebuilt with {len(docs)} chunks.")
        except Exception as e:
            logger.error("Failed to (re)build BM25 retriever.")
            logger.error(traceback.format_exc())
            self.bm25_retriever = None
            self.ensemble = None

    def rebuild(self):
        """Call after new documents are added to the vector store."""
        self._rebuild_bm25()

    def retrieve(self, query: str):
        if self.ensemble is not None:
            return self.ensemble.invoke(query)
        return self.vector_retriever.invoke(query)
