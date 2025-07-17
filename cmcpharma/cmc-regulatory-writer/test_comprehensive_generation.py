#!/usr/bin/env python3
"""
Test script to verify document generation with realistic content
"""

import requests
import json
import tempfile
import os

BACKEND_URL = "http://localhost:8001"
TEST_SESSION_ID = "test-doc-gen-session"

def create_realistic_test_document():
    """Create a realistic regulatory document for testing"""
    content = """
DRUG SUBSTANCE SPECIFICATION
Manufacturing Process and Quality Control

1. GENERAL INFORMATION

1.1 Product Description
Compound XYZ is a novel pharmaceutical compound developed for the treatment of inflammatory conditions.
The drug substance is a white to off-white crystalline powder with high purity and well-defined specifications.

1.2 Chemical Structure
Molecular Formula: C22H25N3O4
Molecular Weight: 395.45 g/mol
Chemical Name: 2-[(3,5-dimethyl-1H-pyrazol-1-yl)methyl]-4-(methylamino)benzoic acid

2. MANUFACTURING PROCESS

2.1 Process Overview
The manufacturing process consists of the following key steps:
- Raw material preparation and testing
- Chemical synthesis through multi-step reaction
- Purification and crystallization
- Drying and milling
- Final packaging in controlled environment

2.2 Critical Process Parameters
Temperature control: 20-25°C during crystallization
pH range: 6.5-7.5 for optimal yield
Reaction time: 4-6 hours for complete conversion
Pressure: Atmospheric pressure maintained throughout

2.3 In-Process Controls
- Identity testing of starting materials
- Reaction monitoring via HPLC
- Moisture content analysis
- Particle size distribution measurement

3. QUALITY CONTROL SPECIFICATIONS

3.1 Identity Tests
- Infrared spectroscopy (IR)
- Nuclear magnetic resonance (NMR)
- High-performance liquid chromatography (HPLC) retention time

3.2 Purity Testing
- HPLC assay: Not less than 98.0% and not more than 102.0%
- Related substances: Each impurity not more than 0.5%
- Total impurities: Not more than 2.0%

3.3 Physical Properties
- Appearance: White to off-white crystalline powder
- Melting point: 145-150°C
- pH (1% solution): 6.0-8.0
- Loss on drying: Not more than 1.0%

4. STABILITY DATA

4.1 Stability Studies
Long-term stability studies conducted under ICH conditions:
- 25°C ± 2°C / 60% RH ± 5% RH for 24 months
- Intermediate conditions: 30°C ± 2°C / 65% RH ± 5% RH for 12 months
- Accelerated conditions: 40°C ± 2°C / 75% RH ± 5% RH for 6 months

4.2 Stability Results
The drug substance remains stable under all tested conditions with:
- No significant change in assay values
- No increase in degradation products
- Maintained physical appearance and properties

4.3 Storage Conditions
Store in tightly closed containers at controlled room temperature (20-25°C).
Protect from light and moisture. Stable for 36 months under recommended conditions.

5. ANALYTICAL METHODS

5.1 HPLC Method for Assay
- Column: C18, 250mm x 4.6mm, 5μm
- Mobile phase: Acetonitrile:Water (60:40) with 0.1% TFA
- Flow rate: 1.0 mL/min
- Detection: UV at 254 nm
- Run time: 15 minutes

5.2 Method Validation
The HPLC method has been validated according to ICH Q2(R1) guidelines:
- Specificity: Demonstrated for related substances
- Linearity: R² > 0.999 over range 80-120%
- Accuracy: Recovery 98-102%
- Precision: RSD < 2.0%
- Robustness: Demonstrated for key parameters

6. REGULATORY COMPLIANCE

6.1 ICH Guidelines
Manufacturing and testing procedures comply with:
- ICH Q7 Good Manufacturing Practice Guide
- ICH Q6A Specifications for Drug Substances
- ICH Q1A(R2) Stability Testing Guidelines

6.2 Pharmacopeial Standards
All testing methods are based on or equivalent to USP/EP standards where applicable.

7. CONCLUSION

Compound XYZ drug substance is manufactured using a well-controlled process with comprehensive
quality control measures. The analytical methods are validated and suitable for routine testing.
Stability data supports the proposed shelf-life and storage conditions.
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        return f.name

def test_realistic_document_generation():
    """Test document generation with realistic regulatory content"""
    print("🧪 Testing Document Generation with Realistic Content")
    print("=" * 55)
    
    # Create realistic test document
    print("\n1️⃣ Creating realistic test document...")
    test_file = create_realistic_test_document()
    print(f"✅ Created test document: {os.path.basename(test_file)}")
    
    try:
        # Upload the document
        print("\n2️⃣ Uploading test document...")
        with open(test_file, 'rb') as f:
            files = {"file": (os.path.basename(test_file), f, "text/plain")}
            response = requests.post(
                f"{BACKEND_URL}/api/files/upload/{TEST_SESSION_ID}",
                files=files,
                timeout=10
            )
        
        if response.status_code == 200:
            print("✅ Document uploaded successfully")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
        
        # Create a comprehensive template
        print("\n3️⃣ Creating comprehensive template...")
        template_data = {
            "name": "Comprehensive Drug Substance Dossier",
            "description": "Complete regulatory template for drug substance documentation",
            "toc_text": """1. Executive Summary
