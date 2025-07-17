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

    def get_session_files(self) -> List[FileItem]:
        """Returns a list of FileItem objects for all files in the session."""
        files = []
        if not os.path.isdir(self.session_dir):
            return files
        
        for filename in os.listdir(self.session_dir):
            file_path = os.path.join(self.session_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                files.append(FileItem(
                    name=filename,
                    size=file_size,
                    mime_type=self._get_mime_type(filename),
                    path=os.path.join(self.session_id, filename)
                ))
        return files

    def _get_mime_type(self, filename: str) -> str:
        """Simple mime type detection based on file extension."""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        mime_types = {
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        return mime_types.get(ext, 'application/octet-stream')
