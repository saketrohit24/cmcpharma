# Files Components

This directory contains components for file management in the CMC regulatory writing application.

## Components

### FileManager

A comprehensive file upload and management component that supports drag-and-drop functionality for vendor documents.

**Features:**
- **Drag & Drop Upload**: Users can drag files directly onto the upload zone
- **Browse Files**: Click-to-browse functionality with file picker
- **File Type Filtering**: Accepts PDF, DOCX, and DOC files
- **File List Display**: Shows uploaded files with names, sizes, and remove buttons
- **File Size Formatting**: Automatically formats file sizes (B, KB, MB)
- **Visual Feedback**: Upload zone changes appearance during drag operations

**Props:**
```typescript
interface FileManagerProps {
  onFilesChange: (files: UploadedFile[]) => void;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  uploadedAt: Date;
}
```

**Usage:**
```typescript
import { FileManager } from './components/Files';

const MyComponent = () => {
  const handleFilesChange = (files) => {
    console.log('Files updated:', files);
    // Handle file state changes
  };

  return (
    <FileManager onFilesChange={handleFilesChange} />
  );
};
```

## Integration

The FileManager is integrated into the RightPanel component and can be toggled on/off alongside the chat functionality. Files are managed locally in component state but can be lifted up to parent components through the `onFilesChange` callback.

## Styling

The component uses a combination of Tailwind CSS classes and custom CSS classes defined in `src/styles/regulatory.css` for consistent styling with the rest of the application.

## Future Enhancements

- File preview functionality
- Integration with cloud storage
- Progress indicators for large uploads
- File validation and error handling
- Metadata extraction from uploaded files
- Search and filter capabilities for large file lists