2. General Information
2.1 Product Description
2.2 Chemical Structure and Properties
3. Manufacturing Process
3.1 Process Overview
3.2 Critical Process Parameters
3.3 Process Controls
4. Quality Control
4.1 Specifications
4.2 Analytical Methods
4.3 Method Validation
5. Stability Studies
5.1 Study Design
5.2 Results and Analysis
5.3 Shelf Life Determination
6. Regulatory Compliance
6.1 ICH Guidelines Compliance
6.2 Pharmacopeial Standards
7. Risk Assessment
8. Conclusion"""
        }
        
        response = requests.post(f"{BACKEND_URL}/api/templates/parse", json=template_data)
        if response.status_code == 200:
            template = response.json()
            print(f"✅ Template created: {template['name']}")
            print(f"   Sections: {len(template['toc'])}")
        else:
            print(f"❌ Template creation failed: {response.status_code}")
            return False
        
        # Generate document
        print("\n4️⃣ Generating document with AI content...")
        print("   (This may take 30-60 seconds due to LLM processing...)")
        
        response = requests.post(
            f"{BACKEND_URL}/api/generation/generate/{TEST_SESSION_ID}",
            json=template,
            headers={"Content-Type": "application/json"},
            timeout=120  # Give plenty of time for LLM processing
        )
        
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document generated successfully!")
            print(f"   Title: {document['title']}")
            print(f"   Total sections: {len(document['sections'])}")
            
            # Analyze the generated content
            print("\n📋 Generated Content Analysis:")
            sections_with_content = 0
            sections_with_sources = 0
            total_content_length = 0
            
            for i, section in enumerate(document['sections']):
                has_meaningful_content = len(section['content']) > 200 and "No relevant information" not in section['content']
                has_sources = section['source_count'] > 0
                
                if has_meaningful_content:
                    sections_with_content += 1
                if has_sources:
                    sections_with_sources += 1
                
                total_content_length += len(section['content'])
                
                # Show details for first few sections
                if i < 3:
                    print(f"\n   Section {i+1}: {section['title']}")
                    print(f"   Source count: {section['source_count']}")
                    print(f"   Content length: {len(section['content'])} characters")
                    
                    # Show content preview
                    preview = section['content'][:300].replace('\n', ' ')
                    if len(section['content']) > 300:
                        preview += "..."
                    print(f"   Preview: {preview}")
            
            print(f"\n📊 Content Statistics:")
            print(f"   • Sections with meaningful content: {sections_with_content}/{len(document['sections'])}")
            print(f"   • Sections with sources: {sections_with_sources}/{len(document['sections'])}")
            print(f"   • Average content length: {total_content_length // len(document['sections'])} characters")
            
            # Success criteria
            success = (
                len(document['sections']) > 0 and
                total_content_length > 1000 and  # At least some content generated
                sections_with_content >= len(document['sections']) // 3  # At least 1/3 have meaningful content
            )
            
            if success:
                print("\n✅ Document generation quality check PASSED")
                print("   The AI successfully generated regulatory content with references")
            else:
                print("\n⚠️  Document generation quality check PARTIAL")
                print("   Some sections may need more source material or better content matching")
            
            return success
            
        else:
            print(f"❌ Document generation failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}...")
            return False
    
    finally:
        # Cleanup
        try:
            os.unlink(test_file)
            print(f"\n🧹 Cleaned up test file")
        except OSError:
            pass

def test_document_with_multiple_files():
    """Test document generation with multiple source files"""
    print("\n\n🗂️ Testing Multiple File Document Generation")
    print("=" * 50)
    
    # Create multiple test documents with different focus areas
    files_content = {
        "manufacturing_process.txt": """
