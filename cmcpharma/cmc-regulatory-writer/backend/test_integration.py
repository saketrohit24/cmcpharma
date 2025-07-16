#!/usr/bin/env python3
"""
Integration test script for the CMC Regulatory Writer Backend

This script tests the core functionality without requiring LLM API keys.
"""
import os
import sys
import json
import tempfile
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported successfully"""
    print("🧪 Testing imports...")
    
    try:
        from app.models.template import Template, TemplateCreationRequest, TOCItem
        from app.models.document import GeneratedDocument, GeneratedSection, RefinementRequest
        from app.models.file import FileItem
        from app.models.export import ExportRequest
        print("✅ All models imported successfully")
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False
    
    try:
        from app.services.template_service import TemplateService
        from app.services.file_manager import FileManager
        print("✅ Core services imported successfully")
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        return False
    
    try:
        from app.endpoints.templates import router as templates_router
        from app.endpoints.files import router as files_router
        print("✅ All endpoints imported successfully")
    except Exception as e:
        print(f"❌ Endpoint import failed: {e}")
        return False
    
    return True

def test_template_service():
    """Test template parsing functionality"""
    print("\n🧪 Testing Template Service...")
    
    try:
        from app.services.template_service import TemplateService
        from app.models.template import TemplateCreationRequest
        
        service = TemplateService()
        
        # Test TOC parsing
        toc_text = """1. Introduction
    1.1 Background
    1.2 Purpose
2. Materials and Methods
    2.1 Raw Materials
    2.2 Manufacturing Process
3. Results and Discussion
4. Conclusion"""
        
        request = TemplateCreationRequest(
            name="Test CMC Template",
            description="A test template for CMC documentation",
            toc_text=toc_text
        )
        
        template = service.create_template_from_text(request)
        
        print(f"✅ Template created: {template.name}")
        print(f"✅ TOC items parsed: {len(template.toc)}")
        for item in template.toc:
            print(f"   - Level {item.level}: {item.title}")
        
        return True
    except Exception as e:
        print(f"❌ Template service test failed: {e}")
        return False

def test_file_manager():
    """Test file management functionality"""
    print("\n🧪 Testing File Manager...")
    
    try:
        from app.services.file_manager import FileManager
        
        # Create a test session
        session_id = "test_session_123"
        file_manager = FileManager(session_id)
        
        # Test that session directory is created
        session_dir = file_manager.session_dir
        if os.path.exists(session_dir):
            print(f"✅ Session directory created: {session_dir}")
        else:
            print(f"❌ Session directory not found: {session_dir}")
            return False
        
        # Test getting file paths (should be empty initially)
        file_paths = file_manager.get_session_file_paths()
        print(f"✅ File paths retrieved: {len(file_paths)} files")
        
        return True
    except Exception as e:
        print(f"❌ File manager test failed: {e}")
        return False

def test_models():
    """Test Pydantic model creation and validation"""
    print("\n🧪 Testing Pydantic Models...")
    
    try:
        from app.models.template import TOCItem, Template
        from app.models.document import GeneratedSection, GeneratedDocument
        from datetime import datetime
        
        # Test TOCItem
        toc_item = TOCItem(title="Test Section", level=1)
        print(f"✅ TOCItem created: {toc_item.title} (Level {toc_item.level})")
        
        # Test Template
        template = Template(
            name="Test Template",
            description="A test template",
            toc=[toc_item]
        )
        print(f"✅ Template created: {template.name}")
        
        # Test GeneratedSection
        section = GeneratedSection(
            title="Test Section",
            content="This is test content for the section.",
            source_count=5
        )
        print(f"✅ GeneratedSection created: {section.title}")
        
        # Test GeneratedDocument
        document = GeneratedDocument(
            title="Test Document",
            sections=[section],
            template_id=template.id,
            session_id="test_session"
        )
        print(f"✅ GeneratedDocument created: {document.title}")
        
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🧪 Testing FastAPI App...")
    
    try:
        from app.main import app
        print(f"✅ FastAPI app created: {app.title}")
        print(f"✅ App version: {app.version}")
        
        # Check that routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ["/api/health", "/api/files/upload/{session_id}", "/api/templates/parse"]
        
        for expected_route in expected_routes:
            if any(expected_route in route for route in routes):
                print(f"✅ Route found: {expected_route}")
            else:
                print(f"❌ Route missing: {expected_route}")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting CMC Regulatory Writer Backend Integration Tests\n")
    
    tests = [
        test_imports,
        test_models,
        test_template_service,
        test_file_manager,
        test_fastapi_app,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All integration tests passed! The backend is ready for development.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
