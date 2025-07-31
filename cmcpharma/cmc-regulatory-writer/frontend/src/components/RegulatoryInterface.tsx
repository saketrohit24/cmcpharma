import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { Header, Sidebar, RightPanel } from './Layout';
import { DocumentEditor } from './Editor';
import { FileManagerPage } from './Files';
import { TemplateManagerPage } from './Templates';
import { CitationManager } from './Citations/CitationManager';
import { sampleCitations, sampleSections } from './Editor/sampleData';
import '../styles/regulatory.css';

const RegulatoryInterface: React.FC = () => {
  const [currentView, setCurrentView] = useState<'editor' | 'files' | 'templates' | 'history' | 'connection-test' | 'citations'>('editor');

  const handleViewChange = (view: 'editor' | 'files' | 'templates' | 'history' | 'connection-test' | 'citations') => {
    setCurrentView(view);
  };
  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentView={currentView} onViewChange={handleViewChange} />
      {currentView === 'files' ? (
        <FileManagerPage />
      ) : currentView === 'templates' ? (
        <TemplateManagerPage />
      ) : currentView === 'history' ? (
        <div className="main-container">
          <div className="p-8 text-center">
            <h2 className="text-xl font-semibold mb-4">Document History</h2>
            <p className="text-gray-600">History view not implemented yet</p>
          </div>
        </div>
      ) : currentView === 'connection-test' ? (
        <div className="main-container">
          <div className="p-8 text-center">
            <h2 className="text-xl font-semibold mb-4">Connection Test</h2>
            <p className="text-gray-600">Connection test view not implemented yet</p>
          </div>
        </div>
      ) : currentView === 'citations' ? (
        <div className="main-container">
          <CitationManager className="max-w-6xl mx-auto" />
        </div>
      ) : (
        <div className="main-container">
          <Sidebar />
          <DocumentEditor sections={sampleSections} citations={sampleCitations} />
          <RightPanel onNavigateToTemplates={() => setCurrentView('templates')} />
        </div>
      )}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </div>
  );
};

export default RegulatoryInterface;
