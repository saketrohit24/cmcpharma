# Quick Start Scripts

This document contains quick commands to run the CMC Regulatory Writer application.

## Quick Commands

### Start Backend Server

```bash
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

If port 8000 is busy, use port 8001:

```bash
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Start Frontend Development Server

```bash
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/frontend && npm run dev
```

### Both Services in One Terminal (Sequential)

```bash
# This will start backend first, then you'll need to open a new terminal for frontend
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then in a new terminal:

```bash
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/frontend && npm run dev
```

## Development Workflow

1. **First Terminal** - Backend:
   ```bash
   cd /Users/rohit/cmcpharma/cmc-regulatory-writer/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Second Terminal** - Frontend:
   ```bash
   cd /Users/rohit/cmcpharma/cmc-regulatory-writer/frontend && npm run dev
   ```

3. **Access Points**:
   - Frontend: http://localhost:3000 or http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Common Issues & Solutions

### Backend Issues

**Port in use error:**
```bash
# Try port 8001 instead
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Missing dependencies:**
```bash
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/backend
pip install -r requirements.txt
```

**Environment variables missing:**
Create `backend/.env` file with:
```
NVIDIA_API_KEY=your_key_here
LLM_API_KEY=your_key_here
```

### Frontend Issues

**Missing dependencies:**
```bash
cd /Users/rohit/cmcpharma/cmc-regulatory-writer/frontend
npm install
```

**Port in use:**
Vite will automatically suggest an available port (usually 5173 if 3000 is taken)

## Testing the Application

1. **Test Backend Health:**
   - Open: http://localhost:8000/health
   - Should return: `{"status": "ok", "message": "Service is healthy"}`

2. **Test Frontend:**
   - Open: http://localhost:3000 or http://localhost:5173
   - Should show the CMC Regulatory Writer interface

3. **Test Chat Functionality:**
   - Type a message in the chat interface
   - Should get responses from the LLM

4. **Test Document Generation:**
   - Upload PDF files in the Files section
   - Create a template in the Templates section
   - Generate a document and verify sections are created with AI content

## Environment Variables Required

Make sure you have these in `backend/.env`:

```bash
NVIDIA_API_KEY=nvapi-your-key-here
LLM_API_KEY=nvapi-your-key-here
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```
