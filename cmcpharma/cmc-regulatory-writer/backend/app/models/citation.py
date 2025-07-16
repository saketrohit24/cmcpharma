"""
Pydantic models for citation management
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation model for document references"""
    id: int = Field(..., description="Unique citation identifier")
    text: str = Field(..., min_length=1, description="Citation text")
    source: str = Field(..., min_length=1, description="Citation source")
    page: int = Field(..., ge=1, description="Page number in source document")
    source_file_id: Optional[str] = Field(None, description="ID of the source file")
    url: Optional[str] = Field(None, description="URL reference")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    authors: Optional[List[str]] = Field(None, description="List of authors")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    journal: Optional[str] = Field(None, description="Journal or publication name")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    pages: Optional[str] = Field(None, description="Page range")
    isbn: Optional[str] = Field(None, description="ISBN for books")
    publisher: Optional[str] = Field(None, description="Publisher name")
    citation_style: Optional[str] = Field(default='APA', description="Citation format style")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    last_modified: datetime = Field(default_factory=datetime.now, description="Last modification timestamp")


class CitationCreate(BaseModel):
    """Model for creating a new citation"""
    text: str = Field(..., min_length=1, description="Citation text")
    source: str = Field(..., min_length=1, description="Citation source")
    page: int = Field(..., ge=1, description="Page number in source document")
    source_file_id: Optional[str] = Field(None, description="ID of the source file")
    url: Optional[str] = Field(None, description="URL reference")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    authors: Optional[List[str]] = Field(None, description="List of authors")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    journal: Optional[str] = Field(None, description="Journal or publication name")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    pages: Optional[str] = Field(None, description="Page range")
    isbn: Optional[str] = Field(None, description="ISBN for books")
    publisher: Optional[str] = Field(None, description="Publisher name")
    citation_style: Optional[str] = Field(default='APA', description="Citation format style")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    notes: Optional[str] = Field(None, description="Additional notes")


class CitationUpdate(BaseModel):
    """Model for updating an existing citation"""
    text: Optional[str] = Field(None, min_length=1, description="Citation text")
    source: Optional[str] = Field(None, min_length=1, description="Citation source")
    page: Optional[int] = Field(None, ge=1, description="Page number in source document")
    source_file_id: Optional[str] = Field(None, description="ID of the source file")
    url: Optional[str] = Field(None, description="URL reference")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    authors: Optional[List[str]] = Field(None, description="List of authors")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    journal: Optional[str] = Field(None, description="Journal or publication name")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    pages: Optional[str] = Field(None, description="Page range")
    isbn: Optional[str] = Field(None, description="ISBN for books")
    publisher: Optional[str] = Field(None, description="Publisher name")
    citation_style: Optional[str] = Field(None, description="Citation format style")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    notes: Optional[str] = Field(None, description="Additional notes")


class CitationSearch(BaseModel):
    """Model for citation search queries"""
    query: str = Field(..., min_length=1, description="Search query")
    authors: Optional[List[str]] = Field(None, description="Filter by authors")
    journal: Optional[str] = Field(None, description="Filter by journal")
    date_from: Optional[datetime] = Field(None, description="Filter by publication date from")
    date_to: Optional[datetime] = Field(None, description="Filter by publication date to")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    citation_style: Optional[str] = Field(None, description="Filter by citation style")


class CitationBatch(BaseModel):
    """Model for batch citation operations"""
    citation_ids: List[int] = Field(..., min_items=1, description="List of citation IDs")
    operation: str = Field(..., description="Batch operation type")
    parameters: Optional[dict] = Field(None, description="Operation parameters")


class CitationImport(BaseModel):
    """Model for importing citations from external sources"""
    source_type: str = Field(..., description="Import source type (BibTeX, EndNote, etc.)")
    data: str = Field(..., description="Citation data to import")
    merge_duplicates: bool = Field(default=True, description="Whether to merge duplicate citations")
    citation_style: str = Field(default='APA', description="Citation style to apply")
