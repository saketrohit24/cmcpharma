from fastapi import APIRouter, Body, HTTPException
from ..models.document import GeneratedDocument, RefinementRequest
from ..models.template import Template
from ..services.rag_service import RAGService
from ..services.generation_service import GenerationService
from ..services.file_manager import FileManager
from datetime import datetime

router = APIRouter()

@router.post("/generate/{session_id}", response_model=GeneratedDocument)
async def generate_document(session_id: str, template: Template = Body(...)):
    """Generates a full regulatory document based on a template and uploaded files."""
    file_manager = FileManager(session_id)
    file_paths = file_manager.get_session_file_paths()

    if not file_paths:
        raise HTTPException(status_code=400, detail="No source files found for this session.")

    try:
        rag_service = RAGService(file_paths=file_paths)
        generation_service = GenerationService()
        
        generated_sections = [
            generation_service.synthesize_section(toc_item.title, rag_service)
            for toc_item in template.toc
        ]
        
        doc = GeneratedDocument(
            title=template.name,
            template_id=template.id,
            session_id=session_id,
            sections=generated_sections
        )
        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

@router.post("/refine", response_model=dict)
async def refine_section(request: RefinementRequest = Body(...)):
    """Refines a single section of a document based on user feedback."""
    try:
        generation_service = GenerationService()
        refined_content = generation_service.refine_section(request)
        return {"refined_content": refined_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
