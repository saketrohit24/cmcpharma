# CMC Regulatory Writer Backend

A FastAPI-based backend for generating regulatory documents using RAG (Retrieval-Augmented Generation) and LLM capabilities.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# Required for RAG functionality
NVIDIA_API_KEY=your_nvidia_api_key_here

# Required for document generation  
LLM_API_KEY=your_llm_api_key_here
```

### 3. Test the Setup
```bash
# Basic functionality test (works without API keys)
python test_basic.py

# Full integration test (requires API keys)
python test_integration.py
```

### 4. Start the Server
```bash
python -m app.main
```

The API will be available at:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📚 API Endpoints

### File Management
- `POST /api/files/upload/{session_id}` - Upload source documents

### Template Management  
- `POST /api/templates/parse` - Parse TOC text into structured template

### Document Generation
- `POST /api/generation/generate/{session_id}` - Generate document from template
- `POST /api/generation/refine` - Refine document sections

### Export
- `POST /api/export/export` - Export document to PDF

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI app and routing
├── core/
│   └── config.py        # Configuration and settings
├── models/              # Pydantic data models
│   ├── template.py
│   ├── document.py  
│   ├── file.py
│   └── export.py
├── services/            # Business logic
│   ├── template_service.py
│   ├── file_manager.py
│   ├── rag_service.py
│   ├── generation_service.py
│   └── export_service.py
├── endpoints/           # API route handlers
│   ├── templates.py
│   ├── files.py
│   ├── generation.py
│   └── export.py
└── utils/
    └── parsers.py       # Text parsing utilities
```

## 🔧 Configuration

### Required API Keys

1. **NVIDIA API Key**: Get from [NVIDIA Build](https://build.nvidia.com/)
   - Used for document embeddings and vector search
   - Required for RAG functionality

2. **LLM API Key**: Get from OpenAI or Anthropic
   - Used for document generation and refinement
   - Required for content generation

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NVIDIA_API_KEY` | NVIDIA API key for embeddings | Yes |
| `LLM_API_KEY` | LLM API key for generation | Yes | 
| `DATABASE_URL` | Database connection string | No |
| `DEBUG` | Enable debug mode | No |

## 🧪 Testing

### Basic Tests (No API Keys Required)
```bash
python test_basic.py
```
Tests core functionality like template parsing and file management.

### Full Integration Tests (API Keys Required)
```bash
python test_integration.py
```
Tests complete workflow including RAG and LLM generation.

## 🔗 Frontend Integration

The backend is designed to work with the React frontend. Key integration points:

- **CORS**: Configured for `localhost:3000` and `localhost:5173`
- **API Contract**: Matches frontend expectations exactly
- **Session Management**: File uploads tied to session IDs
- **Error Handling**: Structured error responses for frontend

## 📝 Development

### Adding New Endpoints
1. Create new router in `app/endpoints/`
2. Add business logic in `app/services/`
3. Include router in `app/main.py`

### Adding New Models
1. Create Pydantic models in `app/models/`
2. Update `__init__.py` imports
3. Use in services and endpoints

## 🚀 Production Deployment

1. Set `DEBUG=false` in environment
2. Use production database (PostgreSQL)
3. Add proper logging and monitoring
4. Configure HTTPS and security headers
5. Set up API rate limiting

## 📄 License

MIT License - see LICENSE file for details.
