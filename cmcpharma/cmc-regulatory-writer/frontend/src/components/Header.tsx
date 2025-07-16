import React from 'react';
import { Menu, ArrowLeft, CheckCircle2, Plus } from 'lucide-react';
import { cn } from '../utils/cn';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    'Module 3.2.S - Drug Substance',
    'Module 3.2.P - Drug Product',
    'Specifications'
  ];

  return (
    <header className="header">
      <div className="header-main">
        <div className="header-left">
          <button className="menu-btn">
            <Menu size={20} />
          </button>
          <div className="doc-info">
            <div className="doc-id">CMC-2024-001</div>
            <div className="doc-title">Module 3 Quality Documentation</div>
          </div>
        </div>
        <div className="header-right">
          <button className={cn("btn btn-secondary", "flex items-center gap-2")}>
            <ArrowLeft size={16} />
            Back
          </button>
          <button className={cn("btn btn-primary", "flex items-center gap-2")}>
            <CheckCircle2 size={16} />
            Mark all as complete
          </button>
        </div>
      </div>
      
      <div className="tabs-container">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
        <button className="add-tab">
          <Plus size={16} />
        </button>
      </div>
    </header>
  );
};

export default Header;
