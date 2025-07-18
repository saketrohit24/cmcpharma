"""
Chat service for AI-pow        # Initialize LLM
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is not set in the environment.")
        self.llm = ChatNVIDIA(
            model="meta/llama-4-scout-17b-16e-instruct", 
            nvidia_api_key=settings.LLM_API_KEY, 
            max_tokens=512,
            temperature=0.7
        ) functionality
"""
import uuid
import asyncio
import json
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from app.models.chat import (
    ChatMessage, ChatSession, ChatRequest, ChatResponse,
    ChatGenerationRequest, ChatSessionCreate, ChatSessionUpdate, ChatFeedback
)
from app.services.generation_service import GenerationService
from app.services.rag_service import RAGService
from app.services.graph_rag_service import RAGConfig
from app.core.config import settings


class ChatService:
    """
    Service for handling AI chat functionality and content generation
    """

    def __init__(self):
        """Initialize chat service"""
        self.sessions_storage: Dict[str, ChatSession] = {}
        self.message_feedback: Dict[str, ChatFeedback] = {}
        
        # Initialize LLM
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is not set in the environment.")
        self.llm = ChatNVIDIA(
            model="meta/llama-4-scout-17b-16e-instruct", 
            nvidia_api_key=settings.LLM_API_KEY, 
            max_tokens=512,
            temperature=1.0
        )
        
        # Initialize related services
        self.generation_service = GenerationService()
        
        # Configure GraphRAG if enabled
        graph_rag_config = None
        if settings.USE_GRAPH_RAG:
            graph_rag_config = RAGConfig(
                working_dir=settings.GRAPH_RAG_WORKING_DIR,
                chunk_size=settings.GRAPH_RAG_CHUNK_SIZE,
                chunk_overlap=settings.GRAPH_RAG_CHUNK_OVERLAP,
                embedding_batch_num=settings.GRAPH_RAG_EMBEDDING_BATCH_NUM,
                max_async=settings.GRAPH_RAG_MAX_ASYNC,
                global_max_consider_community=settings.GRAPH_RAG_GLOBAL_MAX_CONSIDER_COMMUNITY,
                local_search_top_k=settings.GRAPH_RAG_LOCAL_SEARCH_TOP_K
            )
        
        self.rag_service = RAGService(
            file_paths=[], 
            use_graph_rag=settings.USE_GRAPH_RAG,
            graph_rag_config=graph_rag_config
        )
        
        # Chat configuration
        self.max_history_length = 50
        self.session_timeout_minutes = 30

    async def create_session(self, session_data: ChatSessionCreate) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            id=str(uuid.uuid4()),
            messages=[],
            created_at=datetime.now(),
            last_activity=datetime.now(),
            title=session_data.title,
            user_id=session_data.user_id,
            context=session_data.context or {},
            is_active=True
        )
        
        self.sessions_storage[session.id] = session
        return session

    async def get_sessions(self, user_id: Optional[str] = None, active_only: bool = True) -> List[ChatSession]:
        """Get chat sessions for a user"""
        sessions = list(self.sessions_storage.values())
        
        # Filter by user
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        # Filter by active status
        if active_only:
            sessions = [s for s in sessions if s.is_active]
        
        # Sort by last activity (most recent first)
        sessions.sort(key=lambda s: s.last_activity, reverse=True)
        
        return sessions

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a specific chat session"""
        return self.sessions_storage.get(session_id)

    async def update_session(self, session_id: str, session_data: ChatSessionUpdate) -> Optional[ChatSession]:
        """Update a chat session"""
        session = self.sessions_storage.get(session_id)
        if not session:
            return None
        
        # Update fields if provided
        if session_data.title is not None:
            session.title = session_data.title
        if session_data.context is not None:
            session.context = session_data.context
        if session_data.is_active is not None:
            session.is_active = session_data.is_active
        
        session.last_activity = datetime.now()
        self.sessions_storage[session_id] = session
        return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        if session_id in self.sessions_storage:
            del self.sessions_storage[session_id]
            return True
        return False

    async def send_message(self, chat_request: ChatRequest) -> ChatResponse:
        """Send a message and get AI response"""
        try:
            # Get or create session
            session = None
            if chat_request.session_id:
                session = self.sessions_storage.get(chat_request.session_id)
            
            if not session:
                # Create new session
                session = ChatSession(
                    id=str(uuid.uuid4()),
                    messages=[],
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                    is_active=True
                )
                self.sessions_storage[session.id] = session
            
            # Create user message
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                text=chat_request.message,
                sender="user",
                timestamp=datetime.now(),
                context=chat_request.context,
                session_id=session.id
            )
            
            # Add user message to session
            session.messages.append(user_message)
            
            # Generate AI response
            ai_response_text = await self._generate_ai_response(
                chat_request.message,
                session,
                chat_request.context,
                chat_request.max_tokens,
                chat_request.temperature,
                chat_request.include_citations
            )
            
            # Create AI message
            ai_message = ChatMessage(
                id=str(uuid.uuid4()),
                text=ai_response_text,
                sender="assistant",
                timestamp=datetime.now(),
                context=chat_request.context,
                session_id=session.id
            )
            
            # Add AI message to session
            session.messages.append(ai_message)
            
            # Update session activity
            session.last_activity = datetime.now()
            
            # Trim message history if too long
            if len(session.messages) > self.max_history_length:
                session.messages = session.messages[-self.max_history_length:]
            
            self.sessions_storage[session.id] = session
            
            # Create response
            response = ChatResponse(
                message=ai_message,
                session=session,
                citations=None,  # TODO: Extract citations if requested
                tokens_used=len(ai_response_text.split()),  # Mock token count
                processing_time=1.5  # Mock processing time
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Chat message processing failed: {str(e)}")

    async def generate_content(self, generation_request: ChatGenerationRequest) -> ChatResponse:
        """Generate content using AI with specific parameters"""
        try:
            # Get relevant context if files specified
            context_content = []
            if generation_request.context_files:
                context_content = await self.rag_service.retrieve_relevant_content(
                    generation_request.prompt,
                    generation_request.context_files,
                    top_k=5
                )
            
            # Generate content based on type
            if generation_request.generation_type == "content":
                generated_text = await self._generate_content(
                    generation_request.prompt,
                    context_content,
                    generation_request.parameters
                )
            elif generation_request.generation_type == "summary":
                generated_text = await self._generate_summary(
                    generation_request.prompt,
                    context_content
                )
            elif generation_request.generation_type == "revision":
                generated_text = await self._generate_revision(
                    generation_request.prompt,
                    context_content,
                    generation_request.parameters
                )
            elif generation_request.generation_type == "citation":
                generated_text = await self._generate_citation_help(
                    generation_request.prompt,
                    context_content
                )
            else:
                generated_text = await self._generate_content(
                    generation_request.prompt,
                    context_content,
                    generation_request.parameters
                )
            
            # Create message
            message = ChatMessage(
                id=str(uuid.uuid4()),
                text=generated_text,
                sender="assistant",
                timestamp=datetime.now(),
                context={
                    "generation_type": generation_request.generation_type,
                    "document_id": generation_request.document_id,
                    "section_id": generation_request.section_id,
                    "template_id": generation_request.template_id
                },
                session_id="generation_session"
            )
            
            # Create mock session for generation
            session = ChatSession(
                id="generation_session",
                messages=[message],
                created_at=datetime.now(),
                last_activity=datetime.now(),
                title=f"Content Generation - {generation_request.generation_type}",
                is_active=True
            )
            
            return ChatResponse(
                message=message,
                session=session,
                citations=None,
                tokens_used=len(generated_text.split()),
                processing_time=2.0
            )
            
        except Exception as e:
            raise Exception(f"Content generation failed: {str(e)}")

    async def clear_session(self, session_id: str) -> bool:
        """Clear all messages from a chat session"""
        session = self.sessions_storage.get(session_id)
        if not session:
            return False
        
        session.messages = []
        session.last_activity = datetime.now()
        self.sessions_storage[session_id] = session
        return True

    async def export_session(self, session: ChatSession, format: str = "json") -> str:
        """Export chat session to specified format"""
        if format == "json":
            import json
            
            export_data = {
                "session_id": session.id,
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "message_count": len(session.messages),
                "messages": [
                    {
                        "id": msg.id,
                        "text": msg.text,
                        "sender": msg.sender,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in session.messages
                ]
            }
            
            return json.dumps(export_data, indent=2)
        
        elif format == "txt":
            lines = [
                f"Chat Session: {session.title or session.id}",
                f"Created: {session.created_at}",
                f"Messages: {len(session.messages)}",
                "-" * 50
            ]
            
            for msg in session.messages:
                lines.append(f"\n{msg.sender.upper()} ({msg.timestamp}):")
                lines.append(msg.text)
                lines.append("")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def submit_feedback(self, message_id: str, rating: str, feedback_text: Optional[str] = None):
        """Submit feedback for a chat message"""
        feedback = ChatFeedback(
            message_id=message_id,
            rating=rating,
            feedback_text=feedback_text,
            timestamp=datetime.now()
        )
        
        self.message_feedback[message_id] = feedback

    async def cleanup_inactive_sessions(self):
        """Clean up inactive sessions (run periodically)"""
        cutoff_time = datetime.now() - timedelta(minutes=self.session_timeout_minutes)
        
        inactive_sessions = [
            session_id for session_id, session in self.sessions_storage.items()
            if session.last_activity < cutoff_time and session.is_active
        ]
        
        for session_id in inactive_sessions:
            session = self.sessions_storage[session_id]
            session.is_active = False
            self.sessions_storage[session_id] = session

    # Private helper methods

    async def _generate_ai_response(
        self,
        user_message: str,
        session: ChatSession,
        context: Optional[Dict] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        include_citations: bool = True
    ) -> str:
        """Generate AI response to user message using actual LLM"""
        try:
            # Build conversation context
            conversation_history = []
            for msg in session.messages[-5:]:  # Last 5 messages for context
                conversation_history.append(f"{msg.sender}: {msg.text}")
            
            # Create prompt with context
            if conversation_history:
                prompt = f"""You are a helpful AI assistant. You can answer both general questions and specialized pharmaceutical/regulatory questions.

