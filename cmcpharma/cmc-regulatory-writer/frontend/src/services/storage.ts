interface DocumentSection {
  id: string;
  title: string;
  content: string;
  type: 'text' | 'table';
}

interface DocumentCitation {
  id: number;
  text: string;
  source: string;
  page: number;
}

interface StoredDocument {
  id: string;
  title: string;
  docId: string;
  sections: DocumentSection[];
  citations: DocumentCitation[];
  createdAt: string;
  updatedAt: string;
  status: 'draft' | 'review' | 'approved';
}

interface StoredFile {
  id: string;
  documentId: string;
  filename: string;
  size: number;
  uploadedAt: string;
}

interface SessionData {
  currentView: string;
  documentId?: string;
  lastSaved?: string;
  [key: string]: unknown;
}

export interface GeneratedDocument {
  id: string;
  title: string;
  sections: DocumentSection[];
  citations: DocumentCitation[];
  templateId: string;
  generatedAt: Date;
  savedAt?: string;
  [key: string]: unknown;
}

export interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  children?: FileItem[];
  expanded?: boolean;
}

export interface AppState {
  projectName: string;
  projectStructure: FileItem[];
  activeTabId: string | null;
  editedSections: {[key: string]: string};
}

export const storage = {
  // Generated Document Persistence
  saveGeneratedDocument: (doc: GeneratedDocument) => {
    try {
      localStorage.setItem('cmc_generated_document', JSON.stringify({
        ...doc,
        savedAt: new Date().toISOString()
      }));
      console.log('📄 Generated document saved to localStorage');
    } catch (error) {
      console.error('Failed to save generated document:', error);
    }
  },

  getGeneratedDocument: (): GeneratedDocument | null => {
    try {
      const saved = localStorage.getItem('cmc_generated_document');
      if (saved) {
        const doc = JSON.parse(saved);
        console.log('📄 Retrieved generated document from localStorage');
        return doc;
      }
    } catch (error) {
      console.error('Failed to retrieve generated document:', error);
    }
    return null;
  },

  clearGeneratedDocument: () => {
    try {
      localStorage.removeItem('cmc_generated_document');
      console.log('📄 Generated document cleared from localStorage');
    } catch (error) {
      console.error('Failed to clear generated document:', error);
    }
  },

  // Session State Persistence
  saveAppState: (state: AppState) => {
    try {
      const stateToSave = {
        ...state,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem('cmc_app_state', JSON.stringify(stateToSave));
      console.log('💾 App state saved to localStorage');
    } catch (error) {
      console.error('Failed to save app state:', error);
    }
  },

  getAppState: (): AppState | null => {
    try {
      const saved = localStorage.getItem('cmc_app_state');
      if (saved) {
        const state = JSON.parse(saved);
        console.log('💾 Retrieved app state from localStorage');
        return state;
      }
    } catch (error) {
      console.error('Failed to retrieve app state:', error);
    }
    return null;
  },

  clearAppState: () => {
    try {
      localStorage.removeItem('cmc_app_state');
      console.log('💾 App state cleared from localStorage');
    } catch (error) {
      console.error('Failed to clear app state:', error);
    }
  },

  // Document Management
  saveDocument: (doc: StoredDocument) => {
    const docs = storage.getDocuments();
    const existingIndex = docs.findIndex(d => d.id === doc.id);
    
    if (existingIndex >= 0) {
      docs[existingIndex] = { ...doc, updatedAt: new Date().toISOString() };
    } else {
      docs.push(doc);
    }
    
    localStorage.setItem('cmc_documents', JSON.stringify(docs));
  },
  
  getDocuments: (): StoredDocument[] => {
    const stored = localStorage.getItem('cmc_documents');
    return stored ? JSON.parse(stored) : [];
  },
  
  getDocument: (id: string): StoredDocument | null => {
    const docs = storage.getDocuments();
    return docs.find(d => d.id === id) || null;
  },
  
  deleteDocument: (id: string) => {
    const docs = storage.getDocuments().filter(d => d.id !== id);
    localStorage.setItem('cmc_documents', JSON.stringify(docs));
  },
  
  // File Management
  saveFiles: (files: StoredFile[]) => {
    localStorage.setItem('cmc_files', JSON.stringify(files));
  },
  
  getFiles: (documentId?: string): StoredFile[] => {
    const stored = localStorage.getItem('cmc_files');
    const files: StoredFile[] = stored ? JSON.parse(stored) : [];
    return documentId ? files.filter((f: StoredFile) => f.documentId === documentId) : files;
  },
  
  // Session Management
  saveSession: (sessionData: SessionData) => {
    sessionStorage.setItem('cmc_current_session', JSON.stringify({
      ...sessionData,
      lastSaved: new Date().toISOString()
    }));
  },
  
  getSession: (): SessionData | null => {
    const stored = sessionStorage.getItem('cmc_current_session');
    return stored ? JSON.parse(stored) : null;
  },
  
  clearSession: () => {
    sessionStorage.removeItem('cmc_current_session');
  }
};

// Sample data for testing
export const generateSampleData = () => {
  const sampleDocs: StoredDocument[] = [
    {
      id: 'doc-1',
      title: 'Drug Substance Specification',
      docId: 'CMC-2024-001',
      sections: [
        {
          id: 'section-1',
          title: '3.2.S.4 Control of Drug Substance',
          content: 'This section describes the specifications and analytical procedures for the drug substance.',
          type: 'text'
        }
      ],
      citations: [
        {
          id: 1,
          text: 'ICH Q6A guideline for specifications',
          source: 'ICH Q6A',
          page: 15
        }
      ],
      createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'approved'
    },
    {
      id: 'doc-2',
      title: 'Manufacturing Process Description',
      docId: 'CMC-2024-002',
      sections: [
        {
          id: 'section-2',
          title: '3.2.S.2 Manufacture',
          content: 'Detailed description of the manufacturing process including critical process parameters.',
          type: 'text'
        }
      ],
      citations: [
        {
          id: 2,
          text: 'Process validation guidelines',
          source: 'FDA Guidelines',
          page: 22
        }
      ],
      createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'review'
    },
    {
      id: 'doc-3',
      title: 'Stability Study Protocol',
      docId: 'CMC-2024-003',
      sections: [
        {
          id: 'section-3',
          title: '3.2.S.7 Stability',
          content: 'Stability study protocol and preliminary results for the drug substance.',
          type: 'text'
        }
      ],
      citations: [],
      createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      status: 'draft'
    }
  ];

  // Only add sample data if no documents exist
  const existingDocs = storage.getDocuments();
  if (existingDocs.length === 0) {
    sampleDocs.forEach(doc => storage.saveDocument(doc));
  }
};

export type { StoredDocument, StoredFile, DocumentSection, DocumentCitation, SessionData };
