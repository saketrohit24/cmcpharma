"""
Document management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.document import StoredDocument, DocumentCreate, DocumentUpdate, DocumentSearch
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_service() -> DocumentService:
    """Dependency to get document service instance"""
    return DocumentService()


@router.get("", response_model=List[StoredDocument])
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    document_service: DocumentService = Depends(get_document_service)
):
    """Get all documents with optional filtering"""
    try:
        return await document_service.get_documents(
            skip=skip,
            limit=limit,
            status=status,
            tag=tag
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=StoredDocument)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get a specific document by ID"""
    try:
        document = await document_service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=StoredDocument)
async def create_document(
    document_data: DocumentCreate,
    document_service: DocumentService = Depends(get_document_service)
):
    """Create a new document"""
    try:
        return await document_service.create_document(document_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{document_id}", response_model=StoredDocument)
async def update_document(
    document_id: str,
    document_data: DocumentUpdate,
    document_service: DocumentService = Depends(get_document_service)
):
    """Update an existing document"""
    try:
        document = await document_service.update_document(document_id, document_data)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Delete a document"""
    try:
        success = await document_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[StoredDocument])
async def search_documents(
    search_query: DocumentSearch,
    document_service: DocumentService = Depends(get_document_service)
):
    """Search documents by content and metadata"""
    try:
        return await document_service.search_documents(search_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/versions")
async def get_document_versions(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get all versions of a document"""
    try:
        versions = await document_service.get_document_versions(document_id)
        return {"document_id": document_id, "versions": versions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/duplicate", response_model=StoredDocument)
async def duplicate_document(
    document_id: str,
    new_title: Optional[str] = None,
    document_service: DocumentService = Depends(get_document_service)
):
    """Create a duplicate of an existing document"""
    try:
        document = await document_service.duplicate_document(document_id, new_title)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/archive")
async def archive_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Archive a document"""
    try:
        success = await document_service.archive_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document archived successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/restore")
async def restore_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Restore an archived document"""
    try:
        success = await document_service.restore_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document restored successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
