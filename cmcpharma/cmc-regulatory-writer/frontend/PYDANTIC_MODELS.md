# TypeScript Interfaces for FastAPI Pydantic Models

## 🔄 **Exact Interface Mapping for FastAPI**

### **Copy these interfaces to create your Pydantic models:**

```python
# models/base.py
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum

# models/template.py
class TOCItem(BaseModel):
    id: str
    title: str
    level: int
    page_number: Optional[int] = None
    children: Optional[List['TOCItem']] = None

class TemplateStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready" 
    GENERATING = "generating"

class TemplateType(str, Enum):
    UPLOADED = "uploaded"
    MANUAL = "manual"

class Template(BaseModel):
    id: str
    name: str
    description: str
    type: TemplateType
    created_at: datetime
    last_modified: datetime
    toc: List[TOCItem]
    content: Optional[str] = None
    status: TemplateStatus

# models/document.py
class SectionType(str, Enum):
    TEXT = "text"
    TABLE = "table"

class GeneratedSection(BaseModel):
    id: str
    title: str
    content: str
    type: SectionType

class GeneratedCitation(BaseModel):
    id: int
    text: str
    source: str
    page: int
    source_file_id: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_date: Optional[datetime] = None

class GeneratedDocument(BaseModel):
    id: str
    title: str
    sections: List[GeneratedSection]
    citations: List[GeneratedCitation]
    template_id: str
    generated_at: datetime

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class StoredDocument(BaseModel):
    id: str
    title: str
    content: str
    template_id: Optional[str] = None
    created_at: datetime
    last_modified: datetime
    version: int
    status: DocumentStatus
    tags: List[str] = []

# models/files.py
class FileType(str, Enum):
    FILE = "file"
    FOLDER = "folder"

class FileItem(BaseModel):
    id: str
    name: str
    type: FileType
    size: Optional[int] = None
    last_modified: datetime
    path: str
    parent: Optional[str] = None
    mime_type: Optional[str] = None
    children: Optional[List['FileItem']] = None

class UploadStatus(str, Enum):
    UPLOADING = "uploading"
    COMPLETED = "completed"
    ERROR = "error"

class UploadProgress(BaseModel):
    file_id: str
    file_name: str
    progress: int  # 0-100
    status: UploadStatus

# models/export.py
class ExportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    TXT = "txt"

class PageSize(str, Enum):
    A4 = "a4"
    LETTER = "letter"

class ExportOptions(BaseModel):
    format: ExportFormat
    include_metadata: bool = True
    include_citations: bool = True
    page_size: Optional[PageSize] = PageSize.A4
    margins: Optional[Dict[str, float]] = None

# models/chat.py
class MessageSender(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    id: str
    text: str
    sender: MessageSender
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    id: str
    messages: List[ChatMessage]
    created_at: datetime
    last_activity: datetime

# models/llm.py
class LLMProvider(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    LOCAL = "local"

class LLMConfig(BaseModel):
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    base_url: Optional[str] = None  # For local models

class GenerationOptions(BaseModel):
    include_citations: bool = True
    regulatory_focus: Literal["ICH", "FDA", "EMA"] = "ICH"
    content_length: Literal["standard", "detailed", "concise"] = "standard"
    custom_instructions: Optional[str] = None
```

## 🚀 **FastAPI Route Examples**

```python
# endpoints/templates.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from models.template import Template, TOCItem

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("/", response_model=List[Template])
async def get_templates():
    """Get all templates - matches frontend getTemplates()"""
    # Your implementation
    pass

@router.post("/", response_model=Template)
async def create_template(template: Template):
    """Create template - matches frontend createTemplate()"""
    # Your implementation  
    pass

@router.post("/upload", response_model=Template)
async def upload_template(file: UploadFile = File(...)):
    """Upload template file - matches frontend file upload"""
    # Parse file and extract TOC
    pass

# endpoints/generation.py
from models.document import GeneratedDocument
from models.llm import LLMConfig, GenerationOptions

@router.post("/generate-document", response_model=GeneratedDocument)
async def generate_document(
    template_id: str,
    llm_config: Optional[LLMConfig] = None,
    options: Optional[GenerationOptions] = None
):
    """Main LLM generation - matches frontend generateFromTemplate()"""
    # Your LLM integration here
    pass

# endpoints/documents.py
from models.document import StoredDocument

@router.get("/", response_model=List[StoredDocument])
async def get_documents(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """Get documents - matches frontend document history"""
    pass

@router.post("/", response_model=StoredDocument)
async def save_document(document: StoredDocument):
    """Save document - matches frontend save functionality"""
    pass

# endpoints/export.py
from fastapi.responses import FileResponse
from models.export import ExportOptions

@router.post("/")
async def export_document(
    document_id: str,
    options: ExportOptions
) -> FileResponse:
    """Export document - matches frontend export manager"""
    # Generate file and return
    pass

# endpoints/files.py
from models.files import FileItem, UploadProgress

@router.get("/", response_model=List[FileItem])
async def get_files(path: Optional[str] = None):
    """Get files - matches frontend file manager"""
    pass

@router.post("/upload", response_model=FileItem)
async def upload_file(file: UploadFile = File(...)):
    """Upload file - matches frontend file upload"""
    pass

# endpoints/chat.py
from models.chat import ChatSession, ChatMessage

@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(
    document_id: Optional[str] = None,
    initial_message: Optional[str] = None
):
    """Create chat session - matches frontend chat interface"""
    pass

@router.post("/sessions/{session_id}/messages", response_model=ChatMessage)
async def send_message(
    session_id: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
):
    """Send chat message - matches frontend chat functionality"""
    # Your AI chat logic here
    pass
```

## 🔧 **Database Models (SQLAlchemy)**

```python
# database/models.py
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TemplateModel(Base):
    __tablename__ = "templates"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # 'uploaded' or 'manual'
    created_at = Column(DateTime, nullable=False)
    last_modified = Column(DateTime, nullable=False)
    toc = Column(JSON, nullable=False)  # Store TOC as JSON
    content = Column(Text)
    status = Column(String, default="draft")

class DocumentModel(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    template_id = Column(String, ForeignKey("templates.id"))
    created_at = Column(DateTime, nullable=False)
    last_modified = Column(DateTime, nullable=False)
    version = Column(Integer, default=1)
    status = Column(String, default="draft")
    tags = Column(JSON, default=[])
    
    template = relationship("TemplateModel")

class FileModel(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'file' or 'folder'
    size = Column(Integer)
    last_modified = Column(DateTime, nullable=False)
    path = Column(String, nullable=False)
    parent = Column(String, ForeignKey("files.id"))
    mime_type = Column(String)

class CitationModel(Base):
    __tablename__ = "citations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    page = Column(Integer, nullable=False)
    source_file_id = Column(String, ForeignKey("files.id"))
    url = Column(String)
    doi = Column(String)
    authors = Column(JSON)
    publication_date = Column(DateTime)

class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, nullable=False)
    
class ChatMessageModel(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    text = Column(Text, nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'assistant'
    timestamp = Column(DateTime, nullable=False)
    context = Column(JSON)
    
    session = relationship("ChatSessionModel")
```

## 🎯 **Integration Steps**

1. **Copy these Pydantic models** to your FastAPI project
2. **Create SQLAlchemy models** for database persistence
3. **Implement the API endpoints** using these exact interfaces
4. **Update frontend API calls** to point to your FastAPI URL
5. **Test integration** one component at a time

Your FastAPI backend will match the frontend perfectly with these models! 🚀
