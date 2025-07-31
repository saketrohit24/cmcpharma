"""
Citation Tracker Service for automated citation management during document generation
"""
import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from app.models.citation_tracker import (
    ChunkCitation, InlineCitation, DocumentCitationRegistry,
    CitationConfig, CitationStyle
)
import logging

logger = logging.getLogger(__name__)

# Global registry storage to persist citations across service instances
_global_registries: Dict[str, "DocumentCitationRegistry"] = {}


class CitationTracker:
    """
    Service for tracking and managing citations during document generation
    """
    
    def __init__(self, config: Optional[CitationConfig] = None):
        """Initialize citation tracker with configuration"""
        self.config = config or CitationConfig()
        # Use global registry for persistence across instances
        self.registries = _global_registries
    
    def create_registry(self, document_id: str, session_id: str) -> DocumentCitationRegistry:
        """Create a new citation registry for a document"""
        registry = DocumentCitationRegistry(
            document_id=document_id,
            session_id=session_id,
            citation_style=self.config.citation_style,
            auto_generate_references=self.config.auto_generate_references
        )
        self.registries[document_id] = registry
        logger.info(f"Created citation registry for document {document_id}")
        return registry
    
    def get_registry(self, document_id: str) -> Optional[DocumentCitationRegistry]:
        """Get citation registry for a document"""
        return self.registries.get(document_id)
    
    def extract_citation_from_chunk(self, 
                                  chunk_content: str, 
                                  chunk_metadata: Dict[str, Any],
                                  chunk_id: Optional[str] = None) -> ChunkCitation:
        """Extract citation information from a content chunk and its metadata"""
        
        if chunk_id is None:
            chunk_id = str(uuid.uuid4())
        
        # Extract basic information from metadata
        pdf_name = chunk_metadata.get('source', 'Unknown Source')
        page_number = chunk_metadata.get('page', 1)
        
        # Try to extract page number from various metadata formats
        if isinstance(page_number, str):
            try:
                page_number = int(re.search(r'\d+', page_number).group())
            except (AttributeError, ValueError):
                page_number = 1
        
        # Extract section information if available
        section = chunk_metadata.get('section') or chunk_metadata.get('chapter')
        
        # Create text excerpt (first 150 characters)
        text_excerpt = chunk_content[:150] + "..." if len(chunk_content) > 150 else chunk_content
        
        # Extract additional metadata
        authors = chunk_metadata.get('authors', [])
        if isinstance(authors, str):
            authors = [authors]
        
        external_link = chunk_metadata.get('url') or chunk_metadata.get('file_path')
        
        citation = ChunkCitation(
            chunk_id=chunk_id,
            pdf_name=pdf_name,
            page_number=page_number,
            section=section,
            text_excerpt=text_excerpt,
            citation_style=self.config.citation_style,
            external_link=external_link,
            authors=authors,
            publication_date=chunk_metadata.get('publication_date'),
            publisher=chunk_metadata.get('publisher'),
            doi=chunk_metadata.get('doi'),
            isbn=chunk_metadata.get('isbn'),
            journal=chunk_metadata.get('journal'),
            volume=chunk_metadata.get('volume'),
            issue=chunk_metadata.get('issue')
        )
        
        logger.debug(f"Created citation for chunk {chunk_id}: {pdf_name}, page {page_number}")
        return citation
    
    def track_chunk_citation(self, 
                           chunk_content: str, 
                           chunk_metadata: Dict[str, Any],
                           chunk_id: Optional[str] = None,
                           document_id: Optional[str] = None) -> ChunkCitation:
        """Track a citation from chunk content and metadata, and add to document registry if provided"""
        # Extract citation information from chunk
        chunk_citation = self.extract_citation_from_chunk(chunk_content, chunk_metadata, chunk_id)
        
        # If document_id is provided, add to the document's registry
        if document_id:
            registry = self.registries.get(document_id)
            if registry:
                registry.add_citation(chunk_citation)
                logger.debug(f"Added citation to document {document_id}: {chunk_citation.pdf_name}, page {chunk_citation.page_number}")
        
        return chunk_citation
    
    def add_citation_to_document(self, 
                               document_id: str, 
                               chunk_citation: ChunkCitation) -> InlineCitation:
        """Add a citation to a document's registry"""
        registry = self.registries.get(document_id)
        if not registry:
            raise ValueError(f"No citation registry found for document {document_id}")
        
        inline_citation = registry.add_citation(chunk_citation)
        logger.debug(f"Added citation {inline_citation.citation_number} to document {document_id}")
        return inline_citation
    
    def inject_inline_citations(self, 
                              content: str, 
                              citations: List[InlineCitation],
                              injection_points: Optional[List[int]] = None) -> str:
        """
        Inject inline citation markers into content at specified points
        """
        if not citations or not self.config.show_inline_citations:
            return content
        
        if injection_points is None:
            # Auto-detect injection points (end of sentences/paragraphs)
            injection_points = self._detect_citation_points(content, len(citations))
        
        # Sort citations and injection points together
        citation_injections = list(zip(citations, injection_points))
        citation_injections.sort(key=lambda x: x[1], reverse=True)  # Inject from end to start
        
        modified_content = content
        for citation, point in citation_injections:
            citation_html = self._create_citation_html(citation)
            modified_content = (
                modified_content[:point] + 
                citation_html + 
                modified_content[point:]
            )
        
        return modified_content
    
    def _detect_citation_points(self, content: str, num_citations: int) -> List[int]:
        """Automatically detect good points to insert citations"""
        # Find sentence endings
        sentence_endings = [m.end() for m in re.finditer(r'[.!?]\s+', content)]
        
        if not sentence_endings:
            # No sentence endings found, distribute evenly
            content_length = len(content)
            return [int(i * content_length / num_citations) for i in range(1, num_citations + 1)]
        
        if len(sentence_endings) <= num_citations:
            return sentence_endings
        
        # Distribute citations evenly across sentence endings
        step = len(sentence_endings) // num_citations
        return [sentence_endings[i * step] for i in range(num_citations)]
    
    def _create_citation_html(self, citation: InlineCitation) -> str:
        """Create HTML for an inline citation marker with hoverable tooltip"""
        tooltip_content = citation.hover_content.replace('"', '&quot;')  # Escape quotes for HTML
        
        return (
            f'<span class="citation-wrapper">'
            f'<sup>'
            f'<a href="#{citation.reference_id}" '
            f'id="{citation.cite_id}" '
            f'class="citation-link" '
            f'data-tooltip="{tooltip_content}" '
            f'title="{citation.hover_content}">'
            f'{citation.citation_number}'
            f'</a>'
            f'</sup>'
            f'</span>'
        )
    
    def generate_references_section(self, document_id: str) -> str:
        """Generate the references section for a document"""
        registry = self.registries.get(document_id)
        if not registry or not registry.auto_generate_references:
            return ""
        
        return registry.generate_references_section()
    
    def append_references_to_content(self, content: str, document_id: str) -> str:
        """Append references section to document content"""
        references_section = self.generate_references_section(document_id)
        if not references_section:
            return content
        
        # Check if references section already exists
        if "## References" in content:
            logger.info("References section already exists, not appending")
            return content
        
        # Append references section
        return content + "\n\n" + references_section
    
    def process_generated_content(self, 
                                content: str,
                                document_id: str,
                                retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Process generated content by:
        1. Creating citations for each chunk
        2. Injecting inline citation markers
        3. Appending references section
        """
        registry = self.get_registry(document_id)
        if not registry:
            logger.warning(f"No citation registry found for document {document_id}")
            return content
        
        # Create citations for each chunk
        citations = []
        for chunk_data in retrieved_chunks:
            chunk_citation = self.extract_citation_from_chunk(
                chunk_content=chunk_data.get('content', ''),
                chunk_metadata=chunk_data.get('metadata', {}),
                chunk_id=chunk_data.get('chunk_id', str(uuid.uuid4()))
            )
            inline_citation = self.add_citation_to_document(document_id, chunk_citation)
            citations.append(inline_citation)
        
        # Inject inline citations
        content_with_citations = self.inject_inline_citations(content, citations)
        
        # Append references section
        final_content = self.append_references_to_content(content_with_citations, document_id)
        
        logger.info(f"Processed content for document {document_id}: {len(citations)} citations added")
        return final_content
    
    def get_citation_statistics(self, document_id: str) -> Dict[str, Any]:
        """Get citation statistics for a document"""
        registry = self.registries.get(document_id)
        if not registry:
            return {}
        
        unique_sources = set(cite.chunk_citation.pdf_name for cite in registry.inline_citations)
        
        return {
            "total_citations": len(registry.inline_citations),
            "unique_sources": len(unique_sources),
            "citation_style": registry.citation_style.value,
            "sources": list(unique_sources),
            "auto_references_enabled": registry.auto_generate_references
        }
    
    def export_citations(self, document_id: str, format: str = "json") -> str:
        """Export citations in specified format"""
        registry = self.registries.get(document_id)
        if not registry:
            return ""
        
        if format == "bibtex":
            return self._export_bibtex(registry)
        elif format == "ris":
            return self._export_ris(registry)
        else:
            return registry.model_dump_json()
    
    def _export_bibtex(self, registry: DocumentCitationRegistry) -> str:
        """Export citations as BibTeX"""
        entries = []
        for inline_cite in registry.inline_citations:
            citation = inline_cite.chunk_citation
            key = f"cite{inline_cite.citation_number}"
            
            entry_lines = [f"@article{{{key},"]
            
            if citation.authors:
                authors_str = " and ".join(citation.authors)
                entry_lines.append(f"  author = {{{authors_str}}},")
            
            entry_lines.append(f"  title = {{{citation.pdf_name}}},")
            entry_lines.append(f"  pages = {{{citation.page_number}}},")
            
            if citation.journal:
                entry_lines.append(f"  journal = {{{citation.journal}}},")
            
            if citation.publication_date:
                entry_lines.append(f"  year = {{{citation.publication_date.year}}},")
            
            if citation.doi:
                entry_lines.append(f"  doi = {{{citation.doi}}},")
            
            if citation.external_link:
                entry_lines.append(f"  url = {{{citation.external_link}}},")
            
            entry_lines.append("}")
            entries.append("\n".join(entry_lines))
        
        return "\n\n".join(entries)
    
    def _export_ris(self, registry: DocumentCitationRegistry) -> str:
        """Export citations as RIS format"""
        entries = []
        for inline_cite in registry.inline_citations:
            citation = inline_cite.chunk_citation
            
            entry_lines = ["TY  - JOUR"]  # Journal article type
            
            if citation.authors:
                for author in citation.authors:
                    entry_lines.append(f"AU  - {author}")
            
            entry_lines.append(f"TI  - {citation.pdf_name}")
            entry_lines.append(f"SP  - {citation.page_number}")
            
            if citation.journal:
                entry_lines.append(f"JO  - {citation.journal}")
            
            if citation.publication_date:
                entry_lines.append(f"PY  - {citation.publication_date.year}")
            
            if citation.doi:
                entry_lines.append(f"DO  - {citation.doi}")
            
            if citation.external_link:
                entry_lines.append(f"UR  - {citation.external_link}")
            
            entry_lines.append("ER  - ")
            entries.append("\n".join(entry_lines))
        
        return "\n\n".join(entries)
