from langchain_nvidia_ai_endpoints import ChatNVIDIA
from .rag_service import RAGService
from .citation_service import CitationService
from ..core.config import settings
from .citation_tracker import CitationTracker
from ..models.citation_tracker import CitationConfig, ChunkCitation, InlineCitation
from ..models.document import GeneratedSection, RefinementRequest
import uuid
import asyncio

# Dynamic prompts based on context
SECTION_SYNTHESIS_PROMPT = """You are an expert technical writer. Your task is to write a comprehensive section for "{section_title}" based EXCLUSIVELY on the retrieved content from uploaded source documents.

Retrieved Content from Source Documents:
{retrieved_content}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. ONLY use information that is explicitly present in the retrieved content above
2. Write content that directly addresses "{section_title}" using the source material
3. NEVER add information not found in the source documents
4. DO NOT assume this is about pharmaceuticals, drugs, CMC, or manufacturing unless explicitly stated in the source
5. DO NOT use regulatory boilerplate language unless it appears in the source documents
6. FOCUS on the actual topics, organizations, and content mentioned in the source material
7. If the source discusses NIST, cybersecurity, instruments, etc., write about those topics
8. If the source discusses biology, write about biology
9. If the source discusses engineering, write about engineering

Content Formatting Guidelines:
- Start directly with the main content (DO NOT repeat the section title as a header)
- Use clear, logical structure with subsections
- Use ## for main subsections, ### for sub-subsections
- Include bullet points (-) and numbered lists where appropriate
- Generate 800-1000 words but ensure all content comes from the source material
- Include references [1], [2] when citing specific sources
- Use **bold** sparingly, only for key terms or important concepts  
- Ensure proper paragraph breaks for readability
- DO NOT include a "References" section or list at the end - citations will be compiled separately
- DO NOT add any bibliography, reference list, or sources section
- ABSOLUTELY NO references section of any kind (##References, Bibliography, etc.)

Structure your response with clear subsections that flow logically to address "{section_title}".

If the retrieved content is insufficient for "{section_title}", state clearly what information is missing and what type of documentation would be needed based on the section title.

Write a comprehensive section about "{section_title}" using ONLY the provided source material:"""

REFINEMENT_PROMPT = """You are an expert medical regulatory writer. You need to refine the following section based on user feedback.

Section Title: {section_title}

Current Content:
{current_content}

Refinement Request:
{refinement_request}

Please provide an improved version of the content that addresses the refinement request while maintaining regulatory compliance and professional standards."""

