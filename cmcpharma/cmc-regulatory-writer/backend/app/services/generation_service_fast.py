from langchain_nvidia_ai_endpoints import ChatNVIDIA
from .rag_service import RAGService
from .citation_service import CitationService
from .citation_tracker import CitationTracker
from ..models.citation_tracker import CitationConfig
from ..core.config import settings
from ..models.document import GeneratedSection, RefinementRequest
import uuid
import asyncio
import time

# Simplified prompt for faster generation
FAST_SECTION_PROMPT = """You are an expert technical writer. Write a comprehensive section for "{section_title}" using the provided source content.

Source Content:
{retrieved_content}

Instructions:
- Write 400-600 words focused on "{section_title}"
- Use ONLY information from the source content
- Include [1], [2], etc. citations for sources
- Use clear structure with ## headings
- Be direct and concise

Write the section:"""

REFINEMENT_PROMPT = """Refine this section based on the feedback:

Section: {section_title}
Current Content: {current_content}
Feedback: {refinement_request}

Provide the improved version:"""

class GenerationService:
    def __init__(self):
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is not set in the environment.")
        
        print("🚀 Initializing GenerationService with fast settings...")
        
        # Use faster settings for quicker responses
        self.llm = ChatNVIDIA(
            model="meta/llama-4-scout-17b-16e-instruct", 
            nvidia_api_key=settings.LLM_API_KEY, 
            max_tokens=1024,  # Reduced for speed
            temperature=0.5   # Lower for consistency
        )
        self.citation_service = CitationService()
        self.citation_tracker = CitationTracker(CitationConfig())
        
        print("✅ GenerationService initialized successfully")

    async def synthesize_section(self, section_title: str, rag_service: RAGService, use_graph_mode: str = "local", session_id: str = "default", document_id: str = None) -> GeneratedSection:
        """Generate a section using RAG and LLM with automatic citation tracking"""
        start_time = time.time()
        
        try:
            print(f"🔍 Generating section: '{section_title}'")
            
            # Create or get citation registry for this session/document
            if document_id is None:
                document_id = f"{session_id}-{section_title.replace(' ', '-').lower()}"
            
            citation_registry = self.citation_tracker.get_registry(document_id)
            if not citation_registry:
                citation_registry = self.citation_tracker.create_registry(document_id, session_id)
            
            # Retrieve content with timeout
            retrieval_start = time.time()
            print(f"📄 Retrieving content for '{section_title}'...")
            
            retrieved_docs = await asyncio.wait_for(
                rag_service.retrieve_relevant_content(
                    query=section_title,
                    file_paths=[],
                    top_k=5,  # Reduced for speed
                    mode="local"  # Force local mode for speed
                ),
                timeout=30.0  # 30 second timeout
            )
            
            retrieval_time = time.time() - retrieval_start
            print(f"⏱️ Content retrieval took {retrieval_time:.2f} seconds")
            print(f"📄 Retrieved {len(retrieved_docs)} documents")
            
            if not retrieved_docs:
                print(f"⚠️ No relevant documents found for '{section_title}'")
                return GeneratedSection(
                    title=section_title,
                    content=f"No relevant content found for '{section_title}'. Please upload relevant documents.",
                    source_count=0
                )
            
            # Prepare context quickly
            context_parts = []
            for i, doc in enumerate(retrieved_docs[:3]):  # Limit to 3 for speed
                source_name = doc.get('source', f'Document {i+1}')
                content = doc.get('content', '')[:800]  # Limit content length
                context_parts.append(f"[Source {i+1}: {source_name}]\n{content}")
            
            context_text = "\n\n".join(context_parts)
            
            # Generate with fast prompt
            generation_start = time.time()
            print(f"🤖 Generating LLM response...")
            
            prompt = FAST_SECTION_PROMPT.format(
                section_title=section_title,
                retrieved_content=context_text
            )
            
            # Generate content with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(self.llm.invoke, prompt),
                timeout=60.0  # 60 second timeout
            )
            
            generation_time = time.time() - generation_start
            print(f"⏱️ LLM generation took {generation_time:.2f} seconds")
            
            # Extract response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Process content with citations quickly
            content_with_citations = self.citation_tracker.process_generated_content(
                content=content,
                document_id=document_id,
                retrieved_chunks=retrieved_docs
            )
            
            # Remove any existing References sections from individual sections
            final_content = self._remove_inline_references_sections(content_with_citations)
            
            total_time = time.time() - start_time
            print(f"✅ Generated '{section_title}' in {total_time:.2f} seconds ({len(final_content)} chars)")
            
            return GeneratedSection(
                title=section_title,
                content=final_content,
                source_count=len(retrieved_docs)
            )
            
        except asyncio.TimeoutError:
            error_msg = f"⚠️ Generation timed out for '{section_title}'"
            print(error_msg)
            return GeneratedSection(
                title=section_title,
                content=f"Generation timed out for '{section_title}'. Please try again or check your network connection.",
                source_count=0
            )
            
        except Exception as e:
            error_msg = f"❌ Error generating '{section_title}': {str(e)}"
            print(error_msg)
            return GeneratedSection(
                title=section_title,
                content=f"Error generating '{section_title}': {str(e)}",
                source_count=0
            )

    def _remove_inline_references_sections(self, content: str) -> str:
        """Remove any References sections from individual content to prevent duplicates"""
        import re
        
        # Remove References sections that might appear in individual sections
        references_pattern = r'\n##\s*References\s*\n.*?(?=\n##|\n#|$)'
        content_without_refs = re.sub(references_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        return content_without_refs.strip()
    
    def generate_complete_document_with_citations(self, sections: list, document_id: str) -> str:
        """Generate a complete document with all sections and a consolidated References section"""
        
        # Combine all sections
        complete_content = ""
        for section in sections:
            complete_content += section + "\n\n"
        
        # Add the consolidated References section at the end
        references_section = self.generate_references_section(document_id)
        if references_section:
            complete_content += "\n\n" + references_section
        
        return complete_content.strip()
    
    def generate_references_section(self, document_id: str) -> str:
        """Generate the references section for a document"""
        return self.citation_tracker.generate_references_section(document_id)
    
    def get_citation_registry(self, document_id: str):
        """Get citation registry for a document"""
        return self.citation_tracker.get_registry(document_id)

    async def refine_section(self, request: RefinementRequest) -> str:
        """Refine a section based on user feedback"""
        try:
            prompt = REFINEMENT_PROMPT.format(
                section_title=request.section_title,
                current_content=request.current_content,
                refinement_request=request.refinement_request
            )
            
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            return f"Error refining section: {str(e)}"
