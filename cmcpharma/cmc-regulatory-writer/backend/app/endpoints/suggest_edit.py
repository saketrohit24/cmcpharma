from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
from ..services.generation_service import GenerationService
from ..services.rag_service import RAGService
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

class SuggestEditRequest(BaseModel):
    content: str
    preset: Optional[str] = None
    custom_instructions: Optional[str] = None
    use_rag: bool = False
    maintain_tone: bool = True
    preserve_technical_accuracy: bool = True
    session_id: str
    section_id: Optional[str] = None

class SuggestEditResponse(BaseModel):
    edited_content: str
    edit_summary: str
    changes_made: list[str]

# Initialize services
generation_service = GenerationService()

PRESET_PROMPTS = {
    "shorten": """Shorten the following content while preserving all key points and technical accuracy. Remove redundancy and wordiness but maintain the essential meaning and regulatory compliance requirements.

Content to edit:
{content}

Provide a shortened version that:
- Retains all critical technical information
- Maintains regulatory compliance language
- Removes unnecessary words and phrases
- Preserves the original tone and structure
- Maintains the EXACT same formatting (paragraphs, headers, lists, etc.)
- Keeps all subsection headers and organizational structure
- Does NOT add any new references or citations
- Only returns the edited content without additional references""",

    "clarify": """Improve the clarity and readability of the following content while maintaining technical accuracy and regulatory compliance.

Content to edit:
{content}

Provide a clarified version that:
- Uses clearer, more direct language
- Improves sentence structure and flow
- Maintains all technical terms and regulatory requirements
- Enhances understanding without changing meaning
- Maintains the EXACT same formatting (paragraphs, headers, lists, etc.)
- Keeps all subsection headers and organizational structure
- Does NOT add any new references or citations
- Only returns the edited content without additional references""",

    "improve_flow": """Improve the logical flow and transitions in the following content while maintaining technical accuracy and regulatory compliance.

Content to edit:
{content}

Provide an improved version that:
- Enhances transitions between ideas
- Creates better logical progression
- Maintains all technical information
- Improves overall readability and coherence
- Maintains the EXACT same formatting (paragraphs, headers, lists, etc.)
- Keeps all subsection headers and organizational structure
- Does NOT add any new references or citations
- Only returns the edited content without additional references""",

    "make_concise": """Make the following content more concise by removing redundancy and unnecessary words while preserving all essential information.

Content to edit:
{content}

Provide a concise version that:
- Eliminates redundant phrases and information
- Uses more efficient language
- Maintains all critical technical details
- Preserves regulatory compliance requirements
- Maintains the EXACT same formatting (paragraphs, headers, lists, etc.)
- Keeps all subsection headers and organizational structure
- Does NOT add any new references or citations
- Only returns the edited content without additional references""",

    "expand_detail": """Add more comprehensive detail and explanation to the following content while maintaining accuracy and regulatory compliance.

Content to edit:
{content}

{rag_context}

Provide an expanded version that:
- Adds relevant technical details from available sources
- Provides more comprehensive explanations
- Maintains accuracy and regulatory compliance
- Enhances the depth of information
- Maintains the EXACT same formatting (paragraphs, headers, lists, etc.)
- Keeps all subsection headers and organizational structure
- Does NOT add any new references or citations
- Only returns the edited content without additional references""",

    "simplify": """Simplify the language and structure of the following content while maintaining technical accuracy and all essential information.

Content to edit:
{content}

Provide a simplified version that:
- Uses simpler, more accessible language
- Breaks down complex concepts
- Maintains all technical requirements
- Preserves regulatory compliance needs
- Maintains the EXACT same formatting (paragraphs, headers, lists, etc.)
- Keeps all subsection headers and organizational structure
- Does NOT add any new references or citations
- Only returns the edited content without additional references"""
}

async def get_generation_service():
    return generation_service

