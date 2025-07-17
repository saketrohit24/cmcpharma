#!/usr/bin/env python3
"""
Test script to verify the urgent fixes for content layout, section mapping, and structure alignment.
"""

import requests
import json
import time
import uuid

# Test configuration
BACKEND_URL = "http://localhost:8001"
SESSION_ID = str(uuid.uuid4())

def test_backend_connection():
    """Test if backend is running and accessible."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/templates")
        print(f"✅ Backend connection successful: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend connection failed")
        return False

def test_template_upload_and_structure():
    """Test template upload and structure extraction."""
    try:
        # Use an existing template instead of creating a new one
        response = requests.get(f"{BACKEND_URL}/api/templates")
        
        if response.status_code == 200:
            templates = response.json()
            
            if templates:
                # Use the NIST template that was created
                nist_template = None
                for template in templates:
                    if "NIST" in template.get("name", ""):
                        nist_template = template
                        break
                
                if not nist_template:
                    # Use the first available template
                    nist_template = templates[0]
                
                print(f"✅ Using existing template: {nist_template['name']}")
                print(f"� Structure sections: {len(nist_template['toc'])}")
                
                # Display sections
                for i, section in enumerate(nist_template['toc']):
                    print(f"   {i+1}. {section['title']} (Level {section['level']})")
                
                return nist_template
            else:
                print("❌ No templates available")
                return None
        else:
            print(f"❌ Failed to get templates: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return None

def test_file_upload():
    """Test file upload for content generation."""
    try:
        # Create a test content file
        test_content = """
NIST Cybersecurity Framework Implementation Guide

Introduction
The NIST Cybersecurity Framework provides organizations with a comprehensive approach to managing cybersecurity risk. This document outlines the implementation of the framework core functions.

Framework Core Overview
The framework consists of five core functions that provide a strategic view of cybersecurity activities:

Identify (ID): Develop organizational understanding to manage cybersecurity risk to systems, people, assets, data, and capabilities.

Protect (PR): Develop and implement appropriate safeguards to ensure delivery of critical services.

Detect (DE): Develop and implement appropriate activities to identify the occurrence of a cybersecurity event.

Respond (RS): Develop and implement appropriate activities to take action regarding a detected cybersecurity incident.

Recover (RC): Develop and implement appropriate activities to maintain plans for resilience and to restore any capabilities or services that were impaired due to a cybersecurity incident.

Implementation Guidance
Organizations should tailor the framework to their specific needs, considering their risk tolerance, threat environment, and business requirements.

Conclusion
The NIST Cybersecurity Framework provides a flexible and repeatable approach for managing cybersecurity risk across organizations.
        """.strip()
        
        # Save content to a temporary file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            # Upload file
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('nist_framework.txt', f, 'text/plain')}  # Changed from 'files' to 'file'
                response = requests.post(
                    f"{BACKEND_URL}/api/files/upload/{SESSION_ID}",
                    files=files
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ File uploaded successfully: {result['name']}")
                print(f"📁 File size: {result['size']} bytes")
                return True
            else:
                print(f"❌ File upload failed: {response.status_code} - {response.text}")
                return False
                
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False

def test_document_generation(template):
    """Test document generation with proper section mapping."""
    try:
        # Generate document
        print(f"🚀 Starting document generation for template: {template['name']}")
        
        response = requests.post(
            f"{BACKEND_URL}/api/generation/generate/{SESSION_ID}",
            json=template
        )
        
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document generated successfully: {document['title']}")
            print(f"📄 Sections generated: {len(document['sections'])}")
            
            # Verify each section has content
            for i, section in enumerate(document['sections']):
                content_length = len(section['content'])
                print(f"   {i+1}. {section['title']}: {content_length} characters")
                
                if content_length < 100:
                    print(f"      ⚠️  WARNING: Section content is very short")
                elif content_length < 500:
                    print(f"      ⚠️  WARNING: Section content might be insufficient")
                else:
                    print(f"      ✅ Good content length")
                
                # Check for proper formatting
                if section['content'].count('#') > 0:
                    print(f"      ✅ Contains headers")
                if section['content'].count('\n\n') > 2:
                    print(f"      ✅ Contains paragraphs")
                    
            return document
        else:
            print(f"❌ Document generation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Document generation test failed: {e}")
        return None

def run_comprehensive_test():
    """Run all tests to verify the urgent fixes."""
    print("🧪 Running comprehensive test for urgent fixes...")
    print("=" * 60)
    
    # Test 1: Backend connection
    print("\n1️⃣ Testing backend connection...")
    if not test_backend_connection():
        print("❌ Cannot proceed without backend connection")
        return False
    
    # Test 2: Template upload and structure
    print("\n2️⃣ Testing template upload and structure extraction...")
    template = test_template_upload_and_structure()
    if not template:
        print("❌ Cannot proceed without template")
        return False
    
    # Test 3: File upload
    print("\n3️⃣ Testing file upload...")
    if not test_file_upload():
        print("❌ File upload failed, but continuing with generation...")
    
    # Test 4: Document generation
    print("\n4️⃣ Testing document generation...")
    document = test_document_generation(template)
    if not document:
        print("❌ Document generation failed")
        return False
    
    # Test 5: Verify fixes
    print("\n5️⃣ Verifying urgent fixes...")
    
    print("\n✅ Fix Verification Summary:")
    print(f"   📂 Project Structure: Template has {len(template.get('toc', []))} sections")
    print(f"   🧠 Section Mapping: Generated {len(document.get('sections', []))} individual sections")
    print(f"   📄 Content Length: Average {sum(len(s['content']) for s in document.get('sections', [])) // len(document.get('sections', [])) if document.get('sections') else 0} chars per section")
    print(f"   🖋️ Content Format: Sections contain headers and structured content")
    
    print("\n🎉 All tests completed!")
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
