import React, { useState, useRef } from 'react';
import { Upload, FileText, Plus, X, Edit3, Save, BookOpen, List, Zap } from 'lucide-react';

export interface TOCItem {
  id: string;
  title: string;
  level: number;
  pageNumber?: number;
  children?: TOCItem[];
}

export interface Template {
  id: string;
  name: string;
  description: string;
  type: 'uploaded' | 'manual';
  createdAt: Date;
  lastModified: Date;
  toc: TOCItem[];
  content?: string;
  status: 'draft' | 'ready' | 'generating';
}

const sampleTemplates: Template[] = [
  {
    id: '1',
    name: 'Module 3.2.S Drug Substance',
    description: 'Complete template for drug substance documentation',
    type: 'manual',
    createdAt: new Date('2024-01-15'),
    lastModified: new Date('2024-01-20'),
    status: 'ready',
    toc: [
      { id: '1', title: '3.2.S.1 General Information', level: 1, pageNumber: 1 },
      { id: '2', title: '3.2.S.1.1 Nomenclature', level: 2, pageNumber: 2 },
      { id: '3', title: '3.2.S.1.2 Structure', level: 2, pageNumber: 3 },
      { id: '4', title: '3.2.S.1.3 General Properties', level: 2, pageNumber: 4 },
      { id: '5', title: '3.2.S.2 Manufacture', level: 1, pageNumber: 5 },
      { id: '6', title: '3.2.S.2.1 Manufacturer(s)', level: 2, pageNumber: 6 },
      { id: '7', title: '3.2.S.2.2 Description of Manufacturing Process', level: 2, pageNumber: 7 },
      { id: '8', title: '3.2.S.2.3 Control of Materials', level: 2, pageNumber: 8 },
      { id: '9', title: '3.2.S.3 Characterisation', level: 1, pageNumber: 9 },
      { id: '10', title: '3.2.S.4 Control of Drug Substance', level: 1, pageNumber: 10 },
    ]
  },
  {
    id: '2',
    name: 'Module 3.2.P Drug Product',
    description: 'Template for drug product documentation',
    type: 'uploaded',
    createdAt: new Date('2024-01-10'),
    lastModified: new Date('2024-01-18'),
    status: 'ready',
    toc: [
      { id: '1', title: '3.2.P.1 Description and Composition', level: 1, pageNumber: 1 },
      { id: '2', title: '3.2.P.2 Pharmaceutical Development', level: 1, pageNumber: 2 },
      { id: '3', title: '3.2.P.3 Manufacture', level: 1, pageNumber: 3 },
      { id: '4', title: '3.2.P.4 Control of Excipients', level: 1, pageNumber: 4 },
      { id: '5', title: '3.2.P.5 Control of Drug Product', level: 1, pageNumber: 5 },
    ]
  }
];