class GenerationService:
    def __init__(self):
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is not set in the environment.")
        # Use the same fast model as the chat service
        self.llm = ChatNVIDIA(
            model="meta/llama-4-scout-17b-16e-instruct", 
            nvidia_api_key=settings.LLM_API_KEY, 
            max_tokens=2048,
            temperature=0.7
        )
        # Initialize citation service and tracker with config
        self.citation_service = CitationService()
        self.citation_tracker = CitationTracker(CitationConfig())

    async def synthesize_section(self, section_title: str, rag_service: RAGService, use_graph_mode: str = "local", session_id: str = "default", document_id: str = None) -> GeneratedSection:
        """Generate a section using RAG and LLM"""
        try:
            print(f"🔍 Generating section: '{section_title}'")
            
            # Create or get citation registry for this session/document
            if document_id is None:
                document_id = f"{session_id}-{section_title.replace(' ', '-').lower()}"
            
            print(f"🔍 Looking for citation registry with document_id: {document_id}")
            citation_registry = self.citation_tracker.get_registry(document_id)
            if not citation_registry:
                print(f"✅ Creating new citation registry for document_id: {document_id}")
                citation_registry = self.citation_tracker.create_registry(document_id, session_id)
            else:
                print(f"✅ Found existing citation registry with {len(citation_registry.inline_citations)} citations")
            
            # Get relevant content from uploaded documents with expanded search
            retrieved_docs = await rag_service.retrieve_relevant_content(
                query=section_title,
                file_paths=[],  # RAG service already has the files
                top_k=8,  # Increased from 5 to get more context
                mode=use_graph_mode  # Pass GraphRAG mode (local/global)
            )
            
            print(f"📄 Retrieved {len(retrieved_docs)} documents for '{section_title}'")
            
            if not retrieved_docs:
                print(f"⚠️ No relevant documents found for '{section_title}'")
                content = f"""# {section_title}

## Information Gap Notice

No relevant information was found in the uploaded source documents for the section "{section_title}". This indicates that either:

1. The uploaded documents do not contain information relevant to this section topic
2. Additional source documents may be needed
3. The section title may need to be refined to better match available content

## What This Section Should Address

Based on the section title "{section_title}", this section would typically include:

### Key Information Areas
- Background and context relevant to {section_title.lower()}
- Technical details and specifications
- Methodologies and approaches
- Supporting data and evidence
- References to authoritative sources

### Required Documentation

To generate meaningful content for this section, please ensure that your uploaded documents contain:
- Information directly related to "{section_title}"
- Supporting technical documentation
- Relevant data, studies, or analyses
- Background materials and context

## Next Steps

**Recommended Actions:**
1. **Review Uploaded Documents**: Verify that your source files contain information relevant to "{section_title}"
2. **Upload Additional Sources**: If needed, upload additional documents that address this section topic
3. **Refine Section Title**: Consider whether the section title accurately reflects the content you want to generate
4. **Check Document Format**: Ensure uploaded files are in supported formats (PDF, DOCX, TXT) and are text-searchable

Once relevant source material is available, this section can be regenerated with substantive, document-based content that directly addresses "{section_title}".

**Note**: This system generates content based on your uploaded documents. Without relevant source material, meaningful section content cannot be produced."""
                source_count = 0
            else:
                # Log retrieved content for debugging
                print(f"📝 Content sources for '{section_title}':")
                for i, doc in enumerate(retrieved_docs):
                    print(f"  {i+1}. {doc.get('source', 'Unknown')} - {len(doc.get('content', ''))} chars")
                
                # Prepare context from retrieved documents with better formatting
                context_parts = []
                for i, doc in enumerate(retrieved_docs):
                    content_preview = doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', '')
                    context_parts.append(f"""[Source {i+1}: {doc.get('source', 'Unknown')}]
{doc.get('content', '')}""")
                
                context_text = "\n\n" + "="*50 + "\n\n".join(context_parts)
                
                print(f"🤖 Generating LLM response for '{section_title}' with {len(context_text)} chars of context")
                
                # Create prompt with context
                prompt = SECTION_SYNTHESIS_PROMPT.format(
                    section_title=section_title,
                    retrieved_content=context_text
                )
                
                # Generate content using LLM
                response = await asyncio.to_thread(self.llm.invoke, prompt)
                
                # Extract response text
                if hasattr(response, 'content'):
                    content = response.content
                else:
                    content = str(response)
                
                # Remove any References sections that the LLM might have generated
                content = self._remove_references_from_content(content)
                
                # Process citations from RAG metadata directly
                print(f"🔗 Processing citations for '{section_title}' using RAG metadata...")
                try:
                    # Store citation numbers for content insertion
                    new_citation_numbers = []
                    
                    for i, doc in enumerate(retrieved_docs):
                        # Create chunk citation from RAG metadata
                        metadata = doc.get('metadata', {})
                        chunk_citation = ChunkCitation(
                            chunk_id=f"{document_id}-chunk-{uuid.uuid4()}",  # Use unique ID
                            pdf_name=doc.get('source', metadata.get('source', f'Document {i+1}')),
                            page_number=metadata.get('page', 1),
                            text_excerpt=doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', ''),
                            authors=metadata.get('authors', []),
                            external_link=metadata.get('url', '')
                        )
                        
                        print(f"🔗 Creating citation for: {chunk_citation.pdf_name} (page {chunk_citation.page_number})")
                        
                        # Add citation to registry (this creates both chunk and inline citation)
                        inline_citation = citation_registry.add_citation(chunk_citation)
                        new_citation_numbers.append(inline_citation.citation_number)
                        print(f"✅ Added citation [{inline_citation.citation_number}] to registry")
                    
                    # Add citations to the content at appropriate places
                    if new_citation_numbers:
                        # Simple approach: add citations at the end of paragraphs
                        paragraphs = content.split('\n\n')
                        processed_paragraphs = []
                        
                        for i, paragraph in enumerate(paragraphs):
                            if paragraph.strip() and len(paragraph.strip()) > 50:
                                if i < len(new_citation_numbers):
                                    # Add one citation per paragraph
                                    citation_ref = f" [{new_citation_numbers[i]}]"
                                    if paragraph.rstrip().endswith('.'):
                                        paragraph = paragraph.rstrip()[:-1] + citation_ref + '.'
                                    else:
                                        paragraph = paragraph.rstrip() + citation_ref
                                elif i == len(paragraphs) - 1 and len(new_citation_numbers) > 1:
                                    # Add remaining citations as individual citations to the last paragraph
                                    remaining_citations = [str(num) for num in new_citation_numbers[1:]]
                                    if remaining_citations:
                                        # Add each citation individually with proper spacing
                                        individual_citations = ' '.join([f"[{num}]" for num in remaining_citations])
                                        citation_ref = f" {individual_citations}"
                                        if paragraph.rstrip().endswith('.'):
                                            paragraph = paragraph.rstrip()[:-1] + citation_ref + '.'
                                        else:
                                            paragraph = paragraph.rstrip() + citation_ref
                                            
                                print(f"📝 Added citation {new_citation_numbers[min(i, len(new_citation_numbers)-1)] if i < len(new_citation_numbers) else 'N/A'} to paragraph {i+1}")
                            
                            processed_paragraphs.append(paragraph)
                        
                        content = '\n\n'.join(processed_paragraphs)
                    
                    print(f"✅ Added {len(retrieved_docs)} citations from RAG sources for '{section_title}'")
                    print(f"🔗 Citation registry now has {len(citation_registry.inline_citations)} total citations")
                    for citation in citation_registry.inline_citations:
                        print(f"  [{citation.citation_number}] {citation.chunk_citation.pdf_name} (page {citation.chunk_citation.page_number})")
                except Exception as citation_error:
                    print(f"⚠️ Citation processing failed for '{section_title}': {citation_error}")
                    import traceback
                    traceback.print_exc()
                    # Continue with original content if citation processing fails
                
                source_count = len(retrieved_docs)
                print(f"✅ Generated {len(content)} chars for '{section_title}' using {source_count} sources")
            
            return GeneratedSection(
                title=section_title,
                content=content,
                source_count=source_count
            )
            
        except Exception as e:
            print(f"Error generating section '{section_title}': {e}")
            # Return error section with more helpful content
            return GeneratedSection(
                title=section_title,
                content=f"""# {section_title}

## Error Notice

An error occurred while generating this section: {str(e)}

## Recommended Actions

1. **Check Source Documents**: Ensure that relevant documents containing information about "{section_title}" have been uploaded to the system.

2. **Verify File Format**: Confirm that uploaded files are in supported formats (PDF, DOCX, TXT) and are not corrupted.

3. **Review Content**: Make sure the uploaded documents contain relevant information for "{section_title}".

4. **Try Again**: Re-attempt the generation process after addressing the above points.

## Standard Section Framework

While resolving the technical issue, this section typically should include:

### Key Components
- Technical specifications and requirements
- Regulatory compliance documentation
- Quality control measures
- Data analysis and interpretation

### Documentation Standards
- Adherence to regulatory guidelines
- Proper referencing and citations
- Clear methodology descriptions
- Comprehensive data presentation

Please contact support if this error persists after following the recommended actions.""",
                source_count=0
            )

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
    
    def generate_references_section(self, document_id: str) -> str:
        """Generate a references section for the document"""
        return self.citation_tracker.generate_references_section(document_id)
    
    def get_citation_registry(self, document_id: str):
        """Get citation registry for a document"""
        return self.citation_tracker.get_registry(document_id)
    
    def get_citation_statistics(self, document_id: str):
        """Get citation statistics for a document"""
        registry = self.citation_tracker.get_registry(document_id)
        if not registry:
            return None
        
        return {
            "document_id": document_id,
            "total_citations": len(registry.inline_citations),
            "unique_sources": len(set(cite.chunk_citation.pdf_name for cite in registry.inline_citations)),
            "citation_style": registry.citation_style,
            "sources": [cite.chunk_citation.pdf_name for cite in registry.inline_citations],
            "auto_references_enabled": registry.auto_generate_references
        }
    
    def export_citations(self, document_id: str, format: str):
        """Export citations in specified format"""
        registry = self.citation_tracker.get_registry(document_id)
        if not registry:
            return None
        
        if format == "json":
            import json
            return json.dumps({
                "document_id": document_id,
                "citations": [
                    {
                        "citation_number": cite.citation_number,
                        "text": cite.chunk_citation.text_excerpt,
                        "source": cite.chunk_citation.pdf_name,
                        "page": cite.chunk_citation.page_number
                    }
                    for cite in registry.inline_citations
                ]
            })
        elif format == "bibtex":
            # Simple BibTeX format
            entries = []
            for cite in registry.inline_citations:
                entries.append(f"""@misc{{cite{cite.citation_number},
  title={{{cite.chunk_citation.text_excerpt[:50]}...}},
  author={{{', '.join(cite.chunk_citation.authors) if cite.chunk_citation.authors else 'Unknown'}}},
  note={{p. {cite.chunk_citation.page_number}}}
}}""")
            return '\n\n'.join(entries)
        
        return None
    
    def _remove_references_from_content(self, content: str) -> str:
        """Remove any References sections that the LLM might have generated"""
        import re
        
        # Remove References sections and everything after them
        # Pattern matches various forms of References headers
        patterns = [
            r'\n\s*#+\s*References.*$',              # ## References or # References
            r'\n\s*#+\s*REFERENCES.*$',              # ## REFERENCES or # REFERENCES
            r'\n\s*References\s*\n.*$',              # References as standalone line
            r'\n\s*REFERENCES\s*\n.*$',              # REFERENCES as standalone line
            r'\n\s*References:\s*\n.*$',             # References: as standalone line
            r'\n\s*REFERENCES:\s*\n.*$',             # REFERENCES: as standalone line
            r'\n\s*Bibliography.*$',                 # Bibliography section
            r'\n\s*BIBLIOGRAPHY.*$',                 # BIBLIOGRAPHY section
            r'\n\s*Sources.*$',                      # Sources section
            r'\n\s*SOURCES.*$',                      # SOURCES section
            r'\n\s*Reference\s+List.*$',             # Reference List section
            r'\n\s*REFERENCE\s+LIST.*$',             # REFERENCE LIST section
            r'\n\s*\*\*References\*\*.*$',           # **References** markdown bold
            r'\n\s*\*\*REFERENCES\*\*.*$',           # **REFERENCES** markdown bold
            r'\n\s*#+\s*Bibliography.*$',            # ## Bibliography 
            r'\n\s*#+\s*Reference List.*$',          # ## Reference List
            r'\n\s*Reference List\s*\n.*$',          # Reference List as standalone
            r'\n\s*#+\s*Citations.*$',               # ## Citations
            r'\n\s*Citations\s*\n.*$'                # Citations as standalone line
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # Also remove any trailing reference lists that might not have a header
        # Look for patterns like [1] Author. Title. at the end of content
        ref_list_patterns = [
            r'\n\s*\[\d+\]\s+[^\n]+\.[^\n]*(\n\s*\[\d+\]\s+[^\n]+\.[^\n]*)*\s*$',  # [1] Author format
            r'\n\s*\d+\.\s+[^\n]+\.[^\n]*(\n\s*\d+\.\s+[^\n]+\.[^\n]*)*\s*$',      # 1. Author format
            r'\n\s*\([0-9]+\)\s+[^\n]+\.[^\n]*(\n\s*\([0-9]+\)\s+[^\n]+\.[^\n]*)*\s*$'  # (1) Author format
        ]
        
        for pattern in ref_list_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        return content.strip()
