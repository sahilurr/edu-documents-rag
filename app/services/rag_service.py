from app.services.hybrid_retrieval_service import HybridRetrievalService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService
from app.schemas.chat import ChatResponse, SourceCitation
from app.core.config import settings
from app.core.logger import setup_logger
from langchain_core.prompts import PromptTemplate
import traceback

logger = setup_logger(__name__)


PROMPT_TEMPLATE = PromptTemplate(
    template="""You are a strict educational AI assistant.
Your goal is to answer the student's question using ONLY the provided educational context below.

CRITICAL RULES FOR HALLUCINATION PREVENTION:
1. Base your answer strictly and exclusively on the provided context.
2. If the context does not contain the answer, you MUST reply EXACTLY with: "The answer is not present in the uploaded documents." Do not guess or use outside knowledge.
3. After each factual statement, cite the source using [Source N] notation matching the numbered sources below.
4. Keep your answer clear, concise, and educational.
5. Do not include your internal thoughts or reasoning in the final answer.

EDUCATIONAL CONTEXT:
{context}

STUDENT QUESTION:
{question}

ANSWER:""",
    input_variables=["context", "question"],
)


REFUSAL_TEXT = "The answer is not present in the uploaded documents."
REFUSAL_PHRASES = (
    "not present in the uploaded documents",
    "not present in the provided context",
    "does not contain information",
    "context does not contain",
)


class RAGService:
    def __init__(self):
        try:
            logger.info("Initializing RAG Orchestration Service...")
            self.hybrid = HybridRetrievalService()
            self.llm = LLMService.get_llm()
            # Trigger reranker load at startup so the first query isn't slow.
            RerankerService.get_model()
            self.prompt_template = PROMPT_TEMPLATE
            logger.info("RAG Orchestration Service initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize RAGService")
            logger.error(traceback.format_exc())
            raise e

    def _retrieve(self, query: str):
        candidates = self.hybrid.retrieve(query)
        if not candidates:
            return []
        return RerankerService.rerank(query, candidates, top_k=settings.RERANK_TOP_K)

    def _build_context(self, docs):
        context_text = ""
        sources = []
        for idx, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", "Unknown Document").split("/")[-1]
            page = doc.metadata.get("page", None)
            score = doc.metadata.get("rerank_score")
            snippet = doc.page_content.replace("\n", " ")[:150] + "..."

            context_text += (
                f"\n--- Source {idx} ({source}, Page {page}) ---\n"
                f"{doc.page_content}\n"
            )
            sources.append(
                SourceCitation(
                    source=source,
                    page=page,
                    snippet=snippet,
                    score=score,
                )
            )
        return context_text, sources

    def _is_refusal(self, response_text: str) -> bool:
        lowered = response_text.lower()
        return any(p in lowered for p in REFUSAL_PHRASES)

    def process_query(self, query: str) -> ChatResponse:
        logger.info(f"Processing student query: '{query}'")
        try:
            logger.debug("Step 1: Hybrid retrieval (BM25 + vector)...")
            docs = self._retrieve(query)
            if not docs:
                logger.warning("No relevant context found. Strict refusal.")
                return ChatResponse(answer=REFUSAL_TEXT, sources=[])

            context_text, sources = self._build_context(docs)
            logger.debug(f"Reranked to {len(docs)} chunks for generation.")

            logger.debug("Step 2: Invoking Ollama LLM...")
            final_prompt = self.prompt_template.format(
                context=context_text, question=query
            )
            response_text = self.llm.invoke(final_prompt).strip()
            logger.info("LLM generation complete.")

            if self._is_refusal(response_text):
                logger.info("LLM correctly triggered refusal; clearing citations.")
                return ChatResponse(answer=REFUSAL_TEXT, sources=[])

            return ChatResponse(answer=response_text, sources=sources)
        except Exception as e:
            logger.error("Error during RAG Generation pipeline")
            logger.error(traceback.format_exc())
            raise e

    async def astream_query(self, query: str):
        """Async generator yielding (event_type, payload) tuples for SSE.

        Events:
          - "sources": list[SourceCitation] (sent before any tokens)
          - "token":   str chunk of the answer
          - "done":    final answer string (post-validation)
        """
        logger.info(f"Streaming query: '{query}'")
        try:
            docs = self._retrieve(query)
            if not docs:
                yield "sources", []
                yield "token", REFUSAL_TEXT
                yield "done", REFUSAL_TEXT
                return

            context_text, sources = self._build_context(docs)
            yield "sources", [s.model_dump() for s in sources]

            final_prompt = self.prompt_template.format(
                context=context_text, question=query
            )

            buffer_parts = []
            async for chunk in self.llm.astream(final_prompt):
                if not chunk:
                    continue
                buffer_parts.append(chunk)
                yield "token", chunk

            full_answer = "".join(buffer_parts).strip()
            if self._is_refusal(full_answer):
                yield "done", REFUSAL_TEXT
            else:
                yield "done", full_answer
        except Exception as e:
            logger.error("Error during streaming RAG pipeline")
            logger.error(traceback.format_exc())
            yield "error", str(e)