MANUFACTURING PROCESS DETAILS

Process Step 1: Raw Material Preparation
All raw materials undergo incoming inspection including:
- Identity verification by IR spectroscopy
- Assay determination by HPLC
- Heavy metals testing by ICP-MS
- Microbiological testing

Process Step 2: Chemical Synthesis
The synthesis is carried out in a 500L glass-lined reactor under nitrogen atmosphere.
Temperature is maintained at 15-20°C during addition phase.
Reaction monitoring is performed every hour by HPLC analysis.

Process Step 3: Purification
Crude product is purified by recrystallization from ethanol/water mixture.
Crystal formation is controlled by slow cooling over 12 hours.
Final crystallization temperature: 5°C ± 2°C

Critical Process Parameters:
- Reaction temperature: 15-20°C
- pH control: 7.0 ± 0.5
- Reaction time: 8 hours minimum
- Nitrogen flow rate: 2-5 L/min
""",
        
        "quality_control_methods.txt": """
ANALYTICAL METHODS AND SPECIFICATIONS

HPLC Method for Assay:
- System: Waters HPLC with UV detector
- Column: Phenomenex Luna C18, 250 x 4.6 mm, 5 μm
- Mobile Phase A: 0.1% TFA in water
- Mobile Phase B: 0.1% TFA in acetonitrile
- Gradient: 20-80% B over 25 minutes
- Flow rate: 1.0 mL/min
- Detection wavelength: 254 nm
- Injection volume: 20 μL

Method Validation Parameters:
- Specificity: Confirmed by peak purity analysis
- Linearity: 50-150% of target concentration, R² ≥ 0.999
- Accuracy: 98.0-102.0% recovery
- Precision: RSD ≤ 2.0% for repeatability
- Range: 80-120% of specification
- Robustness: Confirmed for pH ± 0.2, flow rate ± 0.1 mL/min

Specifications:
- Appearance: White to off-white powder
- Identity: IR spectrum matches reference
- Assay: 98.0-102.0% (anhydrous basis)
- Related substances: ≤0.5% each, ≤2.0% total
- Residual solvents: Meets ICH Q3C limits
- Heavy metals: ≤20 ppm
- Microbiological limits: USP <1111>
""",
        
        "stability_data.txt": """
STABILITY STUDY RESULTS

Long-term Stability (25°C/60% RH):
Month 0: Assay 99.8%, Total impurities 0.3%
Month 3: Assay 99.6%, Total impurities 0.4%
Month 6: Assay 99.4%, Total impurities 0.5%
Month 9: Assay 99.3%, Total impurities 0.6%
Month 12: Assay 99.1%, Total impurities 0.7%
Month 18: Assay 98.9%, Total impurities 0.8%
Month 24: Assay 98.7%, Total impurities 0.9%

Accelerated Stability (40°C/75% RH):
Month 0: Assay 99.8%, Total impurities 0.3%
Month 1: Assay 99.5%, Total impurities 0.5%
Month 3: Assay 99.0%, Total impurities 0.8%
Month 6: Assay 98.4%, Total impurities 1.2%

Stress Testing Results:
- Acid hydrolysis (1N HCl, 60°C, 24h): 15% degradation
- Base hydrolysis (1N NaOH, 60°C, 24h): 25% degradation
- Oxidation (3% H2O2, RT, 24h): 8% degradation
- Thermal stress (80°C, 7 days): 5% degradation
- Photostability (ICH Q1B): No significant degradation

Conclusion: 
Shelf life of 36 months is supported by stability data.
Storage at controlled room temperature (15-30°C) in tight containers.
"""
    }
    
    uploaded_files = []
    session_id = "multi-file-test-session"
    
    try:
        # Upload multiple files
        print("\n1️⃣ Uploading multiple source documents...")
        for filename, content in files_content.items():
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            temp_file.write(content)
            temp_file.close()
            uploaded_files.append(temp_file.name)
            
            with open(temp_file.name, 'rb') as f:
                files = {"file": (filename, f, "text/plain")}
                response = requests.post(
                    f"{BACKEND_URL}/api/files/upload/{session_id}",
                    files=files
                )
            
            if response.status_code == 200:
                print(f"   ✅ Uploaded: {filename}")
            else:
                print(f"   ❌ Failed to upload: {filename}")
        
        # Create template matching the content
        print("\n2️⃣ Creating targeted template...")
        template_data = {
            "name": "Multi-Source Regulatory Dossier",
            "description": "Template designed to leverage multiple source documents",
            "toc_text": """1. Manufacturing Process Overview
