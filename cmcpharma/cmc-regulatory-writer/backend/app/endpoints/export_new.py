from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse
from ..models.export import ExportRequest
from ..services.export_service import RegulatoryPDFExporter
import os

router = APIRouter()

@router.post("/export", response_class=FileResponse)
async def export_document(request: ExportRequest = Body(...)):
    """Exports a generated document to a formatted PDF file."""
    try:
        exporter = RegulatoryPDFExporter(session_id=request.document.session_id)
        pdf_bytes = exporter.generate_regulatory_document(request.document)
        
        temp_dir = "temp_exports"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"Regulatory_{request.document.session_id}.pdf")
        
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
            
        return FileResponse(
            path=file_path,
            media_type='application/pdf',
            filename=f"{request.document.title.replace(' ', '_')}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export PDF: {e}")
