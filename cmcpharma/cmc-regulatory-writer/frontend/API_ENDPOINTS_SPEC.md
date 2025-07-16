# FastAPI Endpoints Specification for CMC Regulatory Writer

## 🌐 **Complete API Endpoints List**

### **1. Template Management**

```python
# GET /api/templates
# Returns: List[Template]
# Description: Get all available templates

# POST /api/templates  
# Body: Template (without id, timestamps)
# Returns: Template
# Description: Create new template

# GET /api/templates/{template_id}
# Returns: Template
# Description: Get specific template

# PUT /api/templates/{template_id}
# Body: Template
# Returns: Template  
# Description: Update template

# DELETE /api/templates/{template_id}
# Returns: {"message": "Template deleted"}
# Description: Delete template

# POST /api/templates/upload
# Body: multipart/form-data (file)
# Returns: Template
# Description: Upload template file and parse TOC
```

### **2. Document Generation (CORE LLM)**

```python
# POST /api/generate-document
# Body: {
#   "template_id": "string",
#   "llm_config": {
#     "provider": "openai|claude|local",
#     "model": "gpt-4|claude-3",
#     "temperature": 0.7,
#     "max_tokens": 4000
#   },
#   "generation_options": {
#     "include_citations": true,
#     "regulatory_focus": "ICH|FDA|EMA",
#     "content_length": "standard|detailed|concise"
#   }
# }
# Returns: GeneratedDocument
# Description: Generate document using LLM from template

# GET /api/generation/status/{generation_id}
# Returns: {"status": "processing|completed|failed", "progress": 0-100}
# Description: Check generation progress (for async)

# POST /api/generate-section
# Body: {
#   "section_title": "string",
#   "context": "string",
#   "template_context": "string"
# }
# Returns: GeneratedSection
# Description: Generate individual section
```

### **3. Document Management**

```python
# GET /api/documents
# Query params: ?status=draft|published&limit=10&offset=0
# Returns: List[StoredDocument]
# Description: Get user documents with pagination

# POST /api/documents
# Body: StoredDocument (without id, timestamps)
# Returns: StoredDocument
# Description: Save new document

# GET /api/documents/{document_id}
# Returns: StoredDocument
# Description: Get specific document

# PUT /api/documents/{document_id}
# Body: StoredDocument
# Returns: StoredDocument
# Description: Update document

# DELETE /api/documents/{document_id}
# Returns: {"message": "Document deleted"}
# Description: Delete document

# GET /api/documents/{document_id}/versions
# Returns: List[DocumentVersion]
# Description: Get document version history

# POST /api/documents/{document_id}/duplicate
# Returns: StoredDocument
# Description: Create copy of document
```

### **4. File Management**

```python
# GET /api/files
# Query params: ?path=/folder&type=file|folder
# Returns: List[FileItem]
# Description: Get files and folders

# POST /api/files/upload
# Body: multipart/form-data
# Fields: file, path?, metadata?
# Returns: FileItem
# Description: Upload single file

# POST /api/files/upload-multiple
# Body: multipart/form-data (multiple files)
# Returns: List[FileItem]
# Description: Upload multiple files

# GET /api/files/{file_id}
# Returns: FileItem metadata
# Description: Get file information

# GET /api/files/{file_id}/download
# Returns: File stream
# Description: Download file

# DELETE /api/files/{file_id}
# Returns: {"message": "File deleted"}
# Description: Delete file

# POST /api/files/create-folder
# Body: {"name": "string", "parent_path": "string"}
# Returns: FileItem
# Description: Create new folder

# PUT /api/files/{file_id}/move
# Body: {"new_path": "string"}
# Returns: FileItem
# Description: Move file/folder

# GET /api/files/{file_id}/parse-content
# Returns: {"content": "string", "toc": List[TOCItem]}
# Description: Parse file content for templates
```

### **5. Export System**

```python
# POST /api/export
# Body: {
#   "document_id": "string",
#   "format": "pdf|docx|html|txt",
#   "options": ExportOptions
# }
# Returns: File stream or {"download_url": "string"}
# Description: Export document to specified format

# GET /api/export/formats
# Returns: List[{"format": "string", "name": "string", "description": "string"}]
# Description: Get available export formats

# POST /api/export/preview
# Body: {"document_id": "string", "format": "html"}
# Returns: {"html_content": "string"}
# Description: Preview document before export

# GET /api/export/status/{export_id}
# Returns: {"status": "processing|completed|failed", "download_url": "string?"}
# Description: Check export progress (for large files)
```

