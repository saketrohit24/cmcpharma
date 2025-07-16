from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid

class GeneratedSection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    source_count: int

class GeneratedDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    sections: List[GeneratedSection]
    template_id: str
    session_id: str
    generated_at: datetime = Field(default_factory=datetime.now)

class RefinementRequest(BaseModel):
    section_title: str
    current_content: str
    refinement_request: str
