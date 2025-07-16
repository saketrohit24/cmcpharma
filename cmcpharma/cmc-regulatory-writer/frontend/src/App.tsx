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
import { sampleCitations, sampleSections } from './components/Editor/sampleData';
import { FileProvider } from './contexts/FileContext';
import { type StoredDocument } from './services/storage';
import { templateGenerationService, type GeneratedDocument } from './services/templateGeneration';
import { Toaster, toast } from 'react-hot-toast';

interface AppState {
  currentView: 'editor' | 'files' | 'templates' | 'history' | 'connection-test';
  generatedDocument: GeneratedDocument | null;
  showNewDocumentModal: boolean;
  showLLMConfig: boolean;
  currentDocumentId: string | null;
  isGenerating: boolean;
}

function App() {
  const [state, setState] = useState<AppState>({
    currentView: 'editor',
    generatedDocument: null,
    showNewDocumentModal: false,
    showLLMConfig: false,
    currentDocumentId: null,
    isGenerating: false
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

  // Handle template generation
  const handleGenerateFromTemplate = async (template: Template): Promise<void> => {
    try {
      setState(prev => ({ ...prev, isGenerating: true }));
      toast.loading('Generating document from template...', { id: 'generation' });
      
      // Generate document using the service
      const generatedDoc = await templateGenerationService.generateDocument(template);
      
      // Update state with generated content
      setState(prev => ({
        ...prev,
        generatedDocument: generatedDoc,
        currentView: 'editor', // Switch to editor to show generated content
        isGenerating: false
      }));
      
      toast.success(`Document generated successfully from "${template.name}"!`, { id: 'generation' });
    } catch (error) {
      console.error('Error generating document:', error);
      setState(prev => ({ ...prev, isGenerating: false }));
      toast.error('Failed to generate document. Please try again.', { id: 'generation' });
    }
  };

  const renderMainContent = () => {
    console.log('Current view:', state.currentView);
    switch (state.currentView) {
      case 'files':
        return <FileManagerPage />;
      
      case 'templates':
        return (
          <TemplateManagerPage 
            onGenerateFromTemplate={handleGenerateFromTemplate}
            isGenerating={state.isGenerating}
          />
        );
        
      case 'history':
        return <DocumentHistory />;
        
      case 'connection-test':
        return <ConnectionTest />;
      
      case 'editor':
      default:
        return (
          <div className="main-container">
            <Sidebar />
            <DocumentEditor 
              sections={state.generatedDocument?.sections || sampleSections}
              citations={state.generatedDocument?.citations || sampleCitations}
              isGenerating={state.isGenerating}
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
    <FileProvider>
      <div className="App">
        <Toaster position="top-right" />
        <Header 
          currentView={state.currentView} 
          onViewChange={handleViewChange}
          onNewDocument={handleNewDocument}
          onOpenSettings={handleOpenSettings}
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
    </FileProvider>
  );
}

export default App;
