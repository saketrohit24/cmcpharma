import { useState } from 'react';
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
import { SessionDebugPanel } from './components/Debug/SessionDebugPanel';
import { sampleCitations, sampleSections } from './components/Editor/sampleData';
import { FileProvider } from './contexts/FileContext';
import { useFiles } from './contexts/useFiles';
import { type StoredDocument } from './services/storage';
import { templateGenerationService, type GeneratedDocument } from './services/templateGeneration';
import { type TemplateStructure } from './services/backendApi';
import { Toaster, toast } from 'react-hot-toast';

interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  children?: FileItem[];
  expanded?: boolean;
}

interface AppState {
  currentView: 'editor' | 'files' | 'templates' | 'history' | 'connection-test';
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
    generationProgress: null
  });

  const handleViewChange = (view: 'editor' | 'files' | 'templates' | 'history' | 'connection-test') => {
    console.log('Switching to view:', view);
    setState(prev => ({ ...prev, currentView: view }));
  };

  const handleNewDocument = () => {
    setState(prev => ({ ...prev, showNewDocumentModal: true }));
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

        return {
          ...prev,
          generatedDocument: {
            ...generatedDoc,
            sections: updatedSections
          },
          projectName: generatedDoc.title,
          // Set active tab to first matching section ID from project structure
          activeTabId: firstMatchingSection ? (projectStructureIdMap.get(firstMatchingSection.title) || null) : 
                       (updatedSections.length > 0 ? updatedSections[0].id : prev.activeTabId),
          currentView: 'editor', // Switch to editor to show generated content
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
            <SessionDebugPanel />
            <FileManagerPage />
          </div>
        );
      
      case 'templates':
        return (
          <div>
            <SessionDebugPanel />
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
            />
            <RightPanel 
              onNavigateToTemplates={() => setState(prev => ({ ...prev, currentView: 'templates' }))}
              onNavigateToHistory={() => setState(prev => ({ ...prev, currentView: 'history' }))}
              onNavigateToFiles={() => setState(prev => ({ ...prev, currentView: 'files' }))}
              onGenerateFromTemplate={handleGenerateFromTemplate}
              currentDocument={null}
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
