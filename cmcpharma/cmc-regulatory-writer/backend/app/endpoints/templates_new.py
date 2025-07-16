from fastapi import APIRouter, Body
from ..models.template import Template, TemplateCreationRequest
from ..services.template_service import TemplateService

router = APIRouter()

@router.post("/parse", response_model=Template)
async def parse_template_from_text(request: TemplateCreationRequest = Body(...)):
    """Parses raw TOC text and returns a structured Template object."""
    template_service = TemplateService()
    return template_service.create_template_from_text(request)
