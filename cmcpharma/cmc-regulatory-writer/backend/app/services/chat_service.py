"""
Chat service for AI-powered functionality
"""
import uuid
import asyncio
import json
import requests
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from app.models.chat import (
    ChatMessage, ChatSession, ChatRequest, ChatResponse,
    ChatGenerationRequest, ChatSessionCreate, ChatSessionUpdate, ChatFeedback
)
from app.services.generation_service import GenerationService
from app.services.rag_service import RAGService
from app.core.config import settings


class ChatService:
    """
    Service for handling AI chat functionality and content generation
    """

    def __init__(self):
        """Initialize chat service"""
        self.sessions_storage: Dict[str, ChatSession] = {}
        self.message_feedback: Dict[str, ChatFeedback] = {}
        
        # Initialize LLM lazily to avoid blocking initialization
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is not set in the environment.")
        self.llm = None  # Will be initialized on first use
        
        # Initialize related services
        self.generation_service = GenerationService()
        
        # Initialize RAG service lazily to avoid blocking initialization
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

    def _ensure_llm_initialized(self):
        """Lazy initialization of LLM"""
        if self.llm is None:
            try:
                print("🔄 Initializing ChatNVIDIA LLM...")
                self.llm = ChatNVIDIA(
                    model="meta/llama-4-scout-17b-16e-instruct", 
                    nvidia_api_key=settings.LLM_API_KEY, 
                    max_tokens=400,  # Reduced for faster responses
                    temperature=0.7
                )
                print("✅ ChatNVIDIA LLM initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize LLM: {e}")
                self.llm = "error"  # Mark as error to avoid repeated attempts
        return self.llm != "error"

    def _ensure_rag_initialized(self):
        """Lazy initialization of RAG service"""
        if self.rag_service is None:
            try:
                print("🔄 Initializing RAG service...")
                upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "persistent_uploads")
                print(f"🔍 ChatService: Looking for documents in: {upload_dir}")
                available_files = self._get_all_document_files(upload_dir)
                print(f"🔍 ChatService: Found {len(available_files)} documents: {available_files}")
                self.rag_service = RAGService(file_paths=available_files)
                print("✅ RAG service initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize RAG service: {e}")
                self.rag_service = "error"  # Mark as error to avoid repeated attempts
        return self.rag_service != "error"

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
            # Debug logging
            print(f"🔍 _generate_ai_response called with max_tokens={max_tokens}, temp={temperature}")
            
            # Check for fast local responses first (avoid slow LLM calls)
            fast_response = self._get_fast_local_response(user_message, include_citations)
            if fast_response:
                print(f"⚡ Using fast local response for: {user_message}")
                return fast_response
            
            # Check if this is a data verification query
            if self._is_data_verification_query(user_message):
                print(f"📍 Detected data verification query: {user_message}")
                return await self._handle_data_verification_query(user_message, session, context)
            
            # Ensure LLM is initialized
            if not self._ensure_llm_initialized():
                return "I apologize, but I'm having trouble initializing my language model. Please try again in a few moments."
            
            # Build conversation context
            conversation_history = []
            for msg in session.messages[-5:]:  # Last 5 messages for context
                conversation_history.append(f"{msg.sender}: {msg.text}")
            
            # Only use RAG for document-specific queries, not general pharmaceutical knowledge
            should_use_rag = include_citations and self._needs_document_search(user_message)
            
            # Get RAG context with citations only if document search is needed
            rag_context = ""
            citations_list = []
            if should_use_rag:
                try:
                    # Ensure RAG service is initialized
                    if self._ensure_rag_initialized():
                        relevant_docs = await self.rag_service.retrieve_relevant_content(
                            query=user_message,
                            file_paths=[],
                            top_k=5
                        )
                        
                        if relevant_docs:
                            context_parts = []
                            for i, doc in enumerate(relevant_docs):
                                doc_name = doc.get('source', f'Document_{i+1}')
                                page_num = doc.get('page', 1)
                                content = doc.get('content', '')[:400]
                                
                                context_parts.append(f"[{i+1}] From '{doc_name}', Page {page_num}: {content}")
                                citations_list.append(f"[{i+1}] {doc_name}, Page {page_num}")
                            
                            rag_context = f"""
RELEVANT DOCUMENT SOURCES:
{chr(10).join(context_parts)}

IMPORTANT: When referencing information from these sources, include the citation number [1], [2], etc. in your response.
"""
                        else:
                            rag_context = "No relevant information found in uploaded documents."
                    else:
                        rag_context = "Document search service is currently initializing. Using general knowledge."
                except Exception as e:
                    print(f"RAG retrieval failed: {e}")
                    rag_context = "Document search temporarily unavailable."
            
            # Create prompt with pharma focus
            if conversation_history:
                prompt = f"""You are a specialized pharmaceutical regulatory affairs assistant with expertise in CMC (Chemistry, Manufacturing, and Controls), FDA regulations, ICH guidelines, drug development, and pharmaceutical quality systems.

PHARMACEUTICAL EXPERTISE AREAS:
- CMC documentation and submissions
- FDA regulations (21 CFR, etc.)
- ICH guidelines (Q7, Q8, Q9, Q10, Q11, Q12, etc.)
- Pharmaceutical manufacturing and quality
- Regulatory submissions (IND, NDA, ANDA, etc.)
- GMP compliance and validation
- Analytical method development
- Stability studies
- Drug substance and drug product development

{rag_context}

Conversation history:
{chr(10).join(conversation_history)}

User: {user_message}

RESPONSE GUIDELINES:
- For simple greetings (hi, hello, thanks): Give brief, friendly responses without boilerplate text
- For technical pharmaceutical questions: Provide detailed, expert-level guidance  
- For general questions: Answer helpfully and concisely
- Always maintain accuracy and cite relevant regulations or guidelines when applicable
- Use professional pharmaceutical terminology appropriately"""
            else:
                prompt = f"""You are a specialized pharmaceutical regulatory affairs assistant with expertise in CMC (Chemistry, Manufacturing, and Controls), FDA regulations, ICH guidelines, drug development, and pharmaceutical quality systems.

PHARMACEUTICAL EXPERTISE AREAS:
- CMC documentation and submissions
- FDA regulations (21 CFR, etc.)
- ICH guidelines (Q7, Q8, Q9, Q10, Q11, Q12, etc.)
- Pharmaceutical manufacturing and quality
- Regulatory submissions (IND, NDA, ANDA, etc.)
- GMP compliance and validation
- Analytical method development
- Stability studies
- Drug substance and drug product development

{rag_context}

User: {user_message}

RESPONSE GUIDELINES:
- For simple greetings (hi, hello, thanks): Give brief, friendly responses without boilerplate text
- For technical pharmaceutical questions: Provide detailed, expert-level guidance  
- For general questions: Answer helpfully and concisely
- Always maintain accuracy and cite relevant regulations or guidelines when applicable
- Use professional pharmaceutical terminology appropriately"""
            
            # Use shorter prompt for faster responses if max_tokens is low
            if max_tokens <= 100:
                print(f"🔄 Using SHORT prompt mode for max_tokens={max_tokens}")
                # Quick response mode with minimal prompt
                short_prompt = f"""You are a pharmaceutical regulatory expert specializing in CMC and FDA regulations.

User: {user_message}

Provide a concise, expert response (max {max_tokens} tokens):"""
                
                # Create LLM instance with dynamic parameters for short responses
                dynamic_llm = ChatNVIDIA(
                    model="meta/llama-4-scout-17b-16e-instruct", 
                    nvidia_api_key=settings.LLM_API_KEY, 
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(dynamic_llm.invoke, short_prompt), 
                    timeout=6.0  # Even faster timeout for short responses
                )
            else:
                print(f"🔄 Using FULL prompt mode for max_tokens={max_tokens}")
                # Full response mode with detailed prompt and dynamic parameters
                dynamic_llm = ChatNVIDIA(
                    model="meta/llama-4-scout-17b-16e-instruct", 
                    nvidia_api_key=settings.LLM_API_KEY, 
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(dynamic_llm.invoke, prompt), 
                    timeout=12.0  # Reduced timeout for faster responses
                )
            
            # Extract response text
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Add citations to response only if the response actually contains citation numbers
            if include_citations and citations_list and any(f'[{i+1}]' in response_text for i in range(len(citations_list))):
                if not response_text.endswith('\n'):
                    response_text += '\n'
                response_text += '\n**References:**\n'
                for citation in citations_list:
                    response_text += f'{citation}\n'
            
            return response_text
                
        except asyncio.TimeoutError:
            print(f"LLM call timed out after 15 seconds")
            return f"I apologize, but my response is taking longer than expected. Please try asking a shorter question or try again later."
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
            
            # Check for fast local responses first (avoid slow streaming API calls)
            fast_response = self._get_fast_local_response(chat_request.message, chat_request.use_rag)
            if fast_response:
                print(f"⚡ Using fast local response for streaming: {chat_request.message}")
                # Simulate streaming for fast responses
                ai_message_id = str(uuid.uuid4())
                
                # Stream the fast response word by word for better UX
                words = fast_response.split(' ')
                full_response = ""
                
                for i, word in enumerate(words):
                    chunk = word + (' ' if i < len(words) - 1 else '')
                    full_response += chunk
                    yield {
                        "type": "chunk",
                        "chunk": chunk,
                        "message_id": ai_message_id
                    }
                    # Small delay to simulate typing
                    await asyncio.sleep(0.05)
                
                # Create final message and return
                ai_message = ChatMessage(
                    id=ai_message_id,
                    text=full_response,
                    sender="assistant",
                    timestamp=datetime.now(),
                    context=chat_request.context,
                    session_id=session.id
                )
                session.messages.append(ai_message)
                session.last_activity = datetime.now()
                self.sessions_storage[session.id] = session
                
                yield {
                    "type": "complete",
                    "message": {
                        "id": ai_message.id,
                        "text": ai_message.text,
                        "sender": ai_message.sender,
                        "timestamp": ai_message.timestamp.isoformat(),
                        "session_id": session.id
                    },
                    "session": {"id": session.id, "message_count": len(session.messages)}
                }
                return
            
            # Generate AI response with streaming
            ai_message_id = str(uuid.uuid4())
            full_response = ""
            
            # Build conversation context
            conversation_history = []
            for msg in session.messages[-5:]:  # Last 5 messages for context
                conversation_history.append(f"{msg.sender}: {msg.text}")
            
            # Only use RAG for document-specific queries, not general pharmaceutical knowledge
            should_use_rag = chat_request.use_rag and self._needs_document_search(chat_request.message)
            
            # Get RAG context with citations only if document search is needed
            rag_context = ""
            citations_list = []
            if should_use_rag:
                try:
                    # Ensure RAG service is initialized
                    if self._ensure_rag_initialized():
                        relevant_docs = await self.rag_service.retrieve_relevant_content(
                            query=chat_request.message,
                            file_paths=[],
                            top_k=5  # Increased for better context
                        )
                        
                        if relevant_docs:
                            context_parts = []
                            for i, doc in enumerate(relevant_docs):
                                doc_name = doc.get('source', f'Document_{i+1}')
                                page_num = doc.get('page', 1)
                                content = doc.get('content', '')[:400]  # Reduced for speed
                                
                                context_parts.append(f"[{i+1}] From '{doc_name}', Page {page_num}: {content}")
                                citations_list.append(f"[{i+1}] {doc_name}, Page {page_num}")
                            
                            rag_context = f"""
RELEVANT DOCUMENT SOURCES:
{chr(10).join(context_parts)}

IMPORTANT: When referencing information from these sources, include the citation number [1], [2], etc. in your response.
"""
                        else:
                            rag_context = "No relevant information found in uploaded documents."
                    else:
                        rag_context = "Document search service is currently initializing. Using general knowledge."
                        
                except Exception as e:
                    print(f"RAG retrieval failed: {e}")
                    rag_context = "Document search temporarily unavailable."
            
            # Create prompt with pharma focus
            if conversation_history:
                prompt = f"""You are a specialized pharmaceutical regulatory affairs assistant with expertise in CMC (Chemistry, Manufacturing, and Controls), FDA regulations, ICH guidelines, drug development, and pharmaceutical quality systems.

PHARMACEUTICAL EXPERTISE AREAS:
- CMC documentation and submissions
- FDA regulations (21 CFR, etc.)
- ICH guidelines (Q7, Q8, Q9, Q10, Q11, Q12, etc.)
- Pharmaceutical manufacturing and quality
- Regulatory submissions (IND, NDA, ANDA, etc.)
- GMP compliance and validation
- Analytical method development
- Stability studies
- Drug substance and drug product development

{rag_context}

Conversation history:
{chr(10).join(conversation_history)}

User: {chat_request.message}

RESPONSE GUIDELINES:
- For simple greetings (hi, hello, thanks): Give brief, friendly responses without boilerplate text
- For technical pharmaceutical questions: Provide detailed, expert-level guidance  
- For general questions: Answer helpfully and concisely
- Always maintain accuracy and cite relevant regulations or guidelines when applicable
- Use professional pharmaceutical terminology appropriately
- {"ONLY include citations [1], [2] when you actually reference specific information from the document sources. Do NOT add citations for general knowledge." if chat_request.use_rag else "Provide general pharmaceutical knowledge"}"""
            else:
                prompt = f"""You are a specialized pharmaceutical regulatory affairs assistant with expertise in CMC (Chemistry, Manufacturing, and Controls), FDA regulations, ICH guidelines, drug development, and pharmaceutical quality systems.

PHARMACEUTICAL EXPERTISE AREAS:
- CMC documentation and submissions
- FDA regulations (21 CFR, etc.)
- ICH guidelines (Q7, Q8, Q9, Q10, Q11, Q12, etc.)
- Pharmaceutical manufacturing and quality
- Regulatory submissions (IND, NDA, ANDA, etc.)
- GMP compliance and validation
- Analytical method development
- Stability studies
- Drug substance and drug product development

{rag_context}

User: {chat_request.message}

RESPONSE GUIDELINES:
- For simple greetings (hi, hello, thanks): Give brief, friendly responses without boilerplate text
- For technical pharmaceutical questions: Provide detailed, expert-level guidance  
- For general questions: Answer helpfully and concisely
- Always maintain accuracy and cite relevant regulations or guidelines when applicable
- Use professional pharmaceutical terminology appropriately
- {"ONLY include citations [1], [2] when you actually reference specific information from the document sources. Do NOT add citations for general knowledge." if chat_request.use_rag else "Provide general pharmaceutical knowledge"}"""
            
            # Use NVIDIA API directly for streaming
            try:
                invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.LLM_API_KEY}",
                    "Accept": "text/event-stream"
                }
                
                payload = {
                    "model": "meta/llama-4-scout-17b-16e-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 400,  # Reduced for faster responses
                    "temperature": 0.7,
                    "stream": True
                }
                
                # Stream the response with reduced timeout
                response = requests.post(invoke_url, headers=headers, json=payload, stream=True, timeout=12)
                
                if response.status_code != 200:
                    raise Exception(f"API request failed with status {response.status_code}: {response.text}")
                
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
                                
            except requests.exceptions.RequestException as e:
                print(f"NVIDIA API request failed: {e}")
                # Fallback to mock response for streaming
                fallback_response = f"I apologize, but I'm having trouble connecting to the AI service right now. Your question was: '{chat_request.message}'. Please try again later or contact support if this issue persists."
                
                # Stream the fallback response character by character
                for i, char in enumerate(fallback_response):
                    full_response += char
                    yield {
                        "type": "chunk",
                        "chunk": char,
                        "message_id": ai_message_id
                    }
                    # Small delay to simulate streaming
                    if i % 10 == 0:
                        await asyncio.sleep(0.05)
            
            # Add citations to response only if the response actually contains citation numbers
            if chat_request.use_rag and citations_list and any(f'[{i+1}]' in full_response for i in range(len(citations_list))):
                if not full_response.endswith('\n'):
                    full_response += '\n'
                full_response += '\n**References:**\n'
                for citation in citations_list:
                    full_response += f'{citation}\n'
            
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

    def _get_all_document_files(self, upload_dir: str) -> List[str]:
        """Get all document files from the persistent uploads directory"""
        document_files = []
        supported_extensions = ['.txt', '.pdf', '.doc', '.docx', '.md']
        
        try:
            if os.path.exists(upload_dir):
                # Walk through all subdirectories
                for root, _, files in os.walk(upload_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_extension = os.path.splitext(file)[1].lower()
                        if file_extension in supported_extensions:
                            document_files.append(file_path)
                            print(f"📄 Found document: {file_path}")
                
                if document_files:
                    print(f"✅ Loaded {len(document_files)} documents for RAG")
                else:
                    print("⚠️ No documents found in persistent uploads")
            else:
                print(f"⚠️ Upload directory not found: {upload_dir}")
                
        except Exception as e:
            print(f"❌ Error scanning documents: {e}")
            
        return document_files
    
    def _get_fast_local_response(self, user_message: str, include_citations: bool = True) -> Optional[str]:
        """Get fast local responses for common questions without LLM API calls"""
        user_message_lower = user_message.lower().strip()
        
        # Simple greetings - instant responses
        greetings = {
            "hi": "Hi! How can I help you with pharmaceutical or regulatory questions today?",
            "hello": "Hello! What can I assist you with regarding CMC or regulatory matters?",
            "hey": "Hey there! What pharmaceutical question can I help you with?",
            "good morning": "Good morning! How can I assist you with regulatory or pharmaceutical topics today?",
            "good afternoon": "Good afternoon! What can I help you with regarding CMC or regulatory matters?",
            "good evening": "Good evening! How can I assist you with pharmaceutical questions?",
            "thanks": "You're welcome! Feel free to ask any other pharmaceutical or regulatory questions.",
            "thank you": "You're welcome! I'm here to help with any CMC or regulatory topics you need.",
            "bye": "Goodbye! Feel free to return if you have more pharmaceutical questions.",
            "goodbye": "Goodbye! I'm here whenever you need help with regulatory or CMC topics."
        }
        
        for greeting, response in greetings.items():
            if user_message_lower == greeting or user_message_lower == greeting + "!":
                return response
        
        # Common pharmaceutical questions with instant answers (both RAG and non-RAG modes)
        quick_answers = {
            "what is cmc": """CMC stands for Chemistry, Manufacturing, and Controls. It's a critical section of pharmaceutical regulatory submissions that covers:

• **Drug Substance**: Chemical structure, synthesis, specifications
• **Drug Product**: Formulation, manufacturing process, specifications  
• **Analytical Methods**: Testing procedures and validation
• **Stability Studies**: Shelf-life and storage conditions
• **Quality Control**: Release and stability testing

CMC ensures pharmaceutical products meet quality, safety, and efficacy standards.""",

            "what is ich": """ICH stands for International Council for Harmonisation of Technical Requirements for Pharmaceuticals for Human Use. Key ICH guidelines include:

• **Q1A-Q1F**: Stability testing requirements
• **Q2(R1)**: Analytical method validation  
• **Q3A-Q3D**: Impurity guidelines
• **Q7**: Good Manufacturing Practice for APIs
• **Q8-Q12**: Pharmaceutical quality system
• **Q14**: Analytical procedure development

ICH harmonizes regulatory requirements across regions (US, EU, Japan).""",

            "what is gmp": """GMP stands for Good Manufacturing Practice. It's a quality system ensuring pharmaceutical products are:

• **Consistently produced** to quality standards
• **Controlled** through documented procedures
• **Monitored** with appropriate testing
• **Validated** for critical processes
• **Traceable** with proper record keeping

Key GMP areas include facilities, equipment, personnel, documentation, production, quality control, and distribution.""",

            "what is fda": """FDA stands for Food and Drug Administration. It's the US regulatory agency responsible for:

• **Drug Approval**: Reviewing and approving new medications
• **Safety Monitoring**: Post-market surveillance and adverse event reporting  
• **Manufacturing Oversight**: GMP inspections and compliance
• **Quality Standards**: Setting specifications and testing requirements
• **Labeling Requirements**: Prescribing information and warnings

The FDA ensures drugs are safe and effective before reaching patients.""",

            "validation": """Analytical method validation is the process of demonstrating that an analytical procedure is suitable for its intended use. Key validation parameters include:

• **Accuracy**: How close results are to the true value
• **Precision**: Repeatability and reproducibility of results
• **Specificity**: Ability to measure the analyte in presence of impurities
• **Linearity**: Proportional relationship between concentration and response
• **Range**: Concentration interval over which the method is validated
• **Detection/Quantitation Limits**: Lowest detectable/quantifiable amounts""",

            "analytical method": """Analytical methods are scientific procedures used to test pharmaceutical products. They include:

• **Chromatographic Methods**: HPLC, GC for separation and quantification
• **Spectroscopic Methods**: UV, IR, MS for identification and purity
• **Physical Tests**: Dissolution, hardness, disintegration
• **Chemical Tests**: pH, moisture content, residual solvents
• **Microbiological Tests**: Sterility, endotoxins, microbial limits

Methods must be validated to ensure accuracy, precision, and reliability.""",

            "stability": """Stability studies evaluate how drug products change over time under various conditions:

• **Accelerated Studies**: 40°C/75% RH for 6 months
• **Intermediate Studies**: 30°C/65% RH for 12 months  
• **Long-term Studies**: 25°C/60% RH for up to 36 months
• **Stress Testing**: Heat, light, pH to identify degradation pathways
• **Photostability**: ICH Q1B requirements for light exposure

Results determine shelf-life and storage conditions."""
        }
        
        for question, answer in quick_answers.items():
            if question in user_message_lower:
                return answer
        
        # For non-RAG mode, provide more quick answers
        if not include_citations:
            general_answers = {
                "what are you": "I'm a pharmaceutical regulatory assistant specializing in CMC, FDA regulations, and ICH guidelines. I can help with analytical methods, stability studies, regulatory submissions, and quality control topics.",
                "what can you do": "I can help with:\n• CMC documentation\n• Analytical method validation\n• Stability studies\n• FDA/ICH guidelines\n• Regulatory submissions\n• Quality control procedures\n• GMP compliance",
                "help": "I'm here to assist with pharmaceutical regulatory topics! You can ask me about:\n• Analytical methods and validation\n• CMC documentation\n• FDA and ICH guidelines\n• Stability studies\n• Regulatory submissions\n\nWhat specific topic would you like help with?"
            }
            
            for question, answer in general_answers.items():
                if question in user_message_lower:
                    return answer
        
        return None  # No fast response available, use LLM

    def _needs_document_search(self, user_message: str) -> bool:
        """Determine if a query needs document search or can be answered with general knowledge"""
        user_message_lower = user_message.lower().strip()
        
        # These phrases indicate the user wants to search uploaded documents
        document_search_indicators = [
            "in the document", "in the pdf", "in the file", "according to the document",
            "what does the document say", "from the document", "document shows",
            "in my document", "uploaded document", "file says",
            "where does it say", "show me where", "find in document",
            "search document", "document mentions", "pdf contains",
            "according to", "based on the document", "document states"
        ]
        
        # Data verification queries always need RAG
        if self._is_data_verification_query(user_message):
            return True
        
        # If user explicitly asks for document search
        if any(indicator in user_message_lower for indicator in document_search_indicators):
            return True
        
        # Very specific technical questions that might benefit from document examples
        specific_technical_patterns = [
            "specific protocol for", "detailed procedure for", "exact method for",
            "step by step", "specific requirements for", "detailed specification",
            "validation protocol", "testing procedure", "analytical procedure",
            "specific guideline", "exact requirement", "detailed method"
        ]
        
        if any(pattern in user_message_lower for pattern in specific_technical_patterns):
            return True
        
        # For general pharmaceutical questions, use fast responses or general LLM knowledge
        # Don't search documents for basic concepts like "what is ICH", "what is GMP"
        return False

    def _should_use_rag_for_query(self, user_message: str) -> bool:
        """Determine if a query should use RAG context or is just a simple greeting/social query"""
        user_message_lower = user_message.lower().strip()
        
        # Simple greetings and social interactions - no RAG needed
        simple_patterns = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "thanks", "thank you", "bye", "goodbye",
            "what can you do", "what are you", "who are you", "help me",
            "can you help", "what is your name", "nice to meet you"
        ]
        
        # If the message is very short and matches simple patterns, no RAG
        if len(user_message_lower) < 20 and any(pattern in user_message_lower for pattern in simple_patterns):
            return False
        
        # If message contains pharmaceutical/technical terms, use RAG
        technical_patterns = [
            "validation", "analytical", "method", "stability", "specification", "impurity",
            "chromatography", "assay", "potency", "dissolution", "content uniformity",
            "ich", "fda", "gmp", "cmc", "drug substance", "drug product", "api",
            "pharmaceutical", "regulatory", "submission", "guideline", "cfr",
            "hplc", "gc", "ms", "spectroscopy", "purity", "degradation",
            "shelf life", "storage", "temperature", "humidity", "packaging"
        ]
        
        if any(pattern in user_message_lower for pattern in technical_patterns):
            return True
        
        # For medium-length questions that aren't clearly social, use RAG
        if len(user_message_lower) > 30:
            return True
        
        # Default to no RAG for short, unclear queries
        return False

    def _is_data_verification_query(self, user_message: str) -> bool:
        """Detect if the user is asking for data verification/source information"""
        verification_patterns = [
            "where did you find",
            "what document",
            "which page",
            "source of",
            "where does it say",
            "verify",
            "citation for",
            "reference for",
            "document shows",
            "page number",
            "where is this from",
            "show me the source",
            "prove this",
            "evidence for"
        ]
        
        user_message_lower = user_message.lower()
        return any(pattern in user_message_lower for pattern in verification_patterns)
    
    async def _handle_data_verification_query(
        self,
        user_message: str,
        session: ChatSession,
        context: Optional[Dict] = None
    ) -> str:
        """Handle data verification queries by searching for specific claims in documents"""
        try:
            print(f"🔍 Processing data verification query: {user_message}")
            
            # Initialize RAG service if needed
            if not self.rag_service:
                try:
                    # Use session-specific documents or fallback to simple test document
                    session_dir = f"persistent_uploads/session_1752682398021_yzbskt9de"
                    if os.path.exists(session_dir):
                        document_files = self._get_all_document_files(session_dir)
                    else:
                        # Fallback to the test document
                        test_doc = "persistent_uploads/test_document.txt"
                        document_files = [test_doc] if os.path.exists(test_doc) else []
                    if not document_files:
                        return "I don't have access to any uploaded documents to verify data from. Please upload some documents first, then I can help you verify specific claims and their sources."
                    
                    print(f"📚 Initializing RAG with {len(document_files)} documents for verification")
                    self.rag_service = RAGService(file_paths=document_files)
                except Exception as e:
                    print(f"❌ Failed to initialize RAG service: {e}")
                    return "I'm having trouble accessing the document repository. Please try again in a moment."
            
            # Extract the claim/data point from the query
            claim_to_verify = self._extract_claim_from_query(user_message)
            print(f"🎯 Extracted claim to verify: {claim_to_verify}")
            
            # Search for the claim in documents
            retrieved_docs = await self.rag_service.retrieve_relevant_content(
                query=claim_to_verify,
                file_paths=[],  # Use all available documents
                top_k=10,  # Get more results for better verification
                mode="local"
            )
            
            if not retrieved_docs:
                return f"I couldn't find any information about '{claim_to_verify}' in the uploaded documents. The claim might not be present in the available sources, or it might be phrased differently."
            
            # Generate verification response with sources
            return await self._generate_verification_response(
                user_message,
                claim_to_verify,
                retrieved_docs
            )
            
        except Exception as e:
            print(f"❌ Error in data verification: {e}")
            return f"I encountered an error while trying to verify the information. Please try rephrasing your question or try again later. Error: {str(e)}"
    
    def _extract_claim_from_query(self, user_message: str) -> str:
        """Extract the specific claim/data point that needs verification"""
        # Simple extraction - look for quoted text, percentages, numbers, or key phrases
        import re
        
        # Look for quoted text first
        quoted_match = re.search(r'"([^"]+)"', user_message)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for single quotes
        quoted_match = re.search(r"'([^']+)'", user_message)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for percentage patterns
        percentage_match = re.search(r'(\d+(?:\.\d+)?%[^.?!]*)', user_message)
        if percentage_match:
            return percentage_match.group(1)
        
        # Look for numeric claims
        numeric_match = re.search(r'(\d+(?:\.\d+)?[^.?!]*(?:increase|decrease|improvement|reduction|change|patients|subjects|participants)[^.?!]*)', user_message, re.IGNORECASE)
        if numeric_match:
            return numeric_match.group(1)
        
        # Remove common question words and extract key phrases
        clean_message = re.sub(r'\b(?:where|what|which|how|when|did|you|find|document|page|shows?|says?|is|this|from|the|a|an|in|on|at|to|for)\b', '', user_message, flags=re.IGNORECASE)
        clean_message = re.sub(r'\s+', ' ', clean_message).strip()
        
        return clean_message or user_message
    
    async def _generate_verification_response(
        self,
        original_query: str,
        claim_to_verify: str,
        retrieved_docs: List[Dict]
    ) -> str:
        """Generate a response that shows where specific data was found"""
        try:
            # Ensure LLM is initialized
            if not self._ensure_llm_initialized():
                return "I'm having trouble initializing my language model to verify the data. Please try again."
            
            # Prepare context from retrieved documents
            context_parts = []
            for i, doc in enumerate(retrieved_docs[:5]):  # Limit to top 5 for context
                source = doc.get('source', 'Unknown Document')
                page = doc.get('page', 'Unknown Page')
                content = doc.get('content', '')[:300] + '...' if len(doc.get('content', '')) > 300 else doc.get('content', '')
                
                context_parts.append(f"""
[Source {i+1}: {source}, Page {page}]
{content}
""")
            
            context_text = "\n".join(context_parts)
            
            # Create specialized verification prompt
            verification_prompt = f"""You are a data verification specialist. The user is asking about the source of specific information: "{original_query}"

The claim they want to verify is: "{claim_to_verify}"

Here are the relevant document excerpts that were found:

{context_text}

TASK: Analyze the provided documents to verify the claim and provide precise source information.

RESPONSE FORMAT:
1. **Verification Status**: [FOUND/NOT FOUND/PARTIALLY FOUND]
2. **Exact Quote**: [The exact text from the document that contains the claim]
3. **Source Details**: 
   - Document: [Document name]
   - Page: [Page number]
   - Context: [Brief description of where in the document this appears]
4. **Accuracy Assessment**: [How closely the found information matches the user's query]

GUIDELINES:
- Be precise about what was found vs what was asked
- If the exact claim isn't found, mention the closest matching information
- Always provide document name and page number when information is found
- If multiple sources contain similar information, list all of them
- If the claim is not supported by the documents, clearly state this

Respond in a clear, professional manner that helps the user verify their data sources."""

            # Generate verification response
            response = await asyncio.wait_for(
                asyncio.to_thread(self.llm.invoke, verification_prompt),
                timeout=15.0
            )
            
            if hasattr(response, 'content'):
                verification_result = response.content
            else:
                verification_result = str(response)
            
            # Add summary of all sources found
            source_summary = "\n\n**📚 All Sources Found:**\n"
            unique_sources = {}
            for doc in retrieved_docs:
                source_key = f"{doc.get('source', 'Unknown')}|{doc.get('page', 'N/A')}"
                if source_key not in unique_sources:
                    unique_sources[source_key] = {
                        'source': doc.get('source', 'Unknown Document'),
                        'page': doc.get('page', 'N/A'),
                        'preview': doc.get('content', '')[:100] + '...' if len(doc.get('content', '')) > 100 else doc.get('content', '')
                    }
            
            for i, (_, info) in enumerate(unique_sources.items(), 1):
                source_summary += f"{i}. **{info['source']}** (Page {info['page']}): {info['preview']}\n"
            
            return verification_result + source_summary
            
        except Exception as e:
            print(f"❌ Error generating verification response: {e}")
            return f"I found {len(retrieved_docs)} potentially relevant sources but encountered an error while analyzing them. The sources include: " + ", ".join([f"{doc.get('source', 'Unknown')} (Page {doc.get('page', 'N/A')})" for doc in retrieved_docs[:3]])
