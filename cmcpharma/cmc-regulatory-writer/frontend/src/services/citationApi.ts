/**
 * Citation API Service for communicating with backend
 */

export interface Citation {
  id: number;
  text: string;
  source: string;
  page: number;
  source_file_id?: string;
  url?: string;
  doi?: string;
  authors?: string[];
  publication_date?: string;
  journal?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  isbn?: string;
  publisher?: string;
  citation_style?: string;
  tags?: string[];
  notes?: string;
  created_at: string;
  last_modified: string;
}

export interface CitationCreate {
  text: string;
  source: string;
  page: number;
  source_file_id?: string;
  url?: string;
  doi?: string;
  authors?: string[];
  publication_date?: string;
  journal?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  isbn?: string;
  publisher?: string;
  citation_style?: string;
  tags?: string[];
  notes?: string;
}

export interface CitationSearch {
  query: string;
  authors?: string[];
  journal?: string;
  date_from?: string;
  date_to?: string;
  tags?: string[];
  citation_style?: string;
}

export interface CitationStyle {
  code: string;
  name: string;
  description: string;
}

export interface DocumentCitations {
  document_id: string;
  session_id: string;
  citations: Citation[];
  citation_count: number;
  citation_style: string;
  auto_generate_references: boolean;
}

class CitationApiService {
  private baseURL = '/api/citations';

  /**
   * Get all citations with pagination
   */
  async getCitations(skip: number = 0, limit: number = 100): Promise<Citation[]> {
    const response = await fetch(`${this.baseURL}?skip=${skip}&limit=${limit}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch citations: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get a specific citation by ID
   */
  async getCitation(id: number): Promise<Citation> {
    const response = await fetch(`${this.baseURL}/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch citation: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Create a new citation
   */
  async createCitation(citation: CitationCreate): Promise<Citation> {
    const response = await fetch(this.baseURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(citation),
    });
    if (!response.ok) {
      throw new Error(`Failed to create citation: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Update an existing citation
   */
  async updateCitation(id: number, citation: Partial<CitationCreate>): Promise<Citation> {
    const response = await fetch(`${this.baseURL}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(citation),
    });
    if (!response.ok) {
      throw new Error(`Failed to update citation: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Delete a citation
   */
  async deleteCitation(id: number): Promise<void> {
    const response = await fetch(`${this.baseURL}/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete citation: ${response.statusText}`);
    }
  }

  /**
   * Search citations
   */
  async searchCitations(searchQuery: CitationSearch): Promise<Citation[]> {
    const response = await fetch(`${this.baseURL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchQuery),
    });
    if (!response.ok) {
      throw new Error(`Failed to search citations: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Extract citations from text
   */
  async extractCitations(text: string, sourceFileId?: string): Promise<{ citations: Citation[] }> {
    const params = new URLSearchParams({ text });
    if (sourceFileId) {
      params.append('source_file_id', sourceFileId);
    }

    const response = await fetch(`${this.baseURL}/extract?${params}`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to extract citations: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Format a citation in a specific style
   */
  async formatCitation(citationId: number, style: string = 'APA'): Promise<{ formatted_citation: string }> {
    const params = new URLSearchParams({
      citation_id: citationId.toString(),
      style,
    });

    const response = await fetch(`${this.baseURL}/format?${params}`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to format citation: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get available citation styles
   */
  async getCitationStyles(): Promise<{ styles: CitationStyle[] }> {
    const response = await fetch(`${this.baseURL}/styles/available`);
    if (!response.ok) {
      throw new Error(`Failed to fetch citation styles: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Import citations from external format
   */
  async importCitations(data: string, format: string = 'bibtex'): Promise<{ imported_count: number; citations: Citation[] }> {
    const params = new URLSearchParams({
      import_data: data,
      format,
    });

    const response = await fetch(`${this.baseURL}/import?${params}`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to import citations: ${response.statusText}`);
    }
    return response.json();
  }

  // Document-level citation tracking methods

  /**
   * Get citations for a specific document
   */
  async getDocumentCitations(documentId: string): Promise<DocumentCitations> {
    const response = await fetch(`${this.baseURL}/documents/${documentId}`);
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Document citations not found');
      }
      throw new Error(`Failed to fetch document citations: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get citation statistics for a document
   */
  async getCitationStatistics(documentId: string): Promise<{
    total_citations: number;
    unique_sources: number;
    citation_style: string;
    sources: string[];
    auto_references_enabled: boolean;
  }> {
    const response = await fetch(`${this.baseURL}/documents/${documentId}/statistics`);
    if (!response.ok) {
      throw new Error(`Failed to fetch citation statistics: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get references section for a document
   */
  async getReferencesSection(documentId: string): Promise<{ document_id: string; references_markdown: string; references_html: string }> {
    const response = await fetch(`${this.baseURL}/documents/${documentId}/references`);
    if (!response.ok) {
      throw new Error(`Failed to fetch references section: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Export citations for a document
   */
  async exportDocumentCitations(documentId: string, format: string = 'json'): Promise<{
    document_id: string;
    format: string;
    data: string;
    content_type: string;
  }> {
    const response = await fetch(`${this.baseURL}/documents/${documentId}/export?format=${format}`);
    if (!response.ok) {
      throw new Error(`Failed to export citations: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Update citation configuration
   */
  async updateCitationConfig(config: {
    citation_style?: string;
    auto_generate_references?: boolean;
    show_inline_citations?: boolean;
    enable_hover_tooltips?: boolean;
  }): Promise<{
    message: string;
    config: typeof config;
  }> {
    const response = await fetch(`${this.baseURL}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    if (!response.ok) {
      throw new Error(`Failed to update citation config: ${response.statusText}`);
    }
    return response.json();
  }
}

// Export a singleton instance
export const citationApiService = new CitationApiService();
export default citationApiService;
