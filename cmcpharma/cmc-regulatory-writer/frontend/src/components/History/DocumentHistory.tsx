import React, { useState, useEffect } from 'react';
import { Clock, FileText, Trash2, Eye, Download, CheckCircle, AlertCircle } from 'lucide-react';
import { storage, generateSampleData, type StoredDocument } from '../../services/storage';

export const DocumentHistory: React.FC = () => {
  const [documents, setDocuments] = useState<StoredDocument[]>([]);
  const [filter, setFilter] = useState<'all' | 'draft' | 'review' | 'approved'>('all');

  useEffect(() => {
    // Generate sample data if none exists
    generateSampleData();
    loadDocuments();
  }, []);

  const loadDocuments = () => {
    const docs = storage.getDocuments();
    setDocuments(docs.sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    ));
  };

  const handleDelete = (docId: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      storage.deleteDocument(docId);
      loadDocuments();
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'review':
        return <AlertCircle size={16} className="text-yellow-500" />;
      default:
        return <FileText size={16} className="text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const filteredDocs = documents.filter(doc => 
    filter === 'all' || doc.status === filter
  );

  return (
    <div className="document-history p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Document History</h2>
        
        <div className="flex gap-2">
          {['all', 'draft', 'review', 'approved'].map(status => (
            <button
              key={status}
              className={`px-4 py-2 rounded capitalize ${
                filter === status 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-700'
              }`}
              onClick={() => setFilter(status as 'all' | 'draft' | 'review' | 'approved')}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {filteredDocs.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <FileText size={48} className="mx-auto mb-4 opacity-50" />
          <p>No documents found</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredDocs.map(doc => (
            <div 
              key={doc.id} 
              className="bg-white border rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getStatusIcon(doc.status)}
                    <h3 className="font-semibold text-lg">{doc.title}</h3>
                    <span className="text-sm text-gray-500">ID: {doc.docId}</span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <Clock size={14} />
                      Updated: {formatDate(doc.updatedAt)}
                    </span>
                    <span className="capitalize px-2 py-1 bg-gray-100 rounded">
                      {doc.status}
                    </span>
                    <span>
                      {doc.sections?.length || 0} sections, {doc.citations?.length || 0} citations
                    </span>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button
                    className="p-2 hover:bg-gray-100 rounded"
                    title="View Document"
                    onClick={() => console.log('View:', doc.id)}
                  >
                    <Eye size={18} />
                  </button>
                  <button
                    className="p-2 hover:bg-gray-100 rounded"
                    title="Download"
                    onClick={() => console.log('Download:', doc.id)}
                  >
                    <Download size={18} />
                  </button>
                  <button
                    className="p-2 hover:bg-red-100 text-red-500 rounded"
                    title="Delete"
                    onClick={() => handleDelete(doc.id)}
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