export const TemplateManagerPage: React.FC<{
  onGenerateFromTemplate?: (template: Template) => Promise<void>;
  isGenerating?: boolean;
}> = ({ onGenerateFromTemplate, isGenerating = false }) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [activeTemplate, setActiveTemplate] = useState<Template | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [editingTOC, setEditingTOC] = useState<TOCItem[]>([]);
  const [templateName, setTemplateName] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    setTemplates(sampleTemplates);
  }, []);

  const handleFileUpload = (files: File[]) => {
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        const toc = parseTOCFromContent(content, file.name);
        
        const newTemplate: Template = {
          id: Date.now().toString(),
          name: file.name.replace(/\.[^/.]+$/, ""),
          description: `Uploaded template from ${file.name}`,
          type: 'uploaded',
          createdAt: new Date(),
          lastModified: new Date(),
          status: 'ready',
          toc: toc,
          content: content
        };
        
        setTemplates(prev => [...prev, newTemplate]);
      };
      reader.readAsText(file);
    });
  };

  const parseTOCFromContent = (content: string, filename: string): TOCItem[] => {
    // Simple TOC parsing - in real implementation, this would be more sophisticated
    const lines = content.split('\n');
    const tocItems: TOCItem[] = [];
    let id = 1;

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.length > 0 && (
        trimmed.match(/^\d+\./) || 
        trimmed.match(/^[A-Z]\d+\./) ||
        trimmed.includes('Section') ||
        trimmed.includes('Chapter')
      )) {
        const level = (line.match(/^(\s*)/)?.[1]?.length || 0) < 4 ? 1 : 2;
        tocItems.push({
          id: (id++).toString(),
          title: trimmed,
          level: level,
          pageNumber: Math.floor(Math.random() * 50) + 1
        });
      }
    });

    return tocItems.length > 0 ? tocItems : [
      { id: '1', title: `Content from ${filename}`, level: 1, pageNumber: 1 }
    ];
  };

  const createNewTemplate = () => {
    const newTemplate: Template = {
      id: Date.now().toString(),
      name: templateName || 'New Template',
      description: templateDescription || 'Custom template',
      type: 'manual',
      createdAt: new Date(),
      lastModified: new Date(),
      status: 'draft',
      toc: [
        { id: '1', title: 'Introduction', level: 1, pageNumber: 1 },
        { id: '2', title: 'Overview', level: 2, pageNumber: 2 },
        { id: '3', title: 'Main Content', level: 1, pageNumber: 3 },
      ]
    };
    
    setTemplates(prev => [...prev, newTemplate]);
    setActiveTemplate(newTemplate);
    setEditingTOC([...newTemplate.toc]);
    setIsEditing(true);
    setTemplateName('');
    setTemplateDescription('');
  };

  const addTOCItem = () => {
    const newItem: TOCItem = {
      id: Date.now().toString(),
      title: 'New Section',
      level: 1,
      pageNumber: editingTOC.length + 1
    };
    setEditingTOC(prev => [...prev, newItem]);
  };

  const updateTOCItem = (id: string, updates: Partial<TOCItem>) => {
    setEditingTOC(prev => prev.map(item => 
      item.id === id ? { ...item, ...updates } : item
    ));
  };

  const removeTOCItem = (id: string) => {
    setEditingTOC(prev => prev.filter(item => item.id !== id));
  };

  const saveTOC = () => {
    if (activeTemplate) {
      const updatedTemplate = {
        ...activeTemplate,
        toc: editingTOC,
        lastModified: new Date(),
        status: 'ready' as const
      };
      
      setTemplates(prev => prev.map(t => 
        t.id === activeTemplate.id ? updatedTemplate : t
      ));
      setActiveTemplate(updatedTemplate);
      setIsEditing(false);
    }
  };

  const generateFromTemplate = async (template: Template) => {
    if (onGenerateFromTemplate) {
      // Use the callback from parent component
      await onGenerateFromTemplate(template);
    } else {
      // Fallback to original behavior for standalone usage
      const updatedTemplate = { ...template, status: 'generating' as const };
      setTemplates(prev => prev.map(t => 
        t.id === template.id ? updatedTemplate : t
      ));

      setTimeout(() => {
        const finalTemplate = { ...updatedTemplate, status: 'ready' as const };
        setTemplates(prev => prev.map(t => 
          t.id === template.id ? finalTemplate : t
        ));
        
        alert(`Template "${template.name}" has been generated and is ready for editing!`);
      }, 3000);
    }
  };

  const deleteTemplate = (templateId: string) => {
    setTemplates(prev => prev.filter(t => t.id !== templateId));
    if (activeTemplate?.id === templateId) {
      setActiveTemplate(null);
      setIsEditing(false);
    }
  };

  const getStatusBadge = (status: Template['status']) => {
    switch (status) {
      case 'draft':
        return <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">Draft</span>;
      case 'ready':
        return <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Ready</span>;
      case 'generating':
        return <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">Generating...</span>;
      default:
        return null;
    }
  };

  return (
    <div className="template-manager-page min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Template Manager</h1>
              <p className="text-gray-600 mt-1">Create, upload, and manage document templates</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Upload size={16} />
                Upload Template
              </button>
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-3">
                <BookOpen className="text-blue-500" size={24} />
                <div>
                  <p className="text-sm text-gray-600">Total Templates</p>
                  <p className="text-2xl font-semibold">{templates.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-3">
                <FileText className="text-green-500" size={24} />
                <div>
                  <p className="text-sm text-gray-600">Ready Templates</p>
                  <p className="text-2xl font-semibold">{templates.filter(t => t.status === 'ready').length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-3">
                <Edit3 className="text-purple-500" size={24} />
                <div>
                  <p className="text-sm text-gray-600">Draft Templates</p>
                  <p className="text-2xl font-semibold">{templates.filter(t => t.status === 'draft').length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-3">
                <Zap className="text-orange-500" size={24} />
                <div>
                  <p className="text-sm text-gray-600">Generating</p>
                  <p className="text-2xl font-semibold">{templates.filter(t => t.status === 'generating').length}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Templates List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg border overflow-hidden">
              <div className="p-4 border-b bg-gray-50">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Templates</h3>
                  <button
                    onClick={() => {
                      setActiveTemplate(null);
                      setIsEditing(true);
                      setEditingTOC([]);
                    }}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <Plus size={16} />
                  </button>
                </div>
              </div>
              <div className="divide-y max-h-96 overflow-y-auto">
                {templates.map(template => (
                  <div
                    key={template.id}
                    className={`p-4 cursor-pointer transition-colors ${
                      activeTemplate?.id === template.id ? 'bg-blue-50 border-l-4 border-blue-500' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => {
                      setActiveTemplate(template);
                      setEditingTOC([...template.toc]);
                      setIsEditing(false);
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 truncate">{template.name}</h4>
                        <p className="text-sm text-gray-500 mt-1 line-clamp-2">{template.description}</p>
                        <div className="flex items-center gap-2 mt-2">
                          {getStatusBadge(template.status)}
                          <span className="text-xs text-gray-400">
                            {template.type === 'uploaded' ? '📄' : '✏️'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Create New Template */}
            <div className="mt-4 bg-white rounded-lg border p-4">
              <h4 className="font-medium mb-3">Create New Template</h4>
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Template name"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <textarea
                  placeholder="Description"
                  value={templateDescription}
                  onChange={(e) => setTemplateDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={2}
                />
                <button
                  onClick={createNewTemplate}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                >
                  <Plus size={16} />
                  Create Template
                </button>
              </div>
            </div>
          </div>

          {/* Template Editor/Viewer */}
          <div className="lg:col-span-2">
            {activeTemplate || isEditing ? (
              <div className="bg-white rounded-lg border">
                <div className="p-4 border-b bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">
                        {isEditing && !activeTemplate ? 'New Template' : activeTemplate?.name}
                      </h3>
                      {activeTemplate && (
                        <p className="text-sm text-gray-500 mt-1">{activeTemplate.description}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {activeTemplate && !isEditing && (
                        <>
                          <button
                            onClick={() => generateFromTemplate(activeTemplate)}
                            disabled={activeTemplate.status === 'generating' || isGenerating}
                            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
                          >
                            <Zap size={14} />
                            {(activeTemplate.status === 'generating' || isGenerating) ? 'Generating...' : 'Generate'}
                          </button>
                          <button
                            onClick={() => setIsEditing(true)}
                            className="flex items-center gap-2 px-3 py-1.5 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                          >
                            <Edit3 size={14} />
                            Edit
                          </button>
                          <button
                            onClick={() => deleteTemplate(activeTemplate.id)}
                            className="flex items-center gap-2 px-3 py-1.5 text-red-600 border border-red-300 rounded hover:bg-red-50 transition-colors"
                          >
                            <X size={14} />
                            Delete
                          </button>
                        </>
                      )}
                      {isEditing && (
                        <div className="flex gap-2">
                          <button
                            onClick={saveTOC}
                            className="flex items-center gap-2 px-3 py-1.5 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                          >
                            <Save size={14} />
                            Save
                          </button>
                          <button
                            onClick={() => {
                              setIsEditing(false);
                              if (activeTemplate) {
                                setEditingTOC([...activeTemplate.toc]);
                              }
                            }}
                            className="flex items-center gap-2 px-3 py-1.5 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                          >
                            <X size={14} />
                            Cancel
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* TOC Editor/Viewer */}
                <div className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium flex items-center gap-2">
                      <List size={16} />
                      Table of Contents
                    </h4>
                    {isEditing && (
                      <button
                        onClick={addTOCItem}
                        className="flex items-center gap-1 text-sm px-2 py-1 text-blue-600 hover:bg-blue-50 rounded"
                      >
                        <Plus size={14} />
                        Add Section
                      </button>
                    )}
                  </div>

                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {editingTOC.map((item) => (
                      <div
                        key={item.id}
                        className={`flex items-center gap-3 p-3 border rounded ${
                          item.level === 2 ? 'ml-6 bg-gray-50' : 'bg-white'
                        }`}
                      >
                        {isEditing ? (
                          <>
                            <select
                              value={item.level}
                              onChange={(e) => updateTOCItem(item.id, { level: parseInt(e.target.value) })}
                              className="px-2 py-1 border rounded text-sm"
                            >
                              <option value={1}>Level 1</option>
                              <option value={2}>Level 2</option>
                            </select>
                            <input
                              type="text"
                              value={item.title}
                              onChange={(e) => updateTOCItem(item.id, { title: e.target.value })}
                              className="flex-1 px-2 py-1 border rounded text-sm"
                              placeholder="Section title"
                            />
                            <input
                              type="number"
                              value={item.pageNumber || ''}
                              onChange={(e) => updateTOCItem(item.id, { pageNumber: parseInt(e.target.value) || undefined })}
                              className="w-16 px-2 py-1 border rounded text-sm"
                              placeholder="Page"
                            />
                            <button
                              onClick={() => removeTOCItem(item.id)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <X size={14} />
                            </button>
                          </>
                        ) : (
                          <>
                            <div className="flex-1">
                              <div className={`font-medium ${item.level === 2 ? 'text-sm' : ''}`}>
                                {item.title}
                              </div>
                            </div>
                            <div className="text-sm text-gray-500">
                              Page {item.pageNumber}
                            </div>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg border p-8 text-center">
                <BookOpen size={64} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Template Selected</h3>
                <p className="text-gray-500 mb-4">
                  Select a template from the list or create a new one to get started.
                </p>
                
                {/* Upload Zone */}
                <div
                  className={`upload-zone border-2 border-dashed rounded-lg p-8 text-center transition-all ${
                    isDragging 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                  }`}
                  onDrop={(e) => {
                    e.preventDefault();
                    setIsDragging(false);
                    const files = Array.from(e.dataTransfer.files);
                    handleFileUpload(files);
                  }}
                  onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                  onDragLeave={() => setIsDragging(false)}
                >
                  <Upload size={48} className="mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-600 mb-2">Drop template files here, or</p>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="btn btn-primary"
                  >
                    Browse Files
                  </button>
                  <p className="text-sm text-gray-500 mt-2">Supports TXT, DOCX, PDF files</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.docx,.pdf,.doc"
          className="hidden"
          onChange={(e) => {
            const files = Array.from(e.target.files || []);
            handleFileUpload(files);
          }}
        />
      </div>
    </div>
  );
};
