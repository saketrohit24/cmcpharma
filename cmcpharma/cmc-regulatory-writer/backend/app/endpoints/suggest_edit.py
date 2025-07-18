from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import time
import uuid
from ..services.chat_service import ChatService
from ..services.rag_service import RAGService
from ..models.chat import ChatRequest

router = APIRouter()

# Pydantic models for request/response
class SuggestEditRequest(BaseModel):
    """Request model for suggest edit functionality"""
    content: str = Field(..., description="The content to be edited")
    preset: Optional[str] = Field(None, description="Selected preset action")
    custom_instructions: Optional[str] = Field(None, description="Custom user instructions")
    use_rag: bool = Field(False, description="Whether to use RAG for additional research")
    maintain_tone: bool = Field(True, description="Maintain original tone")
    preserve_technical_accuracy: bool = Field(True, description="Preserve technical accuracy")
    session_id: str = Field(..., description="Session ID for tracking")
    section_id: Optional[str] = Field(None, description="ID of the section being edited")

class SuggestEditResponse(BaseModel):
    """Response model for suggest edit functionality"""
    edited_content: str = Field(..., description="The edited content")
    processing_time: float = Field(..., description="Time taken to process the request")
    used_rag: bool = Field(..., description="Whether RAG was used")
    preset_used: Optional[str] = Field(None, description="Preset that was applied")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    citations: Optional[List[Dict[str, Any]]] = Field(None, description="Citations if RAG was used")
    request_id: str = Field(..., description="Unique request ID")

# Initialize services
chat_service = ChatService()
# RAG service will be initialized when needed
rag_service = None

# Preset configurations
PRESET_CONFIGS = {
    "shorten": {
        "prompt": "Shorten this content while keeping all key points and important information. Remove redundancy and wordiness without losing meaning.",
        "requires_rag": False
    },
    "clarify": {
        "prompt": "Improve the clarity and readability of this content. Make it easier to understand while maintaining technical accuracy.",
        "requires_rag": False
    },
    "improve_flow": {
        "prompt": "Improve the logical flow and transitions in this content. Make it read more smoothly and coherently.",
        "requires_rag": False
    },
    "make_concise": {
        "prompt": "Make this content more concise by removing unnecessary words and phrases while preserving all essential information.",
        "requires_rag": False
    },
    "expand_detail": {
        "prompt": "Expand this content with more comprehensive details and information. Add relevant technical details and explanations.",
        "requires_rag": True
    },
    "simplify": {
        "prompt": "Simplify this content using clearer language and simpler sentence structure while maintaining technical accuracy.",
        "requires_rag": False
    }
}

def should_use_rag(preset: str, custom_instructions: str, explicit_rag: bool) -> bool:
    """Determine if RAG should be used based on preset and instructions"""
    if explicit_rag:
        return True
    
    if preset and PRESET_CONFIGS.get(preset, {}).get("requires_rag", False):
        return True
    
    if custom_instructions:
        research_keywords = ["research", "find more", "add details", "investigate", "expand upon", "more information"]
        return any(keyword in custom_instructions.lower() for keyword in research_keywords)
    
    return False

def build_edit_prompt(content: str, preset: str, custom_instructions: str, maintain_tone: bool, preserve_technical_accuracy: bool) -> str:
    """Build the prompt for content editing"""
    
    # Build a simple, direct prompt
    instruction = PRESET_CONFIGS[preset]['prompt'] if preset and preset in PRESET_CONFIGS else 'Edit this text'
    
    # Add custom instructions if provided
    if custom_instructions:
        instruction = f"{instruction} {custom_instructions}"
    
    # Add clear output format instruction
    prompt = f"{instruction}\n\nIMPORTANT: Return ONLY the edited content without explanations.\n\nText: {content}"
    
    return prompt

def clean_edit_response(content: str) -> str:
    """Clean up the model response to extract only the edited content"""
    # Remove common prefixes
    prefixes_to_remove = [
        "Here is the edited content:",
        "Here's the edited content:",
        "Edited content:",
        "Content shortened:",
        "The shortened content:",
        "Shortened:",
        "Clarified content:",
        "Improved content:",
        "Here is the",
        "Here's the",
        "The edited text:",
        "Edited text:",
        "Content:",
        "Text:",
        "Result:",
        "Output:",
        "Shorten the content:",
        "Clarify the content:",
        "Improve the content:",
        "Make the content concise:",
        "Simplify the content:",
        "Expand the content:",
    ]
    
    content = content.strip()
    
    # Remove prefixes
    for prefix in prefixes_to_remove:
        if content.lower().startswith(prefix.lower()):
            content = content[len(prefix):].strip()
            break
    
    # Remove leading colons and newlines
    content = content.lstrip(':').lstrip('\n').strip()
    
    # Remove quotes if the entire content is wrapped in quotes
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1].strip()
    
    # Remove any remaining leading/trailing whitespace
    content = content.strip()
    
    return content

@router.post("/suggest-edit", response_model=SuggestEditResponse)
async def suggest_edit(request: SuggestEditRequest):
    """
    Process content editing based on presets and custom instructions
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Validate input
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        if not request.preset and not request.custom_instructions:
            raise HTTPException(status_code=400, detail="Either preset or custom instructions must be provided")
        
        # Determine if RAG should be used
        use_rag = should_use_rag(request.preset, request.custom_instructions or "", request.use_rag)
        
        # Build the editing prompt
        edit_prompt = build_edit_prompt(
            content=request.content,
            preset=request.preset,
            custom_instructions=request.custom_instructions or "",
            maintain_tone=request.maintain_tone,
            preserve_technical_accuracy=request.preserve_technical_accuracy
        )
        
        # Debug: log the prompt
        print(f"DEBUG: Edit prompt: {edit_prompt}")
        print(f"DEBUG: Content length: {len(request.content)}")
        
        citations = None
        tokens_used = None
        
        if use_rag:
            # For RAG-enhanced editing, we'll use the chat service with additional context
            # In a real implementation, this would retrieve relevant documents first
            enhanced_prompt = f"{edit_prompt}\n\nNote: Use your knowledge base to provide additional relevant information where appropriate."
            
            chat_request = ChatRequest(
                message=enhanced_prompt,
                session_id=request.session_id
            )
            chat_response = await chat_service.send_message(chat_request)
            edited_content = clean_edit_response(chat_response.message.text)
            tokens_used = chat_response.tokens_used
            citations = None  # Would be populated with actual RAG implementation
        else:
            # Use regular chat service for direct editing
            chat_request = ChatRequest(
                message=edit_prompt,
                session_id=request.session_id
            )
            chat_response = await chat_service.send_message(chat_request)
            edited_content = clean_edit_response(chat_response.message.text)
            tokens_used = chat_response.tokens_used
        
        processing_time = time.time() - start_time
        
        return SuggestEditResponse(
            edited_content=edited_content,
            processing_time=processing_time,
            used_rag=use_rag,
            preset_used=request.preset,
            tokens_used=tokens_used,
            citations=citations,
            request_id=request_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing edit suggestion: {str(e)}")

@router.get("/suggest-edit/presets")
async def get_presets():
    """Get available presets for suggest edit functionality"""
    return {
        "presets": [
            {
                "id": "shorten",
                "name": "Shorten",
                "description": "Reduce content length while keeping key points",
                "requires_rag": False
            },
            {
                "id": "clarify",
                "name": "Clarify",
                "description": "Improve readability and clarity",
                "requires_rag": False
            },
            {
                "id": "improve_flow",
                "name": "Improve Flow",
                "description": "Better transitions and logical progression",
                "requires_rag": False
            },
            {
                "id": "make_concise",
                "name": "Make Concise",
                "description": "Remove redundancy and wordiness",
                "requires_rag": False
            },
            {
                "id": "expand_detail",
                "name": "Expand Detail",
                "description": "Add more comprehensive information",
                "requires_rag": True
            },
            {
                "id": "simplify",
                "name": "Simplify",
                "description": "Use simpler language and structure",
                "requires_rag": False
            }
        ]
    }
