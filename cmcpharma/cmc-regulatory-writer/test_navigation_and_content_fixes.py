#!/usr/bin/env python3
"""
Test script to verify both navigation and content fixes are working.
"""

import requests
import json
import uuid

# Test configuration
BACKEND_URL = "http://localhost:8001"
SESSION_ID = str(uuid.uuid4())

def test_nist_content_generation():
    """Test that content is generated from NIST documents, not CMC boilerplate."""
    
    # Upload NIST content
    nist_content = """
NIST Cybersecurity Framework Reference Guide

The National Institute of Standards and Technology (NIST) developed the Cybersecurity Framework to provide organizations with guidance on how to prevent, detect, and respond to cyberattacks.

Core Functions:
1. Identify (ID): Asset management, business environment, governance, risk assessment, risk management strategy
2. Protect (PR): Identity management, awareness training, data security, information protection processes
3. Detect (DE): Anomalies and events, security continuous monitoring, detection processes
4. Respond (RS): Response planning, communications, analysis, mitigation, improvements
5. Recover (RC): Recovery planning, improvements, communications

NIST's unique qualifications include:
- Federal agency with regulatory authority
- Extensive research capabilities
- Industry collaboration programs
- Standardization expertise
- Measurement science leadership

The study utilized multiple analytical instruments:
- Mass spectrometry systems
- Chromatography equipment
- Spectroscopic analyzers
- Proteomics platforms

Operator variability was highest in manual sample preparation steps and lowest in automated analytical procedures.
    """.strip()
    
    # Save to temporary file and upload
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(nist_content)
        temp_file_path = f.name
    
    try:
        # Upload NIST file
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('nist_guide.txt', f, 'text/plain')}
            response = requests.post(f"{BACKEND_URL}/api/files/upload/{SESSION_ID}", files=files)
        
        if response.status_code != 200:
            print(f"❌ File upload failed: {response.status_code}")
            return False
        
        print(f"✅ NIST file uploaded successfully")
        
        # Create a NIST-specific template
        template = {
            "id": "nist-test",
            "name": "NIST Cybersecurity Study",
            "description": "Test NIST content generation",
            "toc": [
                {"id": "1", "title": "Why is NIST uniquely suited to conduct this study?", "level": 1, "children": []},
                {"id": "2", "title": "What analytical instruments were used?", "level": 1, "children": []},
                {"id": "3", "title": "Which technique had the least variability?", "level": 1, "children": []}
            ]
        }
        
        # Generate document
        response = requests.post(f"{BACKEND_URL}/api/generation/generate/{SESSION_ID}", json=template)
        
        if response.status_code != 200:
            print(f"❌ Generation failed: {response.status_code} - {response.text}")
            return False
        
        document = response.json()
        print(f"✅ Document generated with {len(document['sections'])} sections")
        
        # Check content relevance
        nist_content_checks = {
            "NIST": False,
            "Cybersecurity": False,
            "Framework": False,
            "analytical instruments": False,
            "mass spectrometry": False,
            "operator variability": False
        }
        
        cmc_content_checks = {
            "CMC": False,
            "Chemistry, Manufacturing": False,
            "drug substance": False,
            "ICH": False,
            "pharmaceutical": False
        }
        
        all_content = " ".join([section['content'] for section in document['sections']])
        
        # Count NIST-related content
        for term in nist_content_checks:
            if term.lower() in all_content.lower():
                nist_content_checks[term] = True
        
        # Count CMC-related content
        for term in cmc_content_checks:
            if term.lower() in all_content.lower():
                cmc_content_checks[term] = True
        
        nist_matches = sum(nist_content_checks.values())
        cmc_matches = sum(cmc_content_checks.values())
        
        print(f"📊 Content Analysis:")
        print(f"   NIST-related terms found: {nist_matches}/{len(nist_content_checks)}")
        print(f"   CMC-related terms found: {cmc_matches}/{len(cmc_content_checks)}")
        
        # Verify specific section content
        for section in document['sections']:
            print(f"\n📄 Section: {section['title']}")
            print(f"   Length: {len(section['content'])} characters")
            
            if "NIST" in section['title']:
                if "NIST" in section['content'] or "National Institute" in section['content']:
                    print("   ✅ Contains NIST-specific content")
                else:
                    print("   ❌ Missing NIST-specific content")
            
            if "instruments" in section['title'].lower():
                if any(term in section['content'].lower() for term in ['mass spectrometry', 'chromatography', 'analytical']):
                    print("   ✅ Contains instrument-specific content")
                else:
                    print("   ❌ Missing instrument-specific content")
        
        # Final assessment
        if nist_matches >= 3 and cmc_matches <= 1:
            print(f"\n🎉 SUCCESS: Content is relevant to NIST documents (not CMC boilerplate)")
            return True
        else:
            print(f"\n❌ FAILED: Content appears to be generic CMC boilerplate")
            return False
            
    finally:
        os.unlink(temp_file_path)

def test_section_ids_and_navigation():
    """Test that section IDs are properly mapped for navigation."""
    
    # Get templates to find one with sections
    response = requests.get(f"{BACKEND_URL}/api/templates")
    templates = response.json()
    
    if not templates:
        print("❌ No templates available")
        return False
    
    # Use a template with multiple sections
    template = None
    for t in templates:
        if len(t.get('toc', [])) >= 3:
            template = t
            break
    
    if not template:
        print("❌ No suitable template found")
        return False
    
    print(f"✅ Using template: {template['name']} with {len(template['toc'])} sections")
    
    # Generate document
    response = requests.post(f"{BACKEND_URL}/api/generation/generate/{SESSION_ID}", json=template)
    
    if response.status_code != 200:
        print(f"❌ Generation failed: {response.status_code}")
        return False
    
    document = response.json()
    
    # Check that each section has a unique ID and title
    section_ids = set()
    section_titles = set()
    
    for section in document['sections']:
        if section['id'] in section_ids:
            print(f"❌ Duplicate section ID: {section['id']}")
            return False
        section_ids.add(section['id'])
        
        if section['title'] in section_titles:
            print(f"❌ Duplicate section title: {section['title']}")
            return False
        section_titles.add(section['title'])
        
        print(f"✅ Section: {section['title']} -> ID: {section['id']}")
    
    print(f"✅ All {len(document['sections'])} sections have unique IDs and titles")
    return True

if __name__ == "__main__":
    print("🧪 Testing Navigation and Content Fixes")
    print("=" * 60)
    
    print("\n1️⃣ Testing NIST Content Generation (No CMC Boilerplate)...")
    nist_test = test_nist_content_generation()
    
    print("\n2️⃣ Testing Section ID Mapping for Navigation...")
    nav_test = test_section_ids_and_navigation()
    
    print("\n" + "=" * 60)
    if nist_test and nav_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Content is generated from uploaded documents (not CMC boilerplate)")
        print("✅ Section navigation IDs are properly mapped")
    else:
        print("❌ Some tests failed:")
        if not nist_test:
            print("   - Content generation still uses CMC boilerplate")
        if not nav_test:
            print("   - Section navigation IDs are not properly mapped")
    
    exit(0 if (nist_test and nav_test) else 1)
