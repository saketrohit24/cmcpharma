from langchain_nvidia_ai_endpoints import ChatNVIDIA
from .rag_service import RAGService
from .graph_rag_service import RAGConfig
from ..core.config import settings
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

    async def synthesize_section(self, section_title: str, rag_service: RAGService, use_graph_mode: str = "local") -> GeneratedSection:
        """Generate a section using RAG and LLM"""
        try:
            print(f"🔍 Generating section: '{section_title}'")
            
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
