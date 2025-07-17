# Document Generation Troubleshooting

This guide helps resolve issues with document generation not working when uploading templates and files.

## Current Issue Analysis

The document generation feature is not working properly when users upload templates and files and click "Create Document". Here's what we've identified:

### Problem Summary

1. **Frontend Issue**: The frontend `NewDocument` component creates a basic document structure but doesn't call the backend generation API
2. **Backend Issue**: There's a mismatch between method names in the RAG service
3. **Integration Issue**: The template generation service falls back to mock data instead of using real LLM generation

## Step-by-Step Debugging

### 1. Check Backend Server Status

First, ensure the backend is running:

```bash
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify it's working by visiting: http://localhost:8000/health

### 2. Test API Endpoints

Test the generation endpoint directly:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test file upload (replace with actual file)
curl -X POST -F "file=@your-document.pdf" http://localhost:8000/files/upload/test-session

# Test document generation (requires template JSON)
curl -X POST -H "Content-Type: application/json" -d '{"id":"test","name":"Test Template","description":"","toc":[{"id":"1","title":"Introduction","level":1}]}' http://localhost:8000/generation/generate/test-session
```

### 3. Check Environment Variables

Ensure your `backend/.env` file contains:

```bash
NVIDIA_API_KEY=nvapi-your-actual-key-here
LLM_API_KEY=nvapi-your-actual-key-here
```

### 4. Verify Frontend API Configuration

Check that the frontend is pointing to the correct backend URL. In `frontend/src/services/apiClient.ts`, ensure the base URL matches your backend:

```typescript
// Should be something like:
const BASE_URL = 'http://localhost:8000'
```

## Known Issues and Fixes

### Issue 1: RAG Service Method Mismatch

**Problem**: `GenerationService` calls `rag_service.retrieve_relevant_content()` but `RAGService` only has `get_relevant_chunks()`

**Fix**: Update the RAG service to include the missing method or update the generation service to use the correct method name.

### Issue 2: Frontend Not Using Backend API

**Problem**: The `NewDocument` component creates documents locally instead of calling the backend generation API.

**Fix**: Update the document creation flow to use the `backendApi.generateDocument()` method.

### Issue 3: Template Generation Service Fallback

**Problem**: The template generation service falls back to mock data when API calls fail.

**Fix**: Improve error handling and ensure API calls are successful.

## Testing Document Generation End-to-End

### 1. Upload Files

1. Open the frontend application
2. Navigate to the "Files" section
3. Upload one or more PDF documents
4. Verify files appear in the file list

### 2. Create Template

1. Navigate to the "Templates" section
2. Create a new template with sections like:
   ```
   1. Introduction
   2. Manufacturing Process
   3. Quality Control
   4. Stability Data
   5. Conclusion
   ```

### 3. Generate Document

1. Select the template
2. Click "Generate Document" 
3. Wait for the LLM to process each section
4. Verify that:
   - Each section has AI-generated content
   - References are included where appropriate
   - The document structure matches the template

## Expected Behavior

When document generation works correctly:

1. **File Upload**: PDFs are uploaded to the backend and stored in session directories
2. **Template Processing**: Templates are parsed into table-of-contents structures
3. **RAG Processing**: Uploaded files are processed and embedded for semantic search
4. **Section Generation**: Each template section is generated using:
   - LLM (meta/llama-4-scout-17b-16e-instruct)
   - RAG-retrieved content from uploaded files
   - Professional regulatory writing prompts
5. **Reference Integration**: Generated sections include references to source documents
6. **Frontend Display**: The generated document is displayed with:
   - Document title
   - Expandable sections
   - Source count indicators
   - Reference citations

## Debug Commands

### Check Backend Logs

```bash
# If running in background, check logs
tail -f backend.log

# Or run in foreground to see real-time logs
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Check Frontend Console

1. Open browser developer tools (F12)
2. Check Console tab for JavaScript errors
3. Check Network tab for failed API requests
4. Look for any 404, 500, or CORS errors

### Test Individual Components

```bash
# Test file manager
ls -la backend/persistent_uploads/

# Test template parsing
# Use the /docs endpoint to test template creation

# Test RAG service
# Upload a file and try the generation endpoint
```

## Next Steps

If you're still experiencing issues:

1. Check the specific error messages in both frontend and backend logs
2. Verify all dependencies are installed correctly
3. Test each API endpoint individually using the Swagger UI at http://localhost:8000/docs
4. Ensure the NVIDIA API key is valid and has sufficient quota

For additional help, check the main setup documentation in `docs/SETUP.md`.
