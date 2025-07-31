from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse
from ..models.export import ExportRequest
from ..services.export_service import DocumentExporter
import os

router = APIRouter()

@router.post("/export", response_class=FileResponse)
async def export_document(request: ExportRequest = Body(...)):
    """Exports a generated document to a formatted PDF or DOCX file."""
    try:
        exporter = DocumentExporter(session_id=request.document.session_id)
        
        # Export document in the requested format
        if request.format.lower() == 'pdf':
            document_bytes = exporter.export_document(request.document, 'pdf')
            media_type = 'application/pdf'
            file_extension = '.pdf'
        elif request.format.lower() == 'docx':
            document_bytes = exporter.export_document(request.document, 'docx')
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            file_extension = '.docx'
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
        # Create temp directory and save file
        temp_dir = "temp_exports"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"Regulatory_{request.document.session_id}{file_extension}")
        
        with open(file_path, "wb") as f:
            f.write(document_bytes)
            
        # Generate a clean filename
        clean_title = request.document.title.replace(' ', '_').replace('/', '_').replace('\\', '_')
        filename = f"{clean_title}{file_extension}"
            
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export {request.format.upper()}: {str(e)}")
