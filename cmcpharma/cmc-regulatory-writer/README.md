# CMC Pharma Writer 🧬💊

An AI-powered CMC (Chemistry, Manufacturing, and Controls) regulatory writing assistant with streaming chat capabilities.

## 🌟 Features

- **🤖 AI-Powered Chat**: Real-time streaming responses using NVIDIA's Llama-4 Scout model
- **📊 CMC Expertise**: Specialized knowledge in pharmaceutical regulatory writing
- **💬 ChatGPT-like Experience**: Word-by-word streaming with typing indicators
- **🔄 Session Management**: Persistent chat sessions with conversation history
- **📝 Document Generation**: Content generation for regulatory documents
- **🎯 Dual Mode**: Handles both general knowledge and CMC-specific questions

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **NVIDIA API Key** (for LLM access)

### 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/saketrohit24/cmc-pharma-write.git
   cd cmc-pharma-write
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # In backend directory, create .env file
   cp .env.example .env
   
   # Add your NVIDIA API key
   NVIDIA_API_KEY=your_nvidia_api_key_here
   LLM_API_KEY=your_nvidia_api_key_here
   ```

### 🏃‍♂️ Running the Application

1. **Start Backend Server**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🎯 How It Works

### Streaming Chat Experience
- **Real-time Responses**: See AI "typing" word-by-word like ChatGPT
- **Natural Conversations**: Answers general questions without forcing CMC context
- **Expert Knowledge**: Provides detailed pharmaceutical guidance when needed

### AI Model Integration
- **NVIDIA Llama-4 Scout**: Fast 17B parameter model for quick responses
- **Streaming API**: Direct integration with NVIDIA's streaming endpoints
- **Context Awareness**: Maintains conversation history for better responses

## 🏗️ Architecture

```
📁 cmc-pharma-write/
├── 📁 backend/                 # FastAPI Python backend
│   ├── 📁 app/
│   │   ├── 📁 endpoints/       # API route handlers
│   │   ├── 📁 services/        # Business logic (ChatService, etc.)
│   │   ├── 📁 models/          # Pydantic data models
│   │   └── 📁 core/           # Configuration and settings
│   └── 📄 requirements.txt    # Python dependencies
├── 📁 frontend/               # React TypeScript frontend
│   ├── 📁 src/
│   │   ├── 📁 components/     # React components
│   │   ├── 📁 services/       # API communication
│   │   └── 📁 styles/         # CSS styling
│   └── 📄 package.json       # Node.js dependencies
└── 📄 README.md              # This file
```

## 🔌 API Endpoints

### Chat Endpoints
- `POST /api/chat/message` - Send message (standard response)
- `POST /api/chat/message/stream` - Send message (streaming response)
- `GET /api/chat/sessions` - Get chat sessions
- `POST /api/chat/sessions` - Create new session

### Health Check
- `GET /health` - Server health status

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop and mobile
- **Real-time Streaming**: Word-by-word message display
- **Loading States**: "Thinking..." and "Typing..." indicators
- **Message History**: Persistent chat sessions
- **Error Handling**: Graceful error messages

## 🔧 Technical Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **NVIDIA AI Endpoints**: LLM integration via langchain
- **Streaming**: Server-sent events for real-time responses

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **CSS**: Custom styling with animations

## 🌟 Key Features Implemented

### ✅ Streaming Chat
- Real-time word-by-word streaming
- Animated cursor during typing
- Proper loading states

### ✅ Natural AI Responses
- Removed CMC bias from general questions
- Maintains pharmaceutical expertise when needed
- Context-aware conversations

### ✅ Session Management
- Persistent chat sessions
- Conversation history
- Session cleanup

### ✅ Error Handling
- Graceful LLM failures
- Network error recovery
- User-friendly error messages

## 🚀 Deployment

### Backend Deployment
```bash
# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker (optional)
docker build -t cmc-pharma-backend .
docker run -p 8000:8000 cmc-pharma-backend
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files
npm run preview
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NVIDIA**: For providing the AI models and API
- **FastAPI**: For the excellent Python web framework
- **React**: For the frontend framework
- **LangChain**: For LLM integration tools

---

**Built with ❤️ for pharmaceutical regulatory professionals**

Need help with CMC regulatory writing? Just ask! 🧬💊
