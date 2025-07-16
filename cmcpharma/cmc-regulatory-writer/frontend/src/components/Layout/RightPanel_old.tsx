import React, { useState } from 'react';
import { Plus, Square, MessageCircle, Play, Download } from 'lucide-react';
import { ChatBox } from '../Chat/ChatBox';
import { ExportManager } from '../Export/ExportManager';

interface RightPanelProps {
  onNavigateToTemplates?: () => void;
  currentDocument?: any;
}

export const RightPanel: React.FC<RightPanelProps> = ({ onNavigateToTemplates, currentDocument }) => {
  const [showChat, setShowChat] = useState(false);
  const [showExport, setShowExport] = useState(false);
  
  const handleExport = async (format: string) => {
    console.log(`Exporting document as ${format}`);
    // Simulate export process
    return new Promise(resolve => setTimeout(resolve, 1000));
  };

  return (
    <aside className="right-panel">
      <button className="action-btn">
        <div className="action-icon">
          <Plus size={20} />
        </div>
        <span className="action-text">Suggest edits</span>
      </button>
      
      <button className="action-btn">
        <div className="action-icon">
          <Square size={20} />
        </div>
        <span className="action-text">Trace to data source</span>
      </button>
      
      <button className="action-btn" onClick={() => {
        setShowChat(!showChat);
        setShowFiles(false);
      }}>
        <div className="action-icon">
          <MessageCircle size={20} />
        </div>
        <span className="action-text">AI Assistant</span>
      </button>
      
      <button className="action-btn" onClick={() => {
        setShowFiles(!showFiles);
        setShowChat(false);
      }}>
        <div className="action-icon">
          <Upload size={20} />
        </div>
        <span className="action-text">File Manager</span>
      </button>
      
      {!showChat && !showFiles && (
        <div className="info-box">
          <p className="info-text">
            Hi! You can use this space to generate regulatory content, create tables, or get guidance on CMC documentation.
          </p>
        </div>
      )}
      
      {showChat && <ChatBox />}
      
      {showFiles && <FileManager onFilesChange={handleFilesChange} />}
      
      <div className="divider"></div>
      
      <button 
        className="template-btn"
        onClick={() => onNavigateToTemplates?.()}
      >
        <span className="template-text">Generate from template</span>
        <div className="template-icon">
          <Play size={16} />
        </div>
      </button>
    </aside>
  );
};
