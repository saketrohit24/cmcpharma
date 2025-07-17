#!/bin/bash

# CMC Regulatory Writer - Quick Start Script
# This script starts both backend and frontend services

echo "🚀 Starting CMC Regulatory Writer..."
echo "=================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected: /path/to/cmc-regulatory-writer/"
    echo "   Current:  $(pwd)"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Start backend
echo "📦 Starting Backend Server..."
echo "=================================="

cd backend

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: No .env file found in backend directory"
    echo "   Please create backend/.env with your NVIDIA_API_KEY"
    echo ""
fi

# Find available port for backend (8000, 8001, 8002)
BACKEND_PORT=8000
if check_port $BACKEND_PORT; then
    BACKEND_PORT=8001
    if check_port $BACKEND_PORT; then
        BACKEND_PORT=8002
    fi
fi

echo "🎯 Starting backend on port $BACKEND_PORT..."
echo "   API Documentation: http://localhost:$BACKEND_PORT/docs"
echo "   Health Check: http://localhost:$BACKEND_PORT/api/health"
echo ""

# Start backend in background
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Check if backend started successfully
if check_port $BACKEND_PORT; then
    echo "✅ Backend started successfully on port $BACKEND_PORT"
else
    echo "❌ Backend failed to start on port $BACKEND_PORT"
    exit 1
fi

# Start frontend
echo ""
echo "🎨 Starting Frontend Server..."
echo "=================================="

cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "🎯 Starting frontend development server..."
echo "   Note: Vite will automatically find an available port"
echo ""

# Update API URL in frontend to match backend port
if [ $BACKEND_PORT != 8000 ]; then
    echo "🔧 Updating frontend API configuration to use port $BACKEND_PORT..."
    sed -i.bak "s/localhost:800[0-9]/localhost:$BACKEND_PORT/" src/services/apiClient.ts
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!

# Wait for user to stop
echo ""
echo "🎉 CMC Regulatory Writer is now running!"
echo "=================================="
echo "Backend:  http://localhost:$BACKEND_PORT"
echo "Frontend: Check terminal output above for the actual port"
echo "API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "Press Ctrl+C to stop both services..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    
    # Restore original API URL if changed
    if [ $BACKEND_PORT != 8000 ] && [ -f "src/services/apiClient.ts.bak" ]; then
        mv src/services/apiClient.ts.bak src/services/apiClient.ts
    fi
    
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
