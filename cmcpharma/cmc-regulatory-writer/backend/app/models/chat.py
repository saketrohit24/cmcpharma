"""
Pydantic models for chat and AI interaction
"""
from datetime import datetime
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model"""
    id: str = Field(..., description="Unique message identifier")
    text: str = Field(..., min_length=1, description="Message text")
    sender: Literal['user', 'assistant'] = Field(..., description="Message sender")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    context: Optional[Dict[str, str]] = Field(None, description="Message context (document, section, etc.)")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional message metadata")
    session_id: str = Field(..., description="Chat session identifier")


class ChatSession(BaseModel):
    """Chat session model"""
    id: str = Field(..., description="Unique session identifier")
    messages: List[ChatMessage] = Field(default_factory=list, description="Session messages")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation timestamp")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")
    title: Optional[str] = Field(None, description="Session title")
    user_id: Optional[str] = Field(None, description="User identifier")
    context: Optional[Dict[str, str]] = Field(None, description="Session context")
    is_active: bool = Field(default=True, description="Whether session is active")


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Existing session ID")
    context: Optional[Dict[str, str]] = Field(None, description="Request context")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum response tokens")
    temperature: Optional[float] = Field(default=0.7, description="Response creativity")
    include_citations: bool = Field(default=True, description="Include citations in response")


class ChatResponse(BaseModel):
    """Chat response model"""
    message: ChatMessage = Field(..., description="Assistant response message")
    session: ChatSession = Field(..., description="Updated session")
    citations: Optional[List[str]] = Field(None, description="Citations used in response")
    tokens_used: Optional[int] = Field(None, description="Tokens used for response")
    processing_time: Optional[float] = Field(None, description="Response processing time in seconds")


class ChatGenerationRequest(BaseModel):
    """Request for generating content via chat"""
    prompt: str = Field(..., min_length=1, description="Generation prompt")
    document_id: Optional[str] = Field(None, description="Target document ID")
    section_id: Optional[str] = Field(None, description="Target section ID")
    template_id: Optional[str] = Field(None, description="Template to use for generation")
    context_files: Optional[List[str]] = Field(None, description="Context files for RAG")
    generation_type: Literal['content', 'summary', 'revision', 'citation'] = Field(..., description="Type of generation")
    parameters: Optional[Dict[str, str]] = Field(None, description="Additional generation parameters")


class ChatFeedback(BaseModel):
    """Chat feedback model"""
    message_id: str = Field(..., description="Message being rated")
    rating: Literal['thumbs_up', 'thumbs_down'] = Field(..., description="User rating")
    feedback_text: Optional[str] = Field(None, description="Optional feedback text")
    timestamp: datetime = Field(default_factory=datetime.now, description="Feedback timestamp")


class ChatSessionCreate(BaseModel):
    """Model for creating a new chat session"""
    title: Optional[str] = Field(None, description="Session title")
    context: Optional[Dict[str, str]] = Field(None, description="Initial session context")
    user_id: Optional[str] = Field(None, description="User identifier")


class ChatSessionUpdate(BaseModel):
    """Model for updating a chat session"""
    title: Optional[str] = Field(None, description="Session title")
    context: Optional[Dict[str, str]] = Field(None, description="Session context")
    is_active: Optional[bool] = Field(None, description="Whether session is active")


class ChatSettings(BaseModel):
    """Chat settings model"""
    model: str = Field(default="gpt-4", description="AI model to use")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Response creativity")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum response tokens")
    include_citations: bool = Field(default=True, description="Include citations by default")
    auto_save_sessions: bool = Field(default=True, description="Automatically save chat sessions")
    context_window: int = Field(default=10, ge=1, le=50, description="Number of previous messages to include")
