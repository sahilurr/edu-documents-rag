import traceback
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService
from app.core.logger import setup_logger
from app.api.dependencies import get_current_user

logger = setup_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# Try to initialize the global RAG service
try:
    rag_service = RAGService()
except Exception as e:
    logger.error("Failed to globally initialize RAG Service.")
    rag_service = None

@router.post("/", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG Service is not available due to startup errors.")
        
    try:
        logger.info("==== STARTING CHAT REQUEST ====")
        response = rag_service.process_query(request.query)
        logger.info("==== CHAT REQUEST COMPLETE ====")
        return response
    except Exception as e:
        logger.error("==== FATAL ERROR IN CHAT ROUTE ====")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error during chat generation.")
