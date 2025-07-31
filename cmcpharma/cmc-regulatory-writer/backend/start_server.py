import uvicorn
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

if __name__ == "__main__":
    print("🚀 Starting server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
