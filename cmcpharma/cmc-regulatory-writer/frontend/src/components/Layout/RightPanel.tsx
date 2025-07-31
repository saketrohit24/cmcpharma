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
  // citations = [], // Commented out unused parameter
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

  // Track text selection with more robust detection
  React.useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection();
      const selectionText = selection ? selection.toString().trim() : '';
      if (selectionText.length > 0 && selection) {
        // Store both the text and the selection range for later use
        setLastSelection(selectionText);
        // Also store the range information for more precise replacement
        if (selection.rangeCount > 0) {
          // Store range data in session storage as backup
          sessionStorage.setItem('lastSelectedText', selectionText);
          sessionStorage.setItem('lastSelectionValid', 'true');
          // For large selections, also store additional metadata
          if (selectionText.length > 100) {
            sessionStorage.setItem('lastSelectionLength', selectionText.length.toString());
            sessionStorage.setItem('lastSelectionWords', selectionText.split(' ').length.toString());
          }
        }
        console.log('🔄 RightPanel: Selection saved:', selectionText.length > 100 ? 
          `${selectionText.substring(0, 100)}... (${selectionText.length} chars)` : selectionText);
      }
    };

    const handleMouseUp = () => {
      // Additional selection capture on mouse up - with longer delay for large selections
      setTimeout(() => {
        const selection = window.getSelection();
        const selectionText = selection ? selection.toString().trim() : '';
        if (selectionText.length > 0) {
          setLastSelection(selectionText);
          sessionStorage.setItem('lastSelectedText', selectionText);
          sessionStorage.setItem('lastSelectionValid', 'true');
          if (selectionText.length > 100) {
            sessionStorage.setItem('lastSelectionLength', selectionText.length.toString());
            sessionStorage.setItem('lastSelectionWords', selectionText.split(' ').length.toString());
          }
          console.log('🔄 RightPanel: Mouse up selection saved:', selectionText.length > 100 ? 
            `${selectionText.substring(0, 100)}... (${selectionText.length} chars)` : selectionText);
        }
      }, 50); // Longer delay to ensure selection is finalized, especially for large selections
    };

    // Also capture selection on mousedown to catch the start of selection
    const handleMouseDown = () => {
      // Clear any previous selection data when starting new selection
      sessionStorage.removeItem('lastSelectedText');
      sessionStorage.removeItem('lastSelectionValid');
    };

    document.addEventListener('selectionchange', handleSelectionChange);
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('mousedown', handleMouseDown);
    
    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('mousedown', handleMouseDown);
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
  const handleSuggestEditClick = (e: React.MouseEvent) => {
    // Prevent any interference with selection
    e.preventDefault();
    e.stopPropagation();
    
    console.log('🔄 RightPanel: handleSuggestEditClick called');
    
    // Immediately capture selection before anything else
    const selection = window.getSelection();
    const immediateSelectionText = selection ? selection.toString().trim() : '';
    
    // Also try to get selection from session storage as backup
    const backupSelectionText = sessionStorage.getItem('lastSelectedText') || '';
    const isBackupValid = sessionStorage.getItem('lastSelectionValid') === 'true';
    
    console.log('🔄 RightPanel: Immediate selection text:', immediateSelectionText);
    console.log('🔄 RightPanel: Backup selection text:', backupSelectionText);
    console.log('🔄 RightPanel: Saved selection text:', lastSelection);
    
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
    console.log('🔄 RightPanel: currentContent length:', currentContent.length);
    
    // Use the best available selection text (priority: immediate > backup > saved)
    let selectionText = immediateSelectionText;
    if (!selectionText && isBackupValid) {
      selectionText = backupSelectionText;
    }
    if (!selectionText) {
      selectionText = lastSelection;
    }
    
    const hasSelection = selectionText.length > 0;
    
    console.log('🔄 RightPanel: Final selection text:', selectionText);
    console.log('🔄 RightPanel: Has selection:', hasSelection);
    console.log('🔄 RightPanel: Selection length:', selectionText.length);
    
    // Clear the backup selection
    sessionStorage.removeItem('lastSelectedText');
    sessionStorage.removeItem('lastSelectionValid');
    
    // More robust selection validation for large paragraphs
    const isSelectionValid = (selection: string, content: string): boolean => {
      if (!selection || selection.length === 0) return false;
      
      // Normalize both strings for comparison (remove extra whitespace, line breaks)
      const normalizeText = (text: string) => text.replace(/\s+/g, ' ').trim();
      const normalizedSelection = normalizeText(selection);
      const normalizedContent = normalizeText(content);
      
      // For large selections (paragraphs), be much more lenient
      if (selection.length > 50) {
        // Check if the selection contains significant parts of the content
        const words = normalizedSelection.split(' ').filter(word => word.length > 2);
        
        // If selection has many words, check if most of them exist in content
        if (words.length > 5) {
          const matchingWords = words.filter(word => 
            normalizedContent.includes(word)
          );
          const matchRatio = matchingWords.length / words.length;
          console.log('🔄 RightPanel: Large selection match ratio:', matchRatio, 'for', words.length, 'words');
          
          // Be much more lenient - if we have a reasonable match, accept it
          return matchRatio > 0.3; // Only 30% of words need to match for large selections
        }
      }
      
      // For smaller selections, use direct inclusion check
      return normalizedContent.includes(normalizedSelection);
    };
    
    if (hasSelection && selectionText.length > 10) {
      // User has selected a meaningful amount of text - use it regardless of validation
      // This ensures large paragraph selections are always respected
      setSuggestEditContent(selectionText);
      setSuggestEditContentType('selected');
      console.log('✅ RightPanel: Using large selection directly:', selectionText.substring(0, 100) + '...');
      setLastSelection('');
    } else if (hasSelection && isSelectionValid(selectionText, currentContent)) {
      // User has selected text and it exists in current content
      setSuggestEditContent(selectionText);
      setSuggestEditContentType('selected');
      console.log('✅ RightPanel: Set content type to SELECTED');
      setLastSelection('');
    } else if (hasSelection) {
      // User has selected text but it's not found in current content
      // This might happen if selection is from a different section or outdated
      console.log('⚠️ RightPanel: Selection not found in current content, falling back to section edit');
      console.log('🔄 RightPanel: Selection validation failed for:', selectionText.substring(0, 100) + '...');
      setSuggestEditContent(currentContent);
      setSuggestEditContentType('section');
      setLastSelection('');
    } else {
      // No selection or selection not found - edit entire section
      setSuggestEditContent(currentContent);
      setSuggestEditContentType('section');
      console.log('✅ RightPanel: Set content type to SECTION');
      setLastSelection('');
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
    console.log('🔄 RightPanel: activeSection:', { id: activeSection.id, title: activeSection.title });
    console.log('🔄 RightPanel: activeTabId:', activeTabId);
    console.log('🔄 RightPanel: suggestEditContentType:', suggestEditContentType);
    console.log('🔄 RightPanel: editedContent length:', editedContent.length);
    console.log('🔄 RightPanel: editedSections keys before update:', Object.keys(editedSections));
    
    let finalContent = editedContent;
    
    if (suggestEditContentType === 'selected') {
      // Replace selected text within the section
      const currentContent = editedSections[activeSection.id] || activeSection.content;
      const originalSelectedText = suggestEditContent;
      
      console.log('🔄 RightPanel: Replacing selected text');
      console.log('🔄 RightPanel: Current content length:', currentContent.length);
      console.log('🔄 RightPanel: Original selected text length:', originalSelectedText.length);
      console.log('🔄 RightPanel: Original selected text preview:', originalSelectedText.substring(0, 200) + '...');
      console.log('🔄 RightPanel: Edited content preview:', editedContent.substring(0, 200) + '...');
      
      // SMART TEXT REPLACEMENT STRATEGY:
      // Multiple fallback methods to handle various text matching scenarios
      
      const smartTextReplacement = (content: string, originalText: string, newText: string): string | null => {
        // Method 1: Exact match
        if (content.includes(originalText)) {
          console.log('✅ Exact match found');
          return content.replace(originalText, newText);
        }
        
        // Method 2: Normalize whitespace and try again
        const normalizeWhitespace = (text: string) => text.replace(/\s+/g, ' ').trim();
        const normalizedOriginal = normalizeWhitespace(originalText);
        const normalizedContent = normalizeWhitespace(content);
        
        if (normalizedContent.includes(normalizedOriginal)) {
          console.log('✅ Normalized whitespace match found');
          // Create regex that handles flexible whitespace
          const flexibleRegex = new RegExp(
            originalText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+'),
            'gi'
          );
          if (flexibleRegex.test(content)) {
            return content.replace(flexibleRegex, newText);
          }
        }
        
        // Method 3: Try first 50 characters match (handles truncated selections)
        const shortOriginal = originalText.substring(0, 50);
        const shortNormalized = normalizeWhitespace(shortOriginal);
        
        if (shortOriginal.length > 10 && normalizedContent.includes(shortNormalized)) {
          console.log('✅ Short text match found, looking for full context');
          // Find the position and try to match more context
          const startIndex = normalizedContent.indexOf(shortNormalized);
          if (startIndex !== -1) {
            // Extract surrounding context to find the full original text
            const contextBefore = Math.max(0, startIndex - 100);
            const contextAfter = Math.min(normalizedContent.length, startIndex + originalText.length + 100);
            const contextText = normalizedContent.substring(contextBefore, contextAfter);
            
            // Try to find the best matching segment
            const words = normalizedOriginal.split(' ').filter(w => w.length > 2);
            if (words.length >= 3) {
              const firstThreeWords = words.slice(0, 3).join(' ');
              const lastThreeWords = words.slice(-3).join(' ');
              
              const startMatch = contextText.indexOf(firstThreeWords);
              const endMatch = contextText.indexOf(lastThreeWords);
              
              if (startMatch !== -1 && endMatch !== -1 && endMatch > startMatch) {
                const extractedText = contextText.substring(startMatch, endMatch + lastThreeWords.length);
                
                // Now find this in the original content and replace
                const flexibleRegex = new RegExp(
                  extractedText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+'),
                  'gi'
                );
                
                if (flexibleRegex.test(content)) {
                  console.log('✅ Context-based match found');
                  return content.replace(flexibleRegex, newText);
                }
              }
            }
          }
        }
        
        // Method 4: Fuzzy word-based matching for longer texts
        if (originalText.length > 100) {
          const originalWords = normalizeWhitespace(originalText).split(' ').filter(w => w.length > 2);
          const contentWords = normalizeWhitespace(content).split(' ');
          
          // Find the best continuous sequence match
          let bestMatch = { start: -1, end: -1, score: 0 };
          
          for (let i = 0; i < contentWords.length - originalWords.length + 1; i++) {
            let score = 0;
            let consecutiveMatches = 0;
            
            for (let j = 0; j < originalWords.length; j++) {
              if (i + j < contentWords.length && 
                  contentWords[i + j].toLowerCase() === originalWords[j].toLowerCase()) {
                score++;
                consecutiveMatches++;
              } else {
                consecutiveMatches = 0;
              }
              
              // Bonus for consecutive matches
              if (consecutiveMatches > 3) {
                score += consecutiveMatches * 0.1;
              }
            }
            
            const matchRatio = score / originalWords.length;
            if (matchRatio > bestMatch.score && matchRatio > 0.7) {
              bestMatch = { start: i, end: i + originalWords.length, score: matchRatio };
            }
          }
          
          if (bestMatch.start !== -1 && bestMatch.score > 0.7) {
            console.log(`✅ Fuzzy match found with ${Math.round(bestMatch.score * 100)}% confidence`);
            
            // Find the actual text boundaries in the original content
            const beforeWords = contentWords.slice(0, bestMatch.start);
            const afterWords = contentWords.slice(bestMatch.end);
            
            // Reconstruct with proper spacing (approximately)
            const beforeText = beforeWords.join(' ');
            const afterText = afterWords.join(' ');
            
            // Find these boundaries in the original content
            let beforeIndex = 0;
            let afterIndex = content.length;
            
            if (beforeText.length > 0) {
              const beforeMatch = content.indexOf(beforeText.substring(-50)); // Last 50 chars
              if (beforeMatch !== -1) {
                beforeIndex = beforeMatch + beforeText.substring(-50).length;
              }
            }
            
            if (afterText.length > 0) {
              const afterMatch = content.indexOf(afterText.substring(0, 50), beforeIndex); // First 50 chars
              if (afterMatch !== -1) {
                afterIndex = afterMatch;
              }
            }
            
            if (beforeIndex < afterIndex) {
              const beforePart = content.substring(0, beforeIndex);
              const afterPart = content.substring(afterIndex);
              return beforePart + newText + afterPart;
            }
          }
        }
        
        // Method 5: Last resort - find any significant text overlap
        if (originalText.length > 20) {
          const sentences = originalText.split(/[.!?]+/).filter(s => s.trim().length > 10);
          
          for (const sentence of sentences) {
            const cleanSentence = normalizeWhitespace(sentence);
            if (cleanSentence.length > 15 && normalizedContent.includes(cleanSentence)) {
              console.log('✅ Sentence-based match found');
              // Replace this sentence and expand context
              const regex = new RegExp(
                cleanSentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+'),
                'gi'
              );
              
              // Try to replace with some surrounding context
              const expandedRegex = new RegExp(
                `[^.!?]*${cleanSentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+')}[^.!?]*`,
                'gi'
              );
              
              if (expandedRegex.test(content)) {
                return content.replace(expandedRegex, newText);
              } else if (regex.test(content)) {
                return content.replace(regex, newText);
              }
            }
          }
        }
        
        return null;
      };
      
      // Try smart replacement
      const replacedContent = smartTextReplacement(currentContent, originalSelectedText, editedContent);
      
      if (replacedContent) {
        finalContent = replacedContent;
        console.log('✅ RightPanel: Text replacement successful using simple method');
      } else {
        // Show a clear error message and ask for confirmation
        console.error('🚨 RightPanel: Could not find selected text for replacement');
        
        const userWantsToReplace = confirm(
          `⚠️ Selected Text Replacement Failed\n\n` +
          `The selected text could not be found in the current section content. This might happen if:\n` +
          `• The text was from a different section\n` +
          `• The content has been edited since selection\n` +
          `• There was a copy/paste error\n\n` +
          `Selected text preview: "${originalSelectedText.substring(0, 100)}..."\n\n` +
          `Would you like to replace the ENTIRE section instead?\n\n` +
          `• Click "OK" to replace the entire section\n` +
          `• Click "Cancel" to try selecting the text again`
        );
        
        if (userWantsToReplace) {
          finalContent = editedContent;
          console.log('⚠️ User chose to replace entire section');
        } else {
          console.log('✋ User cancelled operation - will try again');
          setShowSuggestEditModal(false);
          alert('Please try selecting the text again and click "Suggest Edit".');
          return;
        }
      }
    } else {
      console.log('🔄 RightPanel: Content type is "section", replacing entire section');
    }
    
    // Use the callback to update the section content
    if (onEditSection) {
      console.log('🔄 RightPanel: About to call onEditSection with:');
      console.log('   - sectionId:', activeSection.id);
      console.log('   - content length:', finalContent.length);
      console.log('   - content preview:', finalContent.substring(0, 200) + '...');
      
      onEditSection(activeSection.id, finalContent);
      
      console.log('✅ RightPanel: onEditSection called successfully');
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
                  style={{ 
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 16px',
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    marginBottom: '12px',
                    width: '100%'
                  }}
                  onMouseDown={(e) => {
                    // Capture selection immediately before any button interaction
                    const selection = window.getSelection();
                    const selectionText = selection ? selection.toString().trim() : '';
                    if (selectionText.length > 0) {
                      sessionStorage.setItem('lastSelectedText', selectionText);
                      sessionStorage.setItem('lastSelectionValid', 'true');
                      setLastSelection(selectionText);
                      console.log('🔄 RightPanel: Pre-click selection captured:', selectionText);
                    }
                    // Prevent the button from stealing focus and clearing selection
                    e.preventDefault();
                    e.stopPropagation();
                  }}
                  onFocus={(e) => {
                    // Prevent focus from clearing selection
                    e.preventDefault();
                  }}
                >
                  <div className="action-icon" style={{
                    width: '32px',
                    height: '32px',
                    backgroundColor: '#ef4444',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '6px'
                  }}>
                    <Plus size={20} />
                  </div>
                  <span className="action-text" style={{ fontSize: '14px', color: '#374151' }}>
                    Suggest edits
                  </span>
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
