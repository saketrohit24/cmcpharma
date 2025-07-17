#!/usr/bin/env python3
"""
Simple test to verify the GraphRAG integration framework is working
without requiring nano-graphrag to be installed.
"""

import os
import sys
from pathlib import Path

# Add the backend app directory to Python path
backend_dir = Path(__file__).parent / "backend" 
sys.path.insert(0, str(backend_dir))

# Set up minimal environment variables for testing
os.environ.setdefault("NVIDIA_API_KEY", "test_key")
os.environ.setdefault("USE_GRAPH_RAG", "false")  # Test traditional RAG first

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    try:
        from app.services.rag_service import RAGService
        from app.services.graph_rag_service import GraphRAGService, RAGConfig
        from app.services.generation_service import GenerationService
        from app.core.config import settings
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    try:
        from app.core.config import settings
        
        # Check GraphRAG settings exist
        assert hasattr(settings, 'USE_GRAPH_RAG')
        assert hasattr(settings, 'GRAPH_RAG_WORKING_DIR')
        assert hasattr(settings, 'GRAPH_RAG_CHUNK_SIZE')
        
        print(f"   USE_GRAPH_RAG: {settings.USE_GRAPH_RAG}")
        print(f"   GRAPH_RAG_WORKING_DIR: {settings.GRAPH_RAG_WORKING_DIR}")
        print("✅ Configuration test passed")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_rag_service_initialization():
    """Test RAGService initialization with GraphRAG disabled"""
    print("\n🔍 Testing RAGService initialization (traditional RAG)...")
    try:
        from app.services.rag_service import RAGService
        from app.services.graph_rag_service import RAGConfig
        
        # Test with empty file paths (should not fail)
        rag_service = RAGService(
            file_paths=[], 
            use_graph_rag=False,
            graph_rag_config=None
        )
        
        assert not rag_service.use_graph_rag
        assert rag_service.graph_rag_service is None
        print("✅ Traditional RAGService initialization successful")
        return True
    except Exception as e:
        print(f"❌ RAGService initialization failed: {e}")
        return False

def test_rag_config():
    """Test RAGConfig creation"""
    print("\n🔍 Testing RAGConfig creation...")
    try:
        from app.services.graph_rag_service import RAGConfig
        
        config = RAGConfig(
            working_dir="./test_storage",
            chunk_size=800,
            chunk_overlap=100
        )
        
        assert config.working_dir == "./test_storage"
        assert config.chunk_size == 800
        assert config.chunk_overlap == 100
        print("✅ RAGConfig creation successful")
        return True
    except Exception as e:
        print(f"❌ RAGConfig creation failed: {e}")
        return False

def test_generation_service():
    """Test GenerationService with GraphRAG support"""
    print("\n🔍 Testing GenerationService...")
    try:
        from app.services.generation_service import GenerationService
        import inspect
        
        gen_service = GenerationService()
        
        # Check if synthesize_section has the new parameter
        sig = inspect.signature(gen_service.synthesize_section)
        if 'use_graph_mode' in sig.parameters:
            print("✅ GenerationService has GraphRAG mode parameter")
        else:
            print("❌ GenerationService missing GraphRAG mode parameter")
            return False
        
        print("✅ GenerationService test passed")
        return True
    except Exception as e:
        print(f"❌ GenerationService test failed: {e}")
        return False

def test_endpoint_integration():
    """Test that endpoints can import and use the services"""
    print("\n🔍 Testing endpoint integration...")
    try:
        from app.endpoints.generation import router
        from app.services.graph_rag_service import RAGConfig
        from app.core.config import settings
        
        # Test creating a RAGConfig from settings
        if settings.USE_GRAPH_RAG:
            config = RAGConfig(
                working_dir=settings.GRAPH_RAG_WORKING_DIR,
                chunk_size=settings.GRAPH_RAG_CHUNK_SIZE,
                chunk_overlap=settings.GRAPH_RAG_CHUNK_OVERLAP,
                embedding_batch_num=settings.GRAPH_RAG_EMBEDDING_BATCH_NUM,
                max_async=settings.GRAPH_RAG_MAX_ASYNC,
                global_max_consider_community=settings.GRAPH_RAG_GLOBAL_MAX_CONSIDER_COMMUNITY,
                local_search_top_k=settings.GRAPH_RAG_LOCAL_SEARCH_TOP_K
            )
            print("✅ GraphRAG config can be created from settings")
        
        print("✅ Endpoint integration test passed")
        return True
    except Exception as e:
        print(f"❌ Endpoint integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Simple GraphRAG Integration Tests\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("RAGService Initialization", test_rag_service_initialization),
        ("RAGConfig Creation", test_rag_config),
        ("GenerationService", test_generation_service),
        ("Endpoint Integration", test_endpoint_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Running {test_name} Test")
        print('='*50)
        
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
        print("\n🎉 All integration tests passed!")
        print("\n📋 GraphRAG Integration Status:")
        print("✅ Framework is properly integrated")
        print("✅ Configuration system working")
        print("✅ Service architecture ready")
        print("✅ Traditional RAG works as fallback")
        print("\n🔧 To enable GraphRAG:")
        print("1. Install nano-graphrag (when dependency issues are resolved)")
        print("2. Set USE_GRAPH_RAG=true")
        print("3. Configure your NVIDIA_API_KEY")
        print("4. Test with real documents")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed.")
        print("Integration framework needs fixes before proceeding.")

if __name__ == "__main__":
    main()