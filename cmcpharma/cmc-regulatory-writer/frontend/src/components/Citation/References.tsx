import React, { useState, useEffect, useCallback } from 'react';

interface Reference {
  citation_number: number;
  reference_id: string;
  formatted_reference: string;
  source_info: {
    pdf_name: string;
    page_number?: number;
    section?: string;
    authors?: string[];
    external_link?: string;
  };
}

interface ReferencesProps {
  documentId: string;
  className?: string;
}

export const References: React.FC<ReferencesProps> = ({ documentId, className = '' }) => {
  const [references, setReferences] = useState<Reference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadReferences = useCallback(async () => {
    if (!documentId) return;
    
    try {
      setLoading(true);
      console.log('🔗 Loading references for document:', documentId);
      
      // First try to get structured references, fallback to basic references
      const apiUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/citations/documents/${documentId}/references`;
      console.log('🔗 Fetching from URL:', apiUrl);
      
      const response = await fetch(apiUrl);
      console.log('🔗 References API response status:', response.status);
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log('🔗 No references found for document');
          setReferences([]);
          setError(null);
          return;
        }
        throw new Error(`Failed to load references: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('🔗 References data received:', data);
      
      // Check if we have structured references or need to parse from markdown
      if (data.references && Array.isArray(data.references)) {
        console.log('🔗 Using structured references:', data.references.length);
        setReferences(data.references);
      } else if (data.references_markdown) {
        console.log('🔗 Parsing markdown references');
        // Parse markdown references into structured format
        const markdownRefs = data.references_markdown;
        const parsedRefs = parseMarkdownReferences(markdownRefs);
        setReferences(parsedRefs);
      } else {
        console.log('🔗 No references data found');
        setReferences([]);
      }
      
      setError(null);
    } catch (err) {
      console.error('🔗 Error loading references:', err);
      setError(err instanceof Error ? err.message : 'Failed to load references');
      setReferences([]);
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  // Helper function to parse markdown references into structured format
  const parseMarkdownReferences = (markdown: string): Reference[] => {
    const references: Reference[] = [];
    const lines = markdown.split('\n');
    
    lines.forEach((line) => {
      // Match pattern like "[1] Author. Title. Source, p. 123"
      const match = line.match(/^\[(\d+)\]\s*(.+)$/);
      if (match) {
        const [, number, content] = match;
        const citationNumber = parseInt(number);
        
        // Basic parsing of reference content
        const parts = content.split(', p. ');
        const mainContent = parts[0];
        const pageNumber = parts[1] ? parseInt(parts[1]) : undefined;
        
        // Extract PDF name (last part before page)
        const contentParts = mainContent.split('. ');
        const pdfName = contentParts[contentParts.length - 1] || 'Unknown Source';
        
        references.push({
          citation_number: citationNumber,
          reference_id: `ref-${citationNumber}`,
          formatted_reference: content,
          source_info: {
            pdf_name: pdfName,
            page_number: pageNumber,
            section: undefined,
            authors: contentParts.length > 1 ? [contentParts[0]] : undefined,
            external_link: undefined
          }
        });
      }
    });
    
    return references;
  };

  useEffect(() => {
    loadReferences();
  }, [loadReferences]);

  if (loading) {
    return (
      <div className={`${className}`}>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading references...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-red-800 mb-2">Error Loading References</h3>
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadReferences}
            className="mt-2 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 rounded-md transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (references.length === 0) {
    return (
      <div className={`${className}`}>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <h3 className="text-lg font-medium text-gray-800 mb-2">No References</h3>
          <p className="text-gray-600">No citations have been added to this document yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="border-b border-gray-200 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">References</h2>
          <p className="text-sm text-gray-600 mt-1">
            {references.length} reference{references.length !== 1 ? 's' : ''} cited in this document
          </p>
        </div>
        
        <div className="p-6">
          <div className="space-y-4">
            {references.map((reference) => (
              <div 
                key={reference.reference_id}
                className="border-l-4 border-blue-200 pl-4 py-2 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium">
                    {reference.citation_number}
                  </span>
                  <div className="flex-1">
                    <p className="text-gray-900 leading-relaxed">
                      {reference.formatted_reference}
                    </p>
                    <div className="mt-2 text-xs text-gray-500">
                      <span className="font-medium">Source:</span> {reference.source_info.pdf_name}
                      {reference.source_info.page_number && (
                        <span>, Page {reference.source_info.page_number}</span>
                      )}
                      {reference.source_info.section && (
                        <span>, Section: {reference.source_info.section}</span>
                      )}
                    </div>
                    {reference.source_info.authors && reference.source_info.authors.length > 0 && (
                      <div className="mt-1 text-xs text-gray-500">
                        <span className="font-medium">Authors:</span> {reference.source_info.authors.join(', ')}
                      </div>
                    )}
                    {reference.source_info.external_link && (
                      <div className="mt-2">
                        <a 
                          href={reference.source_info.external_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-xs underline"
                        >
                          View Source
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default References;
