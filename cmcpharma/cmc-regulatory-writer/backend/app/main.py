from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import files, templates, generation, export, chat, documents, citations, suggest_edit

app = FastAPI(
    title="Medical Regulatory Writing API",
    description="API for generating regulatory documents from source files.",
    version="1.0.0"
)

# CORS Middleware to allow the React frontend to communicate with this API
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Default port for Vite-based React apps
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:5177",
    "http://localhost:5178",
    "http://localhost:5179", # Current frontend port
    "http://localhost:5180", # Current frontend port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the different API endpoint routers
app.include_router(files.router, prefix="/api/files", tags=["File Management"])
app.include_router(templates.router, prefix="/api/templates", tags=["Template Management"])
app.include_router(generation.router, prefix="/api/generation", tags=["Document Generation"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["Document Management"])
app.include_router(citations.router, prefix="/api/citations", tags=["Citations"])
app.include_router(suggest_edit.router, prefix="/api/suggest-edit", tags=["Suggest Edit"])

@app.get("/api/health", tags=["Health Check"])
def health_check():
    """A simple endpoint to confirm that the API is running."""
    return {"status": "ok", "message": "API is healthy and running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
