#!/usr/bin/env python3
"""
Quick test to generate a document using the session with files
"""

import requests
import json

def test_generation_with_existing_session():
    print("🧪 Testing document generation with existing session that has files...")
    
    session_id = "session_1752696706836_z3ezer644"
    print(f"📝 Using session ID: {session_id}")
    
    # Check files in session
    list_url = f"http://localhost:8001/api/files/session/{session_id}"
    response = requests.get(list_url)
    
    if response.status_code == 200:
        files = response.json()
        print(f"✅ Found {len(files)} files in session")
    else:
        print(f"❌ No files found: {response.status_code}")
        return False
    
    # Generate document with simple template
    template_data = {
        "id": "simple-test",
        "name": "Antibody Characterization Report",
        "description": "Test template for antibody analysis",
        "toc": [
            {"id": "1", "title": "Introduction", "level": 1, "children": []},
            {"id": "2", "title": "Analytical Methods", "level": 1, "children": []},
            {"id": "3", "title": "Results and Discussion", "level": 1, "children": []}
        ]
    }
    
    generation_url = f"http://localhost:8001/api/generation/generate/{session_id}"
    response = requests.post(generation_url, json=template_data)
    
    if response.status_code == 200:
        doc = response.json()
        print("✅ Document generated successfully!")
        print(f"   Title: {doc['title']}")
        print(f"   Sections: {len(doc['sections'])}")
        
        # Show preview of first section
        if doc['sections']:
            first_section = doc['sections'][0]
            preview = first_section['content'][:300] + "..." if len(first_section['content']) > 300 else first_section['content']
            print(f"\n📖 Preview of '{first_section['title']}':")
            print(preview)
            print(f"\n📚 Sources used: {first_section['source_count']}")
        
        return True
    else:
        print(f"❌ Generation failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    success = test_generation_with_existing_session()
    if success:
        print("\n🎉 Test passed! Users should now be able to generate documents with uploaded files.")
    else:
        print("\n💥 Test failed. Check the error messages above.")
