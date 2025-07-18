import React, { useState, useRef, useEffect } from 'react';
import { SpecificationTable } from './SpecificationTable';
import { TextWithCitations } from '../Citations/TextWithCitations';
import { SuggestEditModal } from '../SuggestEdit/SuggestEditModal';

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

interface DocumentEditorProps {
  sections?: Section[];
  citations?: Citation[];
  isGenerating?: boolean;
  generationProgress?: {
    currentSection: string;
    completedSections: string[];
    totalSections: number;
  } | null;
  activeTabId?: string;
}

export const DocumentEditor: React.FC<DocumentEditorProps> = ({ 
  sections = [], 
  citations = [],
  isGenerating = false,
  generationProgress = null,
  activeTabId
}) => {
  const [showSuggestEditModal, setShowSuggestEditModal] = useState(false);
  const [suggestEditContent, setSuggestEditContent] = useState('');
  const [suggestEditContentType, setSuggestEditContentType] = useState<'selected' | 'section'>('section');
  const [sectionHighlighted, setSectionHighlighted] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [editedSections, setEditedSections] = useState<{[key: string]: string}>({});
  const defaultSections: Section[] = [
    {
      id: '1',
      title: '3.2.S.4.1 Specification',
      content: 'The specifications for the drug substance have been established based on the manufacturing process capability, stability data, and regulatory requirements [1]. All tests and acceptance criteria are in accordance with ICH Q6A guidelines [2] and current pharmacopeial standards.',
      type: 'text'
    }
  ];

  // Use generated sections if available, otherwise show default
  const sectionsToRender = sections.length > 0 ? sections : defaultSections;
  
  console.log('DocumentEditor render:', {
    sectionsAvailable: sections.length,
    isGenerating,
    activeTabId,
    sectionsToRender: sectionsToRender.length
  });

  // Find the active section to display using improved matching
  let activeSection: Section | null = null;
  if (activeTabId) {
    // Enhanced section matching strategies with better logging
    console.log('🔍 Looking for section with activeTabId:', activeTabId);
    console.log('📋 Available sections:', sectionsToRender.map(s => ({ id: s.id, title: s.title })));
    
    activeSection = sectionsToRender.find(section => {
      // Direct ID match (highest priority)
      if (section.id === activeTabId) {
        console.log('✅ Found direct ID match:', section.title);
        return true;
      }
      
      // Direct title match
      if (section.title === activeTabId) {
        console.log('✅ Found direct title match:', section.title);
        return true;
      }
      
      // Title contains activeTabId (case insensitive)
      if (section.title.toLowerCase().includes(activeTabId.toLowerCase())) {
        console.log('✅ Found title contains match:', section.title);
        return true;
      }
      
      // ActiveTabId contains section title (for nested matches)
      if (activeTabId.toLowerCase().includes(section.title.toLowerCase())) {
        console.log('✅ Found activeTabId contains match:', section.title);
        return true;
      }
      
      // Clean title matching (remove numbers, special chars, extra whitespace)
      const cleanSectionTitle = section.title.replace(/^\d+\.?\s*/, '').trim().toLowerCase();
      const cleanActiveId = activeTabId.replace(/^\d+\.?\s*/, '').trim().toLowerCase();
      if (cleanSectionTitle === cleanActiveId) {
        console.log('✅ Found clean title match:', section.title);
        return true;
      }
      
      return false;
    }) || null;
    
    if (!activeSection) {
      console.log('❌ No section found for activeTabId:', activeTabId);
    }
  }

  // If no active section found and we have sections, show the first one
  if (!activeSection && sectionsToRender.length > 0) {
    activeSection = sectionsToRender[0];
  }

  console.log('📋 DocumentEditor state:', {
    sectionsCount: sectionsToRender.length,
    activeTabId,
    foundSection: activeSection?.title || 'None',
    availableSections: sectionsToRender.map(s => s.title)
  });

  // Handle text selection
  const handleTextSelection = () => {
    // This function can be used for future text selection features
  };

  // Handle suggest edit button click
  const handleSuggestEditClick = () => {
    console.log('🔄 handleSuggestEditClick called');
    console.log('🔄 activeSection:', activeSection);
    
    if (!activeSection) {
      console.error('❌ No active section found');
      return;
    }
    
    const selection = window.getSelection();
    const selectionText = selection ? selection.toString().trim() : '';
    const hasSelection = selectionText.length > 0;
    
    console.log('🔄 Selection text:', selectionText);
    console.log('🔄 Has selection:', hasSelection);
    
    // Get the current content (edited or original)
    const currentContent = editedSections[activeSection.id] || activeSection.content;
    
    if (hasSelection) {
      // User has selected text - verify it exists in current content
      if (currentContent.includes(selectionText)) {
        setSuggestEditContent(selectionText);
        setSuggestEditContentType('selected');
        console.log('🔄 Set content type to SELECTED');
      } else {
        // Selection doesn't exist in current content, fall back to section edit
        console.log('⚠️ Selected text not found in current content, falling back to section edit');
        setSuggestEditContent(currentContent);
        setSuggestEditContentType('section');
        setSectionHighlighted(true);
        setTimeout(() => setSectionHighlighted(false), 2000);
      }
    } else {
      // No selection - edit entire section with current content
      setSuggestEditContent(currentContent);
      setSuggestEditContentType('section');
      console.log('🔄 Set content type to SECTION, content:', currentContent);
      
      // Highlight the section briefly
      setSectionHighlighted(true);
      setTimeout(() => setSectionHighlighted(false), 2000);
    }
    
    setShowSuggestEditModal(true);
    console.log('🔄 Modal should be open now');
  };

  // Handle applying suggested edits
  const handleApplySuggestedEdit = (editedContent: string) => {
    console.log('🔄 handleApplySuggestedEdit called with:', editedContent);
    console.log('🔄 activeSection:', activeSection);
    console.log('🔄 suggestEditContentType:', suggestEditContentType);
    
    if (!activeSection) {
      console.error('❌ No active section found');
      return;
    }

    // Force a re-render by ensuring the state update is applied
    setEditedSections(prev => {
      const newState = { ...prev };
      
      if (suggestEditContentType === 'section') {
        // Update entire section content
        newState[activeSection.id] = editedContent;
        console.log('✅ Updated entire section content for:', activeSection.id);
      } else if (suggestEditContentType === 'selected') {
        // Replace selected text within the section
        const currentContent = prev[activeSection.id] || activeSection.content;
        const originalSelectedText = suggestEditContent;
        
        console.log('🔄 Current content:', currentContent);
        console.log('🔄 Original selected text:', originalSelectedText);
        console.log('🔄 New edited content:', editedContent);
        
        // Replace the original selected text with the edited content
        const updatedContent = currentContent.replace(originalSelectedText, editedContent);
        newState[activeSection.id] = updatedContent;
        console.log('✅ Updated selected text in section:', activeSection.id);
      }
      
      console.log('🔄 New edited sections state:', newState);
      return newState;
    });
    
    // Close modal after a short delay to ensure state update is processed
    setTimeout(() => {
      setShowSuggestEditModal(false);
    }, 100);
  };

  // Debug effect to track editedSections changes
  useEffect(() => {
    console.log('📝 editedSections state changed:', editedSections);
    console.log('📝 Keys in editedSections:', Object.keys(editedSections));
    if (activeSection) {
      console.log('📝 Content for active section:', activeSection.id, ':', editedSections[activeSection.id] || 'NOT FOUND');
    }
  }, [editedSections, activeSection]);

  // Add keyboard event listener for text selection
  useEffect(() => {
    const handleSelectionChange = () => {
      handleTextSelection();
    };

    document.addEventListener('selectionchange', handleSelectionChange);
    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
    };
  }, []);

  // Debug: Track editedSections state changes
  useEffect(() => {
    console.log('📝 editedSections state changed:', editedSections);
    console.log('📝 Keys in editedSections:', Object.keys(editedSections));
    if (activeSection) {
      console.log('📝 Content for active section:', activeSection.id, ':', editedSections[activeSection.id]);
    }
  }, [editedSections, activeSection]);

  const getTooltipText = () => {
    const selection = window.getSelection();
    const hasSelection = selection && selection.toString().trim();
    
    if (hasSelection) {
      return 'Refine selected text';
    } else {
      return 'Refine current section';
    }
  };

  if (isGenerating) {
    return (
      <div className="document-editor">
        <div className="document-loading p-8 text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Generating Document...</h2>
          {generationProgress ? (
            <div className="generation-progress">
              <div className="mb-4">
                <p className="text-gray-600"><strong>Current:</strong> {generationProgress.currentSection}</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${(generationProgress.completedSections.length / generationProgress.totalSections) * 100}%` 
                    }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  {generationProgress.completedSections.length} of {generationProgress.totalSections} sections completed
                </p>
              </div>
              {generationProgress.completedSections.length > 0 && (
                <div className="completed-sections text-left">
                  <h4 className="font-medium text-gray-700 mb-2">Completed Sections:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {generationProgress.completedSections.map((section, index) => (
                      <li key={index} className="flex items-center">
                        <span className="text-green-500 mr-2">✅</span>
                        {section}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500">Creating content from template. This may take a few moments.</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <main className="content">
      <div className="content-header">
        <h1 className="content-title">
          {activeSection ? activeSection.title : 'Document Editor'}
        </h1>
        <div className="content-actions">
          <button className="icon-btn">↶</button>
          <button className="icon-btn">↷</button>
          <button 
            className="suggest-edit-btn"
            onClick={handleSuggestEditClick}
            title={getTooltipText()}
          >
            ✨ Suggest edits
          </button>
          <div className="toggle-container">
            <div className="toggle">
              <div className="toggle-slider"></div>
            </div>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>View changes</span>
          </div>
        </div>
      </div>
      
      {activeSection ? (
        <div className="section-container">
          {activeSection.type === 'table' ? (
            <SpecificationTable />
          ) : (
            <div 
              className={`section-content ${sectionHighlighted ? 'highlight-section' : ''}`}
              ref={contentRef}
            >
              {editedSections[activeSection.id] && (
                <div className="edited-indicator">
                  <span className="edited-badge">✓ Edited</span>
                </div>
              )}
              <TextWithCitations 
                key={`${activeSection.id}-${editedSections[activeSection.id] ? 'edited' : 'original'}`}
                content={editedSections[activeSection.id] || activeSection.content}
                citations={citations} 
              />
            </div>
          )}
        </div>
      ) : (
        <div className="no-content">
          <div className="text-center p-8">
            {sectionsToRender.length > 0 ? (
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Select a Section</h3>
                <p className="text-gray-500">Click on a section from the Project Structure to view its content.</p>
                <div className="mt-4">
                  <p className="text-sm text-gray-400">Available sections:</p>
                  <ul className="text-sm text-gray-600 mt-2">
                    {sectionsToRender.map(section => (
                      <li key={section.id}>• {section.title}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">No Content Available</h3>
                <p className="text-gray-500">Please generate a document from a template or upload content.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {showSuggestEditModal && (
        <SuggestEditModal 
          isOpen={showSuggestEditModal} 
          onClose={() => setShowSuggestEditModal(false)} 
          content={suggestEditContent}
          contentType={suggestEditContentType}
          onApply={handleApplySuggestedEdit}
          sessionId={sessionId}
          sectionId={activeSection?.id}
        />
      )}
    </main>
  );
};
