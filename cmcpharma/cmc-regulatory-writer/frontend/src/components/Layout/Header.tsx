import React, { useState, useEffect } from 'react';
import { FileText, Upload, BookOpen, Clock, Plus, Settings, Wifi } from 'lucide-react';

interface Tab {
  id: string;
  title: string;
  active: boolean;
}

interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  children?: FileItem[];
  expanded?: boolean;
}

interface HeaderProps {
  currentView?: 'editor' | 'files' | 'templates' | 'history' | 'connection-test';
  onViewChange?: (view: 'editor' | 'files' | 'templates' | 'history' | 'connection-test') => void;
  onNewDocument?: () => void;
  onOpenSettings?: () => void;
  projectStructure?: FileItem[];
  projectName?: string;
  activeTabId?: string;
  onTabChange?: (tabId: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  currentView = 'editor', 
  onViewChange,
  onNewDocument,
  onOpenSettings,
  projectStructure = [],
  projectName = "Regulatory Document Management",
  activeTabId,
  onTabChange
}) => {
  const [tabs, setTabs] = useState<Tab[]>([
    { id: '1', title: 'Module 3.2.S - Drug Substance', active: true },
    { id: '2', title: 'Module 3.2.P - Drug Product', active: false },
    { id: '3', title: 'Specifications', active: false },
  ]);

  // Generate tabs from project structure
  useEffect(() => {
    if (projectStructure && projectStructure.length > 0) {
      const generateTabsFromStructure = (items: FileItem[]): Tab[] => {
        const tabs: Tab[] = [];
        
        const addFileTabs = (items: FileItem[]) => {
          items.forEach(item => {
            if (item.type === 'file') {
              tabs.push({
                id: item.id,
                title: item.name,
                active: activeTabId ? item.id === activeTabId : tabs.length === 0
              });
            } else if (item.children) {
              addFileTabs(item.children);
            }
          });
        };
        
        addFileTabs(items);
        return tabs;
      };
      
      const newTabs = generateTabsFromStructure(projectStructure);
      if (newTabs.length > 0) {
        setTabs(newTabs);
      }
    }
  }, [projectStructure, activeTabId]);

  const handleTabClick = (tabId: string) => {
    setTabs(tabs.map(tab => ({
      ...tab,
      active: tab.id === tabId
    })));
    onTabChange?.(tabId);
  };

  const addNewTab = () => {
    const newTab: Tab = {
      id: Date.now().toString(),
      title: `New Section ${tabs.length + 1}`,
      active: true
    };
    setTabs([...tabs.map(t => ({ ...t, active: false })), newTab]);
  };

  return (
    <header className="header">
      <div className="header-main">
        <div className="header-left">
          <div className="doc-info">
            <div className="doc-id">Otsuka CMC Writer</div>
            <div className="doc-title">{projectName}</div>
          </div>
          
          {/* Navigation */}
          <div className="nav-tabs">
            <button 
              className={`nav-tab ${currentView === 'editor' ? 'active' : ''}`}
              onClick={() => onViewChange?.('editor')}
            >
              <FileText size={16} />
              Editor
            </button>
            <button 
              className={`nav-tab ${currentView === 'files' ? 'active' : ''}`}
              onClick={() => onViewChange?.('files')}
            >
              <Upload size={16} />
              Files
            </button>
            <button 
              className={`nav-tab ${currentView === 'templates' ? 'active' : ''}`}
              onClick={() => onViewChange?.('templates')}
            >
              <BookOpen size={16} />
              Templates
            </button>
            <button 
              className={`nav-tab ${currentView === 'history' ? 'active' : ''}`}
              onClick={() => onViewChange?.('history')}
            >
              <Clock size={16} />
              History
            </button>
            <button 
              className={`nav-tab ${currentView === 'connection-test' ? 'active' : ''}`}
              onClick={() => onViewChange?.('connection-test')}
            >
              <Wifi size={16} />
              Connection Test
            </button>
          </div>
        </div>
        <div className="header-right">
          <button 
            className="btn btn-secondary"
            onClick={() => onOpenSettings?.()}
            title="LLM Settings"
          >
            <Settings size={16} />
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => onNewDocument?.()}
          >
            <Plus size={16} />
            New Document
          </button>
        </div>
      </div>
      
      <div className="tabs-container">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${tab.active ? 'active' : ''}`}
            onClick={() => handleTabClick(tab.id)}
          >
            {tab.title}
          </button>
        ))}
        <button className="add-tab" onClick={addNewTab}>+</button>
      </div>
    </header>
  );
};
