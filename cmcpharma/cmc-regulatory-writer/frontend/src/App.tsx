import { useState, useEffect } from 'react';
import './styles/regulatory.css';
import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Layout/Sidebar';
import { RightPanel } from './components/Layout/RightPanel';
import { DocumentEditor } from './components/Editor/DocumentEditor';
import { FileManagerPage } from './components/Files/FileManagerPage';
import { TemplateManagerPage, type Template } from './components/Templates/TemplateManagerPage';
import { DocumentHistory } from './components/History/DocumentHistory';
import { NewDocument } from './components/Export/NewDocument';
import { LLMConfig } from './components/Settings/LLMConfig';
import ConnectionTest from './components/ConnectionTest';
import { References } from './components/Citation/References';
import { sampleCitations, sampleSections } from './components/Editor/sampleData';
import { FileProvider } from './contexts/FileContext';
import { useFiles } from './contexts/useFiles';
import { storage, type StoredDocument } from './services/storage';
import { templateGenerationService, type GeneratedDocument } from './services/templateGeneration';
import { backendApi, type TemplateStructure } from './services/backendApi';
import { Toaster, toast } from 'react-hot-toast';

interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  children?: FileItem[];
  expanded?: boolean;
}

interface AppState {
  currentView: 'editor' | 'files' | 'templates' | 'history' | 'connection-test' | 'citations';
  generatedDocument: GeneratedDocument | null;
  showNewDocumentModal: boolean;
  showLLMConfig: boolean;
  currentDocumentId: string | null;
  isGenerating: boolean;
  projectStructure: FileItem[];
  projectName: string;
  activeTabId: string | null;
  generationProgress: {
    currentSection: string;
    completedSections: string[];
    totalSections: number;
  } | null;
  editedSections: {[key: string]: string}; // Add edited sections state
}

