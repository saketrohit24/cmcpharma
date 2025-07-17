import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, FileText, Folder } from 'lucide-react';

interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  children?: FileItem[];
  expanded?: boolean;
}

interface SidebarProps {
  fileStructure?: FileItem[];
  activeFileId?: string;
  onFileSelect?: (fileId: string, fileName: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  fileStructure: propFileStructure, 
  activeFileId, 
  onFileSelect 
}) => {
  const defaultFileStructure: FileItem[] = [
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

  const [fileStructure, setFileStructure] = useState<FileItem[]>(propFileStructure || defaultFileStructure);

  // Update local state when prop changes
  useEffect(() => {
    if (propFileStructure) {
      setFileStructure(propFileStructure);
    }
  }, [propFileStructure]);

  const toggleFolder = (folderId: string) => {
    const toggleInStructure = (items: FileItem[]): FileItem[] => 
      items.map(item => 
        item.id === folderId 
          ? { ...item, expanded: !item.expanded }
          : { ...item, children: item.children ? toggleInStructure(item.children) : undefined }
      );
    
    setFileStructure(toggleInStructure);
  };

  const renderFileItem = (item: FileItem, level: number = 0) => {
    if (item.type === 'folder') {
      return (
        <div key={item.id} className="folder">
          <div 
            className="folder-header"
            onClick={() => toggleFolder(item.id)}
            style={{ paddingLeft: `${level * 16}px` }}
          >
            <span>{item.expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}</span>
            <Folder size={16} className="folder-icon" />
            <span>{item.name}</span>
          </div>
          {item.expanded && item.children && (
            <div className="file-list">
              {item.children.map(child => renderFileItem(child, level + 1))}
            </div>
          )}
        </div>
      );
    }

    return (
      <div 
        key={item.id} 
        className={`file-item ${activeFileId === item.id ? 'active' : ''}`}
        style={{ paddingLeft: `${(level + 1) * 16}px` }}
        onClick={() => onFileSelect?.(item.id, item.name)}
      >
        <FileText size={16} />
        <span>{item.name}</span>
      </div>
    );
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-title">Project Structure</div>
        {fileStructure.map(item => renderFileItem(item))}
      </div>
    </aside>
  );
};
