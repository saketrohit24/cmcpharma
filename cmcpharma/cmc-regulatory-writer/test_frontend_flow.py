#!/usr/bin/env python3
"""
Test script to verify the frontend-backend integration flow works correctly.
This simulates what the frontend should be doing.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001/api"

def test_full_flow():
    print("🧪 Testing full frontend-backend flow...")
    
    # Step 1: Create a session ID (simulating frontend)
    session_id = f"test_frontend_session_{int(time.time())}"
    print(f"📝 Using session ID: {session_id}")
    
    # Step 2: Upload a test file
    print("📤 Uploading test file...")
    test_content = """
    This is a comprehensive document about drug substance characterization and manufacturing.
    
    The drug substance is a small molecule compound with the following properties:
    - Molecular weight: 450.5 Da
    - Chemical name: (2S,3R)-2-amino-3-hydroxy-butanoic acid
    - Physical appearance: White crystalline powder
    - Solubility: Freely soluble in water, slightly soluble in ethanol
    
    Manufacturing Process:
    The manufacturing process consists of the following key steps:
    1. Synthesis of the active pharmaceutical ingredient
    2. Purification using column chromatography
    3. Crystallization and drying
    4. Quality control testing
    
    Quality Control:
    - Identity testing by IR spectroscopy
    - Purity analysis by HPLC
    - Impurity profiling
    - Residual solvent testing
    - Microbiological testing
    """
    
    with open("/tmp/test_drug_substance_detailed.txt", "w") as f:
        f.write(test_content)
    
    upload_url = f"{BASE_URL}/files/upload/{session_id}"
    with open("/tmp/test_drug_substance_detailed.txt", "rb") as f:
        files = {"file": ("test_drug_substance_detailed.txt", f, "text/plain")}
        response = requests.post(upload_url, files=files)
    
    if response.status_code == 200:
        print("✅ File uploaded successfully!")
        print(f"   File info: {response.json()}")
    else:
        print(f"❌ File upload failed: {response.status_code} - {response.text}")
        return False
    
    # Step 3: List files in session to verify
    print("📋 Checking files in session...")
    list_url = f"{BASE_URL}/files/session/{session_id}"
    response = requests.get(list_url)
    
    if response.status_code == 200:
        files = response.json()
        print(f"✅ Found {len(files)} files in session")
        for file in files:
            print(f"   - {file['name']} ({file['size']} bytes)")
    else:
        print(f"❌ Failed to list files: {response.status_code} - {response.text}")
        return False
    
    # Step 4: Generate document
    print("🤖 Generating document...")
    template_data = {
        "id": "sample-1",
        "name": "Module 3.2.S Drug Substance",
        "description": "Complete template for drug substance documentation",
        "toc": [
            {"id": "1", "title": "General Information", "level": 1, "children": []},
            {"id": "2", "title": "Nomenclature", "level": 2, "children": []},
            {"id": "3", "title": "Structure", "level": 2, "children": []},
            {"id": "4", "title": "General Properties", "level": 2, "children": []}
        ]
    }
    
    generation_url = f"{BASE_URL}/generation/generate/{session_id}"
    response = requests.post(generation_url, json=template_data, headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        doc = response.json()
        print("✅ Document generated successfully!")
        print(f"   Document ID: {doc['id']}")
        print(f"   Title: {doc['title']}")
        print(f"   Sections: {len(doc['sections'])}")
        
        # Show first section content preview
        if doc['sections']:
            first_section = doc['sections'][0]
            content_preview = first_section['content'][:200] + "..." if len(first_section['content']) > 200 else first_section['content']
            print(f"   First section '{first_section['title']}' preview: {content_preview}")
            print(f"   Sources used: {first_section['source_count']}")
        
        return True
    else:
        print(f"❌ Document generation failed: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    success = test_full_flow()
    if success:
        print("\n🎉 All tests passed! Frontend-backend flow is working correctly.")
    else:
        print("\n💥 Tests failed. Check the logs above for details.")
