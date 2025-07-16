import React, { createContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
  category: 'specification' | 'protocol' | 'report' | 'certificate' | 'other';
  status: 'uploaded' | 'processing' | 'ready' | 'error';
}

export interface FileContextType {
  files: UploadedFile[];
  addFiles: (newFiles: File[]) => void;
  removeFile: (fileId: string) => void;
  removeFiles: (fileIds: string[]) => void;
  updateFileStatus: (fileId: string, status: UploadedFile['status']) => void;
  updateFileCategory: (fileId: string, category: UploadedFile['category']) => void;
  getFilesByCategory: (category: string) => UploadedFile[];
  getTotalSize: () => number;
  getReadyFilesCount: () => number;
}

export const FileContext = createContext<FileContextType | undefined>(undefined);



interface FileProviderProps {
  children: ReactNode;
}

export const FileProvider: React.FC<FileProviderProps> = ({ children }) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const getFileTypeFromExtension = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf': return 'application/pdf';
      case 'docx': return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      case 'doc': return 'application/msword';
      case 'xlsx': return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      case 'xls': return 'application/vnd.ms-excel';
      default: return 'application/octet-stream';
    }
  };

  const guessCategory = (filename: string): UploadedFile['category'] => {
    const name = filename.toLowerCase();
    if (name.includes('spec') || name.includes('specification')) return 'specification';
    if (name.includes('protocol') || name.includes('method')) return 'protocol';
    if (name.includes('report') || name.includes('result')) return 'report';
    if (name.includes('cert') || name.includes('certificate')) return 'certificate';
    return 'other';
  };

  const addFiles = useCallback((newFiles: File[]) => {
    const uploadedFiles: UploadedFile[] = newFiles.map(file => ({
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type || getFileTypeFromExtension(file.name),
      uploadedAt: new Date(),
      category: guessCategory(file.name),
      status: 'uploaded'
    }));
    
    setFiles(prev => [...prev, ...uploadedFiles]);
    
    // Simulate processing
    uploadedFiles.forEach(file => {
      setTimeout(() => {
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'processing' } : f
        ));
        
        setTimeout(() => {
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, status: 'ready' } : f
          ));
        }, 1500);
      }, 500);
    });
  }, []);

  const removeFile = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  }, []);

  const removeFiles = useCallback((fileIds: string[]) => {
    setFiles(prev => prev.filter(f => !fileIds.includes(f.id)));
  }, []);

  const updateFileStatus = useCallback((fileId: string, status: UploadedFile['status']) => {
    setFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, status } : f
    ));
  }, []);

  const updateFileCategory = useCallback((fileId: string, category: UploadedFile['category']) => {
    setFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, category } : f
    ));
  }, []);

  const getFilesByCategory = useCallback((category: string) => {
    if (category === 'all') return files;
    return files.filter(f => f.category === category);
  }, [files]);

  const getTotalSize = useCallback(() => {
    return files.reduce((total, file) => total + file.size, 0);
  }, [files]);

  const getReadyFilesCount = useCallback(() => {
    return files.filter(f => f.status === 'ready').length;
  }, [files]);

  const contextValue: FileContextType = {
    files,
    addFiles,
    removeFile,
    removeFiles,
    updateFileStatus,
    updateFileCategory,
    getFilesByCategory,
    getTotalSize,
    getReadyFilesCount
  };

  return (
    <FileContext.Provider value={contextValue}>
      {children}
    </FileContext.Provider>
  );
};
