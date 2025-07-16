"""
Document service for managing stored documents
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models.document import StoredDocument, DocumentCreate, DocumentUpdate, DocumentSearch


class DocumentService:
    """
    Service for handling document storage, retrieval, and management operations
    """

    def __init__(self):
        """Initialize document service"""
        # In-memory storage for documents (replace with database in production)
        self.documents_storage: Dict[str, StoredDocument] = {}
        self._initialize_sample_documents()

    async def get_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[StoredDocument]:
        """Get documents with optional filtering and pagination"""
        documents = list(self.documents_storage.values())
        
        # Apply filters
        if status:
            documents = [d for d in documents if d.status == status]
        
        if tag:
            documents = [d for d in documents if tag in d.tags]
        
        # Apply pagination
        return documents[skip:skip + limit]

    async def get_document_by_id(self, document_id: str) -> Optional[StoredDocument]:
        """Get a specific document by ID"""
        return self.documents_storage.get(document_id)

    async def create_document(self, document_data: DocumentCreate) -> StoredDocument:
        """Create a new document"""
        document = StoredDocument(
            id=str(uuid.uuid4()),
            title=document_data.title,
            content=document_data.content,
            template_id=document_data.template_id,
            created_at=datetime.now(),
            last_modified=datetime.now(),
            version=1,
            status=document_data.status or 'draft',
            tags=document_data.tags or []
        )
        
        self.documents_storage[document.id] = document
        return document

    async def update_document(self, document_id: str, document_data: DocumentUpdate) -> Optional[StoredDocument]:
        """Update an existing document"""
        document = self.documents_storage.get(document_id)
        if not document:
            return None
        
        # Update fields if provided
        if document_data.title is not None:
            document.title = document_data.title
        if document_data.content is not None:
            document.content = document_data.content
        if document_data.status is not None:
            document.status = document_data.status
        if document_data.tags is not None:
            document.tags = document_data.tags
        
        # Increment version and update timestamp
        document.version += 1
        document.last_modified = datetime.now()
        
        self.documents_storage[document_id] = document
        return document

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        if document_id in self.documents_storage:
            del self.documents_storage[document_id]
            return True
        return False

    async def search_documents(self, search_query: DocumentSearch) -> List[StoredDocument]:
        """Search documents by content and metadata"""
        documents = list(self.documents_storage.values())
        
        # Text search in title and content
        if search_query.query:
            query_lower = search_query.query.lower()
            documents = [
                d for d in documents
                if query_lower in d.title.lower() or query_lower in d.content.lower()
            ]
        
        # Filter by status
        if search_query.status:
            documents = [d for d in documents if d.status in search_query.status]
        
        # Filter by tags
        if search_query.tags:
            documents = [
                d for d in documents
                if any(tag in d.tags for tag in search_query.tags)
            ]
        
        # Filter by date range
        if search_query.created_after:
            documents = [d for d in documents if d.created_at >= search_query.created_after]
        
        if search_query.created_before:
            documents = [d for d in documents if d.created_at <= search_query.created_before]
        
        # Filter by template
        if search_query.template_id:
            documents = [d for d in documents if d.template_id == search_query.template_id]
        
        return documents

    async def get_document_versions(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a document"""
        # In a real implementation, this would query version history from database
        document = self.documents_storage.get(document_id)
        if not document:
            return []
        
        # Mock version history
        return [
            {
                "version": document.version,
                "created_at": document.last_modified.isoformat(),
                "status": document.status,
                "changes": "Current version"
            },
            {
                "version": document.version - 1,
                "created_at": document.created_at.isoformat(),
                "status": "draft",
                "changes": "Initial creation"
            }
        ]

    async def duplicate_document(self, document_id: str, new_title: Optional[str] = None) -> Optional[StoredDocument]:
        """Create a duplicate of an existing document"""
        original = self.documents_storage.get(document_id)
        if not original:
            return None
        
        # Create duplicate with new ID
        duplicate = StoredDocument(
            id=str(uuid.uuid4()),
            title=new_title or f"Copy of {original.title}",
            content=original.content,
            template_id=original.template_id,
            created_at=datetime.now(),
            last_modified=datetime.now(),
            version=1,
            status='draft',
            tags=original.tags.copy()
        )
        
        self.documents_storage[duplicate.id] = duplicate
        return duplicate

    async def archive_document(self, document_id: str) -> bool:
        """Archive a document"""
        document = self.documents_storage.get(document_id)
        if not document:
            return False
        
        document.status = 'archived'
        document.last_modified = datetime.now()
        self.documents_storage[document_id] = document
        return True

    async def restore_document(self, document_id: str) -> bool:
        """Restore an archived document"""
        document = self.documents_storage.get(document_id)
        if not document:
            return False
        
        document.status = 'draft'
        document.last_modified = datetime.now()
        self.documents_storage[document_id] = document
        return True

    async def get_document_stats(self) -> Dict[str, Any]:
        """Get document statistics"""
        documents = list(self.documents_storage.values())
        
        total_documents = len(documents)
        by_status = {}
        for doc in documents:
            by_status[doc.status] = by_status.get(doc.status, 0) + 1
        
        recent_documents = len([
            d for d in documents
            if (datetime.now() - d.last_modified).days <= 7
        ])
        
        return {
            "total_documents": total_documents,
            "by_status": by_status,
            "recent_activity": recent_documents,
            "average_length": sum(len(d.content) for d in documents) / total_documents if total_documents > 0 else 0
        }

    def _initialize_sample_documents(self):
        """Initialize some sample documents for testing"""
        # Sample CMC document
        sample_doc1 = StoredDocument(
            id="doc_001",
            title="CMC Section 2.1 - Drug Substance General Information",
            content="""# 2.1 Drug Substance General Information

## 2.1.1 Nomenclature
The drug substance is known by the following names:
- Generic name: Example Drug
- Chemical name: (2S,3R)-2-amino-3-hydroxybutanoic acid
- CAS Registry Number: 123-45-6

## 2.1.2 Structure
The molecular formula is C4H9NO3 with a molecular weight of 119.12 g/mol.

## 2.1.3 General Properties
The drug substance is a white to off-white crystalline powder that is freely soluble in water and slightly soluble in ethanol.""",
            template_id="template_cmc_001",
            created_at=datetime.now(),
            last_modified=datetime.now(),
            version=1,
            status="published",
            tags=["CMC", "Drug Substance", "Regulatory"]
        )
        
        # Sample Quality document
        sample_doc2 = StoredDocument(
            id="doc_002",
            title="Quality Assessment Summary",
            content="""# Quality Assessment Summary

## Executive Summary
This document presents the quality assessment for the proposed drug product, including analytical methods validation and stability data review.

## Key Findings
- All analytical methods meet ICH Q2 requirements
- Stability data supports proposed shelf life
- Manufacturing process is well-controlled

## Recommendations
The quality profile supports regulatory approval.""",
            template_id="template_quality_001",
            created_at=datetime.now(),
            last_modified=datetime.now(),
            version=2,
            status="draft",
            tags=["Quality", "Assessment", "ICH"]
        )
        
        self.documents_storage[sample_doc1.id] = sample_doc1
        self.documents_storage[sample_doc2.id] = sample_doc2
