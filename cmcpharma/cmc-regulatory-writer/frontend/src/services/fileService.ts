/**
 * File Service for handling file uploads and management
 */

import { backendApi, type FileItem } from './backendApi';

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
  status: 'uploading' | 'uploaded' | 'error';
  errorMessage?: string;
}

class FileService {
  private static instance: FileService;
  private uploadedFiles: Map<string, UploadedFile> = new Map();
  private useBackend: boolean = true;

  private constructor() {}

  static getInstance(): FileService {
    if (!FileService.instance) {
      FileService.instance = new FileService();
    }
    return FileService.instance;
  }

  setBackendMode(enabled: boolean) {
    this.useBackend = enabled;
  }

  async uploadFile(file: File): Promise<UploadedFile> {
    const uploadedFile: UploadedFile = {
      id: `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date(),
      status: 'uploading'
    };

    this.uploadedFiles.set(uploadedFile.id, uploadedFile);

    if (this.useBackend) {
      try {
        const response = await backendApi.uploadFile(file);
        
        if (response.data) {
          // Update with backend response
          uploadedFile.id = response.data.id;
          uploadedFile.status = 'uploaded';
          this.uploadedFiles.set(uploadedFile.id, uploadedFile);
          return uploadedFile;
        } else {
          throw new Error(response.error || 'Upload failed');
        }
      } catch (error) {
        uploadedFile.status = 'error';
        uploadedFile.errorMessage = error instanceof Error ? error.message : 'Upload failed';
        this.uploadedFiles.set(uploadedFile.id, uploadedFile);
        throw error;
      }
    } else {
      // Mock upload - simulate delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      uploadedFile.status = 'uploaded';
      this.uploadedFiles.set(uploadedFile.id, uploadedFile);
      return uploadedFile;
    }
  }

  async uploadMultipleFiles(files: FileList | File[]): Promise<UploadedFile[]> {
    const fileArray = Array.from(files);
    const uploadPromises = fileArray.map(file => this.uploadFile(file));
    
    try {
      return await Promise.all(uploadPromises);
    } catch (error) {
      console.error('Error uploading multiple files:', error);
      throw error;
    }
  }

  getUploadedFiles(): UploadedFile[] {
    return Array.from(this.uploadedFiles.values());
  }

  getFileById(id: string): UploadedFile | undefined {
    return this.uploadedFiles.get(id);
  }

  removeFile(id: string): boolean {
    return this.uploadedFiles.delete(id);
  }

  clearAllFiles(): void {
    this.uploadedFiles.clear();
  }

  getUploadedFileCount(): number {
    return Array.from(this.uploadedFiles.values())
      .filter(file => file.status === 'uploaded').length;
  }

  getTotalFileSize(): number {
    return Array.from(this.uploadedFiles.values())
      .filter(file => file.status === 'uploaded')
      .reduce((total, file) => total + file.size, 0);
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  isValidFileType(file: File, allowedTypes: string[] = []): boolean {
    if (allowedTypes.length === 0) {
      // Default allowed types for regulatory documents
      allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ];
    }
    
    return allowedTypes.includes(file.type) || 
           allowedTypes.some(type => {
             if (type.includes('*')) {
               const baseType = type.split('*')[0];
               return file.type.startsWith(baseType);
             }
             return false;
           });
  }

  validateFile(file: File, maxSize: number = 50 * 1024 * 1024): { valid: boolean; error?: string } {
    if (!this.isValidFileType(file)) {
      return {
        valid: false,
        error: 'File type not supported. Please upload PDF, Word, Excel, or text files.'
      };
    }
    
    if (file.size > maxSize) {
      return {
        valid: false,
        error: `File size exceeds ${this.formatFileSize(maxSize)} limit.`
      };
    }
    
    return { valid: true };
  }
}

export const fileService = FileService.getInstance();
export type { FileItem };
