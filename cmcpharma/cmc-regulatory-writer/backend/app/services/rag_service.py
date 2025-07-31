from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from ..core.config import settings
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, file_paths: List[str]):
        if not settings.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is not set in the environment.")
        
        print("🚀 Initializing RAG with SPEED optimizations...")
        self.file_paths = file_paths
        
        # Try FASTER embedding model
        self.embeddings = NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-e5-v5",  # Try different model
            api_key=settings.NVIDIA_API_KEY
        )
        self.documents = self._load_and_split_docs()
        self.vector_store = self._create_vector_store()
        # OPTIMIZED retriever settings for speed
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",  # Changed from "mmr" for speed
            search_kwargs={"k": 5, "fetch_k": 8}  # Further reduced for speed
        ) if self.vector_store else None
        
        print("✅ RAG initialized successfully")

    def _load_and_split_docs(self) -> List[Document]:
        all_pages = []
        for file_path in self.file_paths:
            try:
                # Determine file type and use appropriate loader
                file_extension = os.path.splitext(file_path)[1].lower()
                
                if file_extension == '.pdf':
                    loader = PyPDFLoader(file_path)
                elif file_extension in ['.txt', '.md']:
                    loader = TextLoader(file_path, encoding='utf-8')
                elif file_extension in ['.doc', '.docx']:
                    loader = UnstructuredWordDocumentLoader(file_path)
                else:
                    # Try to load as text file as fallback
                    print(f"Unknown file type {file_extension}, trying as text file: {file_path}")
                    loader = TextLoader(file_path, encoding='utf-8')
                
                pages = loader.load()
                
                # Add source metadata while preserving existing metadata
                for page in pages:
                    # Preserve original metadata (especially page numbers from PDF)
                    original_metadata = page.metadata.copy()
                    page.metadata['source'] = os.path.basename(file_path)
                    page.metadata['file_path'] = file_path
                    
                    # Ensure page number is preserved from PDF loader
                    if 'page' in original_metadata:
                        page.metadata['page'] = original_metadata['page']
                    elif hasattr(page, 'page_number'):
                        page.metadata['page'] = page.page_number
                    else:
                        # Try to extract from source metadata if available
                        page_num = original_metadata.get('page_number', 1)
                        page.metadata['page'] = page_num
                
                all_pages.extend(pages)
                print(f"Successfully loaded {len(pages)} pages from {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"Warning: Could not load {file_path}. Error: {e}")
        
        if not all_pages:
            print("Warning: No documents were successfully loaded.")
            return []
        
        print(f"Total documents loaded: {len(all_pages)}")
        
        # FASTER document splitting - smaller chunks for speed
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,      # FURTHER REDUCED for faster processing
            chunk_overlap=50     # FURTHER REDUCED for speed
        )
        split_docs = splitter.split_documents(all_pages)
        
        print(f"⚡ Fast-split documents into {len(split_docs)} chunks")
        return split_docs

    def _create_vector_store(self):
        if not self.documents:
            print("Warning: No documents were loaded. RAG functionality will be disabled.")
            return None
        return FAISS.from_documents(self.documents, self.embeddings)

    def get_relevant_chunks(self, query: str, mode: str = "local") -> List[Document]:
        if self.retriever:
            return self.retriever.get_relevant_documents(query)
        else:
            print("Warning: No retriever available. RAG is disabled.")
            return []
    
    async def retrieve_relevant_content(self, query: str, file_paths: List[str] = None, top_k: int = 5, mode: str = "local") -> List[dict]:
        """
        Retrieve relevant content for document generation.
        Returns a list of dictionaries with content and source information.
        
        Args:
            query: The search query
            file_paths: Optional filter by file paths (not used)
            top_k: Number of results to return
            mode: Ignored (was used for GraphRAG)
        """
        try:
            if self.retriever:
                # Use traditional RAG
                docs = self.retriever.get_relevant_documents(query)
                results = []
                for i, doc in enumerate(docs[:top_k]):
                    # Extract page number from metadata
                    page_num = doc.metadata.get('page', doc.metadata.get('page_number', 1))
                    
                    results.append({
                        'content': doc.page_content,
                        'source': doc.metadata.get('source', f'Document {i+1}'),
                        'page': page_num,
                        'metadata': doc.metadata
                    })
                    print(f"📄 Retrieved from {doc.metadata.get('source', 'Unknown')}, page {page_num}: {doc.page_content[:100]}...")
                return results
            else:
                print("Warning: No retriever available. RAG is disabled.")
                return []
        except Exception as e:
            print(f"Error retrieving content: {e}")
            return []
    
    def add_documents(self, new_file_paths: List[str]):
        """Add new documents to the RAG system"""
        # For traditional RAG, we need to reload everything
        self.file_paths.extend(new_file_paths)
        if self.embeddings:
            self.documents = self._load_and_split_docs()
            self.vector_store = self._create_vector_store()
            self.retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 20, "fetch_k": 40}
            ) if self.vector_store else None