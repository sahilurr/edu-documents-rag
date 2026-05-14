import json
import traceback
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
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
    current_user: dict = Depends(get_current_user),
):
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG Service is not available due to startup errors.")

    try:
        logger.info("==== STARTING CHAT REQUEST ====")
        response = rag_service.process_query(request.query)
        logger.info("==== CHAT REQUEST COMPLETE ====")
        return response
    except Exception:
        logger.error("==== FATAL ERROR IN CHAT ROUTE ====")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error during chat generation.")


def _sse(event: str, data) -> str:
    """Format a Server-Sent Events frame."""
    payload = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/stream")
async def ask_question_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Server-Sent Events endpoint.

    Emits three event types:
      - `sources`: JSON array of citations (sent once, before tokens)
      - `token`:   JSON-encoded string chunk of the answer
      - `done`:    JSON-encoded final (post-validated) answer
      - `error`:   JSON-encoded error message
    """
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG Service is not available due to startup errors.")

    async def event_generator():
        try:
            async for event_type, payload in rag_service.astream_query(request.query):
                yield _sse(event_type, payload)
        except Exception as e:
            logger.error("Streaming pipeline error")
            logger.error(traceback.format_exc())
            yield _sse("error", str(e))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
