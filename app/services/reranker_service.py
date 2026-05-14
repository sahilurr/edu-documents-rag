from sentence_transformers import CrossEncoder
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger(__name__)


class RerankerService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            try:
                logger.info(f"Loading cross-encoder reranker: {settings.RERANKER_MODEL}")
                cls._model = CrossEncoder(settings.RERANKER_MODEL)
                logger.info("Reranker model loaded successfully.")
            except Exception as e:
                logger.error("Failed to load cross-encoder reranker.")
                logger.error(traceback.format_exc())
                raise e
        return cls._model

    @classmethod
    def rerank(cls, query: str, docs, top_k: int):
        if not docs:
            return []
        try:
            model = cls.get_model()
            pairs = [(query, d.page_content) for d in docs]
            scores = model.predict(pairs)
            scored = sorted(zip(scores, docs), key=lambda x: float(x[0]), reverse=True)
            top = scored[:top_k]
            out = []
            for score, d in top:
                d.metadata = {**(d.metadata or {}), "rerank_score": float(score)}
                out.append(d)
            return out
        except Exception as e:
            logger.error("Reranking failed; falling back to original order.")
            logger.error(traceback.format_exc())
            return docs[:top_k]