Conversation history:
{chr(10).join(conversation_history)}

User: {user_message}

Please provide a helpful, accurate response. Answer naturally and directly to what the user is asking about."""
            else:
                prompt = f"""You are a helpful AI assistant. You can answer both general questions and specialized pharmaceutical/regulatory questions.

User: {user_message}

Please provide a helpful, accurate response. Answer naturally and directly to what the user is asking about."""
            
            # Call the actual LLM
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            
            # Extract response text
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            print(f"LLM call failed: {e}")
            # Fallback to a simple response
            return f"I apologize, but I'm having trouble processing your request right now. Could you please try asking your question again? You asked: '{user_message}'"

    async def _generate_content(
        self,
        prompt: str,
        context_content: List[Dict],
        parameters: Optional[Dict] = None
    ) -> str:
        """Generate content based on prompt and context"""
        # TODO: Use actual generation service
        return f"Generated content based on: {prompt}"

    async def _generate_summary(self, prompt: str, context_content: List[Dict]) -> str:
        """Generate summary content"""
        return f"Summary of: {prompt}"

    async def _generate_revision(
        self,
        prompt: str,
        context_content: List[Dict],
        parameters: Optional[Dict] = None
    ) -> str:
        """Generate content revision"""
        return f"Revised content for: {prompt}"

    async def _generate_citation_help(self, prompt: str, context_content: List[Dict]) -> str:
        """Generate citation assistance"""
        return f"Citation help for: {prompt}"

    async def stream_message(self, chat_request: ChatRequest):
        """Stream a message response with typing effect"""
        try:
            # Get or create session
            session = None
            if chat_request.session_id:
                session = self.sessions_storage.get(chat_request.session_id)
            
            if not session:
                # Create new session
                session = ChatSession(
                    id=str(uuid.uuid4()),
                    messages=[],
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                    is_active=True
                )
                self.sessions_storage[session.id] = session
            
            # Create user message
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                text=chat_request.message,
                sender="user",
                timestamp=datetime.now(),
                context=chat_request.context,
                session_id=session.id
            )
            
            # Add user message to session
            session.messages.append(user_message)
            
            # Yield user message first
            yield {
                "type": "user_message",
                "message": {
                    "id": user_message.id,
                    "text": user_message.text,
                    "sender": user_message.sender,
                    "timestamp": user_message.timestamp.isoformat(),
                    "session_id": session.id
                }
            }
            
            # Generate AI response with streaming
            ai_message_id = str(uuid.uuid4())
            full_response = ""
            
            # Build conversation context
            conversation_history = []
            for msg in session.messages[-5:]:  # Last 5 messages for context
                conversation_history.append(f"{msg.sender}: {msg.text}")
            
            # Create prompt with context
            if conversation_history:
                prompt = f"""You are a helpful AI assistant. You can answer both general questions and specialized pharmaceutical/regulatory questions.

