# CMC Regulatory Writer v2.1

## 🚀 Enterprise-Grade Document Generation Platform

A sophisticated AI-powered platform for creating regulatory documentation in the pharmaceutical industry with full document persistence and advanced editing capabilities.

## ✨ Version 2.1 Features

### 🎯 **Major New Features**
- **📄 Document Persistence**: Generated documents survive browser reloads
- **📁 File Persistence**: Uploaded files automatically restored across sessions
- **💾 Auto-Save**: All edits automatically saved to localStorage
- **🔄 State Restoration**: Project structure, tabs, and edits preserved
- **✨ Enhanced Selection**: Fixed text selection for all sizes (small text & large paragraphs)
- **🗑️ Clear Document**: Easy reset functionality for starting fresh

### 🔧 **Technical Improvements**
- **Right Panel Integration**: Moved Suggest Edit feature to right panel
- **Robust Selection Logic**: Improved text selection detection and validation
- **Enhanced Storage Service**: Comprehensive localStorage management
- **File Context Persistence**: Files persist across browser sessions
- **Better Error Handling**: Improved user experience with proper error messages

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Port**: 8001
- **Features**: Document generation, file upload, suggest edits API
- **AI Integration**: LLM-powered content generation and editing

### Frontend (React/TypeScript)
- **Port**: 5173 (development)
- **Features**: Document editor, file manager, template system
- **Persistence**: localStorage-based state management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/saketrohit24/cmc-pharma-write.git
   cd cmc-pharma-write/cmc-regulatory-writer
   ```

2. **Start Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8001

## 📋 Usage Workflow

### 1. Upload Files
- Navigate to "Files" tab
- Upload your regulatory documents
- Files are automatically categorized and persisted

### 2. Generate Document
- Go to "Templates" tab
- Select appropriate template
- Generate document using uploaded files
- Document is automatically saved and persists across reloads

### 3. Edit Content
- Use "Suggest Edit" feature in right panel
- Select any text (small or large) for targeted edits
- All changes auto-saved to localStorage

### 4. Persistent Workflow
- Reload browser - your work is preserved
- All uploaded files, generated content, and edits restored
- Use "Clear" button when you want to start fresh

## 🔧 Configuration

### Environment Variables
```bash
# Backend (.env)
OPENAI_API_KEY=your_openai_key
NVIDIA_API_KEY=your_nvidia_key
DATABASE_URL=your_database_url

# Optional
ANTHROPIC_API_KEY=your_anthropic_key
```

## 📁 Project Structure

```
cmc-regulatory-writer/
├── backend/                 # Python/FastAPI backend
│   ├── app/
│   │   ├── endpoints/       # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Data models
│   │   └── main.py         # Application entry
│   └── requirements.txt
├── frontend/               # React/TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API clients
│   │   ├── contexts/       # React contexts
│   │   └── App.tsx        # Main application
│   └── package.json
└── VERSION                # Current version
```

## 🎯 Key Features

### Document Generation
- AI-powered content creation
- Template-based structure
- Multi-file input processing
- Progress tracking with real-time updates

### Advanced Editing
- In-context text selection and editing
- LLM-powered suggestions
- Preserve document formatting
- Undo/redo capabilities

### File Management
- Drag-and-drop upload
- Automatic categorization
- Persistent storage
- Session restoration

### User Experience
- Intuitive interface
- Real-time feedback
- Auto-save functionality
- Cross-session persistence

## 🔄 Version History

### v2.1.0 (Current)
- Document persistence across browser reloads
- File upload persistence and auto-restoration
- Fixed selection detection for all text sizes
- Suggest Edit feature moved to right panel
- Auto-save functionality for all user changes
- Enhanced storage service with localStorage
- Clear document functionality

### v2.0.0
- Initial release with core document generation
- Template system implementation
- File upload and management
- Basic editing capabilities

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, email your-email@domain.com or create an issue on GitHub.

## 🎉 Acknowledgments

- OpenAI for GPT models
- NVIDIA for AI endpoints
- FastAPI and React communities
- All contributors and users

---

**CMC Regulatory Writer v2.1** - Built with ❤️ for the pharmaceutical regulatory community