### **6. Citation Management**

```python
# GET /api/citations
# Query params: ?document_id=string&source=string
# Returns: List[Citation]
# Description: Get citations

# POST /api/citations
# Body: Citation (without id)
# Returns: Citation
# Description: Create citation

# PUT /api/citations/{citation_id}
# Body: Citation
# Returns: Citation
# Description: Update citation

# DELETE /api/citations/{citation_id}
# Returns: {"message": "Citation deleted"}
# Description: Delete citation

# POST /api/citations/auto-generate
# Body: {"content": "string", "context": "regulatory_type"}
# Returns: List[Citation]
# Description: Auto-generate citations for content

# GET /api/citations/search
# Query params: ?query=string&type=regulatory|academic
# Returns: List[Citation]
# Description: Search citation database
```

### **7. AI Chat System**

```python
# POST /api/chat/sessions
# Body: {"document_id": "string?", "initial_message": "string?"}
# Returns: ChatSession
# Description: Create new chat session

# GET /api/chat/sessions/{session_id}
# Returns: ChatSession
# Description: Get chat session

# POST /api/chat/sessions/{session_id}/messages
# Body: {"message": "string", "context": {...}}
# Returns: ChatMessage (assistant response)
# Description: Send message and get AI response

# DELETE /api/chat/sessions/{session_id}
# Returns: {"message": "Session deleted"}
# Description: Delete chat session

# POST /api/chat/suggest-edits
# Body: {"content": "string", "section_type": "string"}
# Returns: {"suggestions": List[string]}
# Description: Get AI suggestions for content improvement

# POST /api/chat/explain-section
# Body: {"section_id": "string", "document_id": "string"}
# Returns: {"explanation": "string"}
# Description: Get AI explanation of document section
```

### **8. Search & Analytics**

```python
# GET /api/search
# Query params: ?q=string&type=documents|templates|citations&limit=10
# Returns: {"results": List[SearchResult], "total": int}
# Description: Search across all content

# GET /api/analytics/usage
# Returns: {"documents_created": int, "templates_used": {...}, "generation_stats": {...}}
# Description: Get usage analytics

# GET /api/analytics/documents/{document_id}/stats
# Returns: {"word_count": int, "sections": int, "citations": int, "last_edited": datetime}
# Description: Get document statistics
```

### **9. Configuration & Settings**

```python
# GET /api/config/llm-providers
# Returns: List[{"name": "string", "models": List[string]}]
# Description: Get available LLM providers

# POST /api/config/llm
# Body: {"provider": "string", "api_key": "string", "model": "string"}
# Returns: {"status": "configured", "test_result": "success|failed"}
# Description: Configure LLM settings

# GET /api/config/export-templates
# Returns: List[ExportTemplate]
# Description: Get export format templates

# POST /api/config/backup
# Returns: {"backup_url": "string"}
# Description: Create data backup
```

## 🔐 **Authentication Endpoints (Optional)**

```python
# POST /api/auth/login
# Body: {"username": "string", "password": "string"}
# Returns: {"access_token": "string", "user": User}

# POST /api/auth/refresh
# Body: {"refresh_token": "string"}
# Returns: {"access_token": "string"}

# POST /api/auth/logout
# Headers: Authorization: Bearer <token>
# Returns: {"message": "Logged out"}
```

## 📊 **Frontend Service Integration**

```typescript
// Update these frontend service calls to use your FastAPI endpoints:

// templateGeneration.ts
const response = await fetch(`${API_BASE}/generate-document`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ template_id: template.id })
});

// storage.ts  
const response = await fetch(`${API_BASE}/documents`, {
  method: 'GET',
  headers: { 'Authorization': `Bearer ${token}` }
});

// Export functionality
const response = await fetch(`${API_BASE}/export`, {
  method: 'POST',
  body: JSON.stringify({ document_id, format: 'pdf' })
});
```

## 🎯 **Priority Implementation Order**

1. **Templates** (`/api/templates/*`) - Foundation
2. **Generation** (`/api/generate-document`) - Core LLM feature  
3. **Documents** (`/api/documents/*`) - Save/load functionality
4. **Export** (`/api/export`) - Output generation
5. **Files** (`/api/files/*`) - File management
6. **Citations** (`/api/citations/*`) - Reference system
7. **Chat** (`/api/chat/*`) - AI assistance
8. **Search** (`/api/search`) - Content discovery

This complete API specification matches your frontend perfectly! 🚀
