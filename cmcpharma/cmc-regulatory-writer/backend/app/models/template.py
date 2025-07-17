from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class TOCItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    level: int
    children: Optional[List['TOCItem']] = []

# This allows the nested 'children' field to correctly reference the TOCItem model
TOCItem.update_forward_refs()

class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    toc: List[TOCItem]
    content: Optional[str] = None  # Store the actual content from uploaded files
    source_file: Optional[str] = None  # Store the original filename
    type: Optional[str] = "manual"  # 'manual' or 'uploaded'

class TemplateCreationRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    toc_text: str # Raw text from a textarea to be parsed
