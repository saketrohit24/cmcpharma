"""
Enhanced citation tracking models for automated citation management
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class CitationStyle(str, Enum):
    """Supported citation styles"""
    APA = "APA"
    CHICAGO = "Chicago"
    MLA = "MLA"
    IEEE = "IEEE"


class ChunkCitation(BaseModel):
    """Citation information for a specific content chunk"""
    chunk_id: str = Field(..., description="Unique identifier for the content chunk")
    pdf_name: str = Field(..., description="Name of the PDF file")
    page_number: int = Field(..., ge=1, description="Page number in the PDF")
    section: Optional[str] = Field(None, description="Section or chapter within the PDF")
    text_excerpt: str = Field(..., description="Excerpt of the text being cited")
    citation_style: CitationStyle = Field(default=CitationStyle.APA, description="Citation format style")
    external_link: Optional[str] = Field(None, description="URL to external source or PDF")
    authors: Optional[List[str]] = Field(default_factory=list, description="List of authors")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    publisher: Optional[str] = Field(None, description="Publisher name")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    isbn: Optional[str] = Field(None, description="ISBN for books")
    journal: Optional[str] = Field(None, description="Journal name")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class InlineCitation(BaseModel):
    """Inline citation marker with formatting information"""
    citation_number: int = Field(..., description="Sequential citation number")
    chunk_citation: ChunkCitation = Field(..., description="Associated chunk citation")
    marker_text: str = Field(..., description="Display text for the citation marker")
    hover_content: str = Field(..., description="Content to display on hover")
    anchor_id: str = Field(..., description="HTML anchor ID for linking")
    
    @property
    def reference_id(self) -> str:
        """Generate reference ID for linking"""
        return f"ref-{self.citation_number}"
    
    @property
    def cite_id(self) -> str:
        """Generate citation ID for linking"""
        return f"cite-{self.citation_number}"


class DocumentCitationRegistry(BaseModel):
    """Registry for managing all citations in a document"""
    document_id: str = Field(..., description="Document identifier")
    session_id: str = Field(..., description="Session identifier")
    citations: Dict[str, ChunkCitation] = Field(default_factory=dict, description="Citations by chunk_id")
    inline_citations: List[InlineCitation] = Field(default_factory=list, description="Ordered inline citations")
    citation_counter: int = Field(default=0, description="Counter for citation numbering")
    citation_style: CitationStyle = Field(default=CitationStyle.APA, description="Default citation style")
    auto_generate_references: bool = Field(default=True, description="Auto-generate references section")
    
    def add_citation(self, chunk_citation: ChunkCitation) -> InlineCitation:
        """Add a new citation and return inline citation, with deduplication by source+page"""
        # Create a unique key based on source file and page number for deduplication
        source_key = f"{chunk_citation.pdf_name}|{chunk_citation.page_number}"
        
        # Check if this source+page combination already exists
        for existing_inline in self.inline_citations:
            existing_key = f"{existing_inline.chunk_citation.pdf_name}|{existing_inline.chunk_citation.page_number}"
            if existing_key == source_key:
                print(f"🔄 Reusing existing citation [{existing_inline.citation_number}] for {chunk_citation.pdf_name}, p. {chunk_citation.page_number}")
                return existing_inline
        
        # Check if chunk_id already exists (fallback check)
        if chunk_citation.chunk_id in self.citations:
            for inline_cite in self.inline_citations:
                if inline_cite.chunk_citation.chunk_id == chunk_citation.chunk_id:
                    return inline_cite
        
        # Add new citation
        self.citation_counter += 1
        self.citations[chunk_citation.chunk_id] = chunk_citation
        
        # Create inline citation
        inline_citation = InlineCitation(
            citation_number=self.citation_counter,
            chunk_citation=chunk_citation,
            marker_text=f"[{self.citation_counter}]",
            hover_content=self._generate_hover_content(chunk_citation),
            anchor_id=f"cite-{self.citation_counter}"
        )
        
        self.inline_citations.append(inline_citation)
        print(f"📋 Created new citation [{self.citation_counter}] for {chunk_citation.pdf_name}, p. {chunk_citation.page_number}")
        return inline_citation
    
    def _generate_hover_content(self, citation: ChunkCitation) -> str:
        """Generate hover tooltip content with PDF name and page number"""
        parts = []
        
        # Add authors - use extracted authors if not provided
        authors = citation.authors if citation.authors else self._extract_authors_from_filename(citation.pdf_name)
        if authors and len(authors) > 0:
            authors_str = ", ".join(authors[:2])
            if len(authors) > 2:
                authors_str += " et al."
            parts.append(f"👤 {authors_str}")
        
        # Add title - use extracted title
        title = self._extract_title_from_filename(citation.pdf_name)
        if title != citation.pdf_name:  # Only add if we successfully extracted a title
            parts.append(f"📖 {title}")
        
        # Add page number
        parts.append(f"📄 Page {citation.page_number}")
        
        # Add section if available
        if citation.section:
            parts.append(f"📑 {citation.section}")
            
        # Add publication year if available
        if citation.publication_date:
            parts.append(f"📅 {citation.publication_date.year}")
        
        return " • ".join(parts)
    
    def generate_references_section(self) -> str:
        """Generate formatted references section"""
        if not self.inline_citations:
            return ""
        
        references = ["## References\n"]
        
        for inline_cite in self.inline_citations:
            formatted_ref = self._format_reference(inline_cite)
            references.append(f"{inline_cite.citation_number}. {formatted_ref}\n")
        
        return "\n".join(references)
    
    def _format_reference(self, inline_cite: InlineCitation) -> str:
        """Format a single reference according to citation style"""
        citation = inline_cite.chunk_citation
        
        if citation.citation_style == CitationStyle.APA:
            return self._format_apa_reference(citation)
        elif citation.citation_style == CitationStyle.CHICAGO:
            return self._format_chicago_reference(citation)
        elif citation.citation_style == CitationStyle.MLA:
            return self._format_mla_reference(citation)
        else:
            return self._format_default_reference(citation)
    
    def _format_apa_reference(self, citation: ChunkCitation) -> str:
        """Format reference in APA style"""
        parts = []
        
        if citation.authors:
            if len(citation.authors) == 1:
                parts.append(f"{citation.authors[0]}.")
            elif len(citation.authors) <= 6:
                authors_str = ", ".join(citation.authors[:-1]) + f", & {citation.authors[-1]}."
                parts.append(authors_str)
            else:
                parts.append(f"{citation.authors[0]} et al.")
        else:
            # Extract authors from PDF filename if not provided
            extracted_authors = self._extract_authors_from_filename(citation.pdf_name)
            if extracted_authors:
                if len(extracted_authors) == 1:
                    parts.append(f"{extracted_authors[0]}.")
                else:
                    parts.append(f"{extracted_authors[0]} et al.")
            else:
                parts.append("[No author].")
        
        if citation.publication_date:
            parts.append(f"({citation.publication_date.year}).")
        
        if citation.journal:
            parts.append(f"*{citation.journal}*.")
        else:
            # Use extracted title if available
            title = self._extract_title_from_filename(citation.pdf_name)
            parts.append(f"*{title}*.")
        
        if citation.external_link:
            parts.append(f"Retrieved from {citation.external_link}")
        else:
            parts.append(f"Page {citation.page_number}.")
        
        return " ".join(parts)
    
    def _format_chicago_reference(self, citation: ChunkCitation) -> str:
        """Format reference in Chicago style"""
        parts = []
        
        if citation.authors:
            if len(citation.authors) == 1:
                parts.append(f"{citation.authors[0]}.")
            else:
                parts.append(f"{citation.authors[0]} et al.")
        else:
            # Extract authors from PDF filename if not provided
            extracted_authors = self._extract_authors_from_filename(citation.pdf_name)
            if extracted_authors:
                parts.append(f"{extracted_authors[0]} et al." if len(extracted_authors) > 1 else f"{extracted_authors[0]}.")
        
        if citation.journal:
            title = self._extract_title_from_filename(citation.pdf_name)
            parts.append(f'"{title}." *{citation.journal}*')
        else:
            title = self._extract_title_from_filename(citation.pdf_name)
            parts.append(f'*{title}*.')
        
        if citation.publication_date:
            parts.append(f"({citation.publication_date.year}):")
        
        parts.append(f"{citation.page_number}.")
        
        if citation.external_link:
            parts.append(f"Accessed {datetime.now().strftime('%B %d, %Y')}. {citation.external_link}.")
        
        return " ".join(parts)
    
    def _format_mla_reference(self, citation: ChunkCitation) -> str:
        """Format reference in MLA style"""
        parts = []
        
        if citation.authors:
            parts.append(f"{citation.authors[0]}.")
        else:
            # Extract authors from PDF filename if not provided
            extracted_authors = self._extract_authors_from_filename(citation.pdf_name)
            if extracted_authors:
                parts.append(f"{extracted_authors[0]}.")
        
        title = self._extract_title_from_filename(citation.pdf_name)
        parts.append(f'"{title}."')
        
        if citation.journal:
            parts.append(f"*{citation.journal}*,")
        
        if citation.publication_date:
            parts.append(f"{citation.publication_date.year},")
        
        parts.append(f"p. {citation.page_number}.")
        
        if citation.external_link:
            parts.append(f"Web. {datetime.now().strftime('%d %b %Y')}.")
        
        return " ".join(parts)
    
    def _format_default_reference(self, citation: ChunkCitation) -> str:
        """Default reference format"""
        parts = []
        
        if citation.authors:
            parts.append(", ".join(citation.authors))
        else:
            # Extract authors from PDF filename if not provided
            extracted_authors = self._extract_authors_from_filename(citation.pdf_name)
            if extracted_authors:
                parts.append(", ".join(extracted_authors))
        
        title = self._extract_title_from_filename(citation.pdf_name)
        parts.append(title)
        parts.append(f"Page {citation.page_number}")
        
        if citation.external_link:
            parts.append(f"Available at: {citation.external_link}")
        
        return ". ".join(parts) + "."
    
    def _extract_authors_from_filename(self, pdf_name: str) -> List[str]:
        """Extract author names from PDF filename"""
        try:
            # Remove file extension
            name_without_ext = pdf_name.replace('.pdf', '').replace('.PDF', '')
            
            # Common patterns for author extraction
            # Pattern: "author-et-al-year-title" or "author1-author2-year-title"
            parts = name_without_ext.split('-')
            
            if len(parts) >= 3:
                # Look for year pattern (e.g., 2015, 2020, etc.)
                year_idx = None
                for i, part in enumerate(parts):
                    if part.isdigit() and len(part) == 4 and 1900 <= int(part) <= 2030:
                        year_idx = i
                        break
                
                if year_idx is not None and year_idx > 0:
                    # Authors are before the year
                    author_parts = parts[:year_idx]
                    
                    # Handle "et-al" pattern
                    if len(author_parts) >= 2 and author_parts[1] == 'et' and len(author_parts) > 2 and author_parts[2] == 'al':
                        # Format: "lastname-et-al"
                        return [author_parts[0].title()]
                    else:
                        # Multiple authors separated by hyphens
                        authors = []
                        for author_part in author_parts:
                            if author_part.lower() not in ['et', 'al', 'and']:
                                authors.append(author_part.title())
                        return authors[:3]  # Limit to first 3 authors
            
            # Fallback: try to extract first part as author
            if parts:
                return [parts[0].title()]
                
        except Exception as e:
            print(f"Error extracting authors from filename {pdf_name}: {e}")
        
        return []
    
    def _extract_title_from_filename(self, pdf_name: str) -> str:
        """Extract title from PDF filename"""
        try:
            # Remove file extension
            name_without_ext = pdf_name.replace('.pdf', '').replace('.PDF', '')
            
            # Common patterns for title extraction
            parts = name_without_ext.split('-')
            
            if len(parts) >= 3:
                # Look for year pattern
                year_idx = None
                for i, part in enumerate(parts):
                    if part.isdigit() and len(part) == 4 and 1900 <= int(part) <= 2030:
                        year_idx = i
                        break
                
                if year_idx is not None and year_idx < len(parts) - 1:
                    # Title is after the year
                    title_parts = parts[year_idx + 1:]
                    title = ' '.join(word.title() for word in title_parts)
                    return title
            
            # Fallback: use the whole filename as title
            return ' '.join(word.title() for word in parts)
                
        except Exception as e:
            print(f"Error extracting title from filename {pdf_name}: {e}")
        
        return pdf_name
    
    def track_chunk_citation(self, chunk_content: str, chunk_metadata: dict) -> ChunkCitation:
        """Track a chunk citation from retrieved content"""
        chunk_id = chunk_metadata.get('chunk_id', str(uuid.uuid4()))
        
        # Extract authors from filename if not provided in metadata
        provided_authors = chunk_metadata.get('authors', [])
        pdf_name = chunk_metadata.get('source', 'unknown.pdf')
        
        if not provided_authors:
            provided_authors = self._extract_authors_from_filename(pdf_name)
        
        # Create ChunkCitation from metadata
        chunk_citation = ChunkCitation(
            chunk_id=chunk_id,
            pdf_name=pdf_name,
            page_number=chunk_metadata.get('page', 1),
            text_excerpt=chunk_content[:200] + '...' if len(chunk_content) > 200 else chunk_content,
            section=chunk_metadata.get('section'),
            authors=provided_authors,
            publication_date=chunk_metadata.get('publication_date'),
            publisher=chunk_metadata.get('publisher'),
            doi=chunk_metadata.get('doi'),
            journal=chunk_metadata.get('journal')
        )
        
        # Add to registry
        self.add_citation(chunk_citation)
        return chunk_citation
    
    def create_inline_citation(self, chunk_id: str, citation_number: int, text_content: str, source_metadata: dict) -> InlineCitation:
        """Create an inline citation directly"""
        # Create ChunkCitation
        chunk_citation = ChunkCitation(
            chunk_id=chunk_id,
            pdf_name=source_metadata.get('pdf_name', source_metadata.get('source', 'unknown.pdf')),
            page_number=source_metadata.get('page', 1),
            text_excerpt=text_content[:200] + '...' if len(text_content) > 200 else text_content,
            section=source_metadata.get('section'),
            authors=source_metadata.get('authors', []),
            publication_date=source_metadata.get('publication_date'),
            publisher=source_metadata.get('publisher'),
            doi=source_metadata.get('doi'),
            journal=source_metadata.get('journal')
        )
        
        # Check if citation already exists
        if chunk_id in self.citations:
            # Find existing inline citation
            for inline_cite in self.inline_citations:
                if inline_cite.chunk_citation.chunk_id == chunk_id:
                    return inline_cite
        
        # Add citation to registry
        self.citations[chunk_id] = chunk_citation
        
        # Create inline citation
        inline_citation = InlineCitation(
            citation_number=citation_number,
            chunk_citation=chunk_citation,
            marker_text=f"[{citation_number}]",
            hover_content=self._generate_hover_content(chunk_citation),
            anchor_id=f"cite-{citation_number}"
        )
        
        self.inline_citations.append(inline_citation)
        return inline_citation


class CitationConfig(BaseModel):
    """Configuration for citation tracking"""
    citation_style: CitationStyle = Field(default=CitationStyle.APA, description="Default citation style")
    auto_generate_references: bool = Field(default=True, description="Auto-generate references section")
    show_inline_citations: bool = Field(default=True, description="Show inline citation markers")
    enable_hover_tooltips: bool = Field(default=True, description="Enable hover tooltips")
    custom_metadata_fields: List[str] = Field(default_factory=list, description="Additional metadata fields")
    include_doi: bool = Field(default=True, description="Include DOI when available")
    include_url: bool = Field(default=True, description="Include URL when available")
