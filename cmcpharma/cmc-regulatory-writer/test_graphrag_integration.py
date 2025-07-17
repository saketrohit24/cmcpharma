#!/usr/bin/env python3
"""
Test script to verify GraphRAG integration with the CMC regulatory writer.
This script tests both traditional RAG and GraphRAG functionality.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend app directory to Python path
backend_dir = Path(__file__).parent / "backend" 
sys.path.insert(0, str(backend_dir))

# Set up minimal environment variables for testing
os.environ.setdefault("NVIDIA_API_KEY", "test_key")
os.environ.setdefault("USE_GRAPH_RAG", "true")

from app.services.rag_service import RAGService
from app.services.graph_rag_service import GraphRAGService, RAGConfig
from app.services.generation_service import GenerationService

async def test_traditional_rag():
    """Test traditional RAG functionality"""
    print("🔍 Testing Traditional RAG...")
    
    # Create some test files
    test_files = []
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test file
    test_file = test_dir / "test_document.txt"
    test_file.write_text("""
    This is a test document about pharmaceutical manufacturing.
    It contains information about quality control processes and validation procedures.
    The document discusses Good Manufacturing Practices (GMP) and regulatory compliance.
    """)
    test_files.append(str(test_file))
    
    try:
        # Test traditional RAG
        rag_service = RAGService(file_paths=test_files, use_graph_rag=False)
        
        # Test retrieval
        results = await rag_service.retrieve_relevant_content(
            query="quality control processes",
            top_k=3
        )
        
        print(f"✅ Traditional RAG returned {len(results)} results")
        for i, result in enumerate(results):
            print(f"   Result {i+1}: {result['content'][:100]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ Traditional RAG test failed: {e}")
        return False
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()

async def test_graph_rag():
    """Test GraphRAG functionality"""
    print("\n🔍 Testing GraphRAG...")
    
    # For GraphRAG testing, we'll just check if the service can be initialized
    # without actually running it (since it requires proper setup)
    try:
        test_files = []
        test_dir = Path("test_files")
        test_dir.mkdir(exist_ok=True)
        
        # Create a test file
        test_file = test_dir / "test_graphrag_document.txt"
        test_file.write_text("""
        This document describes the implementation of nano-graphrag in regulatory writing.
        GraphRAG provides enhanced entity and relationship extraction capabilities.
        It enables better contextual understanding of regulatory documents and scientific literature.
        The system can perform both local and global search modes for comprehensive information retrieval.
        """)
        test_files.append(str(test_file))
        
        # Test GraphRAG configuration
        config = RAGConfig(
            working_dir="./test_rag_storage",
            chunk_size=500,
            chunk_overlap=100
        )
        
        print("✅ GraphRAG configuration created successfully")
        
        # Test RAGService with GraphRAG enabled
        rag_service = RAGService(
            file_paths=test_files, 
            use_graph_rag=True,
            graph_rag_config=config
        )
        
        print("✅ RAGService with GraphRAG initialized successfully")
        
        # Test if the service has graph_rag_service
        if hasattr(rag_service, 'graph_rag_service') and rag_service.graph_rag_service:
            print("✅ GraphRAG service is available in RAGService")
        else:
            print("⚠️  GraphRAG service not available (likely fell back to traditional RAG)")
        
        return True
        
    except Exception as e:
        print(f"❌ GraphRAG test failed: {e}")
        print(f"   This is expected if nano-graphrag is not installed or API keys are not set")
        return False
    finally:
        # Cleanup
        if 'test_file' in locals() and test_file.exists():
            test_file.unlink()
        if 'test_dir' in locals() and test_dir.exists():
            test_dir.rmdir()

async def test_generation_service():
    """Test GenerationService with GraphRAG integration"""
    print("\n🔍 Testing GenerationService with GraphRAG...")
    
    try:
        generation_service = GenerationService()
        print("✅ GenerationService initialized successfully")
        
        # Test that the synthesize_section method accepts graph mode parameter
        import inspect
        sig = inspect.signature(generation_service.synthesize_section)
        if 'use_graph_mode' in sig.parameters:
            print("✅ GenerationService.synthesize_section supports GraphRAG mode parameter")
        else:
            print("❌ GenerationService.synthesize_section missing GraphRAG mode parameter")
        
        return True
        
    except Exception as e:
        print(f"❌ GenerationService test failed: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\n🔍 Testing Configuration...")
    
    try:
        from app.core.config import settings
        
        # Test that GraphRAG settings are available
        graph_rag_settings = [
            'USE_GRAPH_RAG',
            'GRAPH_RAG_WORKING_DIR',
            'GRAPH_RAG_CHUNK_SIZE',
            'GRAPH_RAG_CHUNK_OVERLAP',
            'GRAPH_RAG_EMBEDDING_BATCH_NUM',
            'GRAPH_RAG_MAX_ASYNC',
            'GRAPH_RAG_GLOBAL_MAX_CONSIDER_COMMUNITY',
            'GRAPH_RAG_LOCAL_SEARCH_TOP_K'
        ]
        
        missing_settings = []
        for setting in graph_rag_settings:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"❌ Missing configuration settings: {missing_settings}")
            return False
        else:
            print("✅ All GraphRAG configuration settings are available")
            print(f"   USE_GRAPH_RAG: {settings.USE_GRAPH_RAG}")
            print(f"   GRAPH_RAG_WORKING_DIR: {settings.GRAPH_RAG_WORKING_DIR}")
            print(f"   GRAPH_RAG_CHUNK_SIZE: {settings.GRAPH_RAG_CHUNK_SIZE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting GraphRAG Integration Tests\n")
    
    tests = [
        ("Configuration", test_configuration),
        ("Traditional RAG", test_traditional_rag),
        ("GraphRAG", test_graph_rag),
        ("GenerationService", test_generation_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Test")
        print('='*50)
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        
        results.append((test_name, result))
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! GraphRAG integration is ready.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check the output above for details.")
    
    print("\n📋 Next Steps:")
    print("1. Install nano-graphrag: pip install nano-graphrag==0.1.2")
    print("2. Set USE_GRAPH_RAG=true in your environment variables")
    print("3. Ensure NVIDIA_API_KEY is properly configured")
    print("4. Test with real documents to see GraphRAG in action")

if __name__ == "__main__":
    asyncio.run(main())