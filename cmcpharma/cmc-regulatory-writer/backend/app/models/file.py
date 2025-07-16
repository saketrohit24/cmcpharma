from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class FileItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    size: int
    mime_type: str
    path: str # Relative path in storage for the session
