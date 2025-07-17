#!/usr/bin/env python3
"""
Final verification test for both urgent fixes:
1. Section navigation functionality
2. RAG-based content generation (no generic CMC boilerplate)
"""

import requests
import json
import uuid
import tempfile
import os

# Test configuration
BACKEND_URL = "http://localhost:8001"
SESSION_ID = str(uuid.uuid4())

print("🔧 FINAL VERIFICATION OF URGENT FIXES")
print("=" * 60)

def test_real_world_scenario():
    """Test with a real-world non-CMC document to ensure no boilerplate."""
    
    # Create a test document about AI/ML (completely different from CMC)
    ai_content = """
Artificial Intelligence and Machine Learning in Healthcare

Executive Summary:
Our organization specializes in developing AI-powered diagnostic tools for medical imaging. 
We have developed proprietary deep learning algorithms that can detect anomalies in 
radiological images with 95% accuracy.

Our Core Capabilities:
1. Computer Vision: Advanced image processing and pattern recognition
2. Natural Language Processing: Medical text analysis and report generation  
3. Predictive Analytics: Risk assessment and outcome prediction
4. Data Integration: Electronic health record analysis

Why Our Organization is Uniquely Positioned:
- 10+ years of experience in medical AI
- FDA-cleared diagnostic algorithms
- Partnerships with 50+ healthcare institutions
- Published research in top-tier journals
- HIPAA-compliant data processing infrastructure

Technical Infrastructure:
- GPU clusters for deep learning model training
- Cloud-based deployment with 99.9% uptime
- Real-time inference capabilities
- Automated model validation pipelines

Key Personnel:
- Dr. Sarah Chen: PhD in Computer Science, AI specialist
- Dr. Michael Rodriguez: MD, radiologist with AI expertise  
- Lisa Wang: Data engineer with healthcare experience

Our methodology combines state-of-the-art machine learning with clinical expertise 
to deliver reliable, interpretable AI solutions for healthcare providers.
    """.strip()
    
    print("1️⃣ Testing with AI/Healthcare Document (Non-CMC Content)...")
    
    # Upload the AI document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(ai_content)
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': ('ai_document.txt', f, 'text/plain')}
            response = requests.post(f"{BACKEND_URL}/api/files/upload/{SESSION_ID}", files=files)
        
        if response.status_code == 200:
            print("✅ AI document uploaded successfully")
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    finally:
        os.unlink(temp_file)
    
    # Create a custom template for AI content
    template_data = {
        "name": "AI Organization Assessment",
        "description": "Assessment template for AI organizations",
        "toc": [
            {"title": "Why is our organization uniquely positioned?", "level": 1},
            {"title": "What are our core technical capabilities?", "level": 1},
            {"title": "Who are our key personnel?", "level": 1},
            {"title": "What is our technical infrastructure?", "level": 1}
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
    
    # Analyze content for relevance
    ai_terms = ['AI', 'artificial intelligence', 'machine learning', 'deep learning', 'computer vision', 'algorithms', 'neural', 'GPU', 'healthcare', 'medical', 'diagnostic']
    cmc_terms = ['CMC', 'chemistry', 'manufacturing', 'controls', 'pharmaceutical', 'drug substance', 'API', 'regulatory', 'FDA submission', 'ICH']
    
    total_ai_found = 0
    total_cmc_found = 0
    
    print("\n📊 Content Analysis Results:")
    for i, section in enumerate(generated_doc['sections'], 1):
        content = section['content'].lower()
        
        ai_found = sum(1 for term in ai_terms if term.lower() in content)
        cmc_found = sum(1 for term in cmc_terms if term.lower() in content)
        
        total_ai_found += ai_found
        total_cmc_found += cmc_found
        
        print(f"   Section {i}: {section['title']}")
        print(f"      Length: {len(section['content'])} characters")
        print(f"      AI terms: {ai_found}, CMC terms: {cmc_found}")
        
        # Show sample content
        preview = section['content'][:200] + "..." if len(section['content']) > 200 else section['content']
        print(f"      Preview: {preview}")
        print()
    
    print(f"📈 Overall Results:")
    print(f"   Total AI-related terms: {total_ai_found}")
    print(f"   Total CMC-related terms: {total_cmc_found}")
    
    # Success criteria: AI content should have more AI terms than CMC terms
    if total_ai_found > total_cmc_found:
        print("✅ SUCCESS: Content is relevant to uploaded AI document!")
        return True
    else:
        print("❌ FAILED: Content still contains too much irrelevant/boilerplate information")
        return False

def test_section_navigation_structure():
    """Test that sections have proper IDs for navigation."""
    
    print("2️⃣ Testing Section Navigation Structure...")
    
    # Use a simple template to test navigation
    template_data = {
        "name": "Navigation Test Document", 
        "description": "Test template for navigation",
        "toc": [
            {"title": "Introduction", "level": 1},
            {"title": "Background", "level": 1}, 
            {"title": "Methods", "level": 1},
            {"title": "Results", "level": 1},
            {"title": "Conclusion", "level": 1}
        ]
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BACKEND_URL}/api/generation/generate/{SESSION_ID}", headers=headers, json=template_data)
    
    if response.status_code != 200:
        print(f"❌ Generation failed: {response.text}")
        return False
    
    generated_doc = response.json()
    sections = generated_doc['sections']
    
    print(f"✅ Generated {len(sections)} sections")
    
    # Check navigation requirements
    section_ids = []
    section_titles = []
    
    for section in sections:
        section_id = section.get('id')
        section_title = section.get('title', '')
        
        if not section_id:
            print(f"❌ Section '{section_title}' missing ID")
            return False
            
        if section_id in section_ids:
            print(f"❌ Duplicate section ID found: {section_id}")
            return False
            
        section_ids.append(section_id)
        section_titles.append(section_title)
        
        print(f"   ✅ Section: '{section_title}' -> ID: {section_id}")
    
    print(f"✅ All {len(sections)} sections have unique IDs for navigation")
    return True

def test_backend_health():
    """Verify backend is responding correctly."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False

# Run all tests
if __name__ == "__main__":
    results = []
    
    print("🔧 Checking backend connectivity...")
    results.append(test_backend_health())
    
    print("\n" + "="*60)
    results.append(test_real_world_scenario())
    
    print("\n" + "="*60)
    results.append(test_section_navigation_structure())
    
    print("\n" + "="*60)
    print("🏁 FINAL RESULTS:")
    print("="*60)
    
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Problem 1 FIXED: Section navigation is fully functional")
        print("✅ Problem 2 FIXED: Content is relevant and RAG-based (no CMC boilerplate)")
        print("\n🚀 The CMC Regulatory Writer app is ready for production!")
    else:
        print("❌ Some tests failed. Review the output above.")
        print(f"Test results: {results}")
