from pydantic import BaseModel, Field
from typing import List, Optional

class SourceCitation(BaseModel):
    source: str = Field(..., description="The name of the source document.")
    page: Optional[int] = Field(None, description="The page number where the text was found.")
    snippet: str = Field(..., description="A short preview of the exact text chunk used.")

class ChatRequest(BaseModel):
    query: str = Field(..., description="The student's question to be answered.")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="The generated answer from the AI.")
    sources: List[SourceCitation] = Field(..., description="The citations used to generate the answer.")
