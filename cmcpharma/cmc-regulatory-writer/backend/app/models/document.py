from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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
    citations: Optional[List[Dict[str, Any]]] = []

class RefinementRequest(BaseModel):
    section_title: str
    current_content: str
    refinement_request: str

# Models for document CRUD operations
class DocumentCreate(BaseModel):
    title: str
    content: str
    document_type: str = "regulatory"
    description: Optional[str] = ""
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class DocumentSearch(BaseModel):
    query: str
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class StoredDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    document_type: str = "regulatory"
    description: str = ""
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    status: str = "draft"  # draft, review, approved, archived
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    version: int = 1
