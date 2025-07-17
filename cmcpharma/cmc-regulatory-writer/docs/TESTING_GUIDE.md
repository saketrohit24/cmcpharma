# Document Generation Testing Guide

## Current Status

✅ **Backend**: Running on http://localhost:8001  
✅ **Frontend**: Running on http://localhost:5174  
✅ **API Integration**: Fixed method mismatches and added missing models  

## Testing the Document Generation Flow

### Step 1: Test Basic Connection

1. **Open Frontend**: http://localhost:5174
2. **Check Backend Health**: Visit http://localhost:8001/api/health
   - Should return: `{"status":"ok","message":"API is healthy and running."}`
3. **Test API Docs**: Visit http://localhost:8001/docs
   - Should show Swagger UI with all endpoints

### Step 2: Upload Files

1. Navigate to the **Files** section in the frontend
2. Upload one or more PDF documents (sample regulatory documents work best)
3. Verify files appear in the file list
4. **Backend Check**: Files should be stored in `backend/persistent_uploads/{session_id}/`

### Step 3: Create Template

1. Navigate to the **Templates** section
2. Create a new template with sections like:
   ```
   1. Introduction
   1.1 General Information
   1.2 Scope and Purpose
   2. Manufacturing Process
   2.1 Process Description
   2.2 Critical Parameters
   3. Quality Control
   3.1 Testing Methods
   3.2 Specifications
   4. Stability Data
   4.1 Study Design
   4.2 Results Summary
   5. Conclusion
   ```
3. Save the template

### Step 4: Generate Document

1. **Select Template**: Choose the template you created
2. **Click Generate**: Use the generation button
3. **Expected Behavior**:
   - Loading indicator should appear
   - Each section should be generated using LLM
   - Content should reference uploaded files
   - Document should appear in editor view

### Step 5: Verify Generated Content

**Each generated section should contain**:
- Professional regulatory writing
- References to uploaded documents
- Appropriate technical content
- Source count indicators

**Example expected output for "Introduction" section**:
```
**Introduction**

This section provides comprehensive information regarding introduction. The data presented herein has been compiled in accordance with regulatory guidelines and industry best practices based on the uploaded documentation.

Key considerations include:
- Compliance with current regulatory standards as outlined in [Document 1]
- Adherence to quality management principles referenced in [Document 2]
- Implementation of risk-based approaches
- Maintenance of product quality throughout lifecycle

[Additional AI-generated content based on uploaded files...]

**Sources**: 3 documents referenced
```

## Testing Individual Components

### Test File Upload Endpoint

```bash
# Test file upload (replace with actual PDF file)
curl -X POST -F "file=@/path/to/your/document.pdf" \
  http://localhost:8001/api/files/upload/test-session-123
```

### Test Template Creation

```bash
# Create template via API
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Template",
    "description": "Test description",
    "toc_text": "1. Introduction\n2. Methods\n3. Results\n4. Conclusion"
  }' \
  http://localhost:8001/api/templates/parse
```

### Test Document Generation

```bash
# Generate document (requires files to be uploaded first)
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "id": "template-123",
    "name": "Test Template",
    "description": "Test description",
    "toc": [
      {"id": "1", "title": "Introduction", "level": 1},
      {"id": "2", "title": "Methods", "level": 1}
    ]
  }' \
  http://localhost:8001/api/generation/generate/test-session-123
```

## Common Issues and Solutions

### Frontend Shows "Thinking..." But No Progress

**Possible Causes**:
- Backend API URL mismatch
- CORS issues
- Missing environment variables

**Solutions**:
1. Check browser console for errors
2. Verify API calls in Network tab
3. Ensure backend is running and accessible

### Generated Sections Are Empty or Generic

**Possible Causes**:
- No files uploaded
- RAG service not finding relevant content
- NVIDIA API key issues

**Solutions**:
1. Upload relevant PDF documents first
2. Check backend logs for RAG processing errors
3. Verify NVIDIA API key in backend/.env

### Template Generation Fails

**Possible Causes**:
- Invalid template structure
- Backend API errors

**Solutions**:
1. Use simple section titles
2. Check backend logs for parsing errors
3. Try the template creation API directly

## Environment Variables Required

Ensure your `backend/.env` file contains:

```bash
NVIDIA_API_KEY=nvapi-your-key-here
LLM_API_KEY=nvapi-your-key-here
CORS_ORIGINS=["http://localhost:5174", "http://localhost:3000", "http://localhost:5173"]
```

## Expected Document Structure

The generated document should have:

```
📄 Document Title
  📑 Section 1: Title
     📝 AI-generated content with references
     🔗 Source count: X documents
  📑 Section 2: Title
     📝 AI-generated content with references
     🔗 Source count: X documents
  📑 Section 3: Title
     📝 AI-generated content with references
     🔗 Source count: X documents
```

## Success Criteria

✅ Files upload successfully  
✅ Templates are created and saved  
✅ Document generation starts and completes  
✅ Each section contains AI-generated content  
✅ References to uploaded files are included  
✅ Professional regulatory writing tone  
✅ Source counts are displayed  
✅ Document appears in editor view  

## Next Steps

If document generation is working:
1. Test with different types of regulatory documents
2. Try various template structures
3. Test the refinement feature
4. Export documents to PDF/DOCX
5. Test the chat functionality with document context

## Debug Mode

For detailed debugging:

1. **Backend Logs**: Check terminal running uvicorn for detailed logs
2. **Frontend Console**: Open browser dev tools for JavaScript errors
3. **Network Requests**: Monitor API calls in browser Network tab
4. **File System**: Check `backend/persistent_uploads/` for uploaded files
