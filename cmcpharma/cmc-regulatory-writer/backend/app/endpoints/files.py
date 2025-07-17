from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.file_manager import FileManager
from ..models.file import FileItem
from typing import List

router = APIRouter()

@router.post("/upload/{session_id}", response_model=FileItem)
async def upload_vendor_document(session_id: str, file: UploadFile = File(...)):
    """Uploads a source PDF document to a specific session."""
    try:
        file_manager = FileManager(session_id=session_id)
        saved_file = await file_manager.save_file(file)
        return saved_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

@router.get("/session/{session_id}", response_model=List[FileItem])
async def list_session_files(session_id: str):
    """Lists all files uploaded to a specific session."""
    try:
        file_manager = FileManager(session_id=session_id)
        files = file_manager.get_session_files()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not list files: {e}")
