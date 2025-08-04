from langchain_nvidia_ai_endpoints import ChatNVIDIA
from .rag_service import RAGService
from .citation_service import CitationService
from ..core.config import settings
from .citation_tracker import CitationTracker
from ..models.citation_tracker import CitationConfig, ChunkCitation, InlineCitation
from ..models.document import GeneratedSection, RefinementRequest
import uuid
import asyncio

# Enhanced dynamic prompts for comprehensive content generation
SECTION_SYNTHESIS_PROMPT = """You are a highly skilled technical writer specializing in regulatory and pharmaceutical documentation. Your task is to write a comprehensive, detailed section for "{section_title}" based EXCLUSIVELY on the retrieved content from uploaded source documents.

Retrieved Content from Source Documents:
{retrieved_content}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. ONLY use information that is explicitly present in the retrieved content above
2. Write content that directly addresses "{section_title}" using ALL available source material
3. NEVER add information not found in the source documents
4. DO NOT assume context - write based on what the sources actually discuss
5. FOCUS on the actual topics, organizations, methodologies, and content mentioned in the source material
6. Extract and synthesize ALL relevant information from the provided sources
7. Create connections between different pieces of information from multiple sources when appropriate
8. Provide detailed explanations, methodologies, and technical specifications when available in sources

CONTENT REQUIREMENTS:
- TARGET LENGTH: 1000-1200 words minimum for comprehensive coverage
- Write substantive, detailed content that fully explores the topic
- Include specific data, numbers, percentages, and technical details from sources
- Provide thorough explanations of methodologies, processes, and procedures
- Include detailed background information and context when available in sources
- Cover all relevant subtopics and aspects mentioned in the source material

Content Formatting Guidelines:
- Start directly with substantive content (DO NOT repeat the section title as a header)
- Use clear, hierarchical structure with multiple subsections
- Use ## for main subsections, ### for sub-subsections, #### for detailed points
- Include comprehensive bullet points (-) and numbered lists with detailed explanations
- Use **bold** for key terms, important concepts, and critical findings
- Use *italics* for emphasis on technical terms and definitions
- Ensure proper paragraph breaks for readability (minimum 3-4 sentences per paragraph)
- Include specific quotes and detailed explanations from source material
- Add detailed technical specifications, measurements, and data when available
- Include references [1], [2], [3] when citing specific sources throughout the text
- DO NOT include a "References" section at the end - citations will be compiled separately

STRUCTURE REQUIREMENTS:
- **Introduction Paragraph**: Comprehensive overview of the topic (100-150 words)
- **Main Subsections**: 3-5 detailed subsections covering different aspects (200-300 words each)
- **Technical Details**: Include specific methodologies, procedures, and specifications
- **Data and Results**: Present quantitative information, findings, and analysis when available
- **Detailed Explanations**: Provide thorough explanations of complex concepts and processes
- **Cross-References**: Connect information from multiple sources when relevant

QUALITY STANDARDS:
- Ensure each paragraph contains substantial, meaningful content
- Avoid superficial or generic statements
- Include specific examples, case studies, and detailed procedures from sources
- Provide comprehensive coverage of all aspects mentioned in source material
- Maintain professional, technical writing style appropriate for regulatory documentation
- Use precise terminology and detailed descriptions

If the retrieved content is insufficient for a comprehensive 1000+ word section on "{section_title}", clearly state what specific information is missing and what type of detailed documentation would be needed.

Write a comprehensive, detailed section about "{section_title}" using ALL available source material:"""

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
        # Use Moonshot AI Kimi model for better quality with enhanced settings for longer content
        self.llm = ChatNVIDIA(
            model="moonshotai/kimi-k2-instruct", 
            api_key=settings.LLM_API_KEY, 
            max_tokens=6144,  # Increased for longer, more comprehensive content
            temperature=0.5,  # Slightly lower for more consistent, detailed output
            top_p=0.85        # Adjusted for better coherence in long-form content
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
            
            # Get relevant content from uploaded documents with comprehensive search
            retrieved_docs = await rag_service.retrieve_relevant_content(
                query=section_title,
                file_paths=[],  # RAG service already has the files
                top_k=15,  # Significantly increased for comprehensive content generation
                mode=use_graph_mode  # Pass GraphRAG mode (local/global)
            )
            
            print(f"📄 Retrieved {len(retrieved_docs)} documents for '{section_title}'")
            
            if not retrieved_docs:
                print(f"⚠️ No relevant documents found for '{section_title}'")
                content = f"""## Information Gap Notice for "{section_title}"

**No relevant information was found in the uploaded source documents for this section.** To generate the comprehensive 1000+ word section you've requested, we need substantial source material that directly addresses "{section_title}".

### Current Status
- **Sources Searched**: {len(retrieved_docs) if 'retrieved_docs' in locals() else 'All available'} documents
- **Content Found**: No relevant material for "{section_title}"
- **Target Length**: 1000-1200 words (requires substantial source content)

### What This Section Requires

Based on the section title "{section_title}", a comprehensive section would typically include:

#### Core Content Areas (200-300 words each)
1. **Background and Context**: Historical development, regulatory landscape, industry standards
2. **Technical Specifications**: Detailed methodologies, procedures, and requirements
3. **Implementation Guidelines**: Step-by-step processes, best practices, and compliance measures
4. **Data and Analysis**: Quantitative information, case studies, and performance metrics
5. **Regulatory Considerations**: Compliance requirements, guidelines, and documentation standards

#### Required Source Material Types
- **Primary Documentation**: Technical specifications, regulatory guidelines, standard operating procedures
- **Supporting Data**: Research studies, analytical results, validation reports, case studies
- **Reference Materials**: Industry standards, regulatory guidance documents, technical literature
- **Detailed Procedures**: Step-by-step methodologies, testing protocols, quality control measures

### Recommendations for Comprehensive Content Generation

#### 1. Document Upload Strategy
- **Upload comprehensive source materials** that contain detailed information about "{section_title}"
- **Include multiple document types**: technical reports, regulatory guidance, procedures, case studies
- **Ensure document quality**: Text-searchable PDFs, well-formatted Word documents, clear text files

#### 2. Content Requirements
- **Minimum 5-10 pages** of relevant source material per section
- **Detailed technical information** including procedures, specifications, and data
- **Multiple perspectives** from different sources to enable comprehensive synthesis

#### 3. Section Development Process
- **Phase 1**: Upload comprehensive source documentation
- **Phase 2**: System will retrieve and analyze relevant content (targeting 15+ source excerpts)
- **Phase 3**: Generate detailed 1000+ word section with proper citations and structure

### Expected Output Format

Once adequate source material is available, the generated section will include:

- **Comprehensive Introduction** (150-200 words): Overview and context
- **Multiple Detailed Subsections** (200-300 words each): Covering all aspects found in sources
- **Technical Details**: Specific procedures, specifications, and methodologies
- **Data Integration**: Quantitative information and analytical results
- **Professional Citations**: Proper referencing throughout the content
- **Structured Format**: Clear hierarchy with headings, subheadings, and organized content

**Next Action Required**: Please upload detailed source documents that contain substantial information about "{section_title}" to enable comprehensive content generation."""
                source_count = 0
            else:
                # Log retrieved content for debugging
                print(f"📝 Content sources for '{section_title}':")
                for i, doc in enumerate(retrieved_docs):
                    print(f"  {i+1}. {doc.get('source', 'Unknown')} - {len(doc.get('content', ''))} chars")
                
                # Prepare comprehensive context from retrieved documents for detailed content generation
                context_parts = []
                total_content_length = 0
                
                for i, doc in enumerate(retrieved_docs):
                    source_name = doc.get('source', f'Document_{i+1}')
                    page_num = doc.get('metadata', {}).get('page', doc.get('page', 'N/A'))
                    full_content = doc.get('content', '')
                    
                    # Include more content per source for comprehensive generation
                    # Increase content length limit for better context
                    content_limit = 800  # Increased from 200 for more detailed context
                    if len(full_content) > content_limit:
                        content = full_content[:content_limit] + f"... [Content continues in {source_name}]"
                    else:
                        content = full_content
                    
                    total_content_length += len(content)
                    
                    context_parts.append(f"""[Source {i+1}: {source_name}, Page {page_num}]
{content}

Key Information from {source_name}:
- Contains {len(full_content)} characters of relevant information
- Page {page_num} content for "{section_title}"
""")
                
                context_text = f"""
COMPREHENSIVE SOURCE MATERIAL FOR "{section_title.upper()}"
Total Sources: {len(retrieved_docs)}
Total Content Length: {total_content_length} characters

{"="*80}

""" + f"\n\n{'='*80}\n\n".join(context_parts)
                
                print(f"📝 Prepared comprehensive context: {len(context_text)} characters from {len(retrieved_docs)} sources")
                
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
