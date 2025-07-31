import React, { useRef, useEffect } from 'react';
import { SpecificationTable } from './SpecificationTable';
import { EditableContent } from './EditableContent';
import '../../styles/editable-content.css';

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
  editedSections?: {[key: string]: string};
  onSectionEdit?: (sectionId: string, newContent: string) => void;
  onSectionRevert?: (sectionId: string) => void;
}

export const DocumentEditor: React.FC<DocumentEditorProps> = ({ 
  sections = [], 
  citations = [],
  isGenerating = false,
  generationProgress = null,
  activeTabId,
  editedSections = {},
  onSectionEdit,
  onSectionRevert
}) => {
  const contentRef = useRef<HTMLDivElement>(null);

  // Default handlers if not provided
  const handleSectionEdit = onSectionEdit || ((sectionId: string, newContent: string) => {
    console.log('Section edit:', sectionId, newContent);
  });

  const handleSectionRevert = onSectionRevert || ((sectionId: string) => {
    console.log('Section revert:', sectionId);
  });
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

  // Debug effect to track editedSections changes
  useEffect(() => {
    console.log('📝 DocumentEditor: editedSections state changed:', editedSections);
    console.log('📝 DocumentEditor: Keys in editedSections:', Object.keys(editedSections));
    console.log('📝 DocumentEditor: Current activeTabId:', activeTabId);
    if (activeSection) {
      console.log('📝 DocumentEditor: Active section:', { id: activeSection.id, title: activeSection.title });
      console.log('📝 DocumentEditor: Content for active section:', {
        hasEditedContent: !!editedSections[activeSection.id],
        editedContentLength: editedSections[activeSection.id]?.length || 0,
        originalContentLength: activeSection.content.length
      });
      
      if (editedSections[activeSection.id]) {
        console.log('✅ DocumentEditor: Using EDITED content for section', activeSection.id);
      } else {
        console.log('ℹ️ DocumentEditor: Using ORIGINAL content for section', activeSection.id);
      }
    }
  }, [editedSections, activeSection, activeTabId]);

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
            <div className="section-content" ref={contentRef}>
              {(() => {
                const contentToUse = editedSections[activeSection.id] || activeSection.content;
                console.log('🎯 DocumentEditor RENDER: About to render content for section', activeSection.id);
                console.log('📝 DocumentEditor RENDER: Using edited content?', !!editedSections[activeSection.id]);
                console.log('📝 DocumentEditor RENDER: Content length:', contentToUse?.length || 0);
                console.log('📝 DocumentEditor RENDER: Content preview:', contentToUse?.substring(0, 200) || 'EMPTY');
                
                return (
                  <EditableContent
                    key={`${activeSection.id}-${editedSections[activeSection.id] ? 'edited' : 'original'}`}
                    content={contentToUse}
                    citations={citations}
                    sectionId={activeSection.id}
                    isEdited={!!editedSections[activeSection.id]}
                    onSave={handleSectionEdit}
                    onRevert={handleSectionRevert}
                  />
                );
              })()}
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
    </main>
  );
};
