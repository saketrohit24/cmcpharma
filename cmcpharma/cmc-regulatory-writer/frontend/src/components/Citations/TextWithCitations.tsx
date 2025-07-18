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
  // Debug: Log when content changes
  console.log('📝 TextWithCitations received content:', content);
  
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
    // Enhanced markdown processing for regulatory content
    let processedContent = content;
    
    // Clean up excess markdown symbols and redundant formatting
    processedContent = processedContent.replace(/\*{3,}/g, '**');
    processedContent = processedContent.replace(/_{3,}/g, '__');
    
    // Remove redundant title repetition at the start of content
    // If content starts with a header that repeats the section title, remove it
    const contentLines = processedContent.split('\n');
    if (contentLines.length > 0) {
      const firstLine = contentLines[0].trim();
      // Remove if it's a markdown header that likely repeats the title
      if (firstLine.match(/^#+\s+/) && firstLine.length > 10) {
        // Remove the first line if it looks like a redundant title
        contentLines.shift();
        processedContent = contentLines.join('\n');
      }
    }
    
    // Convert markdown headers to proper HTML structure with better hierarchy
    // H1 should be rare in content (main section titles)
    processedContent = processedContent.replace(/^#{4}\s+(.+)$/gm, '<h4 class="content-h4">$1</h4>');
    processedContent = processedContent.replace(/^#{3}\s+(.+)$/gm, '<h3 class="content-h3">$1</h3>');
    processedContent = processedContent.replace(/^#{2}\s+(.+)$/gm, '<h2 class="content-h2">$1</h2>');
    processedContent = processedContent.replace(/^#{1}\s+(.+)$/gm, '<h1 class="content-h1">$1</h1>');
    
    // Convert bold text (clean up excessive bold formatting)
    processedContent = processedContent.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    processedContent = processedContent.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
    
    // Convert bullet points and lists with better formatting
    processedContent = processedContent.replace(/^[-*•]\s+(.+)$/gm, '<li class="content-li">$1</li>');
    processedContent = processedContent.replace(/^\d+\.\s+(.+)$/gm, '<li class="content-li-numbered">$1</li>');
    
    // Wrap consecutive list items in ul/ol tags with proper classes
    processedContent = processedContent.replace(/(<li class="content-li">.*?<\/li>[\s\n]*)+/gs, (match) => {
      return `<ul class="content-ul">${match}</ul>`;
    });
    
    processedContent = processedContent.replace(/(<li class="content-li-numbered">.*?<\/li>[\s\n]*)+/gs, (match) => {
      return `<ol class="content-ol">${match.replace(/class="content-li-numbered"/g, 'class="content-li"')}</ol>`;
    });
    
    // Handle table formatting
    const lines = processedContent.split('\n');
    let inTable = false;
    const processedLines: string[] = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Detect table rows (lines with | characters)
      if (line.includes('|') && !line.startsWith('<')) {
        if (!inTable) {
          processedLines.push('<table>');
          inTable = true;
        }
        
        const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
        
        // Skip separator lines (lines with just dashes and pipes)
        if (line.match(/^[\s|:-]+$/)) {
          continue;
        }
        
        const isHeader = i === 0 || (lines[i + 1] && lines[i + 1].match(/^[\s|:-]+$/));
        const tag = isHeader ? 'th' : 'td';
        
        if (isHeader && !processedLines[processedLines.length - 1].includes('<thead>')) {
          processedLines.push('<thead>');
        } else if (!isHeader && !processedLines[processedLines.length - 1].includes('<tbody>')) {
          if (processedLines[processedLines.length - 1] === '</thead>') {
            // Close thead if it was open
          } else {
            processedLines.push('</thead>');
          }
          processedLines.push('<tbody>');
        }
        
        const row = `<tr>${cells.map(cell => `<${tag}>${cell}</${tag}>`).join('')}</tr>`;
        processedLines.push(row);
      } else {
        if (inTable) {
          if (processedLines[processedLines.length - 1] !== '</tbody>') {
            processedLines.push('</tbody>');
          }
          processedLines.push('</table>');
          inTable = false;
        }
        processedLines.push(line);
      }
    }
    
    if (inTable) {
      processedLines.push('</tbody></table>');
    }
    
    processedContent = processedLines.join('\n');
    
    // Convert line breaks to paragraphs, but preserve HTML structure
    const sections = processedContent.split(/\n\s*\n/).filter(s => s.trim());
    
    return sections.map((section, sectionIndex) => {
      const citationRegex = /\[(\d+)\]/g;
      const parts = section.split(citationRegex);
      
      const renderedContent = parts.map((part, index) => {
        const citationNumber = parseInt(part);
        
        if (!isNaN(citationNumber) && citationsToUse[citationNumber - 1]) {
          return (
            <CitationPopover
              key={`citation-${sectionIndex}-${index}`}
              number={citationNumber}
              citation={citationsToUse[citationNumber - 1]}
            />
          );
        }
        
        // Render HTML content
        if (part.includes('<')) {
          return <span key={`html-${sectionIndex}-${index}`} dangerouslySetInnerHTML={{ __html: part }} />;
        }
        
        return <span key={`text-${sectionIndex}-${index}`}>{part}</span>;
      });
      
      // If the section contains block-level HTML, render as div, otherwise as paragraph
      const hasBlockElements = section.includes('<h') || section.includes('<ul') || section.includes('<table');
      const WrapperTag = hasBlockElements ? 'div' : 'p';
      
      return (
        <WrapperTag key={`section-${sectionIndex}`} className="content-paragraph">
          {renderedContent}
        </WrapperTag>
      );
    });
  };

  return (
    <div className="section-content">
      {renderContentWithCitations()}
    </div>
  );
};
