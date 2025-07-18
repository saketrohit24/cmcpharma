import React, { useState } from 'react';
import { Plus, Square, MessageCircle, Play, Download } from 'lucide-react';
import { ChatBox } from '../Chat/ChatBox';
import { ExportManager } from '../Export/ExportManager';
import { SuggestEditModal } from '../SuggestEdit/SuggestEditModal';
import type { StoredDocument } from '../../services/storage';
import type { Template } from '../Templates/TemplateManagerPage';

interface Section {
  id: string;
  title: string;
  content: string;
  type: 'text' | 'table';
}

interface Citation {
  id: number;
  text: string;
  source: string;
  page: number;
  sourceFileId?: string;
}

interface RightPanelProps {
  onNavigateToTemplates?: () => void;
  onNavigateToHistory?: () => void;
  onNavigateToFiles?: () => void;
  onGenerateFromTemplate?: (template: Template) => Promise<void>;
  currentDocument?: StoredDocument | null;
  sections?: Section[];
  citations?: Citation[];
  activeTabId?: string;
  editedSections?: {[key: string]: string};
  onEditSection?: (sectionId: string, editedContent: string) => void;
}

export const RightPanel: React.FC<RightPanelProps> = ({ 
  onNavigateToTemplates, 
  onNavigateToHistory, 
  onNavigateToFiles, 
  onGenerateFromTemplate,
  currentDocument,
  sections = [],
  citations = [],
  activeTabId,
  editedSections = {},
  onEditSection
}) => {
  console.log('🔄 RightPanel: Component initialized with props:', {
    sectionsLength: sections.length,
    activeTabId,
    editedSections: Object.keys(editedSections),
    hasOnEditSection: !!onEditSection
  });
  
  // Log all sections for debugging
  console.log('📋 RightPanel: All sections:', sections.map(s => ({ id: s.id, title: s.title })));
  
  const [activeTab, setActiveTab] = useState<'actions' | 'chat' | 'export'>('actions');
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  
  // Suggest Edit Modal states
  const [showSuggestEditModal, setShowSuggestEditModal] = useState(false);
  const [suggestEditContent, setSuggestEditContent] = useState('');
  const [suggestEditContentType, setSuggestEditContentType] = useState<'selected' | 'section'>('section');
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [lastSelection, setLastSelection] = useState<string>('');

  // Track text selection
  React.useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection();
      const selectionText = selection ? selection.toString().trim() : '';
      if (selectionText.length > 0) {
        setLastSelection(selectionText);
        console.log('🔄 RightPanel: Selection saved:', selectionText);
        console.log('🔄 RightPanel: Selection range:', selection?.getRangeAt(0));
      }
    };

    document.addEventListener('selectionchange', handleSelectionChange);
    
    // Also add mouseup event for better selection detection
    const handleMouseUp = () => {
      setTimeout(() => {
        const selection = window.getSelection();
        const selectionText = selection ? selection.toString().trim() : '';
        if (selectionText.length > 0) {
          setLastSelection(selectionText);
          console.log('🔄 RightPanel: Selection saved on mouseup:', selectionText);
        }
      }, 10);
    };

    document.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);
  
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

  // Find the active section based on activeTabId
  const getActiveSection = () => {
    console.log('🔄 getActiveSection called:', { activeTabId, sectionsLength: sections.length });
    
    if (!activeTabId || !sections.length) {
      console.log('❌ No activeTabId or sections');
      return null;
    }
    
    const foundSection = sections.find(section => {
      // Direct ID match
      if (section.id === activeTabId) return true;
      // Direct title match
      if (section.title === activeTabId) return true;
      // Title contains activeTabId (case insensitive)
      if (section.title.toLowerCase().includes(activeTabId.toLowerCase())) return true;
      // ActiveTabId contains section title
      if (activeTabId.toLowerCase().includes(section.title.toLowerCase())) return true;
      return false;
    }) || sections[0]; // Fallback to first section
    
    console.log('🔄 Found section:', foundSection);
    return foundSection;
  };

  // Handle suggest edit button click
  const handleSuggestEditClick = () => {
    console.log('🔄 RightPanel: handleSuggestEditClick called');
    console.log('🔄 RightPanel: activeTabId:', activeTabId);
    console.log('🔄 RightPanel: sections:', sections);
    console.log('🔄 RightPanel: editedSections:', editedSections);
    
    // Immediately capture selection before it can be cleared
    const selection = window.getSelection();
    const immediateSelectionText = selection ? selection.toString().trim() : '';
    console.log('🔄 RightPanel: Immediate selection text:', immediateSelectionText);
    
    // If no sections, show an error
    if (!sections || sections.length === 0) {
      console.error('❌ No sections available');
      return;
    }
    
    // Try to get the active section, fallback to first section
    let activeSection = getActiveSection();
    if (!activeSection) {
      console.log('⚠️ No active section found, using first section');
      activeSection = sections[0];
    }
    
    console.log('🔄 RightPanel: activeSection:', activeSection);
    
    if (!activeSection) {
      console.error('❌ No active section found');
      return;
    }
    
    // Get the current content (edited or original)
    const currentContent = editedSections[activeSection.id] || activeSection.content;
    console.log('🔄 RightPanel: currentContent:', currentContent);
    
    // Check for text selection - prioritize immediate selection, then saved selection
    const selectionText = immediateSelectionText || lastSelection;
    const hasSelection = selectionText.length > 0;
    
    console.log('🔄 RightPanel: Immediate selection text:', immediateSelectionText);
    console.log('🔄 RightPanel: Last saved selection:', lastSelection);
    console.log('🔄 RightPanel: Final selection text:', selectionText);
    console.log('🔄 RightPanel: Has selection:', hasSelection);
    
    if (hasSelection) {
      // User has selected text - verify it exists in current content
      if (currentContent.includes(selectionText)) {
        setSuggestEditContent(selectionText);
        setSuggestEditContentType('selected');
        console.log('🔄 RightPanel: Set content type to SELECTED');
        console.log('🔄 RightPanel: Selected content:', selectionText);
        // Clear the last selection since we're using it
        setLastSelection('');
      } else {
        // Selection doesn't exist in current content, fall back to section edit
        console.log('⚠️ Selected text not found in current content, falling back to section edit');
        console.log('⚠️ Looking for:', selectionText);
        console.log('⚠️ In content:', currentContent);
        setSuggestEditContent(currentContent);
        setSuggestEditContentType('section');
        setLastSelection('');
      }
    } else {
      // No selection - edit entire section with current content
      setSuggestEditContent(currentContent);
      setSuggestEditContentType('section');
      console.log('🔄 RightPanel: Set content type to SECTION');
    }
    setShowSuggestEditModal(true);
    console.log('🔄 RightPanel: Modal should be open now');
  };

  // Handle applying suggested edits
  const handleApplySuggestedEdit = (editedContent: string) => {
    const activeSection = getActiveSection();
    
    if (!activeSection) {
      console.error('❌ No active section found');
      return;
    }

    console.log('🔄 RightPanel: handleApplySuggestedEdit called');
    console.log('🔄 RightPanel: suggestEditContentType:', suggestEditContentType);
    console.log('🔄 RightPanel: editedContent:', editedContent);
    
    let finalContent = editedContent;
    
    if (suggestEditContentType === 'selected') {
      // Replace selected text within the section
      const currentContent = editedSections[activeSection.id] || activeSection.content;
      const originalSelectedText = suggestEditContent;
      
      console.log('🔄 RightPanel: Replacing selected text');
      console.log('🔄 RightPanel: Current content:', currentContent);
      console.log('🔄 RightPanel: Original selected text:', originalSelectedText);
      
      // Use a more robust replacement method
      if (currentContent.includes(originalSelectedText)) {
        finalContent = currentContent.replace(originalSelectedText, editedContent);
        console.log('🔄 RightPanel: Final content after replacement:', finalContent);
      } else {
        // If exact match not found, fall back to section edit
        console.log('⚠️ RightPanel: Selected text not found, using section edit instead');
        finalContent = editedContent;
      }
    }
    
    // Use the callback to update the section content
    if (onEditSection) {
      console.log('🔄 RightPanel: Calling onEditSection with:', activeSection.id, finalContent);
      onEditSection(activeSection.id, finalContent);
    } else {
      console.error('❌ onEditSection callback not available');
    }
    
    setShowSuggestEditModal(false);
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
                
                <button 
                  className="action-btn"
                  onClick={handleSuggestEditClick}
                  onMouseDown={(e) => {
                    // Prevent the mousedown from clearing the selection
                    e.preventDefault();
                  }}
                >
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

      {/* Suggest Edit Modal */}
      {showSuggestEditModal && (
        <SuggestEditModal 
          isOpen={showSuggestEditModal} 
          onClose={() => setShowSuggestEditModal(false)} 
          content={suggestEditContent}
          contentType={suggestEditContentType}
          onApply={handleApplySuggestedEdit}
          sessionId={sessionId}
          sectionId={getActiveSection()?.id}
        />
      )}
    </aside>
  );
};
