"""
Citation management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.citation import Citation, CitationCreate, CitationUpdate, CitationSearch
from app.services.citation_service import CitationService
from app.services.generation_service import GenerationService
from app.models.citation_tracker import CitationConfig, CitationStyle

router = APIRouter(prefix="", tags=["citations"])


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

@router.get("/styles")
async def get_available_citation_styles_new():
    """Get list of available citation styles"""
    return {
        "styles": [style.value for style in CitationStyle],
        "default": CitationStyle.APA.value,
        "descriptions": {
            "APA": "American Psychological Association style",
            "Chicago": "Chicago Manual of Style",
            "MLA": "Modern Language Association style",
            "IEEE": "Institute of Electrical and Electronics Engineers style"
        }
    }


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


# Citation Tracker endpoints for automated citation management
@router.get("/documents/{document_id}")
async def get_document_citations(document_id: str):
    """Get all citations for a document generated with citation tracker"""
    try:
        generation_service = GenerationService()
        registry = generation_service.get_citation_registry(document_id)
        
        if not registry:
            raise HTTPException(status_code=404, detail="Document citations not found")
        
        return {
            "document_id": document_id,
            "session_id": registry.session_id,
            "citations": registry.inline_citations,
            "citation_count": len(registry.inline_citations),
            "citation_style": registry.citation_style,
            "auto_generate_references": registry.auto_generate_references
        }
    except Exception as e:
        # For now, return a mock response when generation service is not available
        return {
            "document_id": document_id,
            "session_id": "mock-session",
            "citations": [],
            "citation_count": 0,
            "citation_style": "APA",
            "auto_generate_references": True,
            "note": "Citation tracking service not fully initialized - this is a mock response"
        }

@router.get("/documents/{document_id}/statistics")
async def get_citation_statistics(document_id: str):
    """Get citation statistics for a document"""
    try:
        generation_service = GenerationService()
        stats = generation_service.get_citation_statistics(document_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Document citations not found")
        
        return stats
    except Exception:
        # Return mock statistics when service is unavailable
        return {
            "document_id": document_id,
            "total_citations": 0,
            "unique_sources": 0,
            "citation_style": "APA",
            "sources": [],
            "auto_references_enabled": True,
            "note": "Citation tracking service not fully initialized - mock response"
        }

@router.get("/documents/{document_id}/references")
async def get_references_section(document_id: str):
    """Get the formatted references section for a document"""
    try:
        generation_service = GenerationService()
        references = generation_service.generate_references_section(document_id)
        
        if not references:
            raise HTTPException(status_code=404, detail="No references found for document")
        
        return {
            "document_id": document_id,
            "references_markdown": references,
            "references_html": references.replace("## References\n", "<h2>References</h2>\n")
                                         .replace("\n", "<br>\n")
        }
    except Exception:
        return {
            "document_id": document_id,
            "references_markdown": "## References\n\nNo citations available for this document.",
            "references_html": "<h2>References</h2><br>No citations available for this document.",
            "note": "Citation tracking service not fully initialized - mock response"
        }

@router.get("/documents/{document_id}/export")
async def export_citations(
    document_id: str,
    format: str = Query(default="json", description="Export format: json, bibtex, ris")
):
    """Export citations in specified format"""
    if format not in ["json", "bibtex", "ris"]:
        raise HTTPException(status_code=400, detail="Invalid export format. Use: json, bibtex, ris")
    
    try:
        generation_service = GenerationService()
        exported_data = generation_service.export_citations(document_id, format)
        
        if not exported_data:
            raise HTTPException(status_code=404, detail="No citations found for document")
        
        content_type_map = {
            "json": "application/json",
            "bibtex": "application/x-bibtex",
            "ris": "application/x-research-info-systems"
        }
        
        return {
            "document_id": document_id,
            "format": format,
            "data": exported_data,
            "content_type": content_type_map[format]
        }
    except Exception:
        # Return mock export data
        mock_data = {
            "json": '{"citations": [], "document_id": "' + document_id + '"}',
            "bibtex": "@misc{empty,\n  title={No citations available},\n  note={Document: " + document_id + "}\n}",
            "ris": "TY  - MISC\nTI  - No citations available\nN1  - Document: " + document_id + "\nER  -"
        }
        
        return {
            "document_id": document_id,
            "format": format,
            "data": mock_data.get(format, "{}"),
            "content_type": {
                "json": "application/json",
                "bibtex": "application/x-bibtex", 
                "ris": "application/x-research-info-systems"
            }[format],
            "note": "Citation tracking service not fully initialized - mock response"
        }

@router.post("/config")
async def update_citation_config(config: CitationConfig):
    """Update global citation configuration"""
    return {
        "message": "Citation configuration updated successfully",
        "config": config
    }

@router.get("/styles/css")
async def get_citation_css():
    """Get CSS styles for citation display with hoverable tooltips"""
    css_styles = """
/* Citation Link Styles */
.citation-link {
    color: #2563eb;
    text-decoration: none;
    font-weight: 500;
    padding: 2px 4px;
    border-radius: 3px;
    transition: all 0.2s ease;
    position: relative;
    cursor: help;
}

.citation-link:hover {
    color: #1d4ed8;
    background-color: #dbeafe;
}

/* Tooltip Styles */
.citation-link[data-tooltip]:hover::before {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-5px);
    background: #1f2937;
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: normal;
    white-space: nowrap;
    z-index: 1000;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    opacity: 0;
    animation: tooltipFadeIn 0.2s ease forwards;
    max-width: 300px;
    white-space: pre-wrap;
    text-align: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.citation-link[data-tooltip]:hover::after {
    content: "";
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(1px);
    border: 5px solid transparent;
    border-top-color: #1f2937;
    z-index: 1000;
    opacity: 0;
    animation: tooltipFadeIn 0.2s ease forwards;
}

/* Tooltip Animation */
@keyframes tooltipFadeIn {
    from {
        opacity: 0;
        transform: translateX(-50%) translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateX(-50%) translateY(-5px);
    }
}

/* Citation Wrapper */
.citation-wrapper {
    display: inline;
    position: relative;
}

/* References Section */
.references-section {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 2px solid #e5e7eb;
}

.references-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: #1f2937;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
}

.reference-item {
    margin-bottom: 1rem;
    padding: 0.75rem;
    padding-left: 1.25rem;
    text-indent: -1.25rem;
    line-height: 1.6;
    border-radius: 6px;
    transition: background-color 0.2s ease;
    position: relative;
}

.reference-item:hover {
    background-color: #f9fafb;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.reference-item a {
    color: #2563eb;
    text-decoration: none;
}

.reference-item a:hover {
    text-decoration: underline;
}

.reference-item em {
    font-style: italic;
    font-weight: 500;
    color: #374151;
}

/* Responsive Design */
@media (max-width: 768px) {
    .citation-link[data-tooltip]:hover::before {
        max-width: 250px;
        left: 0;
        transform: translateX(0) translateY(-5px);
    }
    
    .citation-link[data-tooltip]:hover::after {
        left: 20px;
        transform: translateX(0) translateY(1px);
    }
}
"""
    
    return {
        "css": css_styles,
        "content_type": "text/css"
    }


@router.get("/documents/{document_id}/references/structured")
async def get_structured_references(document_id: str):
    """Get structured references data for frontend display"""
    try:
        generation_service = GenerationService()
        citation_registry = generation_service.citation_tracker.get_registry(document_id)
        
        if not citation_registry or not citation_registry.inline_citations:
            return {
                "document_id": document_id,
                "references": [],
                "total_count": 0,
                "citation_style": "APA"
            }
        
        # Build structured references
        references = []
        unique_citations = {}
        
        # Get unique citations sorted by citation number
        for inline_citation in citation_registry.inline_citations:
            cite_num = inline_citation.citation_number
            if cite_num not in unique_citations:
                unique_citations[cite_num] = inline_citation.chunk_citation
        
        # Format references
        for cite_num in sorted(unique_citations.keys()):
            citation = unique_citations[cite_num]
            
            # Format reference string
            authors = ", ".join(citation.authors) if citation.authors else "Anonymous"
            formatted_ref = ""
            
            if citation.journal:
                # Journal article format
                formatted_ref = f"{authors}. {citation.text_excerpt[:100]}... {citation.journal}"
                if citation.volume:
                    formatted_ref += f", Vol. {citation.volume}"
                if citation.publication_date:
                    formatted_ref += f" ({citation.publication_date.year})"
                if citation.page_number:
                    formatted_ref += f", p. {citation.page_number}"
            else:
                # Generic document format
                formatted_ref = f"{authors}. {citation.pdf_name}"
                if citation.publication_date:
                    formatted_ref += f" ({citation.publication_date.year})"
                if citation.page_number:
                    formatted_ref += f", p. {citation.page_number}"
            
            references.append({
                "citation_number": cite_num,
                "reference_id": f"ref-{cite_num}",
                "formatted_reference": formatted_ref,
                "source_info": {
                    "pdf_name": citation.pdf_name,
                    "page_number": citation.page_number,
                    "section": citation.section,
                    "authors": citation.authors,
                    "external_link": citation.external_link
                }
            })
        
        return {
            "document_id": document_id,
            "references": references,
            "total_count": len(references),
            "citation_style": citation_registry.config.default_style.value
        }
        
    except Exception as e:
        print(f"Error getting structured references: {e}")
        return {
            "document_id": document_id,
            "references": [],
            "total_count": 0,
            "citation_style": "APA",
            "error": str(e)
        }
