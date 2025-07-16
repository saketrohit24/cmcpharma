import React, { useState, useRef } from 'react';
import { Upload, File, X, Search, Filter, Download, Eye, Trash2, Plus, FolderOpen } from 'lucide-react';
import { useFiles } from '../../contexts/useFiles';
import type { UploadedFile } from '../../contexts/FileContext';

interface FileCategory {
  id: string;
  name: string;
  count: number;
  color: string;
}

export const FileManagerPage: React.FC = () => {
  const { files, addFiles, removeFile, removeFiles, getTotalSize, getReadyFilesCount } = useFiles();
  const [isDragging, setIsDragging] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const fileInputRef = useRef<HTMLInputElement>(null);

  const categories: FileCategory[] = [
    { id: 'all', name: 'All Files', count: files.length, color: 'bg-gray-100' },
    { id: 'specification', name: 'Specifications', count: files.filter(f => f.category === 'specification').length, color: 'bg-blue-100' },
    { id: 'protocol', name: 'Protocols', count: files.filter(f => f.category === 'protocol').length, color: 'bg-green-100' },
    { id: 'report', name: 'Reports', count: files.filter(f => f.category === 'report').length, color: 'bg-yellow-100' },
    { id: 'certificate', name: 'Certificates', count: files.filter(f => f.category === 'certificate').length, color: 'bg-purple-100' },
    { id: 'other', name: 'Other', count: files.filter(f => f.category === 'other').length, color: 'bg-gray-100' },
  ];

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const handleFiles = (fileList: File[]) => {
    addFiles(fileList);
  };

  const removeSelectedFiles = () => {
    removeFiles(Array.from(selectedFiles));
    setSelectedFiles(new Set());
  };

  const toggleFileSelection = (fileId: string) => {
    setSelectedFiles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fileId)) {
        newSet.delete(fileId);
      } else {
        newSet.add(fileId);
      }
      return newSet;
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('word') || type.includes('doc')) return '📝';
    if (type.includes('excel') || type.includes('sheet')) return '📊';
    return '📄';
  };

  const getStatusBadge = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploaded':
        return <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">Uploaded</span>;
      case 'processing':
        return <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">Processing</span>;
      case 'ready':
        return <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Ready</span>;
      case 'error':
        return <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">Error</span>;
      default:
        return null;
    }
  };

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || file.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="file-manager-page min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Document Manager</h1>
              <p className="text-gray-600 mt-1">Upload and manage your regulatory documents</p>
            </div>
            <div className="flex gap-3">
              {selectedFiles.size > 0 && (
                <button
                  onClick={removeSelectedFiles}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  <Trash2 size={16} />
                  Delete Selected ({selectedFiles.size})
                </button>
              )}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus size={16} />
                Upload Files
              </button>
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-3">
                <FolderOpen className="text-blue-500" size={24} />
                <div>
                  <p className="text-sm text-gray-600">Total Files</p>
                  <p className="text-2xl font-semibold">{files.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-3">
                <Upload className="text-green-500" size={24} />
                <div>
                  <p className="text-sm text-gray-600">Total Size</p>
                  <p className="text-2xl font-semibold">
                    {formatFileSize(getTotalSize())}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-3">
                <File className="text-purple-500" size={24} />
                <div>
                  <p className="text-sm text-gray-600">Ready Files</p>
                  <p className="text-2xl font-semibold">{getReadyFilesCount()}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-3">
                <Filter className="text-orange-500" size={24} />
                <div>
                  <p className="text-sm text-gray-600">Categories</p>
                  <p className="text-2xl font-semibold">{categories.filter(c => c.count > 0 && c.id !== 'all').length}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Search and Filter */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex gap-2 overflow-x-auto">
              {categories.map(category => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-blue-100 text-blue-700 border border-blue-200'
                      : 'bg-white border border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className={`w-3 h-3 rounded-full ${category.color}`}></div>
                  {category.name} ({category.count})
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Upload Zone */}
        <div
          className={`upload-zone border-2 border-dashed rounded-lg p-12 text-center mb-8 transition-all ${
            isDragging 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50'
          }`}
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
        >
          <Upload size={64} className="mx-auto mb-4 text-gray-400" />
          <h3 className="text-xl font-semibold mb-2">Drop files here to upload</h3>
          <p className="text-gray-600 mb-4">Or click to browse and select files</p>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn btn-primary"
          >
            Browse Files
          </button>
          <p className="text-sm text-gray-500 mt-2">Supports PDF, DOCX, DOC, XLSX, XLS files</p>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.xlsx,.xls"
            className="hidden"
            onChange={(e) => handleFiles(Array.from(e.target.files || []))}
          />
        </div>

        {/* File List */}
        {filteredFiles.length > 0 ? (
          <div className="bg-white rounded-lg border overflow-hidden">
            <div className="p-4 border-b bg-gray-50">
              <h3 className="font-semibold">
                Files ({filteredFiles.length})
                {selectedFiles.size > 0 && ` - ${selectedFiles.size} selected`}
              </h3>
            </div>
            <div className="divide-y">
              {filteredFiles.map(file => (
                <div
                  key={file.id}
                  className={`p-4 hover:bg-gray-50 transition-colors ${
                    selectedFiles.has(file.id) ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <input
                        type="checkbox"
                        checked={selectedFiles.has(file.id)}
                        onChange={() => toggleFileSelection(file.id)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <div className="text-2xl">{getFileIcon(file.type)}</div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 truncate">{file.name}</h4>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>{formatFileSize(file.size)}</span>
                          <span className="capitalize">{file.category}</span>
                          <span>{file.uploadedAt.toLocaleDateString()}</span>
                          {getStatusBadge(file.status)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
                        title="Preview"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded"
                        title="Download"
                      >
                        <Download size={16} />
                      </button>
                      <button
                        onClick={() => {
                          removeFile(file.id);
                          setSelectedFiles(prev => {
                            const newSet = new Set(prev);
                            newSet.delete(file.id);
                            return newSet;
                          });
                        }}
                        className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <FolderOpen size={64} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No files found</h3>
            <p className="text-gray-500">
              {searchTerm || selectedCategory !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Upload some files to get started'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
