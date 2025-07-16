import React, { useState } from 'react';
import { Edit3, Link2, MessageCircle, Send, Play } from 'lucide-react';
import toast from 'react-hot-toast';
import { cn } from '../utils/cn';

interface RightPanelProps {
  chatVisible: boolean;
  toggleChat: () => void;
}

const RightPanel: React.FC<RightPanelProps> = ({ chatVisible, toggleChat }) => {
  const [chatMessage, setChatMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatMessage.trim()) {
      toast.success('Message sent to AI Assistant!');
      console.log('Chat message:', chatMessage);
      setChatMessage('');
    }
  };

  const handleSuggestEdits = () => {
    toast.loading('Analyzing document for suggestions...', { duration: 2000 });
  };

  const handleTraceToSource = () => {
    toast.success('Data source located: Lab Report LR-2024-001');
  };

  return (
    <aside className="right-panel">
      <button className="action-btn" onClick={handleSuggestEdits}>
        <div className="action-icon">
          <Edit3 size={16} />
        </div>
        <span className="action-text">Suggest edits</span>
      </button>
      
      <button className="action-btn" onClick={handleTraceToSource}>
        <div className="action-icon">
          <Link2 size={16} />
        </div>
        <span className="action-text">Trace to data source</span>
      </button>
      
      <button className="action-btn" onClick={toggleChat}>
        <div className="action-icon">
          <MessageCircle size={16} />
        </div>
        <span className="action-text">AI Assistant</span>
      </button>
      
      <div className="info-box">
        <p className="info-text">
          Hi! You can use this space to generate regulatory content, create tables, or get guidance on CMC documentation.
        </p>
      </div>
      
      <div className={`chat-container ${chatVisible ? 'active' : ''}`}>
        <div className="chat-messages">
          <p className="chat-placeholder">Ask me to generate specifications, protocols, or any CMC content...</p>
        </div>
        <form className="chat-form" onSubmit={handleSubmit}>
          <input 
            type="text" 
            className="chat-input" 
            placeholder="Type your message..."
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
          />
          <button type="submit" className={cn("chat-send", "flex items-center justify-center")}>
            <Send size={16} />
          </button>
        </form>
      </div>
      
      <div className="divider"></div>
      
      <button className="template-btn">
        <span className="template-text">Generate from template</span>
        <div className="template-icon">
          <Play size={14} />
        </div>
      </button>
    </aside>
  );
};

export default RightPanel;
