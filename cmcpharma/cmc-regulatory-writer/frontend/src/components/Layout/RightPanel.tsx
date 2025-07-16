import React, { useState } from 'react';
import { Plus, Square, MessageCircle, Play, Download } from 'lucide-react';
import { ChatBox } from '../Chat/ChatBox';
import { ExportManager } from '../Export/ExportManager';
import type { StoredDocument } from '../../services/storage';
import type { Template } from '../Templates/TemplateManagerPage';

interface RightPanelProps {
  onNavigateToTemplates?: () => void;
  onNavigateToHistory?: () => void;
  onNavigateToFiles?: () => void;
  onGenerateFromTemplate?: (template: Template) => Promise<void>;
  currentDocument?: StoredDocument | null;
}

export const RightPanel: React.FC<RightPanelProps> = ({ 
  onNavigateToTemplates, 
  onNavigateToHistory, 
  onNavigateToFiles, 
  onGenerateFromTemplate,
  currentDocument 
}) => {
  const [activeTab, setActiveTab] = useState<'actions' | 'chat' | 'export'>('actions');
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  
  // Quick template options for right panel
  const quickTemplates: Template[] = [
    {
      id: '1',
      name: 'Module 3.2.S Drug Substance',
      description: 'Complete template for drug substance documentation',
      type: 'manual',
      createdAt: new Date(),
      lastModified: new Date(),
      status: 'ready',
      toc: [
        { id: '1', title: '3.2.S.1 General Information', level: 1 },
        { id: '2', title: '3.2.S.2 Manufacture', level: 1 },
        { id: '3', title: '3.2.S.3 Characterisation', level: 1 },
        { id: '4', title: '3.2.S.4 Control of Drug Substance', level: 1 },
      ]
    },
    {
      id: '2',
      name: 'Module 3.2.P Drug Product',
      description: 'Template for drug product documentation',
      type: 'manual',
      createdAt: new Date(),
      lastModified: new Date(),
      status: 'ready',
      toc: [
        { id: '1', title: '3.2.P.1 Description and Composition', level: 1 },
        { id: '2', title: '3.2.P.2 Pharmaceutical Development', level: 1 },
        { id: '3', title: '3.2.P.3 Manufacture', level: 1 },
        { id: '4', title: '3.2.P.4 Control of Excipients', level: 1 },
      ]
    }
  ];

  const handleQuickGenerate = async (template: Template) => {
    setShowTemplateSelector(false);
    if (onGenerateFromTemplate) {
      await onGenerateFromTemplate(template);
    }
  };
  
  const handleExport = async (format: string) => {
    console.log(`Exporting document as ${format}`);
    // Simulate export process
    return new Promise(resolve => setTimeout(resolve, 1000));
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatBox />;
      case 'export':
        return <ExportManager document={currentDocument || null} onExport={handleExport} />;
      case 'actions':
      default:
        return (
          <div className="right-panel-actions">
            {!showTemplateSelector ? (
              <>
                <button 
                  className="action-btn" 
                  onClick={() => setShowTemplateSelector(true)}
                >
                  <div className="action-icon">
                    <Play size={20} />
                  </div>
                  <span className="action-text">Generate from template</span>
                </button>
                
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

                {/* Quick Navigation Section */}
                <div className="quick-nav-section">
                  <h3>Quick Navigation</h3>
                  <div className="quick-nav-buttons">
                    <button 
                      className="quick-nav-btn"
                      onClick={() => onNavigateToHistory?.()}
                    >
                      History
                    </button>
                    <button 
                      className="quick-nav-btn"
                      onClick={() => onNavigateToFiles?.()}
                    >
                      Manage Files
                    </button>
                  </div>
                </div>
                
                <div className="quick-actions-info">
                  <h3>Quick Actions</h3>
                  <ul>
                    <li>Review document sections</li>
                    <li>Validate compliance</li>
                    <li>Check cross-references</li>
                    <li>Generate summary</li>
                  </ul>
                </div>

                <button 
                  className="quick-nav-btn"
                  onClick={() => onNavigateToTemplates?.()}
                  style={{ marginTop: '12px', width: '100%' }}
                >
                  Browse All Templates
                </button>
              </>
            ) : (
              <div className="template-selector">
                <div className="template-selector-header">
                  <h3>Quick Templates</h3>
                  <button 
                    className="close-btn"
                    onClick={() => setShowTemplateSelector(false)}
                  >
                    ✕
                  </button>
                </div>
                
                <div className="template-list">
                  {quickTemplates.map(template => (
                    <div key={template.id} className="template-card">
                      <h4>{template.name}</h4>
                      <p>{template.description}</p>
                      <button 
                        className="template-generate-btn"
                        onClick={() => handleQuickGenerate(template)}
                      >
                        Generate
                      </button>
                    </div>
                  ))}
                </div>
                
                <button 
                  className="quick-nav-btn"
                  onClick={() => {
                    setShowTemplateSelector(false);
                    onNavigateToTemplates?.();
                  }}
                  style={{ marginTop: '12px', width: '100%' }}
                >
                  Browse All Templates
                </button>
              </div>
            )}
          </div>
        );
    }
  };

  return (
    <aside className="right-panel">
      {/* Tab Header */}
      <div className="right-panel-header">
        <button 
          className={`tab-btn ${activeTab === 'actions' ? 'active' : ''}`}
          onClick={() => setActiveTab('actions')}
          title="Quick Actions"
        >
          <Plus size={16} />
        </button>
        
        <button 
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
          title="AI Assistant"
        >
          <MessageCircle size={16} />
        </button>
        
        <button 
          className={`tab-btn ${activeTab === 'export' ? 'active' : ''}`}
          onClick={() => setActiveTab('export')}
          title="Export Document"
        >
          <Download size={16} />
        </button>
      </div>
      
      {/* Content Area */}
      <div className="right-panel-content">
        {renderContent()}
      </div>
    </aside>
  );
};
