/**
 * Citation Display Component for Interactive Citations
 */

export interface CitationData {
  citation_number: number;
  hover_content: string;
  reference_id: string;
  cite_id: string;
  chunk_citation: {
    chunk_id: string;
    pdf_name: string;
    page_number: number;
    section?: string;
    text_excerpt: string;
    authors?: string[];
    external_link?: string;
  };
}

export interface DocumentCitations {
  document_id: string;
  session_id: string;
  citations: CitationData[];
  citation_count: number;
  citation_style: string;
}

export class CitationDisplay {
  private tooltipElement: HTMLElement | null = null;

  constructor() {
    this.initializeTooltips();
    this.setupClickHandlers();
  }

  /**
   * Process content to add interactive citation markers
   */
  processContentWithCitations(content: string, citations?: CitationData[]): string {
    if (!content) return content;

    // If citations are provided, use them for precise matching
    if (citations && citations.length > 0) {
      let processedContent = content;

      // Create a map of citation numbers to citation data for quick lookup
      const citationMap = new Map<number, CitationData>();
      citations.forEach(citation => {
        citationMap.set(citation.citation_number, citation);
      });

      // Handle both individual citations [1] and comma-separated citations [1, 2, 3]
      const citationPattern = /\[([0-9, ]+)\]/g;
      
      processedContent = processedContent.replace(citationPattern, (match, numbersStr) => {
        // Parse the numbers (could be "1" or "1, 2, 3")
        const numbers = numbersStr.split(',').map((n: string) => parseInt(n.trim())).filter((n: number) => !isNaN(n));
        
        if (numbers.length === 1) {
          // Single citation [1]
          const citationNumber = numbers[0];
          const citation = citationMap.get(citationNumber);
          
          if (citation) {
            return `<span class="citation-marker" data-citation="${citationNumber}">
              <a href="#ref-${citationNumber}" 
                 id="${citation.cite_id}" 
                 class="citation-link text-blue-600 hover:text-blue-800 font-medium cursor-pointer"
                 data-tooltip="${citation.hover_content}"
                 title="${citation.hover_content}">
                 [${citationNumber}]
              </a>
            </span>`;
          }
        } else if (numbers.length > 1) {
          // Multiple citations [1, 2, 3] - convert to individual citations
          const individualCitations = numbers.map(citationNumber => {
            const citation = citationMap.get(citationNumber);
            
            if (citation) {
              return `<span class="citation-marker" data-citation="${citationNumber}">
                <a href="#ref-${citationNumber}" 
                   class="citation-link text-blue-600 hover:text-blue-800 font-medium cursor-pointer"
                   data-tooltip="${citation.hover_content}"
                   title="${citation.hover_content}">
                   [${citationNumber}]
                </a>
              </span>`;
            } else {
              // Fallback for missing citation data
              return `<span class="citation-marker" data-citation="${citationNumber}">
                <a href="#ref-${citationNumber}" class="citation-link text-blue-600 hover:text-blue-800 font-medium cursor-pointer">
                  [${citationNumber}]
                </a>
              </span>`;
            }
          }).join(' ');
          
          return individualCitations;
        }
        
        // Return original if no valid numbers found
        return match;
      });

      return processedContent;
    }

    // Fallback: Pattern matching for general citations (enhanced to handle comma-separated)
    const citationPattern = /\[([0-9, ]+)\]/g;
    
    return content.replace(citationPattern, (match, numbersStr) => {
      const numbers = numbersStr.split(',').map((n: string) => parseInt(n.trim())).filter((n: number) => !isNaN(n));
      
      if (numbers.length === 1) {
        // Single citation
        const citationNumber = numbers[0];
        return `<span class="citation-marker" data-citation="${citationNumber}" data-original="${match}">
          <a href="#ref-${citationNumber}" class="citation-link text-blue-600 hover:text-blue-800 font-medium cursor-pointer">
            [${citationNumber}]
          </a>
        </span>`;
      } else if (numbers.length > 1) {
        // Multiple citations - convert to individual
        const individualCitations = numbers.map(citationNumber => {
          return `<span class="citation-marker" data-citation="${citationNumber}">
            <a href="#ref-${citationNumber}" class="citation-link text-blue-600 hover:text-blue-800 font-medium cursor-pointer">
              [${citationNumber}]
            </a>
          </span>`;
        }).join(' ');
        
        return individualCitations;
      }
      
      return match;
    });
  }

