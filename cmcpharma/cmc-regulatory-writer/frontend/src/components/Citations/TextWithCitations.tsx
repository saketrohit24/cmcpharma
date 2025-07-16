import React from 'react';
import { CitationPopover } from './CitationPopover';

interface Citation {
  id: number;
  text: string;
  source: string;
  page: number;
  sourceFileId?: string;
}

interface TextWithCitationsProps {
  content: string;
  citations: Citation[];
}

export const TextWithCitations: React.FC<TextWithCitationsProps> = ({ 
  content, 
  citations = [] 
}) => {
  // Default citations if none provided
  const defaultCitations: Citation[] = [
    {
      id: 1,
      text: "Manufacturing process validated according to ICH Q7",
      source: "process_validation.pdf",
      page: 24
    },
    {
      id: 2,
      text: "ICH Q6A: Specifications: Test Procedures and Acceptance Criteria",
      source: "ICH_Q6A_Guideline.pdf",
      page: 1
    }
  ];

  const citationsToUse = citations.length > 0 ? citations : defaultCitations;

  const renderContentWithCitations = () => {
    const citationRegex = /\[(\d+)\]/g;
    const parts = content.split(citationRegex);
    
    return parts.map((part, index) => {
      const citationNumber = parseInt(part);
      
      if (!isNaN(citationNumber) && citationsToUse[citationNumber - 1]) {
        return (
          <CitationPopover
            key={`citation-${index}`}
            number={citationNumber}
            citation={citationsToUse[citationNumber - 1]}
          />
        );
      }
      
      return <span key={`text-${index}`}>{part}</span>;
    });
  };

  return (
    <div className="section-content">
      {renderContentWithCitations()}
    </div>
  );
};
