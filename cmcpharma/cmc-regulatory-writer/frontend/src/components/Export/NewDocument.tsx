import React, { useState } from 'react';
import { Plus, FileText, X } from 'lucide-react';
import { storage, type StoredDocument } from '../../services/storage';
import { useFiles } from '../../contexts/useFiles';

interface NewDocumentProps {
  onDocumentCreated: (document: StoredDocument) => void;
  onCancel: () => void;
}

export const NewDocument: React.FC<NewDocumentProps> = ({ onDocumentCreated, onCancel }) => {
  const { files } = useFiles();
  const [formData, setFormData] = useState({
    title: '',
    drugName: '',
    documentType: 'drug-substance',
    description: ''
  });

  const documentTypes = [
    { id: 'drug-substance', name: 'Drug Substance (3.2.S)', description: 'Information about the drug substance' },
    { id: 'drug-product', name: 'Drug Product (3.2.P)', description: 'Information about the drug product' },
    { id: 'excipients', name: 'Excipients (3.2.A)', description: 'Information about excipients' },
    { id: 'container-closure', name: 'Container Closure', description: 'Container closure system information' },
    { id: 'stability', name: 'Stability Studies', description: 'Stability data and studies' }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.drugName.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    const newDocument: StoredDocument = {
      id: `doc-${Date.now()}`,
      title: formData.title,
      docId: `${formData.drugName.toUpperCase()}-${Date.now()}`,
      sections: [],
      citations: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      status: 'draft'
    };

    storage.saveDocument(newDocument);
    onDocumentCreated(newDocument);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="new-document-modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold">Create New Document</h2>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-gray-100 rounded"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Drug Substance Specification"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Drug Name *
            </label>
            <input
              type="text"
              value={formData.drugName}
              onChange={(e) => handleInputChange('drugName', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Compound-XYZ"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document Type
            </label>
            <div className="space-y-2">
              {documentTypes.map(type => (
                <label
                  key={type.id}
                  className={`flex items-start p-3 border rounded cursor-pointer hover:bg-gray-50 transition-colors ${
                    formData.documentType === type.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  <input
                    type="radio"
                    name="documentType"
                    value={type.id}
                    checked={formData.documentType === type.id}
                    onChange={(e) => handleInputChange('documentType', e.target.value)}
                    className="mt-1 mr-3"
                  />
                  <div>
                    <p className="font-medium">{type.name}</p>
                    <p className="text-sm text-gray-600">{type.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Brief description of the document..."
            />
          </div>

          {files.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Available Files ({files.length})
              </label>
              <div className="max-h-32 overflow-y-auto border border-gray-200 rounded p-3 bg-gray-50">
                {files.map(file => (
                  <div key={file.id} className="flex items-center gap-2 text-sm py-1">
                    <FileText size={14} />
                    <span className="truncate">{file.name}</span>
                    <span className="text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
                  </div>
                ))}
              </div>
              <p className="text-sm text-gray-600 mt-1">
                These files will be available for reference in your new document.
              </p>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
            >
              <Plus size={16} />
              Create Document
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
