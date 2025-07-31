import React, { useState } from 'react';
import { Download, FileText, FileSpreadsheet, File } from 'lucide-react';
import type { StoredDocument } from '../../services/storage';

interface ExportManagerProps {
  document: StoredDocument | null;
  onExport: (format: string) => void;
}

export const ExportManager: React.FC<ExportManagerProps> = ({ document, onExport }) => {
  const [exporting, setExporting] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState('pdf');

  const exportFormats = [
    { id: 'pdf', name: 'PDF Document', icon: FileText, description: 'Best for review and printing' },
    { id: 'docx', name: 'Word Document', icon: FileText, description: 'Editable document format' },
    { id: 'xlsx', name: 'Excel Spreadsheet', icon: FileSpreadsheet, description: 'For data and tables (coming soon)' },
    { id: 'json', name: 'JSON Data', icon: File, description: 'For system integration' }
  ];

  const handleExport = async () => {
    if (!document) {
      alert('No document selected for export');
      return;
    }

    setExporting(true);
    try {
      // Convert StoredDocument to the backend GeneratedDocument format
      const exportDocument = {
        title: document.title,
        session_id: document.docId,
        template_id: "default-template",
        generated_at: document.updatedAt,
        sections: document.sections.map(section => ({
          id: section.id,
          title: section.title,
          content: section.content,
          source_count: 0
        }))
      };

      const exportRequest = {
        format: selectedFormat,
        document: exportDocument
      };

      console.log('🚀 Exporting document:', exportRequest);

      const response = await fetch('/api/export/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(exportRequest)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Export failed: ${response.status} - ${errorText}`);
      }

      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const downloadLink = window.document.createElement('a');
      downloadLink.href = url;
      downloadLink.download = `${document.title.replace(/[^a-z0-9]/gi, '_')}.${selectedFormat}`;
      window.document.body.appendChild(downloadLink);
      downloadLink.click();
      window.URL.revokeObjectURL(url);
      window.document.body.removeChild(downloadLink);

      setExporting(false);
      console.log(`✅ Document exported successfully as ${selectedFormat.toUpperCase()}`);
      
      // Call the parent onExport callback
      onExport(selectedFormat);
    } catch (error) {
      setExporting(false);
      console.error('❌ Export failed:', error);
      alert(`Export failed: ${error}`);
    }
  };

  if (!document) {
    return (
      <div className="export-manager p-6 bg-white rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Export Document</h3>
        <div className="text-center py-8">
          <FileText size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 mb-2">No document selected for export</p>
          <p className="text-sm text-gray-400">
            Generate a document first to enable export functionality
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="export-manager p-6 bg-white rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Export Document</h3>
      
      <div className="mb-4 p-3 bg-gray-50 rounded">
        <p className="font-medium">{document.title}</p>
        <p className="text-sm text-gray-600">ID: {document.docId}</p>
        <p className="text-sm text-gray-600">
          {document.sections?.length || 0} sections, {document.citations?.length || 0} citations
        </p>
        <p className="text-sm text-gray-600">
          Status: <span className="capitalize">{document.status}</span>
        </p>
      </div>
      
      <div className="space-y-3 mb-6">
        {exportFormats.map(format => (
          <label
            key={format.id}
            className={`flex items-center p-3 border rounded cursor-pointer hover:bg-gray-50 transition-colors ${
              selectedFormat === format.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            } ${format.id === 'xlsx' ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input
              type="radio"
              name="format"
              value={format.id}
              checked={selectedFormat === format.id}
              onChange={(e) => setSelectedFormat(e.target.value)}
              disabled={format.id === 'xlsx'}
              className="mr-3"
            />
            <format.icon size={20} className="mr-3 text-gray-600" />
            <div className="flex-1">
              <p className="font-medium">{format.name}</p>
              <p className="text-sm text-gray-600">{format.description}</p>
            </div>
          </label>
        ))}
      </div>
      
      <button
        className="btn btn-primary w-full flex items-center justify-center gap-2"
        onClick={handleExport}
        disabled={exporting || selectedFormat === 'xlsx'}
      >
        {exporting ? (
          'Exporting...'
        ) : (
          <>
            <Download size={16} />
            Export as {selectedFormat.toUpperCase()}
          </>
        )}
      </button>
      
      {selectedFormat === 'xlsx' && (
        <p className="text-sm text-amber-600 mt-2 text-center">
          Excel export coming soon
        </p>
      )}
    </div>
  );
};
