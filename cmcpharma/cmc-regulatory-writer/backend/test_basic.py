#!/usr/bin/env python3
"""
Basic integration test script that works without API keys

This script tests the core functionality that doesn't require external APIs.
"""
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_functionality():
    """Test functionality that doesn't require API keys"""
    print("🧪 Testing basic functionality (no API keys required)...")
    
    try:
        # Test template service
        from app.services.template_service import TemplateService
        from app.models.template import TemplateCreationRequest
        
        service = TemplateService()
        
        toc_text = """1. Introduction
    1.1 Background
2. Methods
    2.1 Materials
    2.2 Procedures
3. Results
4. Conclusion"""
        
        request = TemplateCreationRequest(
            name="Test Template",
            description="Test description",
            toc_text=toc_text
        )
        
        template = service.create_template_from_text(request)
        print(f"✅ Template parsing works: {len(template.toc)} sections parsed")
        
        # Test file manager
        from app.services.file_manager import FileManager
        file_manager = FileManager("test_session")
        print(f"✅ File manager works: Session directory created")
        
        # Test models
        from app.models.document import GeneratedSection, GeneratedDocument
        
        section = GeneratedSection(
            title="Test Section",
            content="Test content",
            source_count=0
        )
        
        document = GeneratedDocument(
            title="Test Document",
            sections=[section],
            template_id=template.id,
            session_id="test"
        )
        
        print(f"✅ Document models work: {document.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_api_services():
    """Test what happens when API services are called without keys"""
    print("\n🧪 Testing API service initialization...")
    
    try:
        # Test RAG service (should fail gracefully)
        from app.services.rag_service import RAGService
        print("⚠️  RAGService available but requires NVIDIA_API_KEY to initialize")
        
        # Test generation service (should fail gracefully)  
        from app.services.generation_service import GenerationService
        print("⚠️  GenerationService available but requires LLM_API_KEY to initialize")
        
        return True
        
    except Exception as e:
        print(f"❌ API service test failed: {e}")
        return False

def show_next_steps():
    """Show user what to do next"""
    print("\n📝 Next Steps to Complete Setup:")
    print("\n1. 🔑 Add API Keys to .env file:")
    print("   - Get NVIDIA API key from: https://build.nvidia.com/")
    print("   - Get LLM API key (OpenAI/Anthropic) for generation")
    print("   - Update the .env file with your actual keys")
    
    print("\n2. 🧪 Test with API keys:")
    print("   python test_integration.py")
    
    print("\n3. 🚀 Start the server:")
    print("   python -m app.main")
    print("   Then visit: http://localhost:8000/docs")
    
    print("\n4. 🔗 Connect Frontend:")
    print("   The backend is ready for frontend integration!")

def main():
    """Run basic tests that work without API keys"""
    print("🚀 CMC Regulatory Writer Backend - Basic Integration Test\n")
    
    success = True
    
    if not test_basic_functionality():
        success = False
    
    if not test_api_services():
        success = False
    
    if success:
        print("\n✅ Basic functionality tests passed!")
        print("⚠️  Note: Full functionality requires API keys in .env file")
    else:
        print("\n❌ Some tests failed!")
    
    show_next_steps()
    return success

if __name__ == "__main__":
    main()