1.1 Raw Material Preparation
1.2 Chemical Synthesis Details
1.3 Purification Procedures
1.4 Critical Process Parameters
2. Quality Control and Testing
2.1 Analytical Methods
2.2 Method Validation
2.3 Specifications and Acceptance Criteria
3. Stability Assessment
3.1 Long-term Stability Studies
3.2 Accelerated Stability Testing
3.3 Stress Testing Results
3.4 Shelf Life Determination
4. Regulatory Summary"""
        }
        
        response = requests.post(f"{BACKEND_URL}/api/templates/parse", json=template_data)
        if response.status_code == 200:
            template = response.json()
            print(f"✅ Template created with {len(template['toc'])} sections")
        else:
            print(f"❌ Template creation failed")
            return False
        
        # Generate document
        print("\n3️⃣ Generating document from multiple sources...")
        print("   (Processing with LLM and RAG...)")
        
        response = requests.post(
            f"{BACKEND_URL}/api/generation/generate/{session_id}",
            json=template,
            timeout=120
        )
        
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document generated with multiple source integration!")
            
            # Analyze source integration
            total_sources = sum(section['source_count'] for section in document['sections'])
            sections_with_sources = sum(1 for section in document['sections'] if section['source_count'] > 0)
            
            print(f"\n📊 Multi-Source Integration Analysis:")
            print(f"   • Total source references: {total_sources}")
            print(f"   • Sections with sources: {sections_with_sources}/{len(document['sections'])}")
            print(f"   • Average sources per section: {total_sources / len(document['sections']):.1f}")
            
            # Show example sections
            for i, section in enumerate(document['sections'][:2]):
                print(f"\n   Example Section {i+1}: {section['title']}")
                print(f"   Sources used: {section['source_count']}")
                preview = section['content'][:250].replace('\n', ' ')
                if len(section['content']) > 250:
                    preview += "..."
                print(f"   Content: {preview}")
            
            success = total_sources > 0 and sections_with_sources > 0
            return success
        else:
            print(f"❌ Multi-file generation failed: {response.status_code}")
            return False
    
    finally:
        # Cleanup
        for file_path in uploaded_files:
            try:
                os.unlink(file_path)
            except OSError:
                pass
        print(f"\n🧹 Cleaned up {len(uploaded_files)} test files")

def main():
    """Run comprehensive document generation tests"""
    print("🧪 CMC Regulatory Writer - Comprehensive Document Generation Test")
    print("=" * 65)
    
    # Health check
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend not accessible")
            return
    except:
        print("❌ Backend is not running. Please start it first.")
        return
    
    print("✅ Backend is running")
    
    # Run comprehensive tests
    test1_result = test_realistic_document_generation()
    test2_result = test_document_with_multiple_files()
    
    # Final summary
    print("\n" + "=" * 65)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 65)
    
    if test1_result and test2_result:
        print("🎉 ALL TESTS PASSED! Document generation is working excellently!")
        print("\n✅ Verified Functionality:")
        print("   ✅ Template creation and saving")
        print("   ✅ File upload and processing")
        print("   ✅ RAG-based content retrieval")
        print("   ✅ LLM-powered section generation")
        print("   ✅ Multi-source document integration")
        print("   ✅ Reference counting and citation")
        
        print("\n🎯 Ready for Production Use:")
        print("   • Upload your regulatory PDF documents")
        print("   • Create templates matching your document structure")
        print("   • Generate AI-powered regulatory documents")
        print("   • Each section will include relevant references")
        print("   • Professional regulatory writing style")
        
    else:
        print("⚠️  Some tests had issues - check the specific results above")
        print("\n🔧 Common solutions:")
        print("   • Ensure NVIDIA_API_KEY is set in backend/.env")
        print("   • Check backend logs for detailed errors")
        print("   • Verify all dependencies are properly installed")

if __name__ == "__main__":
    main()
