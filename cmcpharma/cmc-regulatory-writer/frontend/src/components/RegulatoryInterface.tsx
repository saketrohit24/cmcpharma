import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { Header, Sidebar, RightPanel } from './Layout';
import { DocumentEditor } from './Editor';
import { FileManagerPage } from './Files';
import { TemplateManagerPage } from './Templates';
import { sampleCitations, sampleSections } from './Editor/sampleData';
import '../styles/regulatory.css';

const RegulatoryInterface: React.FC = () => {
  const [currentView, setCurrentView] = useState<'editor' | 'files' | 'templates'>('editor');

  const handleViewChange = (view: 'editor' | 'files' | 'templates') => {
    setCurrentView(view);
  };
  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentView={currentView} onViewChange={handleViewChange} />
      {currentView === 'files' ? (
        <FileManagerPage />
      ) : currentView === 'templates' ? (
        <TemplateManagerPage />
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
