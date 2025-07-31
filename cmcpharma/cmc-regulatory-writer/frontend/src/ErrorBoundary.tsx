import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('🚨 React Error Boundary caught an error:', error);
    console.error('📋 Error Info:', errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '20px', 
          border: '2px solid red', 
          backgroundColor: '#ffe6e6', 
          fontFamily: 'monospace',
          margin: '20px'
        }}>
          <h1 style={{ color: 'red' }}>🚨 React App Crashed!</h1>
          <h2>Error Details:</h2>
          <pre style={{ 
            backgroundColor: '#fff', 
            padding: '10px', 
            border: '1px solid #ccc',
            overflow: 'auto',
            maxHeight: '200px'
          }}>
            {this.state.error?.toString()}
          </pre>
          
          {this.state.errorInfo && (
            <>
              <h3>Component Stack:</h3>
              <pre style={{ 
                backgroundColor: '#fff', 
                padding: '10px', 
                border: '1px solid #ccc',
                overflow: 'auto',
                maxHeight: '300px'
              }}>
                {this.state.errorInfo.componentStack}
              </pre>
            </>
          )}
          
          <button 
            onClick={() => window.location.reload()} 
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '5px',
              marginTop: '10px'
            }}
          >
            🔄 Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}