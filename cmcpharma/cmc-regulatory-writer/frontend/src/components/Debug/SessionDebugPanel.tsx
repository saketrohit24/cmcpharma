import React, { useState, useEffect } from 'react';
import { backendApi } from '../../services/backendApi';
import { useFiles } from '../../contexts/useFiles';
import type { UploadedFile } from '../../contexts/FileContext';

interface SessionFile {
  id: string;
  name: string;
  size: number;
  mime_type: string;
  path: string;
}

export const SessionDebugPanel: React.FC = () => {
  const [sessionFiles, setSessionFiles] = useState<SessionFile[]>([]);
  const [loading, setLoading] = useState(false);
  const { files } = useFiles();

  const refreshSessionFiles = async () => {
    setLoading(true);
    try {
      const sessionId = backendApi.getSessionId();
      console.log('SessionDebugPanel: Refreshing files for session:', sessionId);
      const response = await fetch(`http://localhost:8001/api/files/session/${sessionId}`);
      if (response.ok) {
        const files = await response.json();
        setSessionFiles(files);
        console.log('SessionDebugPanel: Found', files.length, 'backend files');
      } else {
        console.log('SessionDebugPanel: No files found, status:', response.status);
        setSessionFiles([]);
      }
    } catch (error) {
      console.error('SessionDebugPanel: Error fetching session files:', error);
      setSessionFiles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshSessionFiles();
  }, []);

  return (
    <div className="session-debug-panel bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-yellow-800">Session Debug Info</h3>
        <button
          onClick={refreshSessionFiles}
          disabled={loading}
          className="text-xs bg-yellow-100 hover:bg-yellow-200 px-2 py-1 rounded"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      
      <div className="text-xs space-y-2">
        <div>
          <strong>Session ID:</strong> <span className="font-mono">{backendApi.getSessionId()}</span>
          <button 
            onClick={() => {
              backendApi.setSessionId('session_1752696706836_z3ezer644');
              refreshSessionFiles();
            }}
            className="ml-2 text-xs bg-blue-100 hover:bg-blue-200 px-2 py-1 rounded"
          >
            Use Session with Files
          </button>
        </div>
        
        <div>
          <strong>Frontend Files ({files.length}):</strong>
          {files.length > 0 ? (
            <ul className="ml-4 mt-1">
              {files.map((file: any) => (
                <li key={file.id} className="flex items-center space-x-2">
                  <span className={`inline-block w-2 h-2 rounded-full ${
                    file.status === 'ready' ? 'bg-green-500' : 
                    file.status === 'processing' ? 'bg-yellow-500' :
                    file.status === 'error' ? 'bg-red-500' : 'bg-gray-500'
                  }`}></span>
                  <span>{file.name} ({file.status})</span>
                </li>
              ))}
            </ul>
          ) : (
            <span className="text-gray-500 ml-2">None</span>
          )}
        </div>
        
        <div>
          <strong>Backend Files ({sessionFiles.length}):</strong>
          {sessionFiles.length > 0 ? (
            <ul className="ml-4 mt-1">
              {sessionFiles.map((file) => (
                <li key={file.id}>
                  {file.name} ({file.size} bytes)
                </li>
              ))}
            </ul>
          ) : (
            <span className="text-gray-500 ml-2">None</span>
          )}
        </div>
      </div>
    </div>
  );
};
