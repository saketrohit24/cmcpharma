# History & Storage System

## Overview
The History & Storage system provides comprehensive document management capabilities for the CMC Regulatory Writer application, including local storage, session management, and document history tracking.

## Features

### 1. Document Storage
- **Local Storage**: Persistent storage of documents across browser sessions
- **Auto-save**: Automatic saving of document changes
- **Version Control**: Track document creation and update timestamps
- **Status Management**: Support for draft, review, and approved statuses

### 2. Document History View
- **Chronological Listing**: Documents sorted by last updated date
- **Status Filtering**: Filter documents by status (all, draft, review, approved)
- **Metadata Display**: Show creation date, update date, section count, and citation count
- **Quick Actions**: View, download, and delete documents

### 3. Session Management
- **Session Persistence**: Maintain current working state
- **Auto-recovery**: Restore last working session on app reload
- **Temporary Storage**: Use session storage for temporary data

## Components

### Storage Service (`src/services/storage.ts`)
```typescript
interface StoredDocument {
  id: string;
  title: string;
  docId: string;
  sections: DocumentSection[];
  citations: DocumentCitation[];
  createdAt: string;
  updatedAt: string;
  status: 'draft' | 'review' | 'approved';
}
```

#### Key Methods:
- `saveDocument(doc)` - Save or update a document
- `getDocuments()` - Retrieve all documents
- `getDocument(id)` - Get specific document by ID
- `deleteDocument(id)` - Remove a document
- `saveSession(data)` - Save current session
- `getSession()` - Retrieve session data

### DocumentHistory Component (`src/components/History/DocumentHistory.tsx`)
- Displays all stored documents in a filterable list
- Provides document management actions
- Shows document status and metadata
- Integrates with storage service

## Usage

### Navigation
Access the History view through:
- Header navigation tab (History)
- Quick access toolbar button (when in editor view)

### Document Management
1. **View Documents**: Click the eye icon to view document details
2. **Download**: Click the download icon to export documents
3. **Delete**: Click the trash icon to permanently remove documents
4. **Filter**: Use status buttons to filter by document status

### Sample Data
The system automatically generates sample documents for testing:
- Drug Substance Specification (approved)
- Manufacturing Process Description (review)
- Stability Study Protocol (draft)

## Integration

### With File Context
The storage system works alongside the unified file management system to provide complete document and file tracking.

### With Editor
Documents can be automatically saved from the editor with proper metadata and version tracking.

### With Navigation
The history view is fully integrated into the app's navigation system and supports the same responsive design principles.

## Local Storage Structure

### Documents: `cmc_documents`
```json
[
  {
    "id": "doc-1",
    "title": "Drug Substance Specification",
    "docId": "CMC-2024-001",
    "sections": [...],
    "citations": [...],
    "createdAt": "2024-01-15T10:30:00.000Z",
    "updatedAt": "2024-01-17T14:20:00.000Z",
    "status": "approved"
  }
]
```

### Files: `cmc_files`
```json
[
  {
    "id": "file-1",
    "documentId": "doc-1",
    "filename": "specification.pdf",
    "size": 1024000,
    "uploadedAt": "2024-01-15T10:30:00.000Z"
  }
]
```

### Session: `cmc_current_session` (sessionStorage)
```json
{
  "currentView": "editor",
  "documentId": "doc-1",
  "lastSaved": "2024-01-17T14:20:00.000Z"
}
```

## Browser Compatibility
- Uses localStorage for persistent data
- Uses sessionStorage for temporary data
- Compatible with all modern browsers
- Graceful degradation if storage is unavailable

## Future Enhancements
- Export/Import functionality
- Cloud storage integration
- Real-time collaboration
- Advanced search and filtering
- Document comparison and diff views
