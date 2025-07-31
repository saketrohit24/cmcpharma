import React, { useState, useEffect } from 'react';

interface SuggestEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  contentType: 'selected' | 'section';
  onApply: (editedContent: string) => void;
  sessionId: string;
  sectionId?: string;
}

interface Preset {
  id: string;
  name: string;
  description: string;
  requires_rag: boolean;
}

const PRESETS: Preset[] = [
  { id: 'shorten', name: 'Shorten', description: 'Reduce content length while keeping key points', requires_rag: false },
  { id: 'clarify', name: 'Clarify', description: 'Improve readability and clarity', requires_rag: false },
  { id: 'improve_flow', name: 'Improve Flow', description: 'Better transitions and logical progression', requires_rag: false },
  { id: 'make_concise', name: 'Make Concise', description: 'Remove redundancy and wordiness', requires_rag: false },
  { id: 'expand_detail', name: 'Expand Detail', description: 'Add more comprehensive information', requires_rag: true },
  { id: 'simplify', name: 'Simplify', description: 'Use simpler language and structure', requires_rag: false }
];

export const SuggestEditModal: React.FC<SuggestEditModalProps> = ({
  isOpen,
  onClose,
  content,
  contentType,
  onApply,
  sessionId,
  sectionId
}) => {
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);
  const [customInstructions, setCustomInstructions] = useState('');
  const [useRAG, setUseRAG] = useState(false);
  const [maintainTone, setMaintainTone] = useState(true);
  const [preserveTechnicalAccuracy, setPreserveTechnicalAccuracy] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>('');

  // Auto-enable RAG for certain presets or custom instructions
  useEffect(() => {
    if (selectedPreset === 'expand_detail') {
      setUseRAG(true);
    } else if (customInstructions) {
      const researchKeywords = ['research', 'find more', 'add details', 'investigate', 'expand upon'];
      const shouldAutoEnableRAG = researchKeywords.some(keyword => 
        customInstructions.toLowerCase().includes(keyword)
      );
      setUseRAG(shouldAutoEnableRAG);
    }
  }, [selectedPreset, customInstructions]);

  const handlePresetSelect = (presetId: string) => {
    setSelectedPreset(selectedPreset === presetId ? null : presetId);
    setError(null);
  };

  const handleCustomInstructionsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCustomInstructions(e.target.value);
    setError(null);
  };

  const getWordCount = (text: string) => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  };

  const getCharacterCount = (text: string) => {
    return text.length;
  };

  const canApply = () => {
    return (selectedPreset || customInstructions.trim()) && !isProcessing;
  };

  const handleApply = async () => {
    if (!canApply()) return;

    setIsProcessing(true);
    setError(null);
    
    try {
      // Set processing status based on RAG usage
      if (useRAG) {
        setProcessingStatus('Researching...');
        setTimeout(() => setProcessingStatus('Processing...'), 1000);
      } else {
        setProcessingStatus('Processing...');
      }

      const response = await fetch('http://localhost:8001/api/suggest-edit/suggest-edit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          preset: selectedPreset,
          custom_instructions: customInstructions.trim() || null,
          use_rag: useRAG,
          maintain_tone: maintainTone,
          preserve_technical_accuracy: preserveTechnicalAccuracy,
          session_id: sessionId,
          section_id: sectionId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process edit suggestion');
      }

      const result = await response.json();
      console.log('✅ API Response:', result);
      console.log('✅ About to call onApply with:', result.edited_content);
      
      // Apply the edited content
      onApply(result.edited_content);
      
      // Wait a moment before closing to ensure state update is processed
      setTimeout(() => {
        onClose();
      }, 100);
      
      // Reset form
      setSelectedPreset(null);
      setCustomInstructions('');
      setUseRAG(false);
      setMaintainTone(true);
      setPreserveTechnicalAccuracy(true);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsProcessing(false);
      setProcessingStatus('');
    }
  };

  const handleClose = () => {
    if (!isProcessing) {
      onClose();
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && !isProcessing) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="suggest-edit-modal-overlay" onClick={handleBackdropClick}>
      <div className="suggest-edit-modal">
        <div className="suggest-edit-modal-header">
          <h2>Suggest Edit</h2>
          <button 
            className="suggest-edit-modal-close" 
            onClick={handleClose}
            disabled={isProcessing}
          >
            ×
          </button>
        </div>

        <div className="suggest-edit-modal-content">
          {/* Content Preview */}
          <div className="suggest-edit-preview">
            <h3>
              {contentType === 'selected' ? 'Selected Text' : 'Current Section'}
            </h3>
            <div className="suggest-edit-preview-text">
              {content}
            </div>
            <div className="suggest-edit-preview-stats">
              <span>{getWordCount(content)} words</span>
              <span>{getCharacterCount(content)} characters</span>
            </div>
          </div>

          {/* Quick Actions Grid */}
          <div className="suggest-edit-presets">
            <h3>Quick Actions</h3>
            <div className="suggest-edit-presets-grid">
              {PRESETS.map((preset) => (
                <button
                  key={preset.id}
                  className={`suggest-edit-preset-btn ${
                    selectedPreset === preset.id ? 'active' : ''
                  }`}
                  onClick={() => handlePresetSelect(preset.id)}
                  disabled={isProcessing}
                >
                  <span className="suggest-edit-preset-name">{preset.name}</span>
                  <span className="suggest-edit-preset-description">{preset.description}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Custom Instructions */}
          <div className="suggest-edit-custom">
            <h3>Custom Instructions</h3>
            <textarea
              className="suggest-edit-custom-input"
              placeholder="Describe how you'd like the content to be modified..."
              value={customInstructions}
              onChange={handleCustomInstructionsChange}
              disabled={isProcessing}
              rows={4}
            />
            <div className="suggest-edit-custom-stats">
              {customInstructions.length} characters
            </div>
          </div>

          {/* Advanced Options */}
          <div className="suggest-edit-advanced">
            <h3>Advanced Options</h3>
            <div className="suggest-edit-advanced-options">
              <label className="suggest-edit-checkbox">
                <input
                  type="checkbox"
                  checked={useRAG}
                  onChange={(e) => setUseRAG(e.target.checked)}
                  disabled={isProcessing}
                />
                <span className="suggest-edit-checkbox-label">
                  Use RAG for additional research
                  <span className="suggest-edit-checkbox-tooltip">
                    Search for additional information to enhance content
                  </span>
                </span>
              </label>
              <label className="suggest-edit-checkbox">
                <input
                  type="checkbox"
                  checked={maintainTone}
                  onChange={(e) => setMaintainTone(e.target.checked)}
                  disabled={isProcessing}
                />
                <span className="suggest-edit-checkbox-label">Maintain original tone</span>
              </label>
              <label className="suggest-edit-checkbox">
                <input
                  type="checkbox"
                  checked={preserveTechnicalAccuracy}
                  onChange={(e) => setPreserveTechnicalAccuracy(e.target.checked)}
                  disabled={isProcessing}
                />
                <span className="suggest-edit-checkbox-label">Preserve technical accuracy</span>
              </label>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="suggest-edit-error">
              <span className="suggest-edit-error-icon">⚠️</span>
              {error}
            </div>
          )}

          {/* Processing Status */}
          {isProcessing && (
            <div className="suggest-edit-processing">
              <div className="suggest-edit-processing-spinner"></div>
              <span>{processingStatus}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="suggest-edit-actions">
            <button
              className="suggest-edit-cancel"
              onClick={handleClose}
              disabled={isProcessing}
            >
              Cancel
            </button>
            <button
              className={`suggest-edit-apply ${canApply() ? 'enabled' : 'disabled'}`}
              onClick={handleApply}
              disabled={!canApply()}
            >
              {isProcessing ? 'Processing...' : 'Apply'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuggestEditModal;