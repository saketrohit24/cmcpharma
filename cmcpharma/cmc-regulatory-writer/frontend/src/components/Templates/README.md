# Templates Components

This directory contains components for template management in the CMC regulatory writing application.

## Components

### TemplateManagerPage

A comprehensive template management interface that allows users to create, upload, and manage document templates with Table of Contents (TOC) structures.

**Features:**
- **Template Creation**: Manual template creation with custom TOC
- **File Upload**: Upload existing templates (TXT, DOCX, PDF, DOC)
- **TOC Editor**: Visual editing of hierarchical table of contents
- **Template Operations**: Generate, edit, delete templates
- **Status Tracking**: Monitor template states (Draft, Ready, Generating)
- **Auto-parsing**: Extract TOC structure from uploaded files

**Props:**
```typescript
// No props required - self-contained page component
```

**Key Interfaces:**
```typescript
interface TOCItem {
  id: string;
  title: string;
  level: number;        // 1 = main section, 2 = subsection
  pageNumber?: number;
  children?: TOCItem[];
}

interface Template {
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
```

## Integration

### Navigation
- Accessible via "Templates" tab in header navigation
- Connected to "Generate from template" button in RightPanel
- Seamless switching between Editor, Files, and Templates views

### Workflow
1. **Create/Upload**: Create new templates or upload existing files
2. **Edit TOC**: Build hierarchical table of contents structure
3. **Generate**: Create documents based on template structure
4. **Return to Editor**: Work with generated content in main editor

## Sample Templates

The component includes pre-loaded regulatory templates:

### Module 3.2.S Drug Substance
- Complete ICH M4 structure
- Sections: General Information, Manufacture, Characterisation, Control
- Hierarchical subsections with proper numbering

### Module 3.2.P Drug Product
- ICH M4 drug product structure
- Sections: Description, Development, Manufacture, Excipients, Control
- Standard pharmaceutical documentation format

## File Upload & Processing

### Supported Formats
- **TXT**: Plain text files with section headers
- **DOCX**: Microsoft Word documents
- **PDF**: Portable Document Format files
- **DOC**: Legacy Microsoft Word format

### Auto-parsing Features
- Detects section headers and hierarchical structure
- Assigns appropriate heading levels (1 or 2)
- Generates page numbers automatically
- Recognizes common regulatory document patterns

## TOC Management

### Interactive Editor
- **Add Sections**: Dynamic addition of TOC items
- **Edit Titles**: In-place editing of section names
- **Set Hierarchy**: Choose between Level 1 and Level 2
- **Page Numbers**: Assign page numbers to sections
- **Remove Items**: Delete unwanted sections

### Smart Features
- **Auto-numbering**: Intelligent page number assignment
- **Level Management**: Proper hierarchical structure
- **Validation**: Ensures logical section organization

## Template Operations

### Create
- Manual template creation with custom structure
- Name and description assignment
- Initial TOC scaffolding

### Edit
- Modify existing templates
- Update TOC structure
- Change template metadata

### Generate
- One-click document generation from templates
- Status tracking during generation process
- Integration with main document editor

### Delete
- Remove unwanted templates
- Confirmation for destructive actions
- Clean up associated resources

## Usage Examples

### Basic Template Creation
```typescript
// Navigate to Templates page
// 1. Enter template name and description
// 2. Click "Create Template"
// 3. Add TOC sections using the editor
// 4. Set section titles and hierarchy
// 5. Save template
```

### Upload and Process
```typescript
// Upload existing document
// 1. Drag file to upload zone or browse
// 2. System auto-parses TOC structure
// 3. Review and edit extracted sections
// 4. Save processed template
```

### Generate Document
```typescript
// Create document from template
// 1. Select a Ready template
// 2. Click "Generate" button
// 3. Monitor generation progress
// 4. Navigate to Editor to work with content
```

## Styling

The component uses a combination of:
- **Tailwind CSS**: Utility classes for responsive design
- **Custom CSS**: Specialized styles in `regulatory.css`
- **Interactive Elements**: Hover effects, transitions, animations
- **Status Indicators**: Color-coded badges and progress states

## Future Enhancements

### Planned Features
- **Template Versioning**: Track changes and maintain history
- **Collaboration**: Share templates with team members
- **Template Library**: Curated regulatory template collection
- **Advanced Parsing**: Enhanced content extraction
- **Compliance Checking**: Regulatory requirement validation

### AI Integration
- **Smart TOC Generation**: AI-suggested table of contents
- **Content Prediction**: Predict sections based on document type
- **Regulatory Intelligence**: Suggest sections based on regulations
- **Quality Assessment**: Evaluate template completeness

---

## Component Structure

```
Templates/
├── TemplateManagerPage.tsx     # Main template management interface
├── index.ts                    # Component exports
├── README.md                   # This documentation file
└── TEMPLATE_SYSTEM_GUIDE.md    # Comprehensive usage guide
```

The TemplateManagerPage provides a complete solution for template management, from creation and upload to editing and document generation, fully integrated with the CMC regulatory writing workflow.
