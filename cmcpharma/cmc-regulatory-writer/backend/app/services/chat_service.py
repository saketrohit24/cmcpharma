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
        
        # Fast response cache for common questions
        self.response_cache: Dict[str, str] = {
            "hi": "Hello! I'm your CMC regulatory assistant. I can help with pharmaceutical questions, document analysis, and regulatory guidance. What would you like to know?",
            "hello": "Hi there! I'm here to help with CMC regulatory matters. Ask me about specifications, stability studies, manufacturing processes, or any pharmaceutical questions!",
            "help": "I can assist with:\n• Pharmaceutical specifications\n• Stability studies and storage conditions\n• Manufacturing processes\n• Analytical methods\n• Regulatory guidelines\n• Document analysis\n\nWhat specific topic interests you?",
            "what can you do": "I specialize in pharmaceutical and regulatory matters. I can help with:\n• CMC (Chemistry, Manufacturing, Controls) questions\n• Stability data interpretation\n• Specification development\n• Manufacturing processes\n• Analytical methods\n• Regulatory guidance\n• Document review and analysis\n\nAsk me anything related to these topics!"
        }
        
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
        
        # OPTIMIZATION: Don't auto-discover files at startup - too slow!
        # Only initialize RAG when actually needed
        initial_file_paths = []  # Empty for faster startup
        
        # Configure GraphRAG if enabled (but don't initialize yet)
        self.graph_rag_config = None
        if settings.USE_GRAPH_RAG:
            self.graph_rag_config = RAGConfig(
                working_dir=settings.GRAPH_RAG_WORKING_DIR,
                chunk_size=settings.GRAPH_RAG_CHUNK_SIZE,
                chunk_overlap=settings.GRAPH_RAG_CHUNK_OVERLAP,
                embedding_batch_num=settings.GRAPH_RAG_EMBEDDING_BATCH_NUM,
                max_async=settings.GRAPH_RAG_MAX_ASYNC,
                global_max_consider_community=settings.GRAPH_RAG_GLOBAL_MAX_CONSIDER_COMMUNITY,
                local_search_top_k=settings.GRAPH_RAG_LOCAL_SEARCH_TOP_K
            )
        
        # Initialize empty RAG service for fast startup
        self.rag_service = None  # Will be initialized on first use
        
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
            ai_response_text, citations = await self._generate_ai_response(
                chat_request.message,
                session,
                chat_request.context,
                getattr(chat_request, 'max_tokens', 1000),
                getattr(chat_request, 'temperature', 0.7),
                getattr(chat_request, 'include_citations', True),
                getattr(chat_request, 'use_rag', True)
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
                citations=citations,
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

    async def refresh_rag_documents(self):
        """Refresh RAG service with currently uploaded documents"""
        try:
            import os
            import glob
            
            # Look for uploaded files in the persistent_uploads directory
            upload_dirs = [
                "persistent_uploads",
                "app/persistent_uploads", 
                "../persistent_uploads",
                "../../persistent_uploads"
            ]
            
            file_paths = []
            for upload_dir in upload_dirs:
                if os.path.exists(upload_dir):
                    # Find all supported document files
                    patterns = ["*.pdf", "*.txt", "*.docx", "*.doc"]
                    for pattern in patterns:
                        file_paths.extend(glob.glob(os.path.join(upload_dir, "**", pattern), recursive=True))
                    break
            
            if file_paths:
                print(f"Found {len(file_paths)} documents for RAG: {file_paths}")
                
                # Update RAG service with new files
                if self.rag_service:
                    self.rag_service.add_documents(file_paths)
                else:
                    # Reinitialize RAG service with found files
                    from app.services.rag_service import RAGService
                    from app.services.graph_rag_service import RAGConfig
                    
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
                        file_paths=file_paths, 
                        use_graph_rag=settings.USE_GRAPH_RAG,
                        graph_rag_config=graph_rag_config
                    )
                    print("RAG service reinitialized with uploaded documents")
            else:
                print("No uploaded documents found for RAG")
                
        except Exception as e:
            print(f"Error refreshing RAG documents: {e}")

    def _discover_uploaded_files(self) -> List[str]:
        """Discover uploaded files for initial RAG loading"""
        import os
        import glob
        
        file_paths = []
        
        # Look for uploaded files in the persistent_uploads directory
        upload_dirs = [
            "persistent_uploads",
            "app/persistent_uploads", 
            "../persistent_uploads",
            "../../persistent_uploads"
        ]
        
        for upload_dir in upload_dirs:
            if os.path.exists(upload_dir):
                # Find all supported document files
                patterns = ["*.pdf", "*.txt", "*.docx", "*.doc"]
                for pattern in patterns:
                    file_paths.extend(glob.glob(os.path.join(upload_dir, "**", pattern), recursive=True))
                print(f"Found {len(file_paths)} documents in {upload_dir}: {file_paths}")
                break
        
        return file_paths

    # Private helper methods

    async def _generate_ai_response(
        self,
        user_message: str,
        session: ChatSession,
        context: Optional[Dict] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        include_citations: bool = True,
        use_rag: bool = True
    ) -> tuple[str, Optional[List[str]]]:
        """Generate AI response to user message using actual LLM with optional RAG"""
        try:
            # FAST PATH 1: Check cache for instant responses
            message_key = user_message.lower().strip()
            if message_key in self.response_cache:
                return self.response_cache[message_key], None
            
            # FAST PATH 2: Simple greetings get immediate responses
            if len(message_key) <= 10 and any(greeting in message_key for greeting in ['hi', 'hello', 'hey', 'test']):
                return "Hello! I'm your CMC regulatory assistant. How can I help you today?", None
            
            # Build conversation context (limited for speed)
            conversation_history = []
            for msg in session.messages[-3:]:  # Reduced from 5 to 3 for speed
                conversation_history.append(f"{msg.sender}: {msg.text}")
            
            # Initialize variables
            rag_context = ""
            citations = []
            
            # FAST PATH 3: Only use RAG if explicitly requested and question needs it
            needs_rag = use_rag and self._question_needs_rag(user_message)
            
            # Only do expensive RAG if explicitly requested and necessary
            if needs_rag:
                try:
                    print(f"Using RAG for: {user_message[:50]}...")
                    # Initialize RAG service if needed (lazy loading)
                    await self._ensure_rag_initialized()
                    
                    if self.rag_service and hasattr(self.rag_service, 'get_relevant_chunks'):
                        # Limit RAG results for speed
                        rag_results = self.rag_service.get_relevant_chunks(user_message, mode="local")
                        if rag_results:
                            rag_context = "\n\nRelevant context from documents:\n"
                            # Only use top 2 results instead of 3 for speed
                            for i, result in enumerate(rag_results[:2]):
                                if hasattr(result, 'page_content'):
                                    # Truncate long content for speed
                                    content = result.page_content[:500] + "..." if len(result.page_content) > 500 else result.page_content
                                    rag_context += f"[{i+1}] {content}\n"
                                    if include_citations:
                                        source = getattr(result, 'metadata', {}).get('source', 'Unknown source')
                                        # Clean up the source path for better display
                                        if source and '/' in source:
                                            source = source.split('/')[-1]  # Get filename only
                                        citations.append(source)
                                elif isinstance(result, str):
                                    content = result[:500] + "..." if len(result) > 500 else result
                                    rag_context += f"[{i+1}] {content}\n"
                                    if include_citations:
                                        citations.append("Knowledge base")
                except Exception as e:
                    print(f"RAG search failed (continuing without): {e}")
                    # Continue without RAG context for speed
                    pass
            else:
                print(f"Skipping RAG for speed: {user_message[:50]}...")
            
            # Create optimized prompt (shorter for faster processing)
            if rag_context:
                prompt = f"""You are a helpful CMC regulatory assistant.

{rag_context}

User: {user_message}

Provide a concise, helpful response."""
            else:
                prompt = f"""You are a helpful CMC regulatory assistant specializing in pharmaceutical matters.

User: {user_message}

Provide a helpful, accurate response."""
            
            # Call the actual LLM with reduced max_tokens for speed
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            
            # Extract response text
            response_text = ""
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Only include citations if the response actually uses document information
            if citations and not self._response_uses_document_info(response_text, rag_context):
                citations = None
            
            return response_text, citations if citations else None
                
        except Exception as e:
            print(f"LLM call failed: {e}")
            # Fast fallback response
            return f"I'm here to help with your pharmaceutical questions! Could you please rephrase your question? You asked: '{user_message}'", None

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
            citations = []
            
            # Build conversation context
            conversation_history = []
            for msg in session.messages[-5:]:  # Last 5 messages for context
                conversation_history.append(f"{msg.sender}: {msg.text}")
            
            # Use RAG if enabled and available - but be very selective
            rag_context = ""
            use_rag = getattr(chat_request, 'use_rag', True)
            include_citations = getattr(chat_request, 'include_citations', True)
            
            # FAST PATH: Check cache first
            message_key = chat_request.message.lower().strip()
            if message_key in self.response_cache:
                # Yield cached response immediately
                cached_response = self.response_cache[message_key]
                full_response = cached_response
                
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
                self.sessions_storage[session.id] = session
                
                # Yield completion immediately
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
                    },
                    "citations": None
                }
                return
            
            # Check if RAG should be used (user toggle + question analysis)
            needs_rag = use_rag and self._question_needs_rag(chat_request.message)
            
            if needs_rag:
                try:
                    print(f"Using RAG in streaming for: {chat_request.message[:50]}...")
                    # Initialize RAG service if needed (lazy loading)
                    await self._ensure_rag_initialized()
                    
                    if self.rag_service and hasattr(self.rag_service, 'get_relevant_chunks'):
                        # Get relevant context from RAG - limited for speed
                        rag_results = self.rag_service.get_relevant_chunks(chat_request.message, mode="local")
                        if rag_results:
                            rag_context = "\n\nRelevant context from documents:\n"
                            # Only use top 2 results for speed
                            for i, result in enumerate(rag_results[:2]):
                                if hasattr(result, 'page_content'):
                                    # Truncate for speed
                                    content = result.page_content[:500] + "..." if len(result.page_content) > 500 else result.page_content
                                    rag_context += f"[{i+1}] {content}\n"
                                    if include_citations:
                                        source = getattr(result, 'metadata', {}).get('source', 'Unknown source')
                                        # Clean up the source path for better display
                                        if source and '/' in source:
                                            source = source.split('/')[-1]  # Get filename only
                                        citations.append(source)
                                elif isinstance(result, str):
                                    content = result[:500] + "..." if len(result) > 500 else result
                                    rag_context += f"[{i+1}] {content}\n"
                                    if include_citations:
                                        citations.append("Knowledge base")
                except Exception as e:
                    print(f"RAG search failed in streaming (continuing without): {e}")
                    # Continue without RAG context
                    pass
            else:
                print(f"Skipping RAG in streaming for speed: {chat_request.message[:50]}...")
            
            # Create optimized prompt
            if rag_context:
                prompt = f"""You are a helpful CMC regulatory assistant.

{rag_context}

User: {chat_request.message}

Provide a concise, helpful response."""
            else:
                prompt = f"""You are a helpful CMC regulatory assistant specializing in pharmaceutical matters.

User: {chat_request.message}

Provide a helpful, accurate response."""
            
            # Use NVIDIA API directly for streaming
            invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Accept": "text/event-stream"
            }
            
            payload = {
                "model": "meta/llama-4-scout-17b-16e-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 256,  # Reduced from 512 for faster responses
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
                },
                "citations": citations if citations else None
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "error": f"Stream processing failed: {str(e)}"
            }

    async def _ensure_rag_initialized(self):
        """Initialize RAG service only when needed for speed"""
        if self.rag_service is not None:
            return  # Already initialized
        
        print("Initializing RAG service (first use)...")
        try:
            # Only load a small subset of documents for speed
            file_paths = self._discover_uploaded_files()
            
            # Limit to max 5 documents for speed
            if len(file_paths) > 5:
                file_paths = file_paths[:5]
                print(f"Limited to first 5 documents for speed: {file_paths}")
            
            if file_paths:
                from app.services.rag_service import RAGService
                self.rag_service = RAGService(
                    file_paths=file_paths,
                    use_graph_rag=settings.USE_GRAPH_RAG,
                    graph_rag_config=self.graph_rag_config
                )
                print(f"RAG service initialized with {len(file_paths)} documents")
            else:
                print("No documents found - RAG service not initialized")
        except Exception as e:
            print(f"Failed to initialize RAG service: {e}")
            # Continue without RAG

    def _question_needs_rag(self, user_message: str) -> bool:
        """Determine if a question needs RAG/document context - USER CONTROLLED"""
        message_lower = user_message.lower()
        
        # FAST PATH: Skip RAG for simple greetings and basic interactions
        simple_phrases = [
            'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
            'thanks', 'thank you', 'bye', 'goodbye', 'see you',
            'how are you', 'what\'s up', 'test', 'testing'
        ]
        
        # Check if message is just a simple greeting
        for phrase in simple_phrases:
            if message_lower.strip() == phrase or message_lower.strip() == phrase + '!':
                print(f"Skipping RAG: Simple greeting")
                return False
        
        # Very short messages (likely greetings) - no RAG
        if len(message_lower.strip()) <= 5:
            print(f"Skipping RAG: Very short message")
            return False
        
        # Since user now controls RAG via toggle, be more permissive
        # Let user decide when to use RAG, but still filter out obvious non-document queries
        
        # Skip RAG for very general questions that clearly don't need documents
        general_patterns = [
            'what is the weather', 'how\'s the weather', 'what time is it',
            'what day is it', 'tell me a joke', 'how are you doing',
            'what\'s your name', 'who are you', 'who created you'
        ]
        
        for pattern in general_patterns:
            if pattern in message_lower:
                print(f"Skipping RAG: General non-document query")
                return False
        
        # For everything else, if user has RAG enabled, let them use it
        print(f"Using RAG: User-controlled")
        return True

    def _response_uses_document_info(self, response: str, rag_context: str) -> bool:
        """Check if the response actually uses information from the RAG context"""
        if not rag_context or not response:
            return False
        
        response_lower = response.lower()
        rag_lower = rag_context.lower()
        
        # Look for specific document references in the response
        document_references = [
            'according to', 'based on', 'from the document', 'the document shows',
            'as stated in', 'per the specification', 'the file indicates'
        ]
        
        for ref in document_references:
            if ref in response_lower:
                return True
        
        # Look for specific content from documents in the response
        document_indicators = [
            'testdrug', 'c12h16n2o3', '236.27', 'testcompound',
            'stability data', 'specifications', 'manufacturing process',
            'analytical method', 'hplc', '25°c', '40°c', '60% rh', '75% rh'
        ]
        
        # Check if response contains specific document content
        for indicator in document_indicators:
            if indicator in response_lower and indicator in rag_lower:
                return True
        
        # Check for specific technical values that appear in both response and RAG context
        import re
        # Find technical values (numbers with units, percentages, formulas)
        tech_patterns = [
            r'\d+[°%]\s*[a-z]+',  # Temperature and percentage with units
            r'\d+\.\d+\s*g/mol',  # Molecular weight
            r'\d+:\d+',           # Ratios
            r'c\d+h\d+[a-z]\d*',  # Chemical formulas
            r'\d+\.\d+\s*mg',     # Dosage amounts
            r'\d+\s*ppm'          # Parts per million
        ]
        
        for pattern in tech_patterns:
            response_values = set(re.findall(pattern, response_lower))
            rag_values = set(re.findall(pattern, rag_lower))
            if response_values & rag_values:  # If there's any intersection
                return True
        
        # Check for exact phrase matches (3+ words) between response and RAG context
        response_words = response_lower.split()
        rag_words = rag_lower.split()
        
        # Look for common 3-word phrases
        for i in range(len(response_words) - 2):
            phrase = ' '.join(response_words[i:i+3])
            if len(phrase) > 10 and phrase in rag_lower:  # Avoid short common phrases
                return True
        
        return False
