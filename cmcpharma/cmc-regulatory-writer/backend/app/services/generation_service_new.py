from langchain_nvidia_ai_endpoints import ChatNVIDIA
from .rag_service import RAGService
from ..core.config import settings
from ..models.document import GeneratedSection, RefinementRequest
import uuid

# Prompts can be stored here or in a separate prompts.py file
SECTION_SYNTHESIS_PROMPT = """You are an expert medical regulatory writer specializing in CMC (Chemistry, Manufacturing, and Controls) documentation.

Your task is to synthesize a comprehensive section for "{section_title}" based on the retrieved content from source documents.

Retrieved Content:
{retrieved_content}

Instructions:
1. Write a thorough, well-structured section that addresses all relevant aspects of "{section_title}"
2. Use professional regulatory writing tone and terminology
3. Ensure compliance with regulatory standards (FDA, EMA guidelines)
4. Cite information appropriately from the source documents
5. If information is incomplete, note what additional data may be needed
6. Structure the content with clear headings and logical flow

Please provide a comprehensive section that would be suitable for inclusion in a regulatory submission."""

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
        self.llm = ChatNVIDIA(model="nvidia/llama-3.1-nemotron-ultra-253b-v1", nvidia_api_key=settings.LLM_API_KEY, max_tokens=6144)

    def synthesize_section(self, section_title: str, rag_service: RAGService) -> GeneratedSection:
        retrieved_docs = rag_service.get_relevant_chunks(section_title)
        
        if not retrieved_docs:
            content = "No relevant information was found in the provided documents for this section. Please ensure that source documents containing information about this topic are uploaded, or consider providing additional documentation that covers the required regulatory aspects."
            source_count = 0
        else:
            context_text = "\n\n---\n\n".join([f"Content: {doc.page_content}" for doc in retrieved_docs])
            synthesis_prompt = SECTION_SYNTHESIS_PROMPT.format(
                section_title=section_title,
                retrieved_content=context_text
            )
            response = self.llm.invoke(synthesis_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            source_count = len(retrieved_docs)
        
        return GeneratedSection(
            title=section_title,
            content=content,
            source_count=source_count
        )

    def refine_section(self, request: RefinementRequest) -> str:
        prompt = REFINEMENT_PROMPT.format(
            section_title=request.section_title,
            current_content=request.current_content,
            refinement_request=request.refinement_request
        )
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
