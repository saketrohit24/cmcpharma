import React, { useState } from 'react';
import { Settings, Key, CheckCircle, AlertCircle } from 'lucide-react';
import { templateGenerationService } from '../../services/templateGeneration';

interface LLMConfigProps {
  onClose: () => void;
}

export const LLMConfig: React.FC<LLMConfigProps> = ({ onClose }) => {
  const [apiKey, setApiKey] = useState('');
  const [provider, setProvider] = useState<'openai' | 'claude' | 'local'>('openai');
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSave = () => {
    if (apiKey.trim()) {
      // Enable LLM mode with the provided API key
      templateGenerationService.setLLMMode(true, apiKey);
      localStorage.setItem('llm-config', JSON.stringify({ provider, hasKey: true }));
      onClose();
    }
  };

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    try {
      // Test connection (simplified)
      await new Promise(resolve => setTimeout(resolve, 1000));
      setConnectionStatus('success');
    } catch {
      setConnectionStatus('error');
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleDisableLLM = () => {
    templateGenerationService.setLLMMode(false);
    localStorage.removeItem('llm-config');
    onClose();
  };

  return (
    <div className="llm-config-overlay">
      <div className="llm-config-modal">
        <div className="llm-config-header">
          <div className="header-icon">
            <Settings size={20} />
          </div>
          <h2>LLM Configuration</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="llm-config-content">
          <div className="config-section">
            <h3>AI Provider</h3>
            <div className="provider-options">
              <label className={`provider-option ${provider === 'openai' ? 'selected' : ''}`}>
                <input 
                  type="radio" 
                  value="openai" 
                  checked={provider === 'openai'}
                  onChange={(e) => setProvider(e.target.value as 'openai')}
                />
                <span>OpenAI (GPT-4)</span>
              </label>
              <label className={`provider-option ${provider === 'claude' ? 'selected' : ''}`}>
                <input 
                  type="radio" 
                  value="claude" 
                  checked={provider === 'claude'}
                  onChange={(e) => setProvider(e.target.value as 'claude')}
                />
                <span>Anthropic Claude</span>
              </label>
              <label className={`provider-option ${provider === 'local' ? 'selected' : ''}`}>
                <input 
                  type="radio" 
                  value="local" 
                  checked={provider === 'local'}
                  onChange={(e) => setProvider(e.target.value as 'local')}
                />
                <span>Local Model</span>
              </label>
            </div>
          </div>

          <div className="config-section">
            <h3>API Configuration</h3>
            <div className="api-key-input">
              <div className="input-group">
                <Key size={16} />
                <input
                  type="password"
                  placeholder="Enter your API key"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
              </div>
              
              {connectionStatus === 'success' && (
                <div className="status-message success">
                  <CheckCircle size={16} />
                  <span>Connection successful</span>
                </div>
              )}
              
              {connectionStatus === 'error' && (
                <div className="status-message error">
                  <AlertCircle size={16} />
                  <span>Connection failed</span>
                </div>
              )}
            </div>

            <button 
              className="test-connection-btn"
              onClick={handleTestConnection}
              disabled={!apiKey || isTestingConnection}
            >
              {isTestingConnection ? 'Testing...' : 'Test Connection'}
            </button>
          </div>

          <div className="config-section">
            <h3>Generation Settings</h3>
            <div className="setting-row">
              <label>Use AI for generation</label>
              <input type="checkbox" defaultChecked />
            </div>
            <div className="setting-row">
              <label>Fallback to mock content</label>
              <input type="checkbox" defaultChecked />
            </div>
          </div>
        </div>

        <div className="llm-config-footer">
          <button className="btn btn-secondary" onClick={handleDisableLLM}>
            Use Mock Content
          </button>
          <button 
            className="btn btn-primary"
            onClick={handleSave}
            disabled={!apiKey.trim()}
          >
            Save & Enable AI
          </button>
        </div>
      </div>
    </div>
  );
};
