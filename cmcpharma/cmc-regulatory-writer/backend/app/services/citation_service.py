"""
Citation service for managing citations and references
"""
import uuid
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models.citation import Citation, CitationCreate, CitationUpdate, CitationSearch


class CitationService:
    """
    Service for handling citation management, extraction, and formatting
    """

    def __init__(self):
        """Initialize citation service"""
        # In-memory storage for citations (replace with database in production)
        self.citations_storage: Dict[int, Citation] = {}
        self.citation_counter = 1
        
        # Initialize with sample citations
        self._initialize_sample_citations()

    async def get_citations(self, skip: int = 0, limit: int = 100) -> List[Citation]:
        """Get all citations with pagination"""
        citations = list(self.citations_storage.values())
        return citations[skip:skip + limit]

    async def get_citation_by_id(self, citation_id: int) -> Optional[Citation]:
        """Get a specific citation by ID"""
        return self.citations_storage.get(citation_id)

    async def create_citation(self, citation_data: CitationCreate) -> Citation:
        """Create a new citation"""
        citation = Citation(
            id=self.citation_counter,
            text=citation_data.text,
            source=citation_data.source,
            page=citation_data.page,
            source_file_id=citation_data.source_file_id,
            url=citation_data.url,
            doi=citation_data.doi,
            authors=citation_data.authors or [],
            publication_date=citation_data.publication_date,
            journal=citation_data.journal,
            volume=citation_data.volume,
            issue=citation_data.issue,
            pages=citation_data.pages,
            isbn=citation_data.isbn,
            publisher=citation_data.publisher,
            citation_style=citation_data.citation_style or "APA",
            tags=citation_data.tags or [],
            notes=citation_data.notes,
            created_at=datetime.now(),
            last_modified=datetime.now()
        )
        
        self.citations_storage[self.citation_counter] = citation
        self.citation_counter += 1
        return citation

    async def update_citation(self, citation_id: int, citation_data: CitationUpdate) -> Optional[Citation]:
        """Update an existing citation"""
        citation = self.citations_storage.get(citation_id)
        if not citation:
            return None
        
        # Update fields if provided
        if citation_data.text is not None:
            citation.text = citation_data.text
        if citation_data.source is not None:
            citation.source = citation_data.source
        if citation_data.page is not None:
            citation.page = citation_data.page
        if citation_data.source_file_id is not None:
            citation.source_file_id = citation_data.source_file_id
        if citation_data.url is not None:
            citation.url = citation_data.url
        if citation_data.doi is not None:
            citation.doi = citation_data.doi
        if citation_data.authors is not None:
            citation.authors = citation_data.authors
        if citation_data.publication_date is not None:
            citation.publication_date = citation_data.publication_date
        if citation_data.journal is not None:
            citation.journal = citation_data.journal
        if citation_data.volume is not None:
            citation.volume = citation_data.volume
        if citation_data.issue is not None:
            citation.issue = citation_data.issue
        if citation_data.pages is not None:
            citation.pages = citation_data.pages
        if citation_data.isbn is not None:
            citation.isbn = citation_data.isbn
        if citation_data.publisher is not None:
            citation.publisher = citation_data.publisher
        if citation_data.citation_style is not None:
            citation.citation_style = citation_data.citation_style
        if citation_data.tags is not None:
            citation.tags = citation_data.tags
        if citation_data.notes is not None:
            citation.notes = citation_data.notes
        
        citation.last_modified = datetime.now()
        self.citations_storage[citation_id] = citation
        return citation

    async def delete_citation(self, citation_id: int) -> bool:
        """Delete a citation"""
        if citation_id in self.citations_storage:
            del self.citations_storage[citation_id]
            return True
        return False

    async def search_citations(self, search_query: CitationSearch) -> List[Citation]:
        """Search citations by various criteria"""
        citations = list(self.citations_storage.values())
        
        # Text search in text and source
        if search_query.query:
            query_lower = search_query.query.lower()
            citations = [
                c for c in citations
                if query_lower in c.text.lower() or 
                   query_lower in c.source.lower() or
                   (c.journal and query_lower in c.journal.lower())
            ]
        
        # Filter by authors
        if search_query.authors:
            citations = [
                c for c in citations
                if c.authors and any(author in c.authors for author in search_query.authors)
            ]
        
        # Filter by journal
        if search_query.journal:
            citations = [
                c for c in citations
                if c.journal and search_query.journal.lower() in c.journal.lower()
            ]
        
        # Filter by publication date range
        if search_query.date_from:
            citations = [
                c for c in citations
                if c.publication_date and c.publication_date >= search_query.date_from
            ]
        
        if search_query.date_to:
            citations = [
                c for c in citations
                if c.publication_date and c.publication_date <= search_query.date_to
            ]
        
        # Filter by tags
        if search_query.tags:
            citations = [
                c for c in citations
                if any(tag in c.tags for tag in search_query.tags)
            ]
        
        # Filter by citation style
        if search_query.citation_style:
            citations = [
                c for c in citations
                if c.citation_style == search_query.citation_style
            ]
        
        return citations

    async def extract_citations_from_text(self, text: str, source_file_id: Optional[str] = None) -> List[Citation]:
        """Extract citations from text content using pattern matching"""
        citations = []
        
        # TODO: Implement sophisticated citation extraction
        # This could include:
        # - DOI pattern matching
        # - Author-date patterns
        # - URL extraction
        # - Journal reference patterns
        # - Machine learning-based extraction
        
        # Simple pattern matching for now
        patterns = {
            "doi": r"doi:\s*(10\.\d+/[^\s]+)",
            "url": r"https?://[^\s]+",
            "author_year": r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\((\d{4})\)",
            "journal": r"([A-Z][^.]+\.)[\s]*(\d{4})[^.]*\.[\s]*([^,]+,)"
        }
        
        # Extract DOIs
        doi_matches = re.finditer(patterns["doi"], text, re.IGNORECASE)
        for match in doi_matches:
            doi = match.group(1)
            citation = Citation(
                id=self.citation_counter,
                text=f"DOI reference: {doi}",
                source="Extracted from text",
                page=1,
                source_file_id=source_file_id,
                doi=doi,
                citation_style="APA",
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
            citations.append(citation)
            self.citations_storage[self.citation_counter] = citation
            self.citation_counter += 1
        
        # Extract URLs
        url_matches = re.finditer(patterns["url"], text)
        for match in url_matches:
            url = match.group(0)
            citation = Citation(
                id=self.citation_counter,
                text=f"Web reference: {url}",
                source="Extracted from text",
                page=1,
                source_file_id=source_file_id,
                url=url,
                citation_style="APA",
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
            citations.append(citation)
            self.citations_storage[self.citation_counter] = citation
            self.citation_counter += 1
        
        return citations

    async def format_citation(self, citation: Citation, style: str = "APA") -> str:
        """Format a citation in specified style"""
        if style == "APA":
            return await self._format_apa(citation)
        elif style == "MLA":
            return await self._format_mla(citation)
        elif style == "Chicago":
            return await self._format_chicago(citation)
        elif style == "IEEE":
            return await self._format_ieee(citation)
        elif style == "Vancouver":
            return await self._format_vancouver(citation)
        else:
            return await self._format_apa(citation)  # Default to APA

    async def import_citations(self, import_data: str, format: str = "bibtex") -> List[Citation]:
        """Import citations from external formats"""
        citations = []
        
        # TODO: Implement actual import parsing for different formats
        # - BibTeX parsing
        # - EndNote format
        # - RIS format
        # - JSON format
        
        # Mock implementation
        if format == "bibtex":
            # Simple BibTeX-like parsing
            entries = import_data.split("@")
            for entry in entries[1:]:  # Skip first empty split
                citation = await self._parse_bibtex_entry(entry)
                if citation:
                    citations.append(citation)
        
        return citations

    async def export_citations(self, format: str = "bibtex", citation_ids: Optional[List[int]] = None) -> str:
        """Export citations to external formats"""
        # Get citations to export
        if citation_ids:
            citations = [self.citations_storage.get(cid) for cid in citation_ids if cid in self.citations_storage]
        else:
            citations = list(self.citations_storage.values())
        
        if format == "bibtex":
            return await self._export_bibtex(citations)
        elif format == "json":
            return await self._export_json(citations)
        else:
            return await self._export_bibtex(citations)  # Default to BibTeX

    # Private formatting methods

    async def _format_apa(self, citation: Citation) -> str:
        """Format citation in APA style"""
        parts = []
        
        # Authors
        if citation.authors:
            if len(citation.authors) == 1:
                parts.append(citation.authors[0])
            elif len(citation.authors) == 2:
                parts.append(f"{citation.authors[0]} & {citation.authors[1]}")
            else:
                parts.append(f"{citation.authors[0]} et al.")
        
        # Year
        if citation.publication_date:
            parts.append(f"({citation.publication_date.year})")
        
        # Title (implied from source)
        parts.append(citation.source)
        
        # Journal details
        if citation.journal:
            journal_part = citation.journal
            if citation.volume:
                journal_part += f", {citation.volume}"
            if citation.issue:
                journal_part += f"({citation.issue})"
            if citation.pages:
                journal_part += f", {citation.pages}"
            parts.append(journal_part)
        
        # DOI
        if citation.doi:
            parts.append(f"https://doi.org/{citation.doi}")
        
        return ". ".join(parts) + "."

    async def _format_mla(self, citation: Citation) -> str:
        """Format citation in MLA style"""
        # TODO: Implement MLA formatting
        return f"MLA format for: {citation.source}"

    async def _format_chicago(self, citation: Citation) -> str:
        """Format citation in Chicago style"""
        # TODO: Implement Chicago formatting
        return f"Chicago format for: {citation.source}"

    async def _format_ieee(self, citation: Citation) -> str:
        """Format citation in IEEE style"""
        # TODO: Implement IEEE formatting
        return f"IEEE format for: {citation.source}"

    async def _format_vancouver(self, citation: Citation) -> str:
        """Format citation in Vancouver style"""
        # TODO: Implement Vancouver formatting
        return f"Vancouver format for: {citation.source}"

    async def _parse_bibtex_entry(self, entry: str) -> Optional[Citation]:
        """Parse a single BibTeX entry"""
        # TODO: Implement proper BibTeX parsing
        # For now, create a mock citation
        if "title" in entry.lower():
            citation = Citation(
                id=self.citation_counter,
                text="Imported from BibTeX",
                source="BibTeX import",
                page=1,
                citation_style="APA",
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
            self.citations_storage[self.citation_counter] = citation
            self.citation_counter += 1
            return citation
        return None

    async def _export_bibtex(self, citations: List[Citation]) -> str:
        """Export citations to BibTeX format"""
        bibtex_entries = []
        
        for citation in citations:
            entry = f"@article{{citation_{citation.id},\n"
            entry += f"  title={{{citation.source}}},\n"
            if citation.authors:
                entry += f"  author={{{' and '.join(citation.authors)}}},\n"
            if citation.journal:
                entry += f"  journal={{{citation.journal}}},\n"
            if citation.volume:
                entry += f"  volume={{{citation.volume}}},\n"
            if citation.issue:
                entry += f"  number={{{citation.issue}}},\n"
            if citation.pages:
                entry += f"  pages={{{citation.pages}}},\n"
            if citation.publication_date:
                entry += f"  year={{{citation.publication_date.year}}},\n"
            if citation.doi:
                entry += f"  doi={{{citation.doi}}},\n"
            entry += "}\n"
            bibtex_entries.append(entry)
        
        return "\n".join(bibtex_entries)

    async def _export_json(self, citations: List[Citation]) -> str:
        """Export citations to JSON format"""
        import json
        
        citation_dicts = []
        for citation in citations:
            citation_dict = {
                "id": citation.id,
                "text": citation.text,
                "source": citation.source,
                "page": citation.page,
                "authors": citation.authors,
                "journal": citation.journal,
                "volume": citation.volume,
                "issue": citation.issue,
                "pages": citation.pages,
                "publication_date": citation.publication_date.isoformat() if citation.publication_date else None,
                "doi": citation.doi,
                "url": citation.url,
                "citation_style": citation.citation_style
            }
            citation_dicts.append(citation_dict)
        
        return json.dumps(citation_dicts, indent=2)

    def _initialize_sample_citations(self):
        """Initialize sample citations for testing"""
        sample_citations = [
            Citation(
                id=1,
                text="Pharmaceutical development and quality assessment of drug products",
                source="ICH Q8(R2) Pharmaceutical Development",
                page=15,
                authors=["International Council for Harmonisation"],
                publication_date=datetime(2009, 8, 1),
                journal="ICH Guidelines",
                citation_style="APA",
                tags=["ICH", "Pharmaceutical Development", "Quality"],
                created_at=datetime.now(),
                last_modified=datetime.now()
            ),
            Citation(
                id=2,
                text="Quality risk management principles for pharmaceutical manufacturing",
                source="ICH Q9 Quality Risk Management",
                page=8,
                authors=["International Council for Harmonisation"],
                publication_date=datetime(2005, 11, 1),
                journal="ICH Guidelines",
                citation_style="APA",
                tags=["ICH", "Risk Management", "Quality"],
                created_at=datetime.now(),
                last_modified=datetime.now()
            ),
            Citation(
                id=3,
                text="Analytical method validation requirements and procedures",
                source="ICH Q2(R1) Validation of Analytical Procedures",
                page=12,
                authors=["International Council for Harmonisation"],
                publication_date=datetime(2005, 3, 1),
                journal="ICH Guidelines",
                citation_style="APA",
                tags=["ICH", "Analytical Methods", "Validation"],
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
        ]
        
        for citation in sample_citations:
            self.citations_storage[citation.id] = citation
        
        self.citation_counter = len(sample_citations) + 1
