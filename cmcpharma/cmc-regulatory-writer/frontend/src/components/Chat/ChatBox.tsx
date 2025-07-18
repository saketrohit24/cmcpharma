import React, { useState, useEffect, useRef } from 'react';
import { Bot, User, ArrowRight } from 'lucide-react';
import { chatService, type LocalChatMessage } from '../../services/chatService';

export const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<LocalChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
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
      await chatService.sendMessageStream(
        messageText,
        // onChunk - called for each chunk received
        (chunk: string) => {
          setStreamingText(prev => prev + chunk);
        },
        // onComplete - called when streaming is finished
        (assistantMessage: LocalChatMessage) => {
          setMessages(prev => [...prev, assistantMessage]);
          setStreamingText('');
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
          setIsLoading(false);
        },
        // Options with RAG setting
        { useRAG }
      );
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: LocalChatMessage = {
        id: `error-${Date.now()}`,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
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
              Hello! I'm your RAG-enabled CMC regulatory writing assistant. 
            </p>
            <p className="text-sm text-gray-500 text-center mt-2">
              Ask me about specifications, protocols, stability studies, or any pharmaceutical questions!
              I can answer from your uploaded documents and provide citations.
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
                {/* Display citations if present */}
                {message.citations && message.citations.length > 0 && (
                  <div className="citations-container">
                    <div className="citations-header">
                      <span className="citations-label">Sources:</span>
                    </div>
                    <div className="citations-list">
                      {message.citations.map((citation, index) => (
                        <div key={index} className="citation-item">
                          <span className="citation-number">[{index + 1}]</span>
                          <span className="citation-text">{citation}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
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
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* RAG Toggle Control */}
      <div className="rag-toggle-container">
        <label className="rag-toggle-label">
          <input
            type="checkbox"
            className="rag-toggle-checkbox"
            checked={useRAG}
            onChange={(e) => setUseRAG(e.target.checked)}
          />
          <span className="rag-toggle-slider"></span>
          <span className="rag-toggle-text">
            {useRAG ? '📚 Document search enabled' : '💬 General chat mode'}
          </span>
        </label>
      </div>
      
      <form className="chat-form" onSubmit={handleSend}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about specifications, protocols, stability..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="chat-send"
          disabled={isLoading || !inputValue.trim()}
        >
          <ArrowRight size={16} />
        </button>
      </form>
    </div>
  );
};
