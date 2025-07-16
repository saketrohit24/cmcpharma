/**
 * Connection Test Component to verify backend connectivity
 */

import React, { useState, useEffect } from 'react';
import { templateGenerationService, type GeneratedDocument } from '../services/templateGeneration';
import { fileService } from '../services/fileService';
import { exportService } from '../services/exportService';
import { backendApi } from '../services/backendApi';

interface ConnectionStatus {
  backend: 'testing' | 'connected' | 'failed';
  templateService: 'testing' | 'working' | 'failed';
  fileService: 'testing' | 'working' | 'failed';
  exportService: 'testing' | 'working' | 'failed';
}

const ConnectionTest: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatus>({
    backend: 'testing',
    templateService: 'testing',
    fileService: 'testing',
    exportService: 'testing'
  });

  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testBackendConnection = async () => {
    try {
      addLog('Testing backend connection...');
      const isConnected = await templateGenerationService.testBackendConnection();
      
      if (isConnected) {
        setStatus(prev => ({ ...prev, backend: 'connected' }));
        addLog('✅ Backend connection successful');
        return true;
      } else {
        setStatus(prev => ({ ...prev, backend: 'failed' }));
        addLog('❌ Backend connection failed');
        return false;
      }
    } catch (error) {
      setStatus(prev => ({ ...prev, backend: 'failed' }));
      addLog(`❌ Backend connection error: ${error}`);
      return false;
    }
  };

  const testTemplateService = async () => {
    try {
      addLog('Testing template service...');
      
      const template = await templateGenerationService.createTemplateFromText(
        'Test Template',
        'A test template for connection verification',
        `1. Introduction
        2. Methods
        3. Results
        4. Conclusion`
      );
      
      if (template && template.id) {
        setStatus(prev => ({ ...prev, templateService: 'working' }));
        addLog('✅ Template service working');
        addLog(`Created template: ${template.name} with ${template.toc.length} sections`);
        
        // Test document generation
        addLog('Testing document generation...');
        const document = await templateGenerationService.generateDocument(template);
        
        if (document && document.id) {
          addLog('✅ Document generation working');
          addLog(`Generated document: ${document.title} with ${document.sections.length} sections`);
          return { template, document };
        }
      }
      
      throw new Error('Template or document creation failed');
    } catch (error) {
      setStatus(prev => ({ ...prev, templateService: 'failed' }));
      addLog(`❌ Template service error: ${error}`);
      return null;
    }
  };

  const testFileService = async () => {
    try {
      addLog('Testing file service...');
      
      // Create a test file
      const testContent = 'This is a test file for connection verification';
      const testFile = new File([testContent], 'test.txt', { type: 'text/plain' });
      
      // Test file validation
      const validation = fileService.validateFile(testFile);
      if (!validation.valid) {
        throw new Error(`File validation failed: ${validation.error}`);
      }
      
      addLog('✅ File validation working');
      
      // Test file size formatting
      const formattedSize = fileService.formatFileSize(testFile.size);
      addLog(`File size formatting: ${formattedSize}`);
      
      setStatus(prev => ({ ...prev, fileService: 'working' }));
      addLog('✅ File service working');
      
      return testFile;
    } catch (error) {
      setStatus(prev => ({ ...prev, fileService: 'failed' }));
      addLog(`❌ File service error: ${error}`);
      return null;
    }
  };

  const testExportService = async (document: GeneratedDocument) => {
    try {
      addLog('Testing export service...');
      
      if (!document) {
        throw new Error('No document provided for export test');
      }
      
      // Test PDF export
      const exportResult = await exportService.exportDocument(document, { format: 'pdf' });
      
      if (exportResult.success && exportResult.blob) {
        setStatus(prev => ({ ...prev, exportService: 'working' }));
        addLog('✅ Export service working');
        addLog(`Export successful: ${exportResult.filename} (${exportResult.blob.size} bytes)`);
        return true;
      } else {
        throw new Error(exportResult.error || 'Export failed');
      }
    } catch (error) {
      setStatus(prev => ({ ...prev, exportService: 'failed' }));
      addLog(`❌ Export service error: ${error}`);
      return false;
    }
  };

  const runAllTests = async () => {
    setLogs([]);
    addLog('Starting comprehensive connection test...');
    
    // Reset status
    setStatus({
      backend: 'testing',
      templateService: 'testing',
      fileService: 'testing',
      exportService: 'testing'
    });

    // Test backend connection
    await testBackendConnection();
    
    // Test template service
    const templateResult = await testTemplateService();
    
    // Test file service
    await testFileService();
    
    // Test export service
    if (templateResult?.document) {
      await testExportService(templateResult.document);
    }
    
    addLog('All tests completed!');
  };

  useEffect(() => {
    runAllTests();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'testing': return '🔄';
      case 'connected':
      case 'working': return '✅';
      case 'failed': return '❌';
      default: return '❓';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'testing': return 'text-yellow-600';
      case 'connected':
      case 'working': return 'text-green-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Backend Connection Test</h2>
      
      {/* Status Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-4 border rounded-lg">
          <div className="text-2xl mb-2">{getStatusIcon(status.backend)}</div>
          <div className="font-semibold">Backend</div>
          <div className={`text-sm ${getStatusColor(status.backend)}`}>
            {status.backend}
          </div>
        </div>
        
        <div className="text-center p-4 border rounded-lg">
          <div className="text-2xl mb-2">{getStatusIcon(status.templateService)}</div>
          <div className="font-semibold">Templates</div>
          <div className={`text-sm ${getStatusColor(status.templateService)}`}>
            {status.templateService}
          </div>
        </div>
        
        <div className="text-center p-4 border rounded-lg">
          <div className="text-2xl mb-2">{getStatusIcon(status.fileService)}</div>
          <div className="font-semibold">Files</div>
          <div className={`text-sm ${getStatusColor(status.fileService)}`}>
            {status.fileService}
          </div>
        </div>
        
        <div className="text-center p-4 border rounded-lg">
          <div className="text-2xl mb-2">{getStatusIcon(status.exportService)}</div>
          <div className="font-semibold">Export</div>
          <div className={`text-sm ${getStatusColor(status.exportService)}`}>
            {status.exportService}
          </div>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={runAllTests}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Run All Tests
        </button>
        
        <button
          onClick={testBackendConnection}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Test Backend Only
        </button>
        
        <button
          onClick={() => setLogs([])}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Clear Logs
        </button>
      </div>

      {/* Logs */}
      <div className="bg-gray-100 p-4 rounded-lg h-64 overflow-y-auto">
        <h3 className="font-semibold mb-2">Test Logs:</h3>
        {logs.length === 0 ? (
          <div className="text-gray-500">No logs yet...</div>
        ) : (
          <div className="space-y-1">
            {logs.map((log, index) => (
              <div key={index} className="text-sm font-mono">
                {log}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* API Information */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold mb-2">Connection Information:</h3>
        <div className="text-sm space-y-1">
          <div><strong>Backend API:</strong> http://localhost:8000</div>
          <div><strong>Frontend:</strong> http://localhost:5179</div>
          <div><strong>Session ID:</strong> {backendApi.getSessionId()}</div>
        </div>
      </div>
    </div>
  );
};

export default ConnectionTest;
