from pydantic import BaseModel
from typing import Literal
from .document import GeneratedDocument

class ExportRequest(BaseModel):
    format: Literal['pdf', 'docx'] = 'pdf'
    document: GeneratedDocument
