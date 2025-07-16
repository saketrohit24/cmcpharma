import React, { useState } from 'react';
import { FileText, ExternalLink } from 'lucide-react';

interface Citation {
  id: number;
  text: string;
  source: string;
  page: number;
  sourceFileId?: string;
}

interface CitationPopoverProps {
  citation: Citation;
  number: number;
}

export const CitationPopover: React.FC<CitationPopoverProps> = ({ citation, number }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleViewSource = () => {
    console.log('Jumping to source:', citation.sourceFileId, 'page:', citation.page);
    // TODO: Implement actual source viewing
  };

  return (
    <span className="relative inline-block">
      <button
        className="citation-marker"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          color: '#3b82f6',
          fontSize: '12px',
          fontWeight: 'bold',
          cursor: 'pointer',
          padding: '0 2px'
        }}
      >
        [{number}]
      </button>
      
      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-20">
            <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4 w-64">
              <div className="flex items-start gap-2 mb-3">
                <FileText size={16} className="text-gray-500 mt-1" />
                <p className="text-sm text-gray-700">{citation.text}</p>
              </div>
              
              <div className="border-t pt-3">
                <div className="text-xs text-gray-600 space-y-1">
                  <p><strong>Source:</strong> {citation.source}</p>
                  <p><strong>Page:</strong> {citation.page}</p>
                </div>
                
                <button 
                  className="mt-3 flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
                  onClick={handleViewSource}
                >
                  <ExternalLink size={12} />
                  View Source
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </span>
  );
};
