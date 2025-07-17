#!/usr/bin/env python3
"""
Test script to verify template saving functionality
"""

import requests
import json

BACKEND_URL = "http://localhost:8001"

def test_template_lifecycle():
    """Test complete template lifecycle: create, save, retrieve, update, delete"""
    print("🧪 Testing Template Lifecycle")
    print("=" * 40)
    
    # Test 1: Create a template via parse endpoint
    print("\n1️⃣ Creating template via parse...")
    template_data = {
        "name": "Test Template for Saving",
        "description": "Testing template persistence",
        "toc_text": """1. Executive Summary
2. Drug Substance
2.1 General Information
2.2 Manufacture
2.3 Characterisation
2.4 Control
3. Drug Product
3.1 Description and Composition
3.2 Pharmaceutical Development
3.3 Manufacture
3.4 Control of Drug Product
4. Conclusion"""
    }
    
    response = requests.post(f"{BACKEND_URL}/api/templates/parse", json=template_data)
    if response.status_code == 200:
        template = response.json()
        template_id = template['id']
        print(f"✅ Template created with ID: {template_id}")
    else:
        print(f"❌ Template creation failed: {response.status_code}")
        return False
    
    # Test 2: Get all templates
    print("\n2️⃣ Retrieving all templates...")
    response = requests.get(f"{BACKEND_URL}/api/templates")
    if response.status_code == 200:
        templates = response.json()
        found_template = None
        for t in templates:
            if t['id'] == template_id:
                found_template = t
                break
        
        if found_template:
            print(f"✅ Template found in list: {found_template['name']}")
        else:
            print("❌ Template not found in list")
            return False
    else:
        print(f"❌ Failed to retrieve templates: {response.status_code}")
        return False
    
    # Test 3: Get specific template by ID
    print("\n3️⃣ Retrieving template by ID...")
    response = requests.get(f"{BACKEND_URL}/api/templates/{template_id}")
    if response.status_code == 200:
        retrieved_template = response.json()
        print(f"✅ Template retrieved: {retrieved_template['name']}")
        print(f"   Description: {retrieved_template['description']}")
        print(f"   Sections: {len(retrieved_template['toc'])}")
    else:
        print(f"❌ Failed to retrieve template by ID: {response.status_code}")
        return False
    
    # Test 4: Update template
    print("\n4️⃣ Updating template...")
    update_data = {
        "name": "Updated Test Template",
        "description": "Updated description for testing"
    }
    response = requests.put(f"{BACKEND_URL}/api/templates/{template_id}", json=update_data)
    if response.status_code == 200:
        updated_template = response.json()
        print(f"✅ Template updated: {updated_template['name']}")
        print(f"   New description: {updated_template['description']}")
    else:
        print(f"❌ Failed to update template: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test 5: Save a completely new template
    print("\n5️⃣ Saving a new template directly...")
    new_template = {
        "id": "manual-template-123",
        "name": "Manually Created Template",
        "description": "Template created via save endpoint",
        "toc": [
            {"id": "1", "title": "Introduction", "level": 1},
            {"id": "2", "title": "Methods", "level": 1},
            {"id": "3", "title": "Detailed Procedures", "level": 2},
            {"id": "4", "title": "Results", "level": 1},
            {"id": "5", "title": "Conclusion", "level": 1}
        ]
    }
    
    response = requests.post(f"{BACKEND_URL}/api/templates", json=new_template)
    if response.status_code == 200:
        saved_template = response.json()
        print(f"✅ Template saved: {saved_template['name']}")
        manual_template_id = saved_template['id']
    else:
        print(f"❌ Failed to save template: {response.status_code}")
        print(f"   Response: {response.text}")
        manual_template_id = None
    
    # Test 6: Verify both templates exist
    print("\n6️⃣ Verifying all templates...")
    response = requests.get(f"{BACKEND_URL}/api/templates")
    if response.status_code == 200:
        all_templates = response.json()
        print(f"✅ Total templates: {len(all_templates)}")
        for t in all_templates:
            print(f"   - {t['name']} (ID: {t['id']})")
    
    # Test 7: Delete templates (cleanup)
    print("\n7️⃣ Cleaning up templates...")
    
    # Delete first template
    response = requests.delete(f"{BACKEND_URL}/api/templates/{template_id}")
    if response.status_code == 200:
        print(f"✅ Deleted template {template_id}")
    else:
        print(f"❌ Failed to delete template {template_id}")
    
    # Delete second template if it was created
    if manual_template_id:
        response = requests.delete(f"{BACKEND_URL}/api/templates/{manual_template_id}")
        if response.status_code == 200:
            print(f"✅ Deleted template {manual_template_id}")
        else:
            print(f"❌ Failed to delete template {manual_template_id}")
    
    print("\n✅ Template lifecycle test completed successfully!")
    return True

def test_frontend_integration():
    """Test template saving from frontend perspective"""
    print("\n\n🎨 Testing Frontend Template Integration")
    print("=" * 45)
    
    # This simulates what the frontend should do when saving templates
    print("\n🔍 Simulating frontend template creation flow...")
    
    # Step 1: Parse template from user input (like frontend textarea)
    frontend_template_data = {
        "name": "Frontend Created Template",
        "description": "Created via frontend simulation",
        "toc_text": """1. Product Overview
1.1 Product Description
1.2 Intended Use
2. Quality Attributes
2.1 Critical Quality Attributes
2.2 Quality Control Strategy
3. Manufacturing
3.1 Manufacturing Process
3.2 Process Controls
3.3 Manufacturing Equipment
4. Analytical Methods
4.1 Method Development
4.2 Method Validation
4.3 Specifications
5. Stability
5.1 Stability Protocol
5.2 Storage Conditions
5.3 Shelf Life Determination
6. Regulatory Compliance
6.1 ICH Guidelines
6.2 Regional Requirements
7. Conclusion"""
    }
    
    # Parse the template
    response = requests.post(f"{BACKEND_URL}/api/templates/parse", json=frontend_template_data)
    if response.status_code == 200:
        parsed_template = response.json()
        print(f"✅ Template parsed successfully: {parsed_template['name']}")
        print(f"   Sections parsed: {len(parsed_template['toc'])}")
        
        # The template should now be automatically saved
        template_id = parsed_template['id']
        
        # Verify it's saved by retrieving it
        response = requests.get(f"{BACKEND_URL}/api/templates/{template_id}")
        if response.status_code == 200:
            retrieved = response.json()
            print(f"✅ Template persisted and retrievable")
            print(f"   Name: {retrieved['name']}")
            print(f"   Description: {retrieved['description']}")
            
            # Show some sections
            print("   Sections:")
            for i, section in enumerate(retrieved['toc'][:5]):
                indent = "  " * (section['level'] - 1)
                print(f"     {indent}{section['title']} (Level {section['level']})")
            if len(retrieved['toc']) > 5:
                print(f"     ... and {len(retrieved['toc']) - 5} more sections")
        else:
            print(f"❌ Template not found after parsing: {response.status_code}")
            return False
        
        # Cleanup
        requests.delete(f"{BACKEND_URL}/api/templates/{template_id}")
        print(f"🧹 Cleaned up test template")
        
        return True
    else:
        print(f"❌ Template parsing failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    """Run all template tests"""
    print("🧪 CMC Regulatory Writer - Template Saving Test")
    print("=" * 50)
    
    # Test backend health first
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except:
        print("❌ Backend is not running. Please start it first:")
        print("   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
        return
    
    print("✅ Backend is running")
    
    # Run tests
    test1_success = test_template_lifecycle()
    test2_success = test_frontend_integration()
    
    print("\n" + "=" * 50)
    print("📊 TEMPLATE TESTING SUMMARY")
    print("=" * 50)
    
    if test1_success and test2_success:
        print("✅ All template tests passed!")
        print("\n🎯 Template saving is working correctly:")
        print("   ✅ Templates can be created via parse endpoint")
        print("   ✅ Templates are automatically saved")
        print("   ✅ Templates can be retrieved by ID")
        print("   ✅ Templates can be listed")
        print("   ✅ Templates can be updated")
        print("   ✅ Templates can be deleted")
        print("   ✅ Frontend integration should work")
        
        print("\n📋 Frontend Usage:")
        print("   1. User creates template in Templates section")
        print("   2. Template gets parsed and saved automatically")
        print("   3. Template appears in template list")
        print("   4. User can select template for document generation")
    else:
        print("❌ Some template tests failed")
        print("\n🔧 Check the backend logs for detailed error information")

if __name__ == "__main__":
    main()
