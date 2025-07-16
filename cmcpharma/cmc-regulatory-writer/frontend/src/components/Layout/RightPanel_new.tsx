import React, { useState } from 'react';
import { Plus, Square, MessageCircle, Play, Download } from 'lucide-react';
import { ChatBox } from '../Chat/ChatBox';
import { ExportManager } from '../Export/ExportManager';
import type { StoredDocument } from '../../services/storage';

interface RightPanelProps {
  onNavigateToTemplates?: () => void;
  currentDocument?: StoredDocument | null;
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
        setShowExport(false);
      }}>
        <div className="action-icon">
          <MessageCircle size={20} />
        </div>
        <span className="action-text">AI Assistant</span>
      </button>
      
      <button className="action-btn" onClick={() => {
        setShowExport(!showExport);
        setShowChat(false);
      }}>
        <div className="action-icon">
          <Download size={20} />
        </div>
        <span className="action-text">Export Document</span>
      </button>
      
      <button className="action-btn" onClick={() => onNavigateToTemplates?.()}>
        <div className="action-icon">
          <Play size={20} />
        </div>
        <span className="action-text">Generate from template</span>
      </button>
      
      {!showChat && !showExport && (
        <div className="right-panel-content">
          <h3>Quick Actions</h3>
          <ul>
            <li>Review document sections</li>
            <li>Validate compliance</li>
            <li>Check cross-references</li>
            <li>Generate summary</li>
          </ul>
        </div>
      )}
      
      {showChat && <ChatBox />}
      {showExport && <ExportManager document={currentDocument || null} onExport={handleExport} />}
    </aside>
  );
};