  /**
   * Load citations for a document
   */
  async loadDocumentCitations(documentId: string): Promise<DocumentCitations | null> {
    try {
      const response = await fetch(`/api/citations/documents/${documentId}`);
      if (!response.ok) {
        if (response.status === 404) {
          console.log(`No citations found for document ${documentId}`);
          return null;
        }
        throw new Error(`Failed to load citations: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error loading citations:', error);
      return null;
    }
  }

  /**
   * Initialize interactive tooltips for citations
   */
  private initializeTooltips(): void {
    // Create tooltip element only if it doesn't exist
    if (!this.tooltipElement) {
      this.tooltipElement = document.createElement('div');
      this.tooltipElement.className = 'citation-tooltip';
      this.tooltipElement.style.cssText = `
        position: fixed;
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: normal;
        white-space: nowrap;
        z-index: 10000;
        box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
        pointer-events: none;
        opacity: 0;
        transition: all 0.15s ease;
        max-width: 400px;
        white-space: pre-wrap;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.4;
        visibility: hidden;
      `;
      document.body.appendChild(this.tooltipElement);
    }

    // Setup hover events
    document.addEventListener('mouseover', this.handleCitationHover.bind(this));
    document.addEventListener('mouseout', this.handleCitationOut.bind(this));
    document.addEventListener('mousemove', this.handleMouseMove.bind(this));
  }

  /**
   * Setup click handlers for citation navigation
   */
  private setupClickHandlers(): void {
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      
      if (target.classList.contains('citation-link')) {
        event.preventDefault();
        const href = target.getAttribute('href');
        if (href && href.startsWith('#')) {
          this.scrollToReference(href.substring(1));
        }
      }
    });
  }

  /**
   * Handle citation hover to show tooltip
   */
  private handleCitationHover(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    
    if (target.classList.contains('citation-link') && target.hasAttribute('data-tooltip')) {
      const tooltipContent = target.getAttribute('data-tooltip');
      if (tooltipContent && this.tooltipElement) {
        console.log('🔗 Citation hover detected:', tooltipContent);
        this.tooltipElement.textContent = tooltipContent;
        this.tooltipElement.style.visibility = 'visible';
        this.tooltipElement.style.opacity = '1';
        this.updateTooltipPosition(event);
      }
    }
  }

  /**
   * Handle mouse out to hide tooltip
   */
  private handleCitationOut(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    
    if (target.classList.contains('citation-link')) {
      if (this.tooltipElement) {
        this.tooltipElement.style.opacity = '0';
        this.tooltipElement.style.visibility = 'hidden';
      }
    }
  }

  /**
   * Update tooltip position based on mouse movement
   */
  private handleMouseMove(event: MouseEvent): void {
    if (this.tooltipElement && this.tooltipElement.style.visibility === 'visible') {
      this.updateTooltipPosition(event);
    }
  }

  /**
   * Update tooltip position
   */
  private updateTooltipPosition(event: MouseEvent): void {
    if (!this.tooltipElement) return;

    const tooltip = this.tooltipElement;
    const mouseX = event.clientX;
    const mouseY = event.clientY;
    
    // Get viewport dimensions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Show tooltip temporarily to get dimensions
    tooltip.style.visibility = 'hidden';
    tooltip.style.opacity = '1';
    tooltip.style.left = '0px';
    tooltip.style.top = '0px';
    const rect = tooltip.getBoundingClientRect();
    
    // Calculate optimal position
    let left = mouseX + 15;
    let top = mouseY - rect.height - 10;
    
    // Adjust horizontal position if tooltip would go off right edge
    if (left + rect.width > viewportWidth - 10) {
      left = mouseX - rect.width - 15;
    }
    
    // Adjust horizontal position if tooltip would go off left edge
    if (left < 10) {
      left = 10;
    }
    
    // Adjust vertical position if tooltip would go off top edge
    if (top < 10) {
      top = mouseY + 25;
    }
    
    // Adjust vertical position if tooltip would go off bottom edge
    if (top + rect.height > viewportHeight - 10) {
      top = viewportHeight - rect.height - 10;
    }
    
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
    tooltip.style.visibility = 'visible';
  }

  /**
   * Scroll to reference in document
   */
  private scrollToReference(referenceId: string): void {
    const element = document.getElementById(referenceId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Highlight the reference briefly
      element.style.backgroundColor = '#fef3c7';
      setTimeout(() => {
        element.style.backgroundColor = '';
      }, 2000);
    }
  }

  /**
   * Generate references section HTML
   */
  generateReferencesHTML(citations: CitationData[]): string {
    if (!citations || citations.length === 0) return '';

    let referencesHTML = '<div class="references-section"><h2>References</h2>';
    
    citations.forEach(citation => {
      const chunk = citation.chunk_citation;
      let referenceText = '';

      // Build reference text
      if (chunk.authors && chunk.authors.length > 0) {
        referenceText += chunk.authors.join(', ') + '. ';
      }
      
      referenceText += `<em>${chunk.pdf_name}</em>`;
      
      if (chunk.section) {
        referenceText += `, ${chunk.section}`;
      }
      
      referenceText += `, p. ${chunk.page_number}`;
      
      if (chunk.external_link) {
        referenceText += `. <a href="${chunk.external_link}" target="_blank">Available online</a>`;
      }

      referencesHTML += `
        <div class="reference-item" id="${citation.reference_id}">
          ${citation.citation_number}. ${referenceText}
        </div>
      `;
    });

    referencesHTML += '</div>';
    return referencesHTML;
  }

  /**
   * Get CSS styles for citations
   */
  static getCSSStyles(): string {
    return `
      .citation-link {
        color: #2563eb;
        text-decoration: none;
        font-weight: 600;
        background: rgba(37, 99, 235, 0.1);
        padding: 2px 4px;
        border-radius: 4px;
        transition: all 0.2s ease;
        border: 1px solid rgba(37, 99, 235, 0.2);
        font-size: 0.85em;
        vertical-align: super;
        line-height: 1;
      }
      
      .citation-link:hover {
        color: #1d4ed8;
        background: rgba(29, 78, 216, 0.15);
        border-color: rgba(29, 78, 216, 0.3);
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
      }
      
      .citation-tooltip {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      .references-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 2px solid #e5e7eb;
      }
      
      .references-section h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1f2937;
      }
      
      .reference-item {
        margin-bottom: 0.75rem;
        padding: 0.5rem;
        padding-left: 1rem;
        text-indent: -1rem;
        line-height: 1.5;
        border-radius: 4px;
        transition: background-color 0.2s ease;
      }
      
      .reference-item:hover {
        background-color: #f9fafb;
      }
      
      .reference-item a {
        color: #2563eb;
        text-decoration: none;
      }
      
      .reference-item a:hover {
        text-decoration: underline;
      }
      
      .reference-item em {
        font-style: italic;
        font-weight: 500;
      }
    `;
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    if (this.tooltipElement) {
      document.body.removeChild(this.tooltipElement);
      this.tooltipElement = null;
    }
  }
}

// Global citation display instance to ensure single initialization
let globalCitationDisplay: CitationDisplay | null = null;

export const getGlobalCitationDisplay = (): CitationDisplay => {
  if (!globalCitationDisplay && typeof document !== 'undefined') {
    globalCitationDisplay = new CitationDisplay();
  }
  return globalCitationDisplay!;
};

// Auto-initialize when DOM is ready
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    // Add CSS styles only once
    const existingStyle = document.getElementById('citation-display-styles');
    if (!existingStyle) {
      const style = document.createElement('style');
      style.id = 'citation-display-styles';
      style.textContent = CitationDisplay.getCSSStyles();
      document.head.appendChild(style);
    }
    
    // Initialize global citation display
    const citationDisplay = getGlobalCitationDisplay();
    
    // Make it globally available for debugging
    (window as unknown as { citationDisplay: CitationDisplay }).citationDisplay = citationDisplay;
  });
}

export default CitationDisplay;
