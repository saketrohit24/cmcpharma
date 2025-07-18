import React, { createContext, useState, useCallback, useEffect } from 'react';
import type { ReactNode } from 'react';
import { backendApi } from '../services/backendApi';

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
  category: 'specification' | 'protocol' | 'report' | 'certificate' | 'other';
  status: 'uploaded' | 'processing' | 'ready' | 'error';
  backendPath?: string; // Path on backend for the uploaded file
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

  // Load files from localStorage on component mount
  useEffect(() => {
    const loadPersistedFiles = () => {
      try {
        const savedFiles = localStorage.getItem('cmc_uploaded_files');
        if (savedFiles) {
          const parsedFiles = JSON.parse(savedFiles);
          // Convert uploadedAt back to Date objects
          const restoredFiles = parsedFiles.map((file: UploadedFile & { uploadedAt: string }) => ({
            ...file,
            uploadedAt: new Date(file.uploadedAt)
          }));
          setFiles(restoredFiles);
          console.log('📁 Restored', restoredFiles.length, 'files from localStorage');
        }
      } catch (error) {
        console.error('Failed to load persisted files:', error);
      }
    };

    loadPersistedFiles();
  }, []);

  // Save files to localStorage whenever files change
  useEffect(() => {
    try {
      localStorage.setItem('cmc_uploaded_files', JSON.stringify(files));
      console.log('📁 Saved', files.length, 'files to localStorage');
    } catch (error) {
      console.error('Failed to save files to localStorage:', error);
    }
  }, [files]);

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

  const addFiles = useCallback(async (newFiles: File[]) => {
    // Create local file entries immediately for UI feedback
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
    
    console.log('FileContext: Starting file upload with session ID:', backendApi.getSessionId());
    
    // Upload files to backend asynchronously
    for (const [index, file] of newFiles.entries()) {
      const localFile = uploadedFiles[index];
      
      try {
        // Update status to processing
        setFiles(prev => prev.map(f => 
          f.id === localFile.id ? { ...f, status: 'processing' } : f
        ));
        
        console.log(`FileContext: Uploading file ${file.name} to session ${backendApi.getSessionId()}`);
        
        // Upload to backend
        const response = await backendApi.uploadFile(file);
        
        if (response.status === 200 && response.data) {
          console.log(`FileContext: Successfully uploaded ${file.name}`, response.data);
          // Update status to ready and store backend path
          setFiles(prev => prev.map(f => 
            f.id === localFile.id ? { 
              ...f, 
              status: 'ready',
              backendPath: response.data?.path 
            } : f
          ));
        } else {
          console.error(`FileContext: Upload failed for ${file.name}:`, response.error);
          // Handle upload error
          setFiles(prev => prev.map(f => 
            f.id === localFile.id ? { ...f, status: 'error' } : f
          ));
        }
      } catch (error) {
        console.error(`FileContext: Upload error for ${file.name}:`, error);
        // Handle upload error
        setFiles(prev => prev.map(f => 
          f.id === localFile.id ? { ...f, status: 'error' } : f
        ));
      }
    }
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
