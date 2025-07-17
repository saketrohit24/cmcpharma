#!/usr/bin/env python3
"""
Test the complete flow to verify sections are clickable and content is displayed
"""

import requests
import json

def test_complete_flow():
    print("🧪 Testing complete editor flow...")
    
    # Use the session with existing files
    session_id = "session_1752696706836_z3ezer644"
    
    # Generate a simple 2-section document
    template_data = {
        "id": "test-sections",
        "name": "Test Document for Section Navigation",
        "description": "Test template with multiple sections",
        "toc": [
            {"id": "intro", "title": "Introduction", "level": 1, "children": []},
            {"id": "methods", "title": "Analytical Methods", "level": 1, "children": []},
        ]
    }
    
    print(f"📝 Generating document with {len(template_data['toc'])} sections...")
    
    generation_url = f"http://localhost:8001/api/generation/generate/{session_id}"
    response = requests.post(generation_url, json=template_data)
    
    if response.status_code == 200:
        doc = response.json()
        print("✅ Document generated successfully!")
        print(f"   Title: {doc['title']}")
        print(f"   Sections: {len(doc['sections'])}")
        
        for i, section in enumerate(doc['sections']):
            print(f"\n📖 Section {i+1}: {section['title']}")
            print(f"   ID: {section['id']}")
            print(f"   Content length: {len(section['content'])} characters")
            print(f"   Content preview: {section['content'][:100]}...")
            
        print(f"\n🎯 Frontend should now:")
        print(f"   1. Show project structure with {len(doc['sections'])} clickable sections")
        print(f"   2. Display content when each section is clicked")
        print(f"   3. Highlight active section in blue")
        print(f"   4. Show section title in editor header")
        
        return True
    else:
        print(f"❌ Generation failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n🎉 Backend is ready! Test the frontend by:")
        print("   1. Go to Templates tab")
        print("   2. Click 'Use Session with Files'")
        print("   3. Generate a document")
        print("   4. Click sections in Project Structure")
        print("   5. Verify content appears in editor")
    else:
        print("\n💥 Backend test failed.")
