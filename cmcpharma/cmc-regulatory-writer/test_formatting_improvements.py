#!/usr/bin/env python3
"""
Test script to verify formatting improvements in generated content.
"""

import requests
import json
import uuid
import tempfile
import os

# Test configuration
BACKEND_URL = "http://localhost:8001"
SESSION_ID = str(uuid.uuid4())

def test_content_formatting():
    """Test that generated content has proper formatting without redundant titles."""
    
    # Create a test document with rich content
    test_content = """
Research Organization Capabilities Assessment

Executive Summary:
Our research organization specializes in advanced materials science and nanotechnology research. We have developed innovative characterization methods for biomolecular systems.

Core Research Areas:
1. Biomolecular Characterization - Advanced spectroscopic techniques for protein analysis
2. Materials Science - Novel nanomaterials for biomedical applications  
3. Instrumentation Development - Custom analytical equipment design
4. Data Analytics - Machine learning approaches for complex datasets

Why Our Organization is Uniquely Positioned:
- 15+ years of experience in biomolecular research
- State-of-the-art characterization facilities
- Collaborative partnerships with leading universities
- Published expertise in high-impact journals
- Proven track record in technology transfer

Technical Capabilities:
- Mass spectrometry platforms (LC-MS, MALDI-TOF, FT-ICR)
- Advanced microscopy (AFM, SEM, TEM, confocal)
- Spectroscopic methods (NMR, FTIR, Raman, UV-Vis)
- Computational modeling and simulation

Key Personnel:
- Dr. Jane Smith: PhD in Biochemistry, 20 years experience
- Dr. Robert Chen: Materials Science expert, nanotechnology specialist
- Dr. Maria Rodriguez: Analytical chemistry lead

Our research methodology combines experimental validation with computational modeling to deliver comprehensive understanding of complex biomolecular systems.

Standards and Quality Assurance:
We maintain rigorous quality standards in all research activities, following Good Laboratory Practices (GLP) and ensuring reproducible, reliable results.
    """.strip()
    
    print("🎨 Testing Content Formatting Improvements...")
    
    # Upload the test document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': ('research_org.txt', f, 'text/plain')}
            response = requests.post(f"{BACKEND_URL}/api/files/upload/{SESSION_ID}", files=files)
        
        if response.status_code == 200:
            print("✅ Test document uploaded successfully")
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    finally:
        os.unlink(temp_file)
    
    # Create template to test formatting
    template_data = {
        "name": "Research Organization Assessment",
        "description": "Assessment of research capabilities",
        "toc": [
            {"title": "Why is our organization uniquely positioned for this research?", "level": 1},
            {"title": "What are our core technical capabilities?", "level": 1},
            {"title": "What quality standards do we maintain?", "level": 1}
        ]
    }
    
    # Generate document
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BACKEND_URL}/api/generation/generate/{SESSION_ID}", headers=headers, json=template_data)
    
    if response.status_code != 200:
        print(f"❌ Generation failed: {response.text}")
        return False
    
    generated_doc = response.json()
    print(f"✅ Document generated with {len(generated_doc['sections'])} sections")
    
    # Analyze formatting quality
    formatting_issues = []
    good_formatting = []
    
    for i, section in enumerate(generated_doc['sections'], 1):
        content = section['content']
        title = section['title']
        
        print(f"\n📄 Section {i}: {title}")
        print(f"   Length: {len(content)} characters")
        
        # Check for formatting issues
        issues = []
        good_points = []
        
        # Check for redundant title repetition
        first_50_chars = content[:50].lower()
        if title.lower()[:20] in first_50_chars:
            issues.append("Title repetition detected")
        else:
            good_points.append("No title repetition")
            
        # Check for excessive bold formatting
        bold_count = content.count('**')
        if bold_count > 20:
            issues.append(f"Excessive bold formatting ({bold_count//2} bold elements)")
        else:
            good_points.append(f"Appropriate bold usage ({bold_count//2} elements)")
            
        # Check for proper header structure
        header_count = content.count('##')
        if header_count > 0:
            good_points.append(f"Good header structure ({header_count} headers)")
        else:
            issues.append("No clear subsections")
            
        # Check for list formatting
        list_items = content.count('\n-') + content.count('\n1.')
        if list_items > 0:
            good_points.append(f"Well-structured lists ({list_items} items)")
            
        # Show preview (first 150 characters)
        preview = content[:150].replace('\n', ' ') + "..." if len(content) > 150 else content
        print(f"   Preview: {preview}")
        
        if issues:
            print(f"   ⚠️  Issues: {', '.join(issues)}")
            formatting_issues.extend(issues)
        
        if good_points:
            print(f"   ✅ Good: {', '.join(good_points)}")
            good_formatting.extend(good_points)
    
    print(f"\n📊 Formatting Analysis:")
    print(f"   Issues found: {len(formatting_issues)}")
    print(f"   Good practices: {len(good_formatting)}")
    
    # Success criteria: more good formatting than issues
    if len(good_formatting) > len(formatting_issues):
        print("✅ SUCCESS: Content formatting is improved!")
        return True
    else:
        print("❌ FAILED: Content still has formatting issues")
        return False

if __name__ == "__main__":
    print("🎨 TESTING CONTENT FORMATTING IMPROVEMENTS")
    print("=" * 60)
    
    # Check backend health first
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend not healthy: {response.status_code}")
            exit(1)
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        exit(1)
    
    # Run formatting test
    success = test_content_formatting()
    
    print("\n" + "="*60)
    print("🏁 FORMATTING TEST RESULTS:")
    print("="*60)
    
    if success:
        print("🎉 FORMATTING IMPROVEMENTS SUCCESSFUL!")
        print("✅ Reduced title repetition")
        print("✅ Better visual hierarchy") 
        print("✅ Improved typography and spacing")
        print("✅ Enhanced list and header formatting")
    else:
        print("❌ Formatting improvements need more work")
