import { useContext } from 'react';
import { FileContext, type FileContextType } from './FileContext';

export const useFiles = (): FileContextType => {
  const context = useContext(FileContext);
  if (!context) {
    throw new Error('useFiles must be used within a FileProvider');
  }
  return context;
};
