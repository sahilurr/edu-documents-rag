import os
import shutil
import traceback
from fastapi import UploadFile
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class DocumentService:
    @staticmethod
    async def save_uploaded_file(file: UploadFile) -> str:
        try:
            logger.debug(f"Attempting to save file to disk: {file.filename}")
            file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.debug(f"File saved successfully at {file_path}")
            return file_path
        except Exception as e:
            logger.error("Failed to save uploaded file to disk.")
            logger.error(traceback.format_exc())
            raise e

    @staticmethod
    def process_and_chunk_document(file_path: str):
        try:
            logger.debug(f"Determining file type for parsing: {file_path}")
            ext = os.path.splitext(file_path)[1].lower()
            
            # Note: Using PyMuPDFLoader instead of PyPDFLoader to match requirements.txt
            if ext == ".pdf":
                logger.debug("Using PyMuPDFLoader for PDF extraction.")
                loader = PyMuPDFLoader(file_path)
            elif ext == ".txt":
                logger.debug("Using TextLoader for TXT extraction.")
                loader = TextLoader(file_path)
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
                
            logger.debug("Loading and parsing document text...")
            documents = loader.load()
            logger.debug(f"Successfully loaded {len(documents)} pages/documents.")
            
            logger.debug(f"Splitting text into chunks (Size: {settings.CHUNK_SIZE}, Overlap: {settings.CHUNK_OVERLAP})...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
            )
            chunks = text_splitter.split_documents(documents)
            logger.debug(f"Successfully created {len(chunks)} chunks.")
            return chunks
        except Exception as e:
            logger.error(f"Error during document processing and chunking for {file_path}")
            logger.error(traceback.format_exc())
            raise e
