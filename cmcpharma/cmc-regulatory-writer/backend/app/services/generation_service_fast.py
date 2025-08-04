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

# Enhanced prompt for comprehensive fast generation
FAST_SECTION_PROMPT = """You are an expert technical writer specializing in regulatory and pharmaceutical documentation. Write a comprehensive, detailed section for "{section_title}" using the provided source content.

Source Content:
{retrieved_content}

CONTENT REQUIREMENTS:
- TARGET LENGTH: 800-1000 words for comprehensive coverage
- Write detailed, substantive content that fully explores the topic
- Include specific data, methodologies, and technical details from sources
- Provide thorough explanations and background context
- Cover multiple aspects and subtopics mentioned in source material

FORMATTING INSTRUCTIONS:
- Use clear hierarchical structure with ## main headings, ### subheadings
- Include detailed bullet points and numbered lists with explanations
- Use **bold** for key terms and important concepts
- Include [1], [2], [3] citations throughout for source references
- Ensure comprehensive paragraph structure (3-4 sentences minimum per paragraph)
- Add specific quotes and detailed technical specifications when available

STRUCTURE REQUIREMENTS:
- Start with comprehensive overview paragraph (100+ words)
- Include 3-4 main subsections with detailed content (200+ words each)
- Add technical details, procedures, and specifications from sources
- Include quantitative data and analytical results when available
- Cross-reference information from multiple sources when relevant

Write a comprehensive, detailed section for "{section_title}":"""

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
        
        # Use Moonshot AI Kimi model optimized for comprehensive content generation
        self.llm = ChatNVIDIA(
            model="moonshotai/kimi-k2-instruct", 
            api_key=settings.LLM_API_KEY, 
            max_tokens=4096,  # Increased for comprehensive 1000+ word content
            temperature=0.5,  # Consistent detailed output
            top_p=0.85        # Balanced coherence for longer content
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
                    top_k=12,  # Increased for comprehensive content generation
                    mode="local"  # Force local mode for speed
                ),
                timeout=45.0  # Extended timeout for more comprehensive retrieval
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
            
            # Prepare comprehensive context for detailed content generation
            context_parts = []
            total_context_length = 0
            
            for i, doc in enumerate(retrieved_docs[:8]):  # Increased from 3 to 8 for more comprehensive context
                source_name = doc.get('source', f'Document {i+1}')
                page_num = doc.get('metadata', {}).get('page', doc.get('page', 'N/A'))
                full_content = doc.get('content', '')
                
                # Increase content length for better context (was 800, now 1200)
                content_limit = 1200
                if len(full_content) > content_limit:
                    content = full_content[:content_limit] + f"... [More content available in {source_name}]"
                else:
                    content = full_content
                
                total_context_length += len(content)
                context_parts.append(f"[Source {i+1}: {source_name}, Page {page_num}]\n{content}")
            
            context_text = f"""COMPREHENSIVE SOURCE MATERIAL FOR "{section_title.upper()}"
Total Sources: {len(retrieved_docs)}
Context Length: {total_context_length} characters

{"="*60}

""" + f"\n\n{'='*60}\n\n".join(context_parts)
            
            print(f"📝 Prepared context: {len(context_text)} characters from {len(retrieved_docs)} sources")
            
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