function AppContent() {
  const { files } = useFiles();
  const defaultProjectStructure: FileItem[] = [
    {
      id: '1',
      name: 'Drug Substance',
      type: 'folder',
      expanded: true,
      children: [
        { id: '1.1', name: '3.2.S.1 General Information', type: 'file' },
        { id: '1.2', name: '3.2.S.2 Manufacture', type: 'file' },
        { id: '1.3', name: '3.2.S.3 Characterization', type: 'file' },
        { id: '1.4', name: '3.2.S.4 Control', type: 'file' },
        { id: '1.5', name: '3.2.S.5 Reference Standards', type: 'file' },
        { id: '1.6', name: '3.2.S.6 Container Closure', type: 'file' },
        { id: '1.7', name: '3.2.S.7 Stability', type: 'file' },
      ]
    },
    {
      id: '2',
      name: 'Drug Product',
      type: 'folder',
      expanded: false,
      children: []
    }
  ];

  const [state, setState] = useState<AppState>({
    currentView: 'editor',
    generatedDocument: null,
    showNewDocumentModal: false,
    showLLMConfig: false,
    currentDocumentId: null,
    isGenerating: false,
    projectStructure: defaultProjectStructure,
    projectName: "Module 3 Quality Documentation",
    activeTabId: null,
    generationProgress: null,
    editedSections: {} // Initialize edited sections
  });

  // Restore document and state on page load
  useEffect(() => {
    console.log('🔄 App: Restoring document and state from localStorage...');
    
    // Restore generated document
    const savedDocument = storage.getGeneratedDocument();
    if (savedDocument) {
      console.log('📄 App: Restored generated document:', savedDocument.title);
      setState(prev => ({
        ...prev,
        generatedDocument: savedDocument
      }));
      toast.success('Document restored from previous session!');
    }
    
    // Restore app state
    const savedState = storage.getAppState();
    if (savedState) {
      console.log('💾 App: Restored app state');
      setState(prev => ({
        ...prev,
        projectName: savedState.projectName,
        projectStructure: savedState.projectStructure,
        activeTabId: savedState.activeTabId,
        editedSections: savedState.editedSections
      }));
    }
  }, []);

  // Auto-save state when it changes
  useEffect(() => {
    if (state.generatedDocument) {
      console.log('💾 App: Auto-saving app state...');
      /* storage.saveAppState({
        projectName: state.projectName,
        projectStructure: state.projectStructure,
        activeTabId: state.activeTabId,
        editedSections: state.editedSections
      }); */
    }
  }, [state.projectName, state.projectStructure, state.activeTabId, state.editedSections, state.generatedDocument]);

  const handleViewChange = (view: 'editor' | 'files' | 'templates' | 'history' | 'connection-test' | 'citations') => {
    console.log('Switching to view:', view);
    setState(prev => ({ ...prev, currentView: view }));
  };

  // Handle editing sections
  const handleEditSection = (sectionId: string, editedContent: string) => {
    console.log('🔄 App: handleEditSection called with:', { 
      sectionId, 
      editedContentLength: editedContent.length,
      editedContentPreview: editedContent.substring(0, 100) + '...' 
    });
    console.log('🔄 App: Current editedSections before update:', Object.keys(state.editedSections));
    console.log('🔄 App: Current activeTabId:', state.activeTabId);
    
    setState(prev => {
      const newEditedSections = {
        ...prev.editedSections,
        [sectionId]: editedContent
      };
      
      console.log('✅ App: New editedSections after update:', Object.keys(newEditedSections));
      console.log('✅ App: Updated section content length:', newEditedSections[sectionId]?.length || 0);
      
      // Auto-save edited sections
      storage.saveAppState({
        projectName: prev.projectName,
        projectStructure: prev.projectStructure,
        activeTabId: prev.activeTabId,
        editedSections: newEditedSections
      });
      
      console.log('💾 App: Auto-saved edited sections to localStorage');
      
      return {
        ...prev,
        editedSections: newEditedSections
      };
    });
  };

  // Handle reverting sections back to original content
  const handleRevertSection = (sectionId: string) => {
    console.log('🔄 App: handleRevertSection called for sectionId:', sectionId);
    console.log('🔄 App: Current editedSections before revert:', Object.keys(state.editedSections));
    
    setState(prev => {
      const newEditedSections = { ...prev.editedSections };
      delete newEditedSections[sectionId]; // Remove the edited version to revert to original
      
      console.log('✅ App: New editedSections after revert:', Object.keys(newEditedSections));
      
      // Auto-save edited sections
      storage.saveAppState({
        projectName: prev.projectName,
        projectStructure: prev.projectStructure,
        activeTabId: prev.activeTabId,
        editedSections: newEditedSections
      });
      
      console.log('💾 App: Auto-saved reverted sections to localStorage');
      
      return {
        ...prev,
        editedSections: newEditedSections
      };
    });
    
    toast.success('Section reverted to original content');
  };

  // Clear persisted data and start fresh
  const handleNewDocument = () => {
    console.log('🗑️ App: Starting new document - clearing persisted data');
    
    // Clear all persisted data
    storage.clearGeneratedDocument();
    storage.clearAppState();
    localStorage.removeItem('cmc_uploaded_files');
    
    // Reset app state
    setState({
      currentView: 'files',
      generatedDocument: null,
      showNewDocumentModal: false,
      showLLMConfig: false,
      currentDocumentId: null,
      isGenerating: false,
      projectStructure: defaultProjectStructure,
      projectName: "Module 3 Quality Documentation",
      activeTabId: null,
      generationProgress: null,
      editedSections: {}
    });
    
    toast.success('Started new document - all data cleared!');
  };

  const handleOpenSettings = () => {
    setState(prev => ({ ...prev, showLLMConfig: true }));
  };

  const handleDocumentCreated = (document: StoredDocument) => {
    setState(prev => ({ 
      ...prev, 
      showNewDocumentModal: false,
      currentDocumentId: document.id,
      currentView: 'editor'
    }));
  };

  const handleCancelNewDocument = () => {
    setState(prev => ({ ...prev, showNewDocumentModal: false }));
  };

  // Handle template structure change and ensure it overrides default structure
  const handleTemplateStructureChange = (structure: TemplateStructure) => {
    console.log('🏗️ Updating project structure from uploaded template:', structure);
    
    // Convert backend template structure to frontend FileItem format
    const convertToFileItems = (sections: TemplateStructure['sections'], parentId = ''): FileItem[] => {
      return sections.map((section, index) => ({
        id: section.id || `${parentId}${index + 1}`,
        name: section.title,
        type: section.children && section.children.length > 0 ? 'folder' : 'file',
        expanded: section.level <= 2, // Expand level 1 and 2 items by default
        children: section.children ? convertToFileItems(section.children, `${section.id || index + 1}.`) : []
      }));
    };

    // Create new structure based entirely on uploaded template
    const newProjectStructure: FileItem[] = convertToFileItems(structure.sections);

    // Get the first file item for active tab
    const findFirstFile = (items: FileItem[]): string | null => {
      for (const item of items) {
        if (item.type === 'file') return item.id;
        if (item.children) {
          const found = findFirstFile(item.children);
          if (found) return found;
        }
      }
      return null;
    };

    const firstFileId = findFirstFile(newProjectStructure);

    setState(prev => ({
      ...prev,
      projectStructure: newProjectStructure, // Use template structure, not default
      projectName: structure.name || 'Generated Document',
      activeTabId: firstFileId
    }));
    
    console.log('✅ Project structure updated with', newProjectStructure.length, 'sections from template');
  };

  // Handle tab changes
  const handleTabChange = (tabId: string) => {
    setState(prev => ({
      ...prev,
      activeTabId: tabId
    }));
  };

  // Handle template generation with section-by-section progress and uploaded files
  const handleGenerateFromTemplate = async (template: Template): Promise<void> => {
    try {
      console.log('🚀 Starting generation process...', template);
      console.log('📊 Backend connection test:', await templateGenerationService.testBackendConnection());
      
      setState(prev => ({ 
        ...prev, 
        isGenerating: true,
        generatedDocument: null, // Clear previous document
        generationProgress: {
          currentSection: '',
          completedSections: [],
          totalSections: 0
        }
      }));
      
      // Count total sections for progress tracking
      const countSections = (toc: typeof template.toc): number => {
        return toc.reduce((count, item) => {
          return count + 1 + (item.children ? countSections(item.children) : 0);
        }, 0);
      };
      
      const totalSections = countSections(template.toc);
      console.log('📝 Total sections to generate:', totalSections);
      
      setState(prev => ({
        ...prev,
        generationProgress: {
          currentSection: 'Starting generation...',
          completedSections: [],
          totalSections
        }
      }));
      
      toast.loading('Starting document generation...', { id: 'generation' });

      // Convert uploaded files to File objects
      const readyFiles = files.filter(f => f.status === 'ready');
      console.log('Ready files for generation:', readyFiles.length);
      
      // Set uploaded files in the template generation service
      templateGenerationService.setUploadedFiles(readyFiles);
      console.log('Files set in templateGenerationService:', readyFiles.length);
      
      // Generate document using the enhanced service with progress callbacks
      const generatedDoc = await templateGenerationService.generateDocumentWithProgress(
        template,
        {
          onSectionStart: (sectionTitle: string) => {
            console.log('Starting section:', sectionTitle);
            setState(prev => ({
              ...prev,
              generationProgress: prev.generationProgress ? {
                ...prev.generationProgress,
                currentSection: sectionTitle
              } : null
            }));
            toast.loading(`Generating content for '${sectionTitle}'...`, { id: 'generation' });
          },
          onSectionComplete: (sectionTitle: string) => {
            console.log('Completed section:', sectionTitle);
            setState(prev => ({
              ...prev,
              generationProgress: prev.generationProgress ? {
                ...prev.generationProgress,
                completedSections: [...prev.generationProgress.completedSections, sectionTitle],
                currentSection: `Finished generating '${sectionTitle}'`
              } : null
            }));
          }
        }
      );
      
      console.log('Generation completed, received document:', generatedDoc);
      
      // Process generated document and ensure proper section mapping
      setState(prev => {
        // Create a mapping of section titles to project structure IDs
        const projectStructureIdMap = new Map<string, string>();
        const buildIdMap = (items: FileItem[]) => {
          items.forEach(item => {
            if (item.type === 'file') {
              projectStructureIdMap.set(item.name, item.id);
            }
            if (item.children) {
              buildIdMap(item.children);
            }
          });
        };
        
        if (prev.projectStructure) {
          buildIdMap(prev.projectStructure);
        }

        // Update sections with IDs that match project structure
        const updatedSections = generatedDoc.sections.map(section => {
          // Use project structure ID if available, otherwise generate one
          const projectId = projectStructureIdMap.get(section.title);
          return {
            ...section,
            id: projectId || section.id || `section-${section.title.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase()}`
          };
        });

        console.log('📄 Mapped sections:', updatedSections.map(s => ({ id: s.id, title: s.title })));
        console.log('📁 Project structure IDs:', Array.from(projectStructureIdMap.entries()));

        // Find the first section that matches the project structure
        const firstMatchingSection = updatedSections.find(section => 
          projectStructureIdMap.has(section.title)
        );

        // The backend now automatically handles References sections
        const updatedDocument = {
          ...generatedDoc,
          sections: updatedSections
        };

        // Update project structure to include all generated sections (including References)
        const updatedProjectStructure = prev.projectStructure ? [...prev.projectStructure] : [];
        
        // Find or create a place for the References section
        const referencesSection = updatedSections.find(section => 
          section.title.toLowerCase().includes('reference')
        );
        
        if (referencesSection && !projectStructureIdMap.has(referencesSection.title)) {
          // Add References section to project structure
          const referencesFileItem: FileItem = {
            id: referencesSection.id,
            name: referencesSection.title,
            type: 'file'
          };
          
          // Add it to the main level (not nested)
          updatedProjectStructure.push(referencesFileItem);
        }

        // Save the generated document to localStorage
        storage.saveGeneratedDocument(updatedDocument);

        return {
          ...prev,
          generatedDocument: updatedDocument,
          projectName: generatedDoc.title,
          projectStructure: updatedProjectStructure, // Include updated structure with References
          // Set active tab to first matching section ID from project structure
          activeTabId: firstMatchingSection ? (projectStructureIdMap.get(firstMatchingSection.title) || null) : 
                       (updatedSections.length > 0 ? updatedSections[0].id : prev.activeTabId),
          currentView: 'editor', // Switch to editor to show generated content
          currentDocumentId: `${backendApi.getSessionId()}-document`, // Set the document ID to match backend
          isGenerating: false,
          generationProgress: null
        };
      });
      
      toast.success(`Document generated successfully! Created ${generatedDoc.sections.length} sections from "${template.name}" using ${readyFiles.length} uploaded files.`, { 
        id: 'generation',
        duration: 5000
      });
      
      // Log success details
      console.log('Generation success:', {
        sectionsGenerated: generatedDoc.sections.length,
        templateName: template.name,
        filesUsed: readyFiles.length
      });
    } catch (error) {
      console.error('Error generating document:', error);
      setState(prev => ({ 
        ...prev, 
        isGenerating: false,
        generationProgress: null
      }));
      toast.error(`Failed to generate document: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`, { 
        id: 'generation',
        duration: 5000
      });
    }
  };

  const renderMainContent = () => {
    console.log('Current view:', state.currentView);
    switch (state.currentView) {
      case 'files':
        return (
          <div>
            <FileManagerPage />
          </div>
        );
      
      case 'templates':
        return (
          <div>
            <TemplateManagerPage 
              onGenerateFromTemplate={handleGenerateFromTemplate}
              onStructureChange={handleTemplateStructureChange}
              isGenerating={state.isGenerating}
            />
          </div>
        );
        
      case 'history':
        return <DocumentHistory />;
        
      case 'connection-test':
        return <ConnectionTest />;
      
      case 'citations':
        return (
          <div className="citations-view p-6">
            <References 
              documentId={state.currentDocumentId || `${backendApi.getSessionId()}-document`} 
              className="max-w-4xl mx-auto"
            />
          </div>
        );
      
      case 'editor':
      default:
        return (
          <div className="main-container">
            <Sidebar 
              fileStructure={state.projectStructure} 
              activeFileId={state.activeTabId || undefined}
              onFileSelect={(fileId: string, fileName: string) => {
                console.log('File selected:', fileId, fileName);
                setState(prev => ({ ...prev, activeTabId: fileId }));
              }}
            />
            <DocumentEditor 
              sections={state.generatedDocument?.sections || sampleSections}
              citations={state.generatedDocument?.citations || sampleCitations}
              isGenerating={state.isGenerating}
              generationProgress={state.generationProgress}
              activeTabId={state.activeTabId || undefined}
              editedSections={state.editedSections}
              onSectionEdit={handleEditSection}
              onSectionRevert={handleRevertSection}
            />
            <RightPanel 
              onNavigateToTemplates={() => setState(prev => ({ ...prev, currentView: 'templates' }))}
              onNavigateToHistory={() => setState(prev => ({ ...prev, currentView: 'history' }))}
              onNavigateToFiles={() => setState(prev => ({ ...prev, currentView: 'files' }))}
              onGenerateFromTemplate={handleGenerateFromTemplate}
              currentDocument={state.generatedDocument ? {
                id: state.currentDocumentId || 'generated-doc',
                title: state.generatedDocument.title || 'Generated Document',
                docId: state.currentDocumentId || 'generated-doc',
                sections: state.generatedDocument.sections || [],
                citations: state.generatedDocument.citations || [],
                createdAt: state.generatedDocument.generatedAt 
                  ? (state.generatedDocument.generatedAt instanceof Date 
                      ? state.generatedDocument.generatedAt.toISOString() 
                      : new Date(state.generatedDocument.generatedAt).toISOString())
                  : new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                status: 'draft' as const
              } : null}
              sections={state.generatedDocument?.sections || sampleSections}
              citations={state.generatedDocument?.citations || sampleCitations}
              activeTabId={state.activeTabId || undefined}
              editedSections={state.editedSections}
              onEditSection={handleEditSection}
            />
          </div>
        );
    }
  };

  return (
    <div className="App">
      <Toaster position="top-right" />
      <Header 
        currentView={state.currentView} 
        onViewChange={handleViewChange}
        onNewDocument={handleNewDocument}
        onOpenSettings={handleOpenSettings}
        projectStructure={state.projectStructure}
        projectName={state.projectName}
        activeTabId={state.activeTabId || undefined}
        onTabChange={handleTabChange}
      />
      
      {renderMainContent()}

    {/* New Document Modal */}
    {state.showNewDocumentModal && (
      <NewDocument
        onDocumentCreated={handleDocumentCreated}
        onCancel={handleCancelNewDocument}
      />
    )}

    {/* LLM Configuration Modal */}
    {state.showLLMConfig && (
      <LLMConfig
        onClose={() => setState(prev => ({ ...prev, showLLMConfig: false }))}
      />
    )}
    </div>
  );
}

function App() {
  return (
    <FileProvider>
      <AppContent />
    </FileProvider>
  );
}

export default App;
