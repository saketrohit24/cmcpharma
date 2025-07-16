from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import files, templates, generation, export

app = FastAPI(
    title="Medical Regulatory Writing API",
    description="API for generating regulatory documents from source files.",
    version="1.0.0"
)

# CORS Middleware to allow the React frontend to communicate with this API
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Default port for Vite-based React apps
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

@app.get("/api/health", tags=["Health Check"])
def health_check():
    """A simple endpoint to confirm that the API is running."""
    return {"status": "ok", "message": "API is healthy and running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
