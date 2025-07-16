# Template Management System - Complete Guide

## Overview
The CMC Regulatory Writer now includes a comprehensive template management system that allows users to create, upload, and manage document templates with Table of Contents (TOC) structures for automated document generation.

## Features

### 📚 **Template Manager Page**
A dedicated full-page interface for comprehensive template management accessible via the "Templates" tab in the header.

### 🎯 **Core Capabilities**

#### **Template Creation**
- **Manual Creation**: Build templates from scratch with custom TOC
- **File Upload**: Upload existing templates (TXT, DOCX, PDF, DOC)
- **Auto-parsing**: Automatically extract TOC structure from uploaded files
- **Smart Categorization**: Intelligent section detection and organization

#### **TOC Management** 
- **Visual Editor**: Interactive editing of table of contents
- **Hierarchical Structure**: Support for multiple heading levels (Level 1, Level 2)
- **Page Numbers**: Assign page numbers to sections
- **Drag & Drop**: Reorder sections easily
- **Add/Remove**: Dynamic addition and removal of TOC items

#### **Template Operations**
- **Generate Documents**: One-click generation from templates
- **Edit Templates**: Modify existing templates and TOC structures  
- **Delete Templates**: Remove unwanted templates
- **Status Tracking**: Monitor template states (Draft, Ready, Generating)

## Navigation & Access

### **Multiple Access Points**
1. **Header Tab**: Click "Templates" in the main navigation
2. **Generate Button**: Click "Generate from template" in the right panel
3. **Direct Navigation**: Integrated with the main application workflow

### **Seamless Integration**
- Switch between Editor, Files, and Templates views
- Templates connect to document generation workflow
- Generated content appears in the main editor

## Template Types

### **Manual Templates**
- **Created**: Built using the in-app template editor
- **Features**: Custom TOC, editable structure, flexible organization
- **Use Case**: Creating standardized document structures from scratch

### **Uploaded Templates**
- **Source**: Uploaded from existing files
- **Parsing**: Automatic TOC extraction from content
- **Formats**: TXT, DOCX, PDF, DOC support
- **Use Case**: Converting existing documents into reusable templates

## Template Status System

### **📝 Draft**
- Template is being created or edited
- TOC structure may be incomplete
- Not ready for document generation

### **✅ Ready** 
- Template is complete and validated
- TOC structure is finalized
- Available for document generation

### **⚡ Generating**
- Template is being used to generate a document
- Shows progress during generation process
- Temporarily unavailable for editing

## Usage Workflow

### **Creating a New Template**

1. **Navigate to Templates**
   - Click "Templates" tab in header
   - Or click "Generate from template" in right panel

2. **Create Template**
   - Enter template name and description
   - Click "Create Template"
   - Template opens in edit mode

3. **Build TOC Structure**
   - Add sections using "Add Section" button
   - Set section titles and hierarchy levels
   - Assign page numbers
   - Use Level 1 for main sections, Level 2 for subsections

4. **Save Template**
   - Click "Save" to finalize template
   - Status changes from Draft to Ready

### **Uploading an Existing Template**

1. **Upload File**
   - Drag file to upload zone or click "Browse Files"
   - Supported formats: TXT, DOCX, PDF, DOC

2. **Auto-processing**
   - System extracts TOC structure from content
   - Sections are automatically detected and organized
   - Page numbers are assigned

3. **Review & Edit**
   - Select uploaded template from list
   - Review auto-generated TOC
   - Edit sections if needed
   - Save changes

### **Generating Documents from Templates**

1. **Select Template**
   - Choose a Ready template from the list
   - Review TOC structure

2. **Generate Document**
   - Click "Generate" button
   - Template status changes to "Generating"
   - System creates document based on TOC structure

3. **Access Generated Content**
   - Generated document appears in main editor
   - Navigate back to Editor view to work with content
   - Content follows the template's TOC structure

## Sample Templates

### **Pre-loaded Templates**
The system comes with regulatory-specific templates:

#### **Module 3.2.S Drug Substance**
- Complete ICH M4 structure for drug substance documentation
- Sections: General Information, Manufacture, Characterisation, Control
- Subsections: Nomenclature, Structure, Properties, Manufacturing Process

#### **Module 3.2.P Drug Product**  
- ICH M4 structure for drug product documentation
- Sections: Description, Development, Manufacture, Excipients, Control
- Standard pharmaceutical development organization

## Integration Points

### **With Document Editor**
- Templates generate structured content in the main editor
- TOC becomes document outline and navigation structure
- Sections become editable document parts

### **With File Manager**
- Uploaded template files are managed in the file system
- Templates can reference uploaded supporting documents
- Integration with citation system for references

### **With AI Assistant**
- AI can help generate content for template sections
- Smart suggestions for TOC structure based on document type
- Auto-completion of regulatory sections

## Advanced Features

### **TOC Structure Intelligence**
- **Auto-detection**: Recognizes common regulatory document patterns
- **Numbering Systems**: Supports ICH, FDA, and custom numbering schemes
- **Hierarchy Validation**: Ensures logical section organization

### **Template Categories**
- **Regulatory Modules**: ICH M1-M5 structured templates
- **Custom Templates**: User-defined document structures
- **Protocol Templates**: Clinical and analytical protocol formats
- **Specification Templates**: Product and testing specifications

### **Content Generation**
- **Section Scaffolding**: Pre-populate sections with placeholder content
- **Regulatory Guidance**: Include regulatory requirements for each section
- **Cross-references**: Automatic linking between related sections

## Technical Implementation

### **File Processing Pipeline**
1. **Upload**: File validation and security checks
2. **Parsing**: Content extraction and TOC analysis  
3. **Processing**: Structure recognition and organization
4. **Ready**: Template available for use

### **TOC Data Structure**
```typescript
interface TOCItem {
  id: string;
  title: string;
  level: number;        // 1 = main section, 2 = subsection
  pageNumber?: number;
  children?: TOCItem[]; // Nested structure support
}
```

### **Template Metadata**
- Creation and modification timestamps
- Template type (manual vs uploaded)
- Status tracking and version control
- Usage statistics and history

## Future Enhancements

### **Planned Features**
- **Template Versioning**: Track changes and maintain history
- **Collaboration**: Share templates with team members
- **Template Library**: Curated collection of regulatory templates
- **Advanced Parsing**: Enhanced content extraction from complex documents
- **Template Validation**: Regulatory compliance checking
- **Export Options**: Share templates as files

### **AI Integration**
- **Smart TOC Generation**: AI-suggested table of contents
- **Content Prediction**: Predict required sections based on document type
- **Regulatory Intelligence**: Suggest sections based on regulatory requirements
- **Quality Assessment**: Evaluate template completeness and compliance

---

## Quick Start Guide

1. **Access Templates**: Click "Templates" tab in header
2. **Create Template**: Enter name/description, click "Create Template"
3. **Build TOC**: Add sections, set hierarchy, assign page numbers
4. **Save Template**: Click "Save" to make template ready
5. **Generate Document**: Click "Generate" to create document from template
6. **Edit Content**: Switch to Editor view to work with generated content

The template management system provides a powerful foundation for creating consistent, structured regulatory documents while maintaining flexibility for custom requirements.

## Integration with Generate Button

The "Generate from template" button in the right panel now directly connects to the Template Manager:
- **Click Action**: Navigates to Templates page
- **Context Aware**: Maintains workflow between editor and templates
- **Return Path**: Easy navigation back to editor with generated content

This creates a seamless workflow from template selection to document generation to content editing.
