from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from nano_graphrag import GraphRAG, QueryParam
from nano_graphrag.base import BaseKVStorage
from ..core.config import settings
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    """Configuration for GraphRAG service"""
    working_dir: str = "./rag_storage"
    chunk_size: int = 1200
    chunk_overlap: int = 200
    embedding_batch_num: int = 32
    max_async: int = 16
    global_max_consider_community: int = 512
    local_search_top_k: int = 20
    
class GraphRAGService:
    """
    Simplified Graph-based RAG using nano-graphrag.
    This provides better retrieval through entity and relationship extraction.
    """
    
    def __init__(self, file_paths: List[str], config: Optional[RAGConfig] = None):
        if not settings.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is not set in the environment.")
        
        self.file_paths = file_paths
        self.config = config or RAGConfig()
        
        # Initialize embeddings
        self.embeddings = NVIDIAEmbeddings(
            model="nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1",
            api_key=settings.NVIDIA_API_KEY
        )
        
        # Create custom embedding function for nano-graphrag
        self.embedding_func = self._create_embedding_func()
        
        # Initialize nano-graphrag
        self.graph_rag = GraphRAG(
            working_dir=self.config.working_dir,
            enable_llm_cache=True,
            
            # Use NVIDIA embeddings
            embedding_func=self.embedding_func,
            embedding_batch_num=self.config.embedding_batch_num,
            embedding_func_max_async=self.config.max_async,
            
            # You can customize LLM functions here if needed
            # best_model_func=your_custom_llm_func,
            # cheap_model_func=your_cheap_llm_func,
        )
        
        # Load documents
        self._load_documents()
    
    def _create_embedding_func(self):
        """Create embedding function compatible with nano-graphrag"""
        async def nvidia_embedding_func(texts: List[str]) -> List[List[float]]:
            try:
                # Use NVIDIA embeddings
                embeddings = await asyncio.gather(*[
                    asyncio.to_thread(self.embeddings.embed_query, text)
                    for text in texts
                ])
                return embeddings
            except Exception as e:
                logger.error(f"Error creating embeddings: {e}")
                raise
        
        # Add required attributes for nano-graphrag
        nvidia_embedding_func.embedding_dim = 1024  # Adjust based on your model
        nvidia_embedding_func.max_token_size = 8192
        
        return nvidia_embedding_func
    
    def _load_documents(self):
        """Load documents and insert into graph"""
        all_texts = []
        
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
                    logger.warning(f"Unknown file type {file_extension}, trying as text file: {file_path}")
                    loader = TextLoader(file_path, encoding='utf-8')
                
                documents = loader.load()
                
                # Split documents according to config
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.config.chunk_size,
                    chunk_overlap=self.config.chunk_overlap
                )
                split_docs = splitter.split_documents(documents)
                
                # Convert to text with source metadata
                for doc in split_docs:
                    source_info = f"\n[Source: {os.path.basename(file_path)}]\n"
                    text_with_source = doc.page_content + source_info
                    all_texts.append(text_with_source)
                
                logger.info(f"Successfully loaded and split {len(documents)} pages into {len(split_docs)} chunks from {os.path.basename(file_path)}")
                
            except Exception as e:
                logger.error(f"Could not load {file_path}. Error: {e}")
        
        if not all_texts:
            logger.warning("No documents were successfully loaded.")
            return
        
        # Insert all texts into the graph
        logger.info(f"Inserting {len(all_texts)} document chunks into graph...")
        try:
            # Insert texts into nano-graphrag
            self.graph_rag.insert(all_texts)
            logger.info("Documents successfully inserted into graph")
        except Exception as e:
            logger.error(f"Error inserting documents: {e}")
            raise
    
    def get_relevant_chunks(self, query: str, mode: str = "local") -> List[Document]:
        """
        Get relevant chunks using nano-graphrag query.
        
        Args:
            query: The search query
            mode: "local" for local search, "global" for global search
        
        Returns:
            List of relevant Document objects
        """
        try:
            # Query the graph
            result = self.graph_rag.query(
                query,
                param=QueryParam(
                    mode=mode,
                    only_need_context=True,  # Only get context, not final answer
                    top_k=self.config.local_search_top_k if mode == "local" else None,
                    global_max_consider_community=self.config.global_max_consider_community if mode == "global" else None
                )
            )
            
            # Parse the context based on mode
            documents = []
            
            if mode == "local":
                # Local mode returns CSV-like format
                lines = result.strip().split('\n')
                content_start = False
                
                for line in lines:
                    if content_start and line.strip():
                        # Extract content from CSV format
                        parts = line.split(',', 1)
                        if len(parts) > 1:
                            content = parts[1].strip()
                            doc = Document(
                                page_content=content,
                                metadata={
                                    'mode': 'local',
                                    'retrieval_type': 'graph_local'
                                }
                            )
                            documents.append(doc)
                    elif 'content' in line.lower():
                        content_start = True
            
            elif mode == "global":
                # Global mode returns analyst reports
                sections = result.split('----Analyst')
                for section in sections[1:]:  # Skip first empty section
                    if section.strip():
                        doc = Document(
                            page_content=section.strip(),
                            metadata={
                                'mode': 'global',
                                'retrieval_type': 'graph_global'
                            }
                        )
                        documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error querying graph: {e}")
            return []
    
    async def retrieve_relevant_content(
        self, 
        query: str, 
        file_paths: Optional[List[str]] = None, 
        top_k: int = 5,
        mode: str = "local"
    ) -> List[dict]:
        """
        Retrieve relevant content using graph-based RAG.
        
        Args:
            query: The search query
            file_paths: Optional filter by file paths (not used in this implementation)
            top_k: Number of results to return
            mode: "local" or "global" search mode
        
        Returns:
            List of dictionaries with content and source information
        """
        try:
            # Get relevant chunks
            chunks = self.get_relevant_chunks(query, mode=mode)
            
            if not chunks:
                return []
            
            # Convert to expected format
            results = []
            for i, chunk in enumerate(chunks[:top_k]):
                # Extract source from content if available
                content = chunk.page_content
                source = "Unknown"
                
                # Try to extract source from content
                if "[Source:" in content:
                    source_start = content.find("[Source:") + 8
                    source_end = content.find("]", source_start)
                    if source_end > source_start:
                        source = content[source_start:source_end].strip()
                        # Remove source from content
                        content = content[:content.find("[Source:")].strip()
                
                result = {
                    'content': content,
                    'source': source,
                    'metadata': {
                        **chunk.metadata,
                        'retrieval_mode': mode,
                        'rank': i + 1
                    }
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving content: {e}")
            return []
    
    async def query_with_answer(self, query: str, mode: str = "local") -> str:
        """
        Query the graph and get a complete answer (not just context).
        
        Args:
            query: The search query
            mode: "local" or "global" search mode
        
        Returns:
            Complete answer as string
        """
        try:
            result = await asyncio.to_thread(
                self.graph_rag.query,
                query,
                QueryParam(
                    mode=mode,
                    only_need_context=False  # Get full answer
                )
            )
            return result
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            return f"Error processing query: {str(e)}"
    
    def add_documents(self, new_file_paths: List[str]):
        """Incrementally add new documents to the graph"""
        self.file_paths.extend(new_file_paths)
        self._load_documents()  # This will load and insert only the new documents