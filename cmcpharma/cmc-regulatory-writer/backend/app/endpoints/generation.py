from fastapi import APIRouter, Body, HTTPException
from ..models.document import GeneratedDocument, GeneratedSection, RefinementRequest
from ..models.template import Template
from ..services.rag_service import RAGService
from ..services.generation_service import GenerationService
from ..services.file_manager import FileManager
from ..core.config import settings
from datetime import datetime
import asyncio

router = APIRouter()

@router.post("/generate/{session_id}", response_model=GeneratedDocument)
async def generate_document(session_id: str, template: Template = Body(...)):
    """Generates a full regulatory document based on a template and uploaded files."""
    file_manager = FileManager(session_id)
    file_paths = file_manager.get_session_file_paths()
    
    print(f"🔍 Generation Debug - Session: {session_id}")
    print(f"📁 File manager session dir: {file_manager.session_dir}")
    print(f"📄 Found file paths: {file_paths}")
    print(f"📊 Number of files: {len(file_paths)}")

    if not file_paths:
        print(f"❌ No files found in session {session_id}")
        raise HTTPException(status_code=400, detail=f"No source files found for session '{session_id}'. Please upload files first.")

    try:
        rag_service = RAGService(file_paths=file_paths)
        generation_service = GenerationService()
        
        # Flatten TOC to get all sections (including nested ones)
        def flatten_toc(toc_items):
            flat_items = []
            for item in toc_items:
                flat_items.append(item)
                if hasattr(item, 'children') and item.children:
                    flat_items.extend(flatten_toc(item.children))
            return flat_items
        
        all_sections = flatten_toc(template.toc)
        print(f"Generating {len(all_sections)} sections from template: {[item.title for item in all_sections]}")
        
        # Generate sections sequentially to ensure proper content distribution
        generated_sections = []
        document_id = f"{session_id}-document"  # Create a document-level ID for citation tracking
        
        for i, toc_item in enumerate(all_sections):
            print(f"Generating section {i+1}/{len(all_sections)}: {toc_item.title}")
            section = await generation_service.synthesize_section(
                toc_item.title, 
                rag_service, 
                session_id=session_id,
                document_id=document_id  # Pass document ID to track citations across sections
            )
            generated_sections.append(section)
        
        # Check if any section is already titled "References" - if so, don't add another one
        existing_references_section = any(
            section.title.lower().strip() == "references" 
            for section in generated_sections
        )
        
        # Generate References section automatically only if:
        # 1. There are citations to reference
        # 2. No section is already titled "References"
        references_content = generation_service.generate_references_section(document_id)
        
        if references_content and not existing_references_section:
            references_section = GeneratedSection(
                title="References",
                content=references_content,
                source_count=0  # References don't have their own sources
            )
            generated_sections.append(references_section)
            print(f"📖 Added document-level References section with {len(references_content)} characters")
        elif existing_references_section:
            print(f"📖 References section already exists in template - skipping auto-generation")
        elif not references_content:
            print(f"📖 No citations found - skipping References section generation")
        
        print(f"Generated document with {len(generated_sections)} sections (including References)")
        
        # Get citations from the citation tracker
        print(f"🔍 Looking for citations in registry for document_id: {document_id}")
        citations_registry = generation_service.citation_tracker.get_registry(document_id)
        citations_data = []
        
        print(f"🔍 Citations registry found: {citations_registry is not None}")
        if citations_registry:
            print(f"🔍 Number of inline citations in registry: {len(citations_registry.inline_citations)}")
        
        if citations_registry and citations_registry.inline_citations:
            print(f"🔗 Processing {len(citations_registry.inline_citations)} citations for response")
            for inline_citation in citations_registry.inline_citations:
                citation_data = {
                    "id": inline_citation.citation_number,
                    "citation_number": inline_citation.citation_number,
                    "text": inline_citation.chunk_citation.text_excerpt,
                    "source": inline_citation.chunk_citation.pdf_name,
                    "page": inline_citation.chunk_citation.page_number,
                    "hover_content": f"{inline_citation.chunk_citation.text_excerpt[:100]}... - {inline_citation.chunk_citation.pdf_name}, p. {inline_citation.chunk_citation.page_number}",
                    "chunk_citation": {
                        "chunk_id": inline_citation.chunk_citation.chunk_id,
                        "pdf_name": inline_citation.chunk_citation.pdf_name,
                        "page_number": inline_citation.chunk_citation.page_number,
                        "text_excerpt": inline_citation.chunk_citation.text_excerpt,
                        "authors": inline_citation.chunk_citation.authors or [],
                        "external_link": inline_citation.chunk_citation.external_link
                    }
                }
                citations_data.append(citation_data)
        
        print(f"Returning {len(citations_data)} citations with the document")
        
        doc = GeneratedDocument(
            title=template.name,
            template_id=template.id,
            session_id=session_id,
            sections=generated_sections,  # Return all sections separately including References
            citations=citations_data  # Include actual citations from uploaded documents
        )
        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

@router.post("/refine", response_model=dict)
async def refine_section(request: RefinementRequest = Body(...)):
    """Refines a single section of a document based on user feedback."""
    try:
        generation_service = GenerationService()
        refined_content = await generation_service.refine_section(request)
        return {"refined_content": refined_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
