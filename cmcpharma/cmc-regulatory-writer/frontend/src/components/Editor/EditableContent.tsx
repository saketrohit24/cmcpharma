import React, { useState, useRef, useEffect } from 'react';
import { Edit3, Save, X, RotateCcw } from 'lucide-react';
import { CitationDisplay, getGlobalCitationDisplay } from '../../services/citationDisplay';

interface Citation {
  id: number;
  text: string;
  source: string;
  page: number;
  sourceFileId?: string;
}

interface EditableContentProps {
  content: string;
  citations: Citation[];
  sectionId: string;
  isEdited?: boolean;
  onSave: (sectionId: string, newContent: string, newTitle?: string) => void;
  onRevert: (sectionId: string) => void;
}

export const EditableContent: React.FC<EditableContentProps> = ({ 
  content, 
  citations = [],
  sectionId,
  isEdited = false,
  onSave,
  onRevert
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(content);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [citationDisplay] = useState(() => getGlobalCitationDisplay());

  // Ensure citation styles are loaded
  useEffect(() => {
    // Check if citation styles are already loaded
    const existingStyle = document.getElementById('citation-styles');
    if (!existingStyle) {
      const style = document.createElement('style');
      style.id = 'citation-styles';
      style.textContent = CitationDisplay.getCSSStyles();
      document.head.appendChild(style);
    }
  }, []);

  // Update edit content when props change
  useEffect(() => {
    console.log('🔄 EditableContent: useEffect triggered', {
      sectionId,
      isEditing,
      contentLength: content.length,
      contentPreview: content.substring(0, 100) + '...'
    });
    
    if (!isEditing) {
      console.log('✅ EditableContent: Updating editContent with new content');
      setEditContent(content);
    } else {
      console.log('⏸️ EditableContent: Skipping content update because isEditing=true');
    }
  }, [content, isEditing, sectionId]);

  // Auto-resize textarea
  useEffect(() => {
    if (isEditing && textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [isEditing, editContent]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    const hasContentChanged = editContent.trim() !== content.trim();
    
    if (hasContentChanged) {
      onSave(sectionId, editContent.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditContent(content);
    setIsEditing(false);
  };

  const handleRevert = () => {
    onRevert(sectionId);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    if (e.key === 'Escape') {
      handleCancel();
    } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSave();
    }
  };

  // Use only the provided citations - no default fallback
  const citationsToUse = citations;

  const renderContentWithCitations = (textContent: string) => {
    // Enhanced markdown processing for regulatory content
    let processedContent = textContent;
    
    // Clean up excess markdown symbols and redundant formatting
    processedContent = processedContent.replace(/\*{3,}/g, '**');
    processedContent = processedContent.replace(/_{3,}/g, '__');
    
    // Remove redundant title repetition at the start of content
    const contentLines = processedContent.split('\n');
    if (contentLines.length > 0) {
      const firstLine = contentLines[0].trim();
      if (firstLine.match(/^#+\s+/) && firstLine.length > 10) {
        contentLines.shift();
        processedContent = contentLines.join('\n');
      }
    }
    
    // Convert markdown headers to proper HTML structure
    processedContent = processedContent.replace(/^#{4}\s+(.+)$/gm, '<h4 class="content-h4">$1</h4>');
    processedContent = processedContent.replace(/^#{3}\s+(.+)$/gm, '<h3 class="content-h3">$1</h3>');
    processedContent = processedContent.replace(/^#{2}\s+(.+)$/gm, '<h2 class="content-h2">$1</h2>');
    processedContent = processedContent.replace(/^#{1}\s+(.+)$/gm, '<h1 class="content-h1">$1</h1>');
    
    // Convert bold and italic text
    processedContent = processedContent.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    processedContent = processedContent.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
    
    // Convert bullet points and lists
    processedContent = processedContent.replace(/^[-*•]\s+(.+)$/gm, '<li class="content-li">$1</li>');
    processedContent = processedContent.replace(/^\d+\.\s+(.+)$/gm, '<li class="content-li-numbered">$1</li>');
    
    // Wrap consecutive list items in ul/ol tags
    processedContent = processedContent.replace(/(<li class="content-li">.*?<\/li>[\s\n]*)+/gs, (match) => {
      return `<ul class="content-ul">${match}</ul>`;
    });
    
    processedContent = processedContent.replace(/(<li class="content-li-numbered">.*?<\/li>[\s\n]*)+/gs, (match) => {
      return `<ol class="content-ol">${match.replace(/class="content-li-numbered"/g, 'class="content-li"')}</ol>`;
    });
    
    // Process citations using CitationDisplay service with actual citation data
    if (citationsToUse && citationsToUse.length > 0) {
      const citationData = citationsToUse.map((citation) => ({
        citation_number: citation.id,
        hover_content: `${citation.text} - ${citation.source}, p. ${citation.page}`,
        reference_id: `ref-${citation.id}`,
        cite_id: `cite-${citation.id}`,
        chunk_citation: {
          chunk_id: citation.sourceFileId || `chunk-${citation.id}`,
          pdf_name: citation.source,
          page_number: citation.page,
          text_excerpt: citation.text,
          authors: [],
          external_link: undefined
        }
      }));
      processedContent = citationDisplay.processContentWithCitations(processedContent, citationData);
    }

    // Split content into paragraphs and wrap properly
    const paragraphs = processedContent.split('\n\n').filter(p => p.trim());
    return paragraphs.map((paragraph, index) => {
      const trimmed = paragraph.trim();
      if (trimmed.startsWith('<h') || trimmed.startsWith('<ul') || trimmed.startsWith('<ol') || trimmed.startsWith('<table')) {
        return <div key={index} dangerouslySetInnerHTML={{ __html: trimmed }} />;
      } else {
        return (
          <p key={index} className="content-paragraph">
            <span dangerouslySetInnerHTML={{ __html: trimmed }} />
          </p>
        );
      }
    });
  };

  // Handle citation clicks
  useEffect(() => {
    if (!isEditing && contentRef.current) {
      const citationMarkers = contentRef.current.querySelectorAll('.citation-marker');
      citationMarkers.forEach(marker => {
        marker.addEventListener('click', (e) => {
          e.stopPropagation();
          const citationId = (e.target as HTMLElement).getAttribute('data-citation-id');
          if (citationId) {
            // Handle citation click - could show popover or navigate
            console.log('Citation clicked:', citationId);
          }
        });
      });
    }
  }, [isEditing, content]);

  return (
    <div className="editable-content-container">
      {(() => {
        console.log('🎯 EditableContent RENDER:', {
          sectionId,
          isEditing,
          contentLength: content.length,
          contentPreview: content.substring(0, 100) + '...'
        });
        return null;
      })()}
      {/* Unified Content Area */}
      <div 
        className={`editable-content ${isEditing ? 'editing' : ''}`}
        ref={contentRef}
      >
        {isEditing ? (
          <div className="edit-mode">
            <div className="edit-header">
              <span className="edit-indicator">Editing Content</span>
              <div className="edit-controls">
                <button
                  onClick={handleSave}
                  className="edit-btn edit-btn-success"
                  title="Save changes (Ctrl+Enter)"
                >
                  <Save size={16} />
                  <span>Save</span>
                </button>
                <button
                  onClick={handleCancel}
                  className="edit-btn edit-btn-cancel"
                  title="Cancel editing (Escape)"
                >
                  <X size={16} />
                  <span>Cancel</span>
                </button>
                {isEdited && (
                  <button
                    onClick={handleRevert}
                    className="edit-btn edit-btn-revert"
                    title="Revert to original"
                  >
                    <RotateCcw size={16} />
                    <span>Revert</span>
                  </button>
                )}
              </div>
            </div>
            
            {/* Editable Content */}
            <div className="edit-content-area">
              <textarea
                ref={textareaRef}
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                onKeyDown={handleKeyDown}
                className="edit-textarea"
                placeholder="Enter content here..."
                spellCheck={true}
              />
            </div>
            
            <div className="edit-footer">
              <span className="edit-stats">
                {editContent.length} chars, {editContent.split('\n').length} lines
              </span>
            </div>
          </div>
        ) : (
          <div className="view-mode">
            <div className="content-header">
              <div className="content-title-area">
                {isEdited && <span className="modified-text">Modified</span>}
              </div>
              <div className="content-actions">
                <button
                  onClick={handleEdit}
                  className="edit-btn edit-btn-primary"
                  title="Edit this section manually"
                >
                  <Edit3 size={16} />
                  <span>Edit</span>
                </button>
              </div>
            </div>
            <div className="content-display">
              {renderContentWithCitations(content)}
            </div>
          </div>
        )}
      </div>

      {/* Citations Reference */}
      {citationsToUse && citationsToUse.length > 0 && !isEditing && (
        <div className="citations-reference">
          <h4 className="citations-title">References</h4>
          <div className="citations-list">
            {citationsToUse.map((citation) => (
              <div key={citation.id} className="citation-item" id={`ref-${citation.id}`}>
                <span className="citation-number">[{citation.id}]</span>
                <div className="citation-details">
                  <span className="citation-source">{citation.source}</span>
                  {citation.page && (
                    <span className="citation-page">Page {citation.page}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