Conversation history:
{chr(10).join(conversation_history)}

User: {chat_request.message}

Please provide a helpful, accurate response. Answer naturally and directly to what the user is asking about."""
            else:
                prompt = f"""You are a helpful AI assistant. You can answer both general questions and specialized pharmaceutical/regulatory questions.

User: {chat_request.message}

Please provide a helpful, accurate response. Answer naturally and directly to what the user is asking about."""
            
            # Use NVIDIA API directly for streaming
            invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Accept": "text/event-stream"
            }
            
            payload = {
                "model": "meta/llama-4-scout-17b-16e-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
                "temperature": 0.7,
                "stream": True
            }
            
            # Stream the response
            response = requests.post(invoke_url, headers=headers, json=payload, stream=True)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    chunk = delta['content']
                                    full_response += chunk
                                    
                                    # Yield the chunk
                                    yield {
                                        "type": "chunk",
                                        "chunk": chunk,
                                        "message_id": ai_message_id
                                    }
                        except json.JSONDecodeError:
                            continue
            
            # Create final AI message
            ai_message = ChatMessage(
                id=ai_message_id,
                text=full_response,
                sender="assistant",
                timestamp=datetime.now(),
                context=chat_request.context,
                session_id=session.id
            )
            
            # Add AI message to session
            session.messages.append(ai_message)
            session.last_activity = datetime.now()
            
            # Trim message history if too long
            if len(session.messages) > self.max_history_length:
                session.messages = session.messages[-self.max_history_length:]
            
            self.sessions_storage[session.id] = session
            
            # Yield completion message
            yield {
                "type": "complete",
                "message": {
                    "id": ai_message.id,
                    "text": ai_message.text,
                    "sender": ai_message.sender,
                    "timestamp": ai_message.timestamp.isoformat(),
                    "session_id": session.id
                },
                "session": {
                    "id": session.id,
                    "message_count": len(session.messages)
                }
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "error": f"Stream processing failed: {str(e)}"
            }
