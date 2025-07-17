from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from ..core.config import settings
from .graph_rag_service import GraphRAGService, RAGConfig
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, file_paths: List[str], use_graph_rag: bool = False, graph_rag_config: Optional[RAGConfig] = None):
        if not settings.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is not set in the environment.")
        
        self.file_paths = file_paths
        self.use_graph_rag = use_graph_rag
        
        # Initialize GraphRAG if enabled
        if self.use_graph_rag:
            try:
                self.graph_rag_service = GraphRAGService(file_paths, graph_rag_config)
                logger.info("GraphRAG service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize GraphRAG, falling back to traditional RAG: {e}")
                self.use_graph_rag = False
                self.graph_rag_service = None
        else:
            self.graph_rag_service = None
        
        # Initialize traditional RAG (as fallback or primary)
        if not self.use_graph_rag:
            self.embeddings = NVIDIAEmbeddings(model="nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1", api_key=settings.NVIDIA_API_KEY)
            self.documents = self._load_and_split_docs()
            self.vector_store = self._create_vector_store()
            self.retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 20, "fetch_k": 40}
            ) if self.vector_store else None
        else:
            self.embeddings = None
            self.documents = []
            self.vector_store = None
            self.retriever = None

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
                
                # Add source metadata
                for page in pages:
                    page.metadata['source'] = os.path.basename(file_path)
                    page.metadata['file_path'] = file_path
                
                all_pages.extend(pages)
                print(f"Successfully loaded {len(pages)} pages from {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"Warning: Could not load {file_path}. Error: {e}")
        
        if not all_pages:
            print("Warning: No documents were successfully loaded.")
            return []
        
        print(f"Total documents loaded: {len(all_pages)}")
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
        split_docs = splitter.split_documents(all_pages)
        
        print(f"Documents split into {len(split_docs)} chunks")
        return split_docs

    def _create_vector_store(self):
        if not self.documents:
            print("Warning: No documents were loaded. RAG functionality will be disabled.")
            return None
        return FAISS.from_documents(self.documents, self.embeddings)

    def get_relevant_chunks(self, query: str, mode: str = "local") -> List[Document]:
        if self.use_graph_rag and self.graph_rag_service:
            return self.graph_rag_service.get_relevant_chunks(query, mode)
        elif self.retriever:
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
            file_paths: Optional filter by file paths (not used in GraphRAG)
            top_k: Number of results to return
            mode: "local" or "global" search mode (only for GraphRAG)
        """
        try:
            if self.use_graph_rag and self.graph_rag_service:
                # Use GraphRAG service
                return await self.graph_rag_service.retrieve_relevant_content(query, file_paths, top_k, mode)
            elif self.retriever:
                # Use traditional RAG
                docs = self.retriever.get_relevant_documents(query)
                results = []
                for i, doc in enumerate(docs[:top_k]):
                    results.append({
                        'content': doc.page_content,
                        'source': doc.metadata.get('source', f'Document {i+1}'),
                        'metadata': doc.metadata
                    })
                return results
            else:
                print("Warning: No retriever available. RAG is disabled.")
                return []
        except Exception as e:
            print(f"Error retrieving content: {e}")
            return []
    
    async def query_with_answer(self, query: str, mode: str = "local") -> Optional[str]:
        """
        Get a complete answer from GraphRAG (if enabled).
        Falls back to None for traditional RAG.
        
        Args:
            query: The search query
            mode: "local" or "global" search mode
        
        Returns:
            Complete answer as string, or None if using traditional RAG
        """
        if self.use_graph_rag and self.graph_rag_service:
            return await self.graph_rag_service.query_with_answer(query, mode)
        return None
    
    def add_documents(self, new_file_paths: List[str]):
        """Add new documents to the RAG system"""
        if self.use_graph_rag and self.graph_rag_service:
            self.graph_rag_service.add_documents(new_file_paths)
        else:
            # For traditional RAG, we'd need to reload everything
            self.file_paths.extend(new_file_paths)
            if self.embeddings:
                self.documents = self._load_and_split_docs()
                self.vector_store = self._create_vector_store()
                self.retriever = self.vector_store.as_retriever(
                    search_type="mmr",
                    search_kwargs={"k": 20, "fetch_k": 40}
                ) if self.vector_store else None