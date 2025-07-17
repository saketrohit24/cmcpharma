#!/usr/bin/env python3
"""
Test script to verify document generation functionality
"""

import asyncio
import json
import requests
import time
import os
import sys
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8001"
TEST_SESSION_ID = "test-session-123"

def test_health():
    """Test if backend is running"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_template_creation():
    """Test template creation and saving"""
    print("\n🔍 Testing template creation...")
    
    template_data = {
        "name": "Test Drug Substance Template",
        "description": "Test template for document generation",
        "toc_text": """1. Introduction
1.1 General Information
1.2 Scope and Purpose
2. Manufacturing Process
2.1 Process Description
2.2 Critical Parameters
3. Quality Control
3.1 Testing Methods
3.2 Specifications
4. Conclusion"""
    }
    
    try:
        # Create template
        response = requests.post(
            f"{BACKEND_URL}/api/templates/parse",
            json=template_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            template = response.json()
            print(f"✅ Template created: {template['name']}")
            print(f"   ID: {template['id']}")
            print(f"   Sections: {len(template['toc'])}")
            return template
        else:
            print(f"❌ Template creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Template creation request failed: {e}")
        return None

def test_get_templates():
    """Test getting all templates"""
    print("\n🔍 Testing template retrieval...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/templates", timeout=5)
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Retrieved {len(templates)} templates")
            for template in templates:
                print(f"   - {template['name']} (ID: {template['id']})")
            return templates
        else:
            print(f"❌ Template retrieval failed: {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Template retrieval request failed: {e}")
        return []

def create_test_file():
    """Create a simple test PDF-like file"""
    print("\n🔍 Creating test file...")
    
    test_content = """
    Test Regulatory Document
    
    This is a test document containing sample regulatory information.
    
    Manufacturing Process:
    The manufacturing process involves several critical steps including preparation,
    synthesis, purification, and packaging. Quality control measures are implemented
    at each stage to ensure product quality and compliance with regulatory standards.
    
    Quality Control:
    Quality control testing includes identity, purity, potency, and impurity testing.
    All testing methods are validated according to ICH guidelines.
    
    Stability:
    Stability studies are conducted under controlled conditions to establish
    shelf-life and storage conditions.
    """
    
    # Create a temporary text file (simulating a document)
    test_file_path = "test_document.txt"
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    print(f"✅ Test file created: {test_file_path}")
    return test_file_path

def test_file_upload(file_path):
    """Test file upload functionality"""
    print("\n🔍 Testing file upload...")
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "text/plain")}
            response = requests.post(
                f"{BACKEND_URL}/api/files/upload/{TEST_SESSION_ID}",
                files=files,
                timeout=10
            )
        
        if response.status_code == 200:
            file_info = response.json()
            print(f"✅ File uploaded successfully")
            print(f"   Name: {file_info['name']}")
            print(f"   Size: {file_info['size']} bytes")
            return True
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ File upload request failed: {e}")
        return False

def test_document_generation(template):
    """Test document generation"""
    print("\n🔍 Testing document generation...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/generation/generate/{TEST_SESSION_ID}",
            json=template,
            headers={"Content-Type": "application/json"},
            timeout=30  # Give more time for LLM processing
        )
        
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document generated successfully")
            print(f"   Title: {document['title']}")
            print(f"   Sections: {len(document['sections'])}")
            
            # Display first few sections
            for i, section in enumerate(document['sections'][:3]):
                print(f"\n   Section {i+1}: {section['title']}")
                print(f"   Source count: {section['source_count']}")
                content_preview = section['content'][:150] + "..." if len(section['content']) > 150 else section['content']
                print(f"   Content preview: {content_preview}")
            
            return document
        else:
            print(f"❌ Document generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Document generation request failed: {e}")
        return None

def cleanup_test_file(file_path):
    """Clean up test file"""
    try:
        os.remove(file_path)
        print(f"\n🧹 Cleaned up test file: {file_path}")
    except OSError:
        pass

def main():
    """Run all tests"""
    print("🧪 CMC Regulatory Writer - Document Generation Test")
    print("=" * 55)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend is not running. Please start the backend first:")
        print("   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
        sys.exit(1)
    
    # Test 2: Template creation
    template = test_template_creation()
    if not template:
        print("\n❌ Template creation failed. Cannot proceed with document generation test.")
        sys.exit(1)
    
    # Test 3: Template retrieval
    templates = test_get_templates()
    
    # Test 4: File operations
    test_file_path = create_test_file()
    
    # Test 5: File upload
    if not test_file_upload(test_file_path):
        print("\n❌ File upload failed. Document generation may not work properly.")
    
    # Test 6: Document generation
    document = test_document_generation(template)
    
    # Cleanup
    cleanup_test_file(test_file_path)
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 TEST SUMMARY")
    print("=" * 55)
    
    if document:
        print("✅ All tests passed! Document generation is working.")
        print("\n🎯 Next steps:")
        print("   1. Open the frontend: http://localhost:5174")
        print("   2. Upload real PDF documents")
        print("   3. Create templates with regulatory sections")
        print("   4. Generate documents and verify AI content")
    else:
        print("❌ Document generation test failed.")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if NVIDIA_API_KEY is set in backend/.env")
        print("   2. Verify backend logs for errors")
        print("   3. Ensure all dependencies are installed")
        print("   4. Check the troubleshooting guide in docs/TROUBLESHOOTING.md")

if __name__ == "__main__":
    main()
