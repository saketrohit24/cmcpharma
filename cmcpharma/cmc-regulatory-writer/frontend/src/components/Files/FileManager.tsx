import React, { useState } from 'react';
import { Upload, File, X } from 'lucide-react';
import { useFiles } from '../../contexts/useFiles';

export const FileManager: React.FC = () => {
  const { files, addFiles, removeFile } = useFiles();
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const handleFiles = (fileList: File[]) => {
    addFiles(fileList);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="file-manager p-4">
      <h3 className="text-lg font-semibold mb-4">Vendor Documents</h3>
      
      <div
        className={`upload-zone border-2 border-dashed rounded-lg p-8 text-center ${
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        }`}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
      >
        <Upload size={48} className="mx-auto mb-4 text-gray-400" />
        <p className="text-gray-600 mb-2">Drag and drop files here, or</p>
        <label className="btn btn-primary cursor-pointer">
          Browse Files
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.doc"
            className="hidden"
            onChange={(e) => handleFiles(Array.from(e.target.files || []))}
          />
        </label>
      </div>
      
      {files.length > 0 && (
        <div className="file-list mt-6">
          <h4 className="font-medium mb-3">Uploaded Files ({files.length})</h4>
          {files.slice(0, 5).map(file => ( // Show only first 5 files in sidebar
            <div key={file.id} className="file-item flex items-center justify-between p-3 border rounded mb-2">
              <div className="flex items-center gap-3">
                <File size={20} className="text-gray-500" />
                <div>
                  <p className="font-medium text-sm truncate max-w-[150px]">{file.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                </div>
              </div>
              <button
                onClick={() => removeFile(file.id)}
                className="text-red-500 hover:text-red-700"
              >
                <X size={18} />
              </button>
            </div>
          ))}
          {files.length > 5 && (
            <p className="text-sm text-gray-500 text-center mt-2">
              +{files.length - 5} more files...
            </p>
          )}
        </div>
      )}
    </div>
  );
};
