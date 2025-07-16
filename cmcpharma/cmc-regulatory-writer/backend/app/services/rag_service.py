from typing import List
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from ..core.config import settings

class RAGService:
    def __init__(self, file_paths: List[str]):
        if not settings.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is not set in the environment.")
        self.file_paths = file_paths
        self.embeddings = NVIDIAEmbeddings(model="nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1", api_key=settings.NVIDIA_API_KEY)
        self.documents = self._load_and_split_docs()
        self.vector_store = self._create_vector_store()
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 20, "fetch_k": 40}
        ) if self.vector_store else None

    def _load_and_split_docs(self) -> List[Document]:
        all_pages = []
        for file_path in self.file_paths:
            try:
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                all_pages.extend(pages)
            except Exception as e:
                print(f"Warning: Could not load {file_path}. Error: {e}")
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
        return splitter.split_documents(all_pages)

    def _create_vector_store(self):
        if not self.documents:
            print("Warning: No documents were loaded. RAG functionality will be disabled.")
            return None
        return FAISS.from_documents(self.documents, self.embeddings)

    def get_relevant_chunks(self, query: str) -> List[Document]:
        if not self.retriever:
            print("Warning: No retriever available. RAG is disabled.")
            return []
        return self.retriever.get_relevant_documents(query)
