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
    { id: 'xlsx', name: 'Excel Spreadsheet', icon: FileSpreadsheet, description: 'For data and tables' },
    { id: 'json', name: 'JSON Data', icon: File, description: 'For system integration' }
  ];

  const handleExport = async () => {
    setExporting(true);
    try {
      await onExport(selectedFormat);
      // Simulate export delay
      setTimeout(() => {
        setExporting(false);
        alert(`Document exported as ${selectedFormat.toUpperCase()}`);
      }, 2000);
    } catch (error) {
      setExporting(false);
      alert('Export failed: ' + error);
    }
  };

  if (!document) {
    return (
      <div className="export-manager p-6 bg-white rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Export Document</h3>
        <p className="text-gray-500">No document selected for export.</p>
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
      </div>
      
      <div className="space-y-3 mb-6">
        {exportFormats.map(format => (
          <label
            key={format.id}
            className={`flex items-center p-3 border rounded cursor-pointer hover:bg-gray-50 transition-colors ${
              selectedFormat === format.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}
          >
            <input
              type="radio"
              name="format"
              value={format.id}
              checked={selectedFormat === format.id}
              onChange={(e) => setSelectedFormat(e.target.value)}
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
        disabled={exporting}
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
    </div>
  );
};
