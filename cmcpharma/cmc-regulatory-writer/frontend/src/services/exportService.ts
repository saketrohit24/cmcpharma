/**
 * Export Service for handling document exports
 */

import { backendApi, type ExportRequest, type GeneratedDocument as BackendGeneratedDocument } from './backendApi';
import type { GeneratedDocument } from './templateGeneration';

export type ExportFormat = 'pdf' | 'docx';

export interface ExportOptions {
  format: ExportFormat;
  includeMetadata?: boolean;
  includeCitations?: boolean;
  pageNumbers?: boolean;
  headerFooter?: boolean;
}

export interface ExportResult {
  success: boolean;
  blob?: Blob;
  filename?: string;
  error?: string;
}

class ExportService {
  private static instance: ExportService;
  private useBackend: boolean = true;

  private constructor() {}

  static getInstance(): ExportService {
    if (!ExportService.instance) {
      ExportService.instance = new ExportService();
    }
    return ExportService.instance;
  }

  setBackendMode(enabled: boolean) {
    this.useBackend = enabled;
  }

  async exportDocument(
    document: GeneratedDocument, 
    options: ExportOptions = { format: 'pdf' }
  ): Promise<ExportResult> {
    if (this.useBackend) {
      try {
        // Convert frontend document to backend format for export
        const backendDocument = this.convertToBackendDocument(document);
        
        const request: ExportRequest = {
          format: options.format,
          document: backendDocument
        };

        const response = await backendApi.exportDocument(request);
        
        if (response.ok) {
          const blob = await response.blob();
          const filename = this.generateFilename(document.title, options.format);
          
          return {
            success: true,
            blob,
            filename
          };
        } else {
          throw new Error(`Export failed: ${response.statusText}`);
        }
      } catch (error) {
        console.warn('Backend export failed, falling back to mock export:', error);
        return this.mockExport(document, options);
      }
    }

    // Fallback to mock export
    return this.mockExport(document, options);
  }

  private async mockExport(document: GeneratedDocument, options: ExportOptions): Promise<ExportResult> {
    // Mock export - generate a simple text file for demo purposes
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate processing time

    const content = this.generateMockContent(document, options);
    const blob = new Blob([content], { 
      type: options.format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
    });
    
    const filename = this.generateFilename(document.title, options.format);

    return {
      success: true,
      blob,
      filename
    };
  }

  private generateMockContent(document: GeneratedDocument, options: ExportOptions): string {
    let content = `${document.title}\n`;
    content += `Generated on: ${document.generatedAt.toLocaleDateString()}\n`;
    content += `Template ID: ${document.templateId}\n\n`;

    if (options.includeMetadata) {
      content += `Document ID: ${document.id}\n`;
      content += `Export Format: ${options.format.toUpperCase()}\n`;
      content += `Export Date: ${new Date().toLocaleDateString()}\n\n`;
    }

    content += "CONTENT:\n";
    content += "========\n\n";

    document.sections.forEach((section, index) => {
      content += `${index + 1}. ${section.title}\n`;
      content += "-".repeat(section.title.length + 3) + "\n";
      content += `${section.content}\n\n`;
    });

    if (options.includeCitations && document.citations.length > 0) {
      content += "\nREFERENCES:\n";
      content += "===========\n\n";
      
      document.citations.forEach((citation) => {
        content += `[${citation.id}] ${citation.text}\n`;
        content += `    Source: ${citation.source}, Page ${citation.page}\n\n`;
      });
    }

    return content;
  }

  private generateFilename(title: string, format: ExportFormat): string {
    const cleanTitle = title
      .replace(/[^a-zA-Z0-9\s-]/g, '') // Remove special characters
      .replace(/\s+/g, '_') // Replace spaces with underscores
      .toLowerCase();
    
    const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    
    return `${cleanTitle}_${timestamp}.${format}`;
  }

  private convertToBackendDocument(frontendDoc: GeneratedDocument): BackendGeneratedDocument {
    return {
      id: frontendDoc.id,
      title: frontendDoc.title,
      sections: frontendDoc.sections.map(section => ({
        id: section.id,
        title: section.title,
        content: section.content,
        source_count: 1 // Default value
      })),
      template_id: frontendDoc.templateId,
      session_id: backendApi.getSessionId(),
      generated_at: frontendDoc.generatedAt instanceof Date 
        ? frontendDoc.generatedAt.toISOString() 
        : new Date(frontendDoc.generatedAt).toISOString()
    };
  }

  downloadBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  async exportAndDownload(
    document: GeneratedDocument, 
    options: ExportOptions = { format: 'pdf' }
  ): Promise<boolean> {
    try {
      const result = await this.exportDocument(document, options);
      
      if (result.success && result.blob && result.filename) {
        this.downloadBlob(result.blob, result.filename);
        return true;
      } else {
        console.error('Export failed:', result.error);
        return false;
      }
    } catch (error) {
      console.error('Export and download failed:', error);
      return false;
    }
  }

  getSupportedFormats(): ExportFormat[] {
    return ['pdf', 'docx'];
  }

  getDefaultOptions(): ExportOptions {
    return {
      format: 'pdf',
      includeMetadata: true,
      includeCitations: true,
      pageNumbers: true,
      headerFooter: true
    };
  }
}

export const exportService = ExportService.getInstance();
