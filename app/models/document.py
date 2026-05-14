from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(str):
    """
    Custom Pydantic V2 type to handle MongoDB ObjectIds gracefully.
    It serializes ObjectId to string for JSON responses, and parses strings back to ObjectId.
    """
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.str_schema(),
        ])

class DocumentMetadata(BaseModel):
    """
    MongoDB Model for storing document metadata.
    This links the file to the user and stores its processing status.
    IMPORTANT ARCHITECTURE RULE: Embeddings themselves are NOT stored here. They belong in ChromaDB.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    filename: str
    file_path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    total_chunks: int = 0
    uploader_id: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )
