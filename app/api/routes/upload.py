import traceback
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.services.document_service import DocumentService
from app.services.vector_db_service import VectorDBService
from app.core.logger import setup_logger
from app.api.dependencies import get_current_active_admin_or_teacher

logger = setup_logger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])
vector_db_service = VectorDBService() 

@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_admin_or_teacher)
):
    if not file.filename.endswith((".pdf", ".txt")):
        logger.warning(f"Rejected file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and TXT are allowed currently.")
    
    try:
        logger.info(f"==== STARTING DOCUMENT PROCESSING PIPELINE ====")
        logger.info(f"File Received: {file.filename}")
        
        # 1. Save file locally
        saved_path = await DocumentService.save_uploaded_file(file)
        logger.info(f"[1/3] File saved successfully.")
        
        # 2. Extract Text and Chunk it
        logger.info("[2/3] Initiating document parsing and chunking...")
        chunks = DocumentService.process_and_chunk_document(saved_path)
        logger.info(f"[2/3] Document parsed into {len(chunks)} chunks.")
        
        # 3. Generate Embeddings and Store in Vector DB
        logger.info("[3/3] Initiating embedding generation and ChromaDB insertion...")
        vector_db_service.store_chunks(chunks)
        logger.info("[3/3] Embeddings generated and stored in Vector Database.")
        
        logger.info(f"==== UPLOAD PIPELINE COMPLETE ====")
        return {
            "filename": file.filename, 
            "message": f"Successfully processed and embedded {len(chunks)} chunks.", 
            "path": saved_path
        }
    except Exception as e:
        logger.error("==== FATAL ERROR IN UPLOAD PIPELINE ====")
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error(f"Error Message: {str(e)}")
        logger.error("Full Traceback:")
        logger.error("\n" + traceback.format_exc())
        logger.error("========================================")
        raise HTTPException(
            status_code=500, 
            detail="Internal Server Error during document processing. Please check the server console for exact error traceback."
        )
