# CMC Regulatory Writer - Setup Guide

This guide will help you set up and run the CMC Regulatory Writer application locally.

## Prerequisites

- Python 3.8+ 
- Node.js 16+
- npm or yarn
- Git

## Environment Variables

Before running the application, make sure you have the required environment variables set up:

### Backend Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```bash
# NVIDIA API Configuration
NVIDIA_API_KEY=your_nvidia_api_key_here
LLM_API_KEY=your_nvidia_api_key_here

# Database Configuration (if using a database)
DATABASE_URL=sqlite:///./cmc_regulatory.db

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Optional: Other API keys
OPENAI_API_KEY=your_openai_key_here  # If using OpenAI as fallback
```

### Getting NVIDIA API Key

1. Go to [NVIDIA NGC](https://ngc.nvidia.com/)
2. Create an account or sign in
3. Navigate to "Setup" -> "Generate API Key"
4. Copy the API key and add it to your `.env` file

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/saketrohit24/cmc-pharma-write.git
cd cmc-pharma-write
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys (see above)
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
# or if using yarn:
# yarn install
```

## Running the Application

### Method 1: Run Both Services Separately

#### Start the Backend Server

```bash
# From the backend directory
cd /path/to/cmc-regulatory-writer/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start the Frontend Development Server

```bash
# From the frontend directory (in a new terminal)
cd /path/to/cmc-regulatory-writer/frontend
npm run dev
# or
yarn dev
```

### Method 2: Using the Provided Scripts

#### Backend Quick Start

```bash
# From the project root
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Quick Start

```bash
# From the project root (in a new terminal)
cd frontend && npm run dev
```

## Access Points

Once both services are running:

- **Frontend Application**: http://localhost:3000 or http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc

## Troubleshooting

### Port Already in Use

If you get an "Address already in use" error:

```bash
# For backend, try a different port:
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# For frontend, Vite will automatically suggest an available port
```

### Missing Dependencies

If you encounter import errors:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Environment Variables Not Loaded

Make sure your `.env` file is in the correct directory (`backend/.env`) and contains all required variables.

### NVIDIA API Issues

- Verify your API key is correct
- Check that you have sufficient credits/quota
- Try the health check endpoint: http://localhost:8000/health

## Development Tips

### Backend Development

- The server runs with auto-reload enabled, so changes will automatically restart the server
- Check logs in the terminal for any errors
- Use the Swagger UI at `/docs` to test API endpoints

### Frontend Development

- Hot reload is enabled, so changes will automatically update the browser
- Check the browser console for any JavaScript errors
- The development server typically runs on port 3000 or 5173

### Testing the Integration

1. Start both backend and frontend servers
2. Open the frontend in your browser
3. Try the chat functionality to test LLM integration
4. Upload some PDF files and create a template
5. Generate a document to test the full pipeline

## Next Steps

Once you have the application running:

1. Upload some sample PDF documents
2. Create or use a template
3. Generate a document with sections
4. Test the chat functionality
5. Export documents in different formats

For more detailed information about the application features, see the main README.md file.