async def get_rag_service():
    """Get RAG service with all available documents"""
    import os
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "persistent_uploads")
    
    def get_all_document_files(upload_dir: str):
        """Get all document files from the persistent uploads directory"""
        document_files = []
        supported_extensions = ['.txt', '.pdf', '.doc', '.docx', '.md']
        
        try:
            if os.path.exists(upload_dir):
                for root, dirs, files in os.walk(upload_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_extension = os.path.splitext(file)[1].lower()
                        if file_extension in supported_extensions:
                            document_files.append(file_path)
        except Exception as e:
            print(f"Error scanning documents: {e}")
            
        return document_files
    
    available_files = get_all_document_files(upload_dir)
    return RAGService(file_paths=available_files)

@router.post("/suggest-edit", response_model=SuggestEditResponse)
async def suggest_edit(
    request: SuggestEditRequest,
    gen_service: GenerationService = Depends(get_generation_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Generate suggested edits for content based on presets or custom instructions
    """
    try:
        logger.info(f"Processing suggest edit request for session {request.session_id}")
        
        # Prepare the editing prompt
        if request.preset and request.preset in PRESET_PROMPTS:
            # Use preset prompt
            base_prompt = PRESET_PROMPTS[request.preset]
            
            # Get RAG context if needed and requested
            rag_context = ""
            if request.use_rag and request.preset == "expand_detail":
                try:
                    relevant_docs = await rag_service.retrieve_relevant_content(
                        query=request.content[:200],  # Use first 200 chars as query
                        file_paths=[],
                        top_k=3
                    )
                    
                    if relevant_docs:
                        context_parts = []
                        for i, doc in enumerate(relevant_docs):
                            context_parts.append(f"Source {i+1}: {doc.get('content', '')[:300]}...")
                        rag_context = f"""
Additional context from uploaded documents:
{chr(10).join(context_parts)}

Use this additional information to enhance the content:"""
                    else:
                        rag_context = "No additional context found in uploaded documents."
                        
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")
                    rag_context = "Additional research unavailable."
            
            prompt = base_prompt.format(content=request.content, rag_context=rag_context)
            
        elif request.custom_instructions:
            # Use custom instructions
            rag_context = ""
            if request.use_rag:
                try:
                    relevant_docs = await rag_service.retrieve_relevant_content(
                        query=request.custom_instructions + " " + request.content[:100],
                        file_paths=[],
                        top_k=3
                    )
                    
                    if relevant_docs:
                        context_parts = []
                        for i, doc in enumerate(relevant_docs):
                            context_parts.append(f"Source {i+1}: {doc.get('content', '')[:300]}...")
                        rag_context = f"""
Additional context from uploaded documents:
{chr(10).join(context_parts)}"""
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")
                    rag_context = ""
            
            prompt = f"""You are an expert regulatory writer. Edit the following content according to these instructions: {request.custom_instructions}

Content to edit:
{request.content}

{rag_context}

CRITICAL INSTRUCTIONS:
- {"Maintain the original tone and style" if request.maintain_tone else "Feel free to adjust tone as needed"}
- {"Preserve all technical accuracy and regulatory compliance" if request.preserve_technical_accuracy else "Focus on the requested changes"}
- Make the requested modifications while ensuring the content remains professional and accurate
- Maintain the EXACT same formatting (paragraphs, headers, lists, etc.)
- Keep all subsection headers and organizational structure
- Do NOT add any new references or citations
- Do NOT include any introductory text, explanations, or phrases like "Here is...", "The edited content...", etc.
- Do NOT add quotation marks around the response
- Return ONLY the edited content itself - start immediately with the actual content
- If the user asks for bullets, convert ONLY the specified content to bullet format without adding introduction

IMPORTANT: Your response must start directly with the edited content. No introduction, no explanation, no "Here is" phrases."""
        else:
            raise HTTPException(status_code=400, detail="Either preset or custom_instructions must be provided")

        # Generate the edited content using the LLM
        try:
            # Use the generation service's LLM directly
            import asyncio
            response = await asyncio.to_thread(gen_service.llm.invoke, prompt)
            
            if hasattr(response, 'content'):
                edited_content = response.content.strip()
            else:
                edited_content = str(response).strip()
            
            # Generate a summary of changes
            summary_prompt = f"""Compare the original and edited content and provide a brief summary of the key changes made.

Original:
{request.content[:200]}...

Edited:
{edited_content[:200]}...

Provide a brief summary of the main changes:"""
            
            summary_response = await asyncio.to_thread(gen_service.llm.invoke, summary_prompt)
            if hasattr(summary_response, 'content'):
                edit_summary = summary_response.content.strip()
            else:
                edit_summary = str(summary_response).strip()
            
            # Generate list of specific changes
            changes_made = []
            if request.preset:
                changes_made.append(f"Applied {request.preset} preset")
            if request.custom_instructions:
                changes_made.append(f"Applied custom instructions: {request.custom_instructions[:50]}...")
            if request.use_rag:
                changes_made.append("Enhanced with additional research from uploaded documents")
            
            return SuggestEditResponse(
                edited_content=edited_content,
                edit_summary=edit_summary,
                changes_made=changes_made
            )
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"Content editing failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Suggest edit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Suggest edit processing failed: {str(e)}")