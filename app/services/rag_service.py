from app.services.vector_db_service import VectorDBService
from app.services.llm_service import LLMService
from app.schemas.chat import ChatResponse, SourceCitation
from app.core.logger import setup_logger
from langchain_core.prompts import PromptTemplate
import traceback

logger = setup_logger(__name__)

class RAGService:
    def __init__(self):
        try:
            logger.info("Initializing RAG Orchestration Service...")
            self.vector_db = VectorDBService()
            self.retriever = self.vector_db.get_vector_store().as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4} # Retrieve top 4 most relevant chunks
            )
            self.llm = LLMService.get_llm()

            # The Core Hallucination-Prevention Prompt
            self.prompt_template = PromptTemplate(
                template="""You are a strict educational AI assistant. 
Your goal is to answer the student's question using ONLY the provided educational context below.

CRITICAL RULES FOR HALLUCINATION PREVENTION:
1. You must base your answer strictly and exclusively on the provided context.
2. If the context does not contain the answer, you MUST reply EXACTLY with: "The answer is not present in the uploaded documents." Do not try to guess or use your own knowledge.
3. Keep your answer clear, concise, and educational.
4. Do not include your internal thoughts or reasoning in the final answer.

EDUCATIONAL CONTEXT:
{context}

STUDENT QUESTION:
{question}

ANSWER:""",
                input_variables=["context", "question"]
            )
            logger.info("RAG Orchestration Service initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize RAGService")
            logger.error(traceback.format_exc())
            raise e

    def process_query(self, query: str) -> ChatResponse:
        logger.info(f"Processing student query: '{query}'")
        
        try:
            # 1. Retrieval Phase
            logger.debug("Step 1: Retrieving semantic chunks from ChromaDB...")
            docs = self.retriever.invoke(query)
            
            if not docs:
                logger.warning("No relevant context found in Vector Database. Executing strict refusal.")
                return ChatResponse(
                    answer="The answer is not present in the uploaded documents.",
                    sources=[]
                )

            # Build the context string and prepare citations
            context_text = ""
            sources = []
            
            for idx, doc in enumerate(docs):
                # Clean up snippet for JSON response
                snippet = doc.page_content.replace('\n', ' ')[:150] + "..."
                # Langchain PyMuPDFLoader stores 'source' and 'page' in metadata automatically
                source = doc.metadata.get('source', 'Unknown Document').split('/')[-1] # Get just the filename
                page = doc.metadata.get('page', None)
                
                # Format exactly how it will be injected into the prompt
                context_text += f"\n--- Source {idx+1} ({source}, Page {page}) ---\n{doc.page_content}\n"
                
                sources.append(SourceCitation(
                    source=source,
                    page=page,
                    snippet=snippet
                ))
                
            logger.debug(f"Retrieved {len(docs)} chunks for generation.")

            # 2. Generation Phase
            logger.debug("Step 2: Constructing strict prompt and invoking Ollama LLM...")
            final_prompt = self.prompt_template.format(context=context_text, question=query)
            
            # This is a blocking call to the local LLM
            response_text = self.llm.invoke(final_prompt).strip()
            logger.info("LLM generation complete.")

            # 3. Post-Generation Validation (Safety Net)
            refusal_phrases = [
                "not present in the uploaded documents",
                "not present in the provided context",
                "does not contain information"
            ]
            
            # If the LLM triggered a refusal, we clear the sources because no citations were actually used
            is_refusal = any(phrase in response_text.lower() for phrase in refusal_phrases)
            if is_refusal:
                logger.info("LLM correctly triggered refusal mechanism. Clearing citations.")
                sources = [] 
                response_text = "The answer is not present in the uploaded documents."

            return ChatResponse(answer=response_text, sources=sources)
            
        except Exception as e:
            logger.error("Error during RAG Generation pipeline")
            logger.error(traceback.format_exc())
            raise e
