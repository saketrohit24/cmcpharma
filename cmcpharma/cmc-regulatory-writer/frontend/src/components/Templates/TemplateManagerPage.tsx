import React, { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Plus, X, Edit3, Save, Zap, AlertCircle, CheckCircle } from 'lucide-react';
import { backendApi, type Template as BackendTemplate } from '../../services/backendApi';

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

interface ProjectSection {
  id: string;
  title: string;
  level: number;
  children: ProjectSection[];
}

interface ProjectStructure {
  id: string;
  name: string;
  description: string;
  type: string;
  sections: ProjectSection[];
}

export const TemplateManagerPage: React.FC<{
  onGenerateFromTemplate?: (template: Template) => Promise<void>;
  onStructureChange?: (structure: ProjectStructure) => void;
  isGenerating?: boolean;
}> = ({ onGenerateFromTemplate, onStructureChange, isGenerating = false }) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [activeTemplate, setActiveTemplate] = useState<Template | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [editingTOC, setEditingTOC] = useState<TOCItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [templateTextInput, setTemplateTextInput] = useState('');
  const [templateNameInput, setTemplateNameInput] = useState('');
  const [templateDescInput, setTemplateDescInput] = useState('');
  const [uploadStatus, setUploadStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  const [showTypeTemplateModal, setShowTypeTemplateModal] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load templates from backend on component mount
  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setIsLoading(true);
      const response = await backendApi.getTemplates();
      if (response.status === 200 && response.data) {
        // Convert backend templates to frontend format
        const frontendTemplates: Template[] = response.data.map(backendTemplate => ({
          id: backendTemplate.id,
          name: backendTemplate.name,
          description: backendTemplate.description,
          type: 'manual' as const, // Default to manual, we'll determine type later
          createdAt: new Date(),
          lastModified: new Date(),
          status: 'ready' as const,
          toc: backendTemplate.toc.map(tocItem => ({
            id: tocItem.id,
            title: tocItem.title,
            level: tocItem.level,
            pageNumber: Math.floor(Math.random() * 50) + 1
          }))
        }));
        setTemplates(frontendTemplates);
      }
    } catch (error) {
      console.error('Failed to load templates:', error);
      setUploadStatus({
        type: 'error',
        message: 'Failed to load templates from server'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (files: File[]) => {
    if (files.length === 0) return;

    setIsLoading(true);
    setUploadStatus({ type: null, message: '' });

    try {
      const file = files[0]; // Handle single file for now
      
      // Upload to backend
      const response = await backendApi.uploadTemplateFile(
        file,
        file.name.replace(/\.[^/.]+$/, ""), // Remove extension for name
        `Template uploaded from ${file.name}`
      );

      if (response.status === 200 && response.data) {
        const backendTemplate = response.data;
        
        // Convert to frontend format
        const newTemplate: Template = {
          id: backendTemplate.id,
          name: backendTemplate.name,
          description: backendTemplate.description,
          type: 'uploaded',
          createdAt: new Date(),
          lastModified: new Date(),
          status: 'ready',
          toc: backendTemplate.toc.map(tocItem => ({
            id: tocItem.id,
            title: tocItem.title,
            level: tocItem.level,
            pageNumber: Math.floor(Math.random() * 50) + 1
          }))
        };

        setTemplates(prev => [...prev, newTemplate]);
        setUploadStatus({
          type: 'success',
          message: `Template "${newTemplate.name}" uploaded successfully!`
        });

        // Update project structure if callback is provided
        if (onStructureChange) {
          try {
            const structureResponse = await backendApi.getTemplateStructure(backendTemplate.id);
            if (structureResponse.status === 200 && structureResponse.data) {
              onStructureChange(structureResponse.data);
            }
          } catch (error) {
            console.error('Failed to get template structure:', error);
          }
        }

        // Clear upload status after 3 seconds
        setTimeout(() => {
          setUploadStatus({ type: null, message: '' });
        }, 3000);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadStatus({
        type: 'error',
        message: `Failed to upload template: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files);
    }
  };

  const createTemplateFromText = async () => {
    if (!templateTextInput.trim() || !templateNameInput.trim()) return;

    setIsLoading(true);
    setUploadStatus({ type: null, message: '' });

    try {
      const request = {
        name: templateNameInput,
        description: templateDescInput || `Template created from text input`,
        toc_text: templateTextInput
      };

      const response = await backendApi.parseTemplate(request);

      if (response.status === 200 && response.data) {
        const backendTemplate = response.data;
        
        // Convert to frontend format
        const newTemplate: Template = {
          id: backendTemplate.id,
          name: backendTemplate.name,
          description: backendTemplate.description,
          type: 'manual',
          createdAt: new Date(),
          lastModified: new Date(),
          status: 'ready',
          toc: backendTemplate.toc.map(tocItem => ({
            id: tocItem.id,
            title: tocItem.title,
            level: tocItem.level,
            pageNumber: Math.floor(Math.random() * 50) + 1
          }))
        };

        setTemplates(prev => [...prev, newTemplate]);
        setUploadStatus({
          type: 'success',
          message: `Template "${newTemplate.name}" created successfully!`
        });

        // Update project structure if callback is provided
        if (onStructureChange) {
          try {
            const structureResponse = await backendApi.getTemplateStructure(backendTemplate.id);
            if (structureResponse.status === 200 && structureResponse.data) {
              onStructureChange(structureResponse.data);
            }
          } catch (error) {
            console.error('Failed to get template structure:', error);
          }
        }

        // Clear inputs
        setTemplateTextInput('');
        setTemplateNameInput('');
        setTemplateDescInput('');
        
        setTimeout(() => {
          setUploadStatus({ type: null, message: '' });
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to create template from text:', error);
      setUploadStatus({
        type: 'error',
        message: 'Failed to create template from text'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const generateFromTemplate = async (template: Template) => {
    if (onGenerateFromTemplate) {
      // Update project structure before generation
      if (onStructureChange) {
        try {
          const structureResponse = await backendApi.getTemplateStructure(template.id);
          if (structureResponse.status === 200 && structureResponse.data) {
            onStructureChange(structureResponse.data);
          }
        } catch (error) {
          console.error('Failed to get template structure:', error);
        }
      }

      await onGenerateFromTemplate(template);
    } else {
      // Fallback behavior for standalone usage
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

  const deleteTemplate = async (templateId: string) => {
    try {
      const response = await backendApi.deleteTemplate(templateId);
      if (response.status === 200) {
        setTemplates(prev => prev.filter(t => t.id !== templateId));
        if (activeTemplate?.id === templateId) {
          setActiveTemplate(null);
          setIsEditing(false);
        }
        setUploadStatus({
          type: 'success',
          message: 'Template deleted successfully'
        });
        setTimeout(() => {
          setUploadStatus({ type: null, message: '' });
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to delete template:', error);
      setUploadStatus({
        type: 'error',
        message: 'Failed to delete template'
      });
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

  const saveTemplate = async () => {
    if (!activeTemplate) return;

    try {
      const updatedTemplate = {
        ...activeTemplate,
        toc: editingTOC,
        lastModified: new Date()
      };

      // Convert to backend format
      const backendTemplate: BackendTemplate = {
        id: updatedTemplate.id,
        name: updatedTemplate.name,
        description: updatedTemplate.description,
        toc: updatedTemplate.toc.map(item => ({
          id: item.id,
          title: item.title,
          level: item.level
        }))
      };

      const response = await backendApi.saveTemplate(backendTemplate);
      if (response.status === 200) {
        setTemplates(prev => prev.map(t => 
          t.id === updatedTemplate.id ? updatedTemplate : t
        ));
        setActiveTemplate(updatedTemplate);
        setIsEditing(false);
        setUploadStatus({
          type: 'success',
          message: 'Template saved successfully'
        });
        setTimeout(() => {
          setUploadStatus({ type: null, message: '' });
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to save template:', error);
      setUploadStatus({
        type: 'error',
        message: 'Failed to save template'
      });
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
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <Upload className="w-5 h-5" />
                Upload Template
              </button>
              <button
                onClick={() => {
                  setTemplateTextInput('');
                  setTemplateNameInput('');
                  setTemplateDescInput('');
                  setShowTypeTemplateModal(true);
                }}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                <FileText className="w-5 h-5" />
                Type Template
              </button>
            </div>
          </div>

          {/* Status Messages */}
          {uploadStatus.type && (
            <div className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${
              uploadStatus.type === 'success' 
                ? 'bg-green-50 text-green-800 border border-green-200' 
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {uploadStatus.type === 'success' ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <AlertCircle className="w-5 h-5" />
              )}
              {uploadStatus.message}
            </div>
          )}
        </div>

        {/* Upload Zone */}
        <div
          className={`mb-8 border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300'
          } ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {isLoading ? 'Processing...' : 'Drag & drop template files here'}
          </h3>
          <p className="text-gray-600 mb-4">
            {isLoading ? 'Please wait while we process your template' : 'Supports PDF, TXT, DOCX, and MD files'}
          </p>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Processing...' : 'Choose Files'}
          </button>
        </div>

        {/* Templates Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {templates.map((template) => (
            <div key={template.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">{template.name}</h3>
                    <p className="text-sm text-gray-600">{template.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(template.status)}
                  <button
                    onClick={() => deleteTemplate(template.id)}
                    className="text-gray-400 hover:text-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-2">{template.toc.length} sections</p>
                <div className="max-h-32 overflow-y-auto text-sm text-gray-600">
                  {template.toc.slice(0, 5).map((item) => (
                    <div key={item.id} className={`py-1 ${item.level === 1 ? 'font-medium' : 'ml-4'}`}>
                      {item.title}
                    </div>
                  ))}
                  {template.toc.length > 5 && (
                    <div className="text-gray-400 py-1">... and {template.toc.length - 5} more</div>
                  )}
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => generateFromTemplate(template)}
                  disabled={isGenerating || template.status === 'generating'}
                  className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex-1"
                >
                  <Zap className="w-4 h-4" />
                  {template.status === 'generating' ? 'Generating...' : 'Generate'}
                </button>
                <button
                  onClick={() => {
                    setActiveTemplate(template);
                    setEditingTOC(template.toc);
                    setIsEditing(true);
                  }}
                  className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded hover:bg-gray-50"
                >
                  <Edit3 className="w-4 h-4" />
                  Edit
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.doc,.docx,.md"
          onChange={(e) => {
            if (e.target.files) {
              handleFileUpload(Array.from(e.target.files));
            }
          }}
          className="hidden"
        />

        {/* Edit Template Modal */}
        {isEditing && activeTemplate && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">Edit Template: {activeTemplate.name}</h2>
                <button
                  onClick={() => setIsEditing(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="mb-6">
                <h3 className="text-lg font-medium mb-4">Table of Contents</h3>
                <div className="space-y-2">
                  {editingTOC.map((item, index) => (
                    <div key={item.id} className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg">
                      <span className="text-sm text-gray-500 w-8">{index + 1}</span>
                      <input
                        type="text"
                        value={item.title}
                        onChange={(e) => {
                          const newTOC = [...editingTOC];
                          newTOC[index] = { ...item, title: e.target.value };
                          setEditingTOC(newTOC);
                        }}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <select
                        value={item.level}
                        onChange={(e) => {
                          const newTOC = [...editingTOC];
                          newTOC[index] = { ...item, level: parseInt(e.target.value) };
                          setEditingTOC(newTOC);
                        }}
                        className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value={1}>Level 1</option>
                        <option value={2}>Level 2</option>
                        <option value={3}>Level 3</option>
                        <option value={4}>Level 4</option>
                      </select>
                      <button
                        onClick={() => {
                          setEditingTOC(prev => prev.filter((_, i) => i !== index));
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => {
                    setEditingTOC(prev => [...prev, {
                      id: Date.now().toString(),
                      title: 'New Section',
                      level: 1
                    }]);
                  }}
                  className="mt-4 flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <Plus className="w-4 h-4" />
                  Add Section
                </button>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={saveTemplate}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Save className="w-4 h-4" />
                  Save Changes
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Text Template Modal */}
        {showTypeTemplateModal && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setShowTypeTemplateModal(false)}
          >
            <div 
              className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-xl font-bold mb-4">Create Template from Text</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
                <input
                  type="text"
                  value={templateNameInput}
                  onChange={(e) => setTemplateNameInput(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter template name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
                <input
                  type="text"
                  value={templateDescInput}
                  onChange={(e) => setTemplateDescInput(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter template description"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Template Structure</label>
                <textarea
                  value={templateTextInput}
                  onChange={(e) => setTemplateTextInput(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={12}
                  placeholder={`Enter your template structure, for example:

1. Introduction
1.1 General Information
1.2 Scope and Purpose

2. Manufacturing Process
2.1 Process Description
2.2 Critical Parameters

3. Quality Control
3.1 Analytical Methods
3.2 Specifications

4. Stability Data
4.1 Stability Protocol
4.2 Results Summary`}
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={async () => {
                  await createTemplateFromText();
                  setShowTypeTemplateModal(false);
                }}
                disabled={!templateTextInput.trim() || !templateNameInput.trim() || isLoading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {isLoading ? 'Creating...' : 'Create Template'}
              </button>
              <button
                onClick={() => {
                  setShowTypeTemplateModal(false);
                  setTemplateTextInput('');
                  setTemplateNameInput('');
                  setTemplateDescInput('');
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
        )}

      </div>
    </div>
  );
};

export default TemplateManagerPage;
