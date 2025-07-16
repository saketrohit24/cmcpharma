// Example usage of FileManager component
import React, { useState } from 'react';
import { FileManager } from './FileManager';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  uploadedAt: Date;
}

export const FileManagerExample: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const handleFilesChange = (updatedFiles: UploadedFile[]) => {
    setFiles(updatedFiles);
    
    // You could also:
    // - Save to localStorage
    // - Send to an API
    // - Update global state (Redux, Zustand, etc.)
    // - Trigger file processing
    
    console.log(`Total files: ${updatedFiles.length}`);
    updatedFiles.forEach(file => {
      console.log(`- ${file.name} (${formatFileSize(file.size)})`);
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getTotalSize = () => {
    return files.reduce((total, file) => total + file.size, 0);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">File Management Demo</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <FileManager onFilesChange={handleFilesChange} />
        </div>
        
        <div className="bg-white p-4 rounded-lg border">
          <h3 className="text-lg font-semibold mb-3">File Statistics</h3>
          <div className="space-y-2">
            <p><strong>Total Files:</strong> {files.length}</p>
            <p><strong>Total Size:</strong> {formatFileSize(getTotalSize())}</p>
            <p><strong>Accepted Types:</strong> PDF, DOCX, DOC</p>
          </div>
          
          {files.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Recent Files:</h4>
              <ul className="text-sm space-y-1">
                {files.slice(-3).map(file => (
                  <li key={file.id} className="text-gray-600">
                    {file.name} - {formatFileSize(file.size)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
