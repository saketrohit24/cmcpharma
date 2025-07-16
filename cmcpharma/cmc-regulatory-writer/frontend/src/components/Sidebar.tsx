import React, { useState } from 'react';

const Sidebar: React.FC = () => {
  const [expandedFolders, setExpandedFolders] = useState<{ [key: string]: boolean }>({
    'Drug Substance': true,
    'Drug Product': false
  });

  const toggleFolder = (folderName: string) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folderName]: !prev[folderName]
    }));
  };

  const drugSubstanceFiles = [
    '3.2.S.1 General Information',
    '3.2.S.2 Manufacture',
    '3.2.S.3 Characterization',
    '3.2.S.4 Control',
    '3.2.S.5 Reference Standards',
    '3.2.S.6 Container Closure',
    '3.2.S.7 Stability'
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-title">Project Structure</div>
        
        <div className="folder">
          <div className="folder-header" onClick={() => toggleFolder('Drug Substance')}>
            <span>{expandedFolders['Drug Substance'] ? '▼' : '▶'}</span>
            <span className="folder-icon">📁</span>
            <span>Drug Substance</span>
          </div>
          {expandedFolders['Drug Substance'] && (
            <div className="file-list">
              {drugSubstanceFiles.map((file, index) => (
                <div key={index} className="file-item">
                  <span style={{ marginLeft: '16px' }}>📄</span>
                  <span>{file}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="folder">
          <div className="folder-header" onClick={() => toggleFolder('Drug Product')}>
            <span>{expandedFolders['Drug Product'] ? '▼' : '▶'}</span>
            <span className="folder-icon">📁</span>
            <span>Drug Product</span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
