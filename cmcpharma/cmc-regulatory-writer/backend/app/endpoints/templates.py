from typing import List
from fastapi import APIRouter, Body, HTTPException, Depends, UploadFile, File, Form
from ..models.template import Template, TemplateCreationRequest
from ..services.template_service import TemplateService
import tempfile
import os

router = APIRouter()

# Create a singleton instance
_template_service = None

def get_template_service() -> TemplateService:
    """Dependency to get template service singleton instance"""
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service

@router.post("/parse", response_model=Template)
async def parse_template_from_text(
    request: TemplateCreationRequest = Body(...),
    template_service: TemplateService = Depends(get_template_service)
):
    """Parses raw TOC text and returns a structured Template object."""
    return template_service.create_template_from_text(request)

@router.get("", response_model=List[Template])
async def get_templates(
    template_service: TemplateService = Depends(get_template_service)
):
    """Get all templates"""
    return await template_service.get_all_templates()

@router.get("/{template_id}", response_model=Template)
async def get_template(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """Get a specific template by ID"""
    template = await template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("", response_model=Template)
async def save_template(
    template: Template = Body(...),
    template_service: TemplateService = Depends(get_template_service)
):
    """Save a template"""
    return await template_service.save_template(template)

@router.put("/{template_id}", response_model=Template)
async def update_template(
    template_id: str,
    template_data: dict = Body(...),
    template_service: TemplateService = Depends(get_template_service)
):
    """Update an existing template"""
    template = await template_service.update_template(template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """Delete a template"""
    success = await template_service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}

@router.post("/upload", response_model=Template)
async def upload_template_file(
    file: UploadFile = File(...),
    name: str = Form(None),
    description: str = Form(""),
    template_service: TemplateService = Depends(get_template_service)
):
    """Upload a file and create a template from it"""
    
    # Validate file type
    allowed_extensions = {'.pdf', '.txt', '.doc', '.docx', '.md'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Create template from file
        template_name = name or os.path.splitext(file.filename)[0]
        template = await template_service.create_template_from_uploaded_file(
            temp_file_path, 
            template_name, 
            description
        )
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return template
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

@router.get("/structure/{template_id}")
async def get_template_structure(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """Get the hierarchical structure of a template for project sidebar"""
    template = await template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Build hierarchical structure for frontend
    structure = {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "type": getattr(template, 'type', 'manual'),
        "sections": []
    }
    
    # Convert flat TOC to hierarchical structure
    def build_hierarchy(toc_items):
        hierarchy = []
        stack = []
        
        for item in toc_items:
            # Create section node
            section_node = {
                "id": item.id,
                "title": item.title,
                "level": item.level,
                "children": []
            }
            
            # Find parent based on level
            while stack and stack[-1]["level"] >= item.level:
                stack.pop()
            
            if stack:
                # Add as child to parent
                stack[-1]["children"].append(section_node)
            else:
                # Add as root level
                hierarchy.append(section_node)
            
            stack.append(section_node)
        
        return hierarchy
    
    structure["sections"] = build_hierarchy(template.toc)
    return structure
