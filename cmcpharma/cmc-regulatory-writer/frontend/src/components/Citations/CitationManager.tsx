import React, { useState, useEffect } from 'react';
import { citationApiService, type Citation, type CitationCreate } from '../../services/citationApi';
import { CitationDisplay } from '../../services/citationDisplay';

interface CitationManagerProps {
  className?: string;
}

export const CitationManager: React.FC<CitationManagerProps> = ({ className = '' }) => {
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [citationStats, setCitationStats] = useState<{
    total_citations: number;
    unique_sources: number;
    citation_style: string;
    sources: string[];
    auto_references_enabled: boolean;
  } | null>(null);

  // Initialize citation display
  useEffect(() => {
    const citationDisplay = new CitationDisplay();
    return () => {
      citationDisplay.destroy();
    };
  }, []);

  // Load citations on component mount
  useEffect(() => {
    loadCitations();
  }, []);

  const loadCitations = async () => {
    try {
      setLoading(true);
      const data = await citationApiService.getCitations();
      setCitations(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load citations');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCitation = async (citationData: CitationCreate) => {
    try {
      const newCitation = await citationApiService.createCitation(citationData);
      setCitations([...citations, newCitation]);
      setShowCreateForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create citation');
    }
  };

  const handleDeleteCitation = async (id: number) => {
    try {
      await citationApiService.deleteCitation(id);
      setCitations(citations.filter(c => c.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete citation');
    }
  };

  const handleSearchCitations = async () => {
    if (!searchQuery.trim()) {
      loadCitations();
      return;
    }

    try {
      const results = await citationApiService.searchCitations({
        query: searchQuery
      });
      setCitations(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search citations');
    }
  };

  const loadDocumentStats = async (documentId: string) => {
    try {
      const stats = await citationApiService.getCitationStatistics(documentId);
      setCitationStats(stats);
    } catch {
      console.log('No stats available for document:', documentId);
    }
  };

  if (loading) {
    return (
      <div className={`p-6 ${className}`}>
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-lg">Loading citations...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-6 ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Citation Manager</h2>
        <p className="text-gray-600">Manage citations and test the citation tracker functionality</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Search Bar */}
      <div className="mb-6 flex gap-4">
        <input
          type="text"
          placeholder="Search citations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          onKeyDown={(e) => e.key === 'Enter' && handleSearchCitations()}
        />
        <button
          onClick={handleSearchCitations}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          Add Citation
        </button>
      </div>

      {/* Create Citation Form */}
      {showCreateForm && <CreateCitationForm onSubmit={handleCreateCitation} onCancel={() => setShowCreateForm(false)} />}

      {/* Citation Statistics */}
      {citationStats && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h3 className="font-semibold mb-2">Document Citation Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>Total: {citationStats.total_citations}</div>
            <div>Sources: {citationStats.unique_sources}</div>
            <div>Style: {citationStats.citation_style}</div>
            <div>Auto-refs: {citationStats.auto_references_enabled ? 'Yes' : 'No'}</div>
          </div>
        </div>
      )}

      {/* Citations List */}
      <div className="space-y-4">
        {citations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No citations found. Create your first citation to get started.
          </div>
        ) : (
          citations.map((citation) => (
            <CitationCard
              key={citation.id}
              citation={citation}
              onSelect={() => setSelectedCitation(citation)}
              onDelete={() => handleDeleteCitation(citation.id)}
              isSelected={selectedCitation?.id === citation.id}
            />
          ))
        )}
      </div>

      {/* Test Citation Tracker */}
      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Test Citation Tracker</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => loadDocumentStats('test-document-1')}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
          >
            Load Test Document Stats
          </button>
          <button
            onClick={async () => {
              try {
                const styles = await citationApiService.getCitationStyles();
                alert(`Available styles: ${styles.styles.map(s => s.code).join(', ')}`);
              } catch {
                alert('Failed to load citation styles');
              }
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          >
            Show Citation Styles
          </button>
        </div>
      </div>

      {/* Selected Citation Details */}
      {selectedCitation && (
        <CitationDetails
          citation={selectedCitation}
          onClose={() => setSelectedCitation(null)}
        />
      )}
    </div>
  );
};

// Citation Card Component
interface CitationCardProps {
  citation: Citation;
  onSelect: () => void;
  onDelete: () => void;
  isSelected: boolean;
}

const CitationCard: React.FC<CitationCardProps> = ({ citation, onSelect, onDelete, isSelected }) => (
  <div
    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
      isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
    }`}
    onClick={onSelect}
  >
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <h4 className="font-semibold text-gray-900">{citation.source}</h4>
        <p className="text-gray-600 mt-1">{citation.text}</p>
        <div className="mt-2 flex flex-wrap gap-2 text-sm text-gray-500">
          <span>Page {citation.page}</span>
          {citation.authors && <span>• {citation.authors.join(', ')}</span>}
          {citation.citation_style && <span>• {citation.citation_style}</span>}
        </div>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="ml-4 text-red-600 hover:text-red-700 transition-colors"
      >
        Delete
      </button>
    </div>
  </div>
);

// Create Citation Form Component
interface CreateCitationFormProps {
  onSubmit: (citation: CitationCreate) => void;
  onCancel: () => void;
}

const CreateCitationForm: React.FC<CreateCitationFormProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<CitationCreate>({
    text: '',
    source: '',
    page: 1,
    citation_style: 'APA'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6 p-4 border border-gray-300 rounded-md bg-gray-50">
      <h3 className="text-lg font-semibold mb-4">Create New Citation</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <input
          type="text"
          placeholder="Citation text"
          value={formData.text}
          onChange={(e) => setFormData({ ...formData, text: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <input
          type="text"
          placeholder="Source"
          value={formData.source}
          onChange={(e) => setFormData({ ...formData, source: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <input
          type="number"
          placeholder="Page"
          value={formData.page}
          onChange={(e) => setFormData({ ...formData, page: parseInt(e.target.value) })}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          min="1"
          required
        />
        <select
          value={formData.citation_style}
          onChange={(e) => setFormData({ ...formData, citation_style: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="APA">APA</option>
          <option value="MLA">MLA</option>
          <option value="Chicago">Chicago</option>
          <option value="IEEE">IEEE</option>
        </select>
      </div>
      <div className="mt-4 flex gap-2">
        <button
          type="submit"
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          Create Citation
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

// Citation Details Component
interface CitationDetailsProps {
  citation: Citation;
  onClose: () => void;
}

const CitationDetails: React.FC<CitationDetailsProps> = ({ citation, onClose }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white p-6 rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold">Citation Details</h3>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-xl">
          ×
        </button>
      </div>
      <div className="space-y-3">
        <div><strong>Source:</strong> {citation.source}</div>
        <div><strong>Text:</strong> {citation.text}</div>
        <div><strong>Page:</strong> {citation.page}</div>
        {citation.authors && <div><strong>Authors:</strong> {citation.authors.join(', ')}</div>}
        {citation.journal && <div><strong>Journal:</strong> {citation.journal}</div>}
        {citation.doi && <div><strong>DOI:</strong> {citation.doi}</div>}
        {citation.url && <div><strong>URL:</strong> <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{citation.url}</a></div>}
        <div><strong>Style:</strong> {citation.citation_style}</div>
        <div><strong>Created:</strong> {new Date(citation.created_at).toLocaleDateString()}</div>
      </div>
    </div>
  </div>
);
