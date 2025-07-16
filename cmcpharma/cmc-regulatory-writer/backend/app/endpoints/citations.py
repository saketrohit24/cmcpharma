"""
Citation management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.citation import Citation, CitationCreate, CitationUpdate, CitationSearch
from app.services.citation_service import CitationService

router = APIRouter(prefix="/citations", tags=["citations"])


def get_citation_service() -> CitationService:
    """Dependency to get citation service instance"""
    return CitationService()


@router.get("", response_model=List[Citation])
async def get_citations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    citation_service: CitationService = Depends(get_citation_service)
):
    """Get all citations with pagination"""
    try:
        return await citation_service.get_citations(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{citation_id}", response_model=Citation)
async def get_citation(
    citation_id: int,
    citation_service: CitationService = Depends(get_citation_service)
):
    """Get a specific citation by ID"""
    try:
        citation = await citation_service.get_citation_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        return citation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=Citation)
async def create_citation(
    citation_data: CitationCreate,
    citation_service: CitationService = Depends(get_citation_service)
):
    """Create a new citation"""
    try:
        return await citation_service.create_citation(citation_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{citation_id}", response_model=Citation)
async def update_citation(
    citation_id: int,
    citation_data: CitationUpdate,
    citation_service: CitationService = Depends(get_citation_service)
):
    """Update an existing citation"""
    try:
        citation = await citation_service.update_citation(citation_id, citation_data)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        return citation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{citation_id}")
async def delete_citation(
    citation_id: int,
    citation_service: CitationService = Depends(get_citation_service)
):
    """Delete a citation"""
    try:
        success = await citation_service.delete_citation(citation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Citation not found")
        return {"message": "Citation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[Citation])
async def search_citations(
    search_query: CitationSearch,
    citation_service: CitationService = Depends(get_citation_service)
):
    """Search citations by various criteria"""
    try:
        return await citation_service.search_citations(search_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_citations_from_text(
    text: str,
    source_file_id: Optional[str] = None,
    citation_service: CitationService = Depends(get_citation_service)
):
    """Extract citations from text content"""
    try:
        citations = await citation_service.extract_citations_from_text(text, source_file_id)
        return {"citations": citations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/format")
async def format_citation(
    citation_id: int,
    style: str = "APA",
    citation_service: CitationService = Depends(get_citation_service)
):
    """Format a citation in specified style"""
    try:
        citation = await citation_service.get_citation_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        
        formatted = await citation_service.format_citation(citation, style)
        return {"formatted_citation": formatted}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/styles/available")
async def get_citation_styles():
    """Get list of available citation styles"""
    return {
        "styles": [
            {"code": "APA", "name": "APA Style", "description": "American Psychological Association"},
            {"code": "MLA", "name": "MLA Style", "description": "Modern Language Association"},
            {"code": "Chicago", "name": "Chicago Style", "description": "Chicago Manual of Style"},
            {"code": "IEEE", "name": "IEEE Style", "description": "Institute of Electrical and Electronics Engineers"},
            {"code": "Vancouver", "name": "Vancouver Style", "description": "International Committee of Medical Journal Editors"}
        ]
    }


@router.post("/import")
async def import_citations(
    import_data: str,
    format: str = "bibtex",
    citation_service: CitationService = Depends(get_citation_service)
):
    """Import citations from external formats (BibTeX, EndNote, etc.)"""
    try:
        citations = await citation_service.import_citations(import_data, format)
        return {
            "imported_count": len(citations),
            "citations": citations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_citations(
    format: str = "bibtex",
    citation_ids: Optional[List[int]] = Query(None),
    citation_service: CitationService = Depends(get_citation_service)
):
    """Export citations to external formats"""
    try:
        exported_data = await citation_service.export_citations(format, citation_ids)
        return {"format": format, "data": exported_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
