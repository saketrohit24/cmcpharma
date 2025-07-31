"""
Chat and AI interaction endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio
from app.models.chat import (
    ChatMessage, ChatSession, ChatRequest, ChatResponse,
    ChatGenerationRequest, ChatSessionCreate, ChatSessionUpdate
)
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])

# Create a single global instance to avoid re-initialization
_chat_service_instance = None

def get_chat_service() -> ChatService:
    """Dependency to get chat service instance - using singleton pattern for performance"""
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
    return _chat_service_instance


@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(
    session_data: ChatSessionCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session"""
    try:
        return await chat_service.create_session(session_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[ChatSession])
async def get_chat_sessions(
    user_id: Optional[str] = None,
    active_only: bool = True,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all chat sessions for a user"""
    try:
        return await chat_service.get_sessions(user_id=user_id, active_only=active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get a specific chat session"""
    try:
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}", response_model=ChatSession)
async def update_chat_session(
    session_id: str,
    session_data: ChatSessionUpdate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Update a chat session"""
    try:
        session = await chat_service.update_session(session_id, session_data)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Delete a chat session"""
    try:
        success = await chat_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return {"message": "Chat session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: str,
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message in a chat session"""
    try:
        # Ensure the session ID matches
        chat_request.session_id = session_id
        
        response = await chat_service.send_message(chat_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=ChatResponse)
async def send_message_new_session(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message (creates new session if none specified)"""
    try:
        response = await chat_service.send_message(chat_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=ChatResponse)
async def generate_content(
    generation_request: ChatGenerationRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Generate content using AI with specific parameters"""
    try:
        response = await chat_service.generate_content(generation_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/clear")
async def clear_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Clear all messages from a chat session"""
    try:
        success = await chat_service.clear_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return {"message": "Chat session cleared successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/export")
async def export_session(
    session_id: str,
    format: str = "json",
    chat_service: ChatService = Depends(get_chat_service)
):
    """Export chat session to specified format"""
    try:
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        exported_data = await chat_service.export_session(session, format)
        return {"format": format, "data": exported_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    message_id: str,
    rating: str,
    feedback_text: Optional[str] = None,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Submit feedback for a chat message"""
    try:
        await chat_service.submit_feedback(message_id, rating, feedback_text)
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/stream")
async def stream_chat_session(
    session_id: str,
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Stream messages in a chat session"""
    async def event_stream():
        try:
            # Ensure the session ID matches
            chat_request.session_id = session_id

            async for response in chat_service.stream_message(chat_request):
                yield f"data: {json.dumps(response.dict())}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/message/stream")
async def stream_message_new_session(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Stream a message response (creates new session if none specified)"""
    async def event_stream():
        try:
            async for chunk in chat_service.stream_message(chat_request):
                yield f"data: {json.dumps(chunk)}\n\n"
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
