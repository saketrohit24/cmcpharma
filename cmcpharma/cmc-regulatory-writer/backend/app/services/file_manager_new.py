import os
import uuid
from fastapi import UploadFile
from typing import List
from ..models.file import FileItem

UPLOAD_DIR = "persistent_uploads"

class FileManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session_dir = os.path.join(UPLOAD_DIR, self.session_id)
        os.makedirs(self.session_dir, exist_ok=True)

    async def save_file(self, file: UploadFile) -> FileItem:
        """Saves an uploaded file to the session directory."""
        file_path = os.path.join(self.session_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return FileItem(
            name=file.filename,
            size=file.size,
            mime_type=file.content_type,
            path=os.path.join(self.session_id, file.filename)
        )

    def get_session_file_paths(self) -> List[str]:
        """Returns a list of full file paths for a given session."""
        if not os.path.isdir(self.session_dir):
            return []
        return [os.path.join(self.session_dir, f) for f in os.listdir(self.session_dir)]
