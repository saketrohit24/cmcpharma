import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, FileText } from 'lucide-react';
import { chatService, type LocalChatMessage } from '../../services/chatService';

export const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<LocalChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  // const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [streamingText, setStreamingText] = useState('');
  const [useRAG, setUseRAG] = useState(true); // RAG toggle state
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load existing messages if any
    const existingMessages = chatService.getSessionMessages();
    if (existingMessages.length > 0) {
      setMessages(existingMessages);
    }
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const messageText = inputValue.trim();
    setInputValue('');
    setIsLoading(true);
    setStreamingText('');

    // Add user message immediately
    const userMessage: LocalChatMessage = {
      id: `user-${Date.now()}`,
      text: messageText,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      // TEMPORARY: Use non-streaming to debug
      console.log('Sending message:', messageText, 'useRAG:', useRAG);
      const assistantMessage = await chatService.sendMessage(messageText, { useRAG });
      console.log('Received response:', assistantMessage);
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
      
      /* Use streaming for better experience
      await chatService.sendMessageStream(
        messageText,
        // onChunk - called for each chunk received
        (chunk: string, messageId: string) => {
          setStreamingMessageId(messageId);
          setStreamingText(prev => prev + chunk);
        },
        // onComplete - called when streaming is finished
        (assistantMessage: LocalChatMessage) => {
          setMessages(prev => [...prev, assistantMessage]);
          setStreamingText('');
          setStreamingMessageId(null);
          setIsLoading(false);
        },
        // onError - called if an error occurs
        (error: string) => {
          console.error('Streaming error:', error);
          const errorMessage: LocalChatMessage = {
            id: `error-${Date.now()}`,
            text: 'Sorry, I encountered an error. Please try again.',
            sender: 'assistant',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, errorMessage]);
          setStreamingText('');
          setStreamingMessageId(null);
          setIsLoading(false);
        },
        // options - include RAG setting
        { useRAG }
      );
      */
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Try fallback to non-streaming mode
      try {
        console.log('Attempting fallback to non-streaming mode...');
        const assistantMessage = await chatService.sendMessage(messageText, { useRAG });
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
        const errorMessage: LocalChatMessage = {
          id: `error-${Date.now()}`,
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}. Please try again.`,
          sender: 'assistant',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
        setIsLoading(false);
      }
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-container active">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-placeholder">
            <Bot size={32} className="mb-2 text-blue-500" />
            <p className="text-gray-600 text-center">
              Hello! I'm your CMC regulatory writing assistant. 
            </p>
            <p className="text-sm text-gray-500 text-center mt-2">
              {useRAG 
                ? 'Ask me about your uploaded documents, specifications, protocols, or any pharmaceutical questions!'
                : 'Ask me general pharmaceutical questions, regulatory guidance, or industry knowledge!'
              }
            </p>
          </div>
        ) : (
          messages.map(message => (
            <div
              key={message.id}
              className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'}`}
            >
              <div className="message-header">
                {message.sender === 'user' ? (
                  <User size={16} className="message-icon" />
                ) : (
                  <Bot size={16} className="message-icon" />
                )}
                <span className="message-time">{formatTime(message.timestamp)}</span>
              </div>
              <div className="message-content">
                {message.text.split('\n').map((line, index) => (
                  <p key={index} className={line.startsWith('**') ? 'font-semibold' : ''}>
                    {line.replace(/\*\*(.*?)\*\*/g, '$1')}
                  </p>
                ))}
              </div>
            </div>
          ))
        )}
        
        {/* Show streaming message */}
        {isLoading && streamingText && (
          <div className="message ai-message">
            <div className="message-header">
              <Bot size={16} className="message-icon" />
              <span className="message-time">Typing...</span>
            </div>
            <div className="message-content">
              {streamingText.split('\n').map((line, index) => (
                <p key={index} className={line.startsWith('**') ? 'font-semibold' : ''}>
                  {line.replace(/\*\*(.*?)\*\*/g, '$1')}
                  {index === streamingText.split('\n').length - 1 && (
                    <span className="streaming-cursor">|</span>
                  )}
                </p>
              ))}
            </div>
          </div>
        )}
        
        {/* Show typing indicator when waiting for first chunk */}
        {isLoading && !streamingText && (
          <div className="message ai-message">
            <div className="message-header">
              <Bot size={16} className="message-icon" />
              <span className="message-time">Thinking...</span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        {/* Show streaming indicator if active */}
        {false && streamingText && (
          <div className="message-streaming" style={{
            padding: '12px',
            marginBottom: '12px',
            backgroundColor: '#f0f0f0',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#666'
          }}>
            <Bot size={16} className="inline mr-2" />
            {streamingText}...
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* RAG Toggle */}
      <div className="rag-toggle-container" style={{
        padding: '8px 16px',
        borderBottom: '1px solid #e5e7eb',
        backgroundColor: '#f9fafb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '14px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText size={16} className={useRAG ? 'text-blue-600' : 'text-gray-400'} />
          <span className={useRAG ? 'text-blue-600 font-medium' : 'text-gray-600'}>
            Document Knowledge
          </span>
        </div>
        <label className="toggle-switch" style={{
          position: 'relative',
          display: 'inline-block',
          width: '44px',
          height: '24px'
        }}>
          <input
            type="checkbox"
            checked={useRAG}
            onChange={(e) => setUseRAG(e.target.checked)}
            style={{
              opacity: 0,
              width: 0,
              height: 0
            }}
          />
          <span 
            className="toggle-slider"
            style={{
              position: 'absolute',
              cursor: 'pointer',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: useRAG ? '#3b82f6' : '#cbd5e1',
              borderRadius: '24px',
              transition: '.4s',
              display: 'flex',
              alignItems: 'center',
              padding: '2px'
            }}
          >
            <div
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: 'white',
                transition: '.4s',
                transform: useRAG ? 'translateX(20px)' : 'translateX(0px)',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}
            />
          </span>
        </label>
      </div>
      <div style={{
        padding: '4px 16px',
        fontSize: '12px',
        color: '#6b7280',
        backgroundColor: '#f9fafb',
        borderBottom: '1px solid #e5e7eb'
      }}>
        {useRAG 
          ? '🔍 Using uploaded documents to enhance responses' 
          : '💬 General chat mode (no document context)'
        }
      </div>
      
      <form className="chat-form" onSubmit={handleSend}>
        <input
          type="text"
          className="chat-input"
          placeholder={useRAG 
            ? "Ask about your documents, specifications, protocols..." 
            : "Ask general pharmaceutical questions..."
          }
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="chat-send"
          disabled={isLoading || !inputValue.trim()}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
};
