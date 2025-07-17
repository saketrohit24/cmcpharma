import type { Template, TOCItem } from '../components/Templates/TemplateManagerPage';
import { llmService } from './llmService';
import { backendApi, type GeneratedDocument as BackendGeneratedDocument, type TemplateCreationRequest, type RefinementRequest, type Template as BackendTemplate, type TOCItem as BackendTOCItem } from './backendApi';

interface GeneratedSection {
  id: string;
  title: string;
  content: string;
  type: 'text' | 'table';
}

interface GeneratedCitation {
  id: number;
  text: string;
  source: string;
  page: number;
}

interface GeneratedDocument {
  id: string;
  title: string;
  sections: GeneratedSection[];
  citations: GeneratedCitation[];
  templateId: string;
  generatedAt: Date;
}

// Enhanced API service for template generation with backend integration
export class TemplateGenerationService {
  private static instance: TemplateGenerationService;
  private useLLM: boolean = false;
  private useBackend: boolean = true; // Enable backend by default

  private constructor() {}

  static getInstance(): TemplateGenerationService {
    if (!TemplateGenerationService.instance) {
      TemplateGenerationService.instance = new TemplateGenerationService();
    }
    return TemplateGenerationService.instance;
  }

  // Enable/disable LLM usage
  setLLMMode(enabled: boolean, apiKey?: string) {
    this.useLLM = enabled;
    if (enabled && apiKey) {
      llmService.setApiKey(apiKey);
    }
  }

  // Enable/disable backend usage
  setBackendMode(enabled: boolean) {
    this.useBackend = enabled;
  }

  // Test backend connection
  async testBackendConnection(): Promise<boolean> {
    if (!this.useBackend) return false;
    return await backendApi.testConnection();
  }

  // Create template from TOC text using backend
  async createTemplateFromText(name: string, description: string, tocText: string): Promise<Template> {
    if (this.useBackend) {
      try {
        const request: TemplateCreationRequest = {
          name,
          description,
          toc_text: tocText
        };
        
        const response = await backendApi.parseTemplate(request);
        
        if (response.data) {
          // Convert backend template to frontend format
          return this.convertBackendTemplate(response.data);
        } else {
          throw new Error(response.error || 'Failed to create template');
        }
      } catch (error) {
        console.warn('Backend template creation failed, falling back to frontend parsing:', error);
        // Fall back to frontend parsing
      }
    }

    // Frontend fallback - parse TOC text manually
    return this.parseTemplateFromText(name, description, tocText);
  }

  async generateDocument(template: Template): Promise<GeneratedDocument> {
    if (this.useBackend) {
      try {
        // Convert frontend template to backend format
        const backendTemplate = this.convertToBackendTemplate(template);
        
        const response = await backendApi.generateDocument(backendTemplate);
        
        if (response.data) {
          // Convert backend response to frontend format
          return this.convertBackendDocument(response.data);
        } else {
          throw new Error(response.error || 'Failed to generate document');
        }
      } catch (error) {
        console.warn('Backend generation failed, falling back to mock generation:', error);
        // Fall back to existing logic
      }
    }

    if (this.useLLM) {
      try {
        // Try LLM generation
        return await llmService.generateDocumentWithLLM(template);
      } catch (error) {
        console.warn('LLM generation failed, falling back to mock generation:', error);
      }
    }

    // Original mock generation logic
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Generate mock content based on template TOC
    const sections: GeneratedSection[] = template.toc.map((tocItem: TOCItem, index: number) => ({
      id: `section-${tocItem.id}`,
      title: tocItem.title,
      content: this.generateSectionContent(tocItem.title),
      type: index % 4 === 3 ? 'table' : 'text'
    }));

    const citations: GeneratedCitation[] = this.generateCitations(template);

    return {
      id: `doc-${Date.now()}`,
      title: `Generated ${template.name}`,
      sections,
      citations,
      templateId: template.id,
      generatedAt: new Date()
    };
  }

  // Enhanced generation with progress callbacks and section-by-section processing
  async generateDocumentWithProgress(
    template: Template,
    callbacks?: {
      onSectionStart?: (sectionTitle: string) => void;
      onSectionComplete?: (sectionTitle: string) => void;
    }
  ): Promise<GeneratedDocument> {
    console.log('TemplateGeneration: Starting document generation with backend...', { template, useBackend: this.useBackend });
    
    if (this.useBackend) {
      try {
        // Use the shared session ID from backendApi instead of creating a new one
        const sessionId = backendApi.getSessionId();
        console.log('TemplateGeneration: Using existing session ID:', sessionId);
        
        // Convert frontend template to backend format
        const backendTemplate = this.convertToBackendTemplate(template);
        console.log('TemplateGeneration: Converted template to backend format:', backendTemplate);
        
        // Call the backend generation endpoint directly with existing session ID
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/generation/generate/${sessionId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(backendTemplate)
        });
        
        console.log('TemplateGeneration: Backend response status:', response.status);
        
        if (response.ok) {
          const backendDoc = await response.json();
          console.log('TemplateGeneration: Backend document response:', backendDoc);
          
          // Simulate section-by-section progress for UX with real sections
          const sections = backendDoc.sections || [];
          for (let i = 0; i < sections.length; i++) {
            const section = sections[i];
            callbacks?.onSectionStart?.(section.title);
            
            // Simulate processing time for better UX
            await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));
            
            callbacks?.onSectionComplete?.(section.title);
          }
          
          // Convert backend response to frontend format
          return this.convertBackendDocument(backendDoc);
        } else {
          const errorText = await response.text();
          console.error('TemplateGeneration: Backend generation failed:', response.status, errorText);
          
          // If backend fails, use fallback but with more realistic content
          console.log('TemplateGeneration: Falling back to enhanced mock generation...');
          return await this.generateDocumentWithProgressFallback(template, callbacks);
        }
      } catch (error) {
        console.error('TemplateGeneration: Backend generation failed with error:', error);
        // Fall back to enhanced mock generation
        console.log('Falling back to enhanced mock generation...');
        return await this.generateDocumentWithProgressFallback(template, callbacks);
      }
    }

    // Fallback with section-by-section processing
    return await this.generateDocumentWithProgressFallback(template, callbacks);
  }

  private async generateDocumentWithProgressFallback(
    template: Template,
    callbacks?: {
      onSectionStart?: (sectionTitle: string) => void;
      onSectionComplete?: (sectionTitle: string) => void;
    }
  ): Promise<GeneratedDocument> {
    const sections: GeneratedSection[] = [];
    const allTocItems = this.flattenTOC(template.toc);
    
    console.log('Generating fallback document with', allTocItems.length, 'sections');
    
    // Process each section with progress updates
    for (let i = 0; i < allTocItems.length; i++) {
      const tocItem = allTocItems[i];
      callbacks?.onSectionStart?.(tocItem.title);
      
      // Simulate processing time but reduce it for better UX
      await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 2000));
      
      // Generate enhanced content for this section
      const sectionContent = await this.generateEnhancedSectionContent(tocItem.title);
      
      sections.push({
        id: `section-${tocItem.id}`,
        title: tocItem.title,
        content: sectionContent,
        type: this.determineSectionType(tocItem.title)
      });
      
      console.log(`Generated section ${i + 1}/${allTocItems.length}: ${tocItem.title}`);
      callbacks?.onSectionComplete?.(tocItem.title);
    }

    const citations: GeneratedCitation[] = this.generateCitations(template);

    console.log('Generated fallback document with', sections.length, 'sections');
    
    return {
      id: `doc-${Date.now()}`,
      title: `Generated ${template.name}`,
      sections,
      citations,
      templateId: template.id,
      generatedAt: new Date()
    };
  }

  private async generateEnhancedSectionContent(title: string): Promise<string> {
    // Try LLM generation first if available
    if (this.useLLM) {
      try {
        return await this.generateSectionWithLLM(title);
      } catch (error) {
        console.warn('LLM generation failed for section, using enhanced template:', error);
      }
    }
    
    // Enhanced template-based generation
    return this.generateDetailedSectionContent(title);
  }

  private generateDetailedSectionContent(title: string): string {
    const lowerTitle = title.toLowerCase();
    
    // More comprehensive content templates based on section type
    if (lowerTitle.includes('introduction') || lowerTitle.includes('overview')) {
      return `# ${title}

This section provides a comprehensive introduction to ${title.toLowerCase()} as part of the regulatory submission. The information presented herein has been compiled in accordance with ICH guidelines and regulatory requirements.

## Background and Context

The development of this pharmaceutical product follows established regulatory pathways and incorporates current industry best practices. This documentation supports the regulatory filing and demonstrates compliance with applicable standards.

## Scope and Purpose

This document section covers:
- Regulatory framework and compliance requirements
- Technical specifications and quality standards
- Manufacturing and control processes
- Risk assessment and mitigation strategies

## Regulatory Framework

The information provided aligns with:
- ICH Q8, Q9, and Q10 guidelines for pharmaceutical development
- Regional regulatory requirements (FDA, EMA, etc.)
- Current pharmacopeial standards
- Industry best practices for quality assurance

*Note: This content has been generated as a template. Please review and update with specific product information and actual data from your development program.*`;
    }
    
    if (lowerTitle.includes('specification') || lowerTitle.includes('control')) {
      return `# ${title}

## Analytical Specifications

The specifications for this pharmaceutical product have been established based on comprehensive analytical development, manufacturing process capability studies, and stability data analysis.

### Test Parameters and Acceptance Criteria

| Test Parameter | Method | Acceptance Criteria | Justification |
|----------------|---------|-------------------|---------------|
| Identity | HPLC/IR Spectroscopy | Conforms to reference standard | Ensures product identity |
| Assay | HPLC | 95.0% - 105.0% | Based on stability and manufacturing data |
| Related Substances | HPLC | Individual: ≤ 0.5%, Total: ≤ 1.0% | Safety and efficacy considerations |
| Water Content | Karl Fischer | ≤ 0.5% | Stability and quality requirements |

### Analytical Methods

All analytical methods have been validated according to ICH Q2(R1) guidelines and demonstrate:
- Accuracy and precision within acceptable limits
- Specificity for the intended analytes
- Linearity across the working range
- Robustness under normal operating conditions

### References and Standards

The specifications are established in accordance with:
- ICH Q6A: Specifications for New Drug Substances and Products
- Regional pharmacopeial requirements
- Company analytical development standards

*Note: This content has been generated as a template. Please review and update with actual analytical data and validated specifications for your specific product.*`;
    }
    
    if (lowerTitle.includes('stability') || lowerTitle.includes('storage')) {
      return `# ${title}

## Stability Study Design

The stability program has been designed in accordance with ICH Q1A(R2) guidelines and includes comprehensive testing under various storage conditions to establish appropriate storage recommendations and shelf-life.

### Storage Conditions Tested

**Long-term studies:**
- 25°C ± 2°C / 60% RH ± 5% RH
- Duration: 36 months (ongoing)

**Intermediate studies:**
- 30°C ± 2°C / 65% RH ± 5% RH  
- Duration: 12 months

**Accelerated studies:**
- 40°C ± 2°C / 75% RH ± 5% RH
- Duration: 6 months

### Testing Schedule

Testing is performed at: 0, 3, 6, 9, 12, 18, 24, and 36 months for long-term conditions, with additional intermediate time points for accelerated and intermediate conditions.

### Analytical Parameters Monitored

- Assay by HPLC
- Related substances and degradation products
- Physical appearance and characteristics
- Water content
- Dissolution profile (if applicable)
- Microbiological testing (as appropriate)

### Preliminary Results and Conclusions

Based on available stability data:
- The product demonstrates acceptable stability under recommended storage conditions
- No significant changes in critical quality attributes observed
- Proposed storage conditions and shelf-life are supported by data

*Note: This content has been generated as a template. Please review and update with actual stability data and study results for your specific product.*`;
    }
    
    if (lowerTitle.includes('manufacture') || lowerTitle.includes('process')) {
      return `# ${title}

## Manufacturing Process Overview

The manufacturing process has been developed to ensure consistent product quality and incorporates Quality by Design (QbD) principles in accordance with ICH Q8 guidelines.

### Process Description

The manufacturing process consists of the following key steps:

1. **Raw Material Preparation**
   - Incoming material testing and release
   - Weighing and dispensing operations
   - Environmental monitoring and controls

2. **Processing Operations**
   - Critical process parameters identified and controlled
   - In-process monitoring and testing
   - Process controls and acceptable ranges established

3. **Finishing Operations**
   - Final product processing steps
   - Quality control testing
   - Packaging and labeling operations

### Critical Process Parameters

Key parameters that have been identified as critical to product quality:
- Temperature control during processing
- Mixing time and conditions
- Environmental conditions (humidity, pressure)
- Equipment operating parameters

### Process Controls

- Real-time monitoring of critical parameters
- Statistical process control implementation
- Deviation investigation procedures
- Continuous improvement programs

### Quality Assurance

The manufacturing process includes:
- Validated analytical methods for testing
- Environmental monitoring programs
- Personnel training and qualification
- Equipment qualification and maintenance

*Note: This content has been generated as a template. Please review and update with actual manufacturing process details and validation data for your specific product.*`;
    }
    
    // Generic regulatory content for other sections
    return `# ${title}

## Section Overview

This section addresses the regulatory requirements and technical specifications related to ${title.toLowerCase()}. The information provided supports the overall quality documentation and regulatory compliance strategy.

## Key Considerations

**Regulatory Compliance:**
- Adherence to applicable ICH guidelines
- Compliance with regional regulatory requirements
- Implementation of current industry standards

**Quality Assurance:**
- Risk-based approach to quality management
- Continuous monitoring and improvement
- Documentation and record-keeping requirements

**Technical Specifications:**
- Detailed technical requirements and specifications
- Testing protocols and acceptance criteria
- Method validation and qualification data

## Documentation Requirements

This section includes:
- Comprehensive technical documentation
- Supporting analytical data and studies
- Risk assessments and mitigation strategies
- Regulatory compliance demonstrations

## References and Guidelines

The approach outlined in this section aligns with:
- Relevant ICH guidelines (Q8, Q9, Q10, Q11, etc.)
- Regional regulatory guidance documents
- Industry best practices and standards
- Company quality management systems

## Conclusion

The information provided in this section demonstrates compliance with regulatory requirements and supports the overall quality and safety profile of the pharmaceutical product.

*Note: This content has been generated as a template. Please review and update with specific product information, actual data, and detailed technical specifications relevant to your development program.*`;
  }

  private determineSectionType(title: string): 'text' | 'table' {
    const lowerTitle = title.toLowerCase();
    // Sections that typically contain tables
    if (lowerTitle.includes('specification') || 
        lowerTitle.includes('testing') || 
        lowerTitle.includes('parameters') ||
        lowerTitle.includes('criteria') ||
        lowerTitle.includes('results')) {
      return 'table';
    }
    return 'text';
  }

  private flattenTOC(toc: TOCItem[]): TOCItem[] {
    const flattened: TOCItem[] = [];
    
    const flatten = (items: TOCItem[]) => {
      items.forEach(item => {
        flattened.push(item);
        if (item.children) {
          flatten(item.children);
        }
      });
    };
    
    flatten(toc);
    return flattened;
  }

  private async generateSectionWithLLM(title: string): Promise<string> {
    try {
      const prompt = `Generate professional regulatory content for the section titled: "${title}". 
      The content should be comprehensive, technically accurate, and follow pharmaceutical regulatory standards.
      Include specific details, requirements, and best practices relevant to this section.`;
      
      return await llmService.generateText(prompt);
    } catch (error) {
      console.warn('LLM generation failed for section, using fallback:', error);
      return this.generateSectionContent(title);
    }
  }

  private generateSectionContent(title: string): string {
    const contentTemplates = {
      general: `This section provides comprehensive information regarding ${title.toLowerCase()}. The data presented herein has been compiled in accordance with regulatory guidelines and industry best practices.

Key considerations include:
- Compliance with current regulatory standards
- Adherence to quality management principles
- Implementation of risk-based approaches
- Maintenance of product quality throughout lifecycle

The information contained in this section supports the overall regulatory submission and demonstrates the commitment to pharmaceutical excellence.`,

      nomenclature: `The drug substance is identified by the following nomenclature:

**Chemical Name:** [Chemical name to be provided]
**Generic Name:** [Generic name to be provided]  
**Trade Name:** [Trade name to be provided]
**CAS Registry Number:** [CAS number to be provided]
**Molecular Formula:** [Molecular formula to be provided]
**Molecular Weight:** [Molecular weight to be provided]

All nomenclature follows current international standards and conventions as established by recognized pharmaceutical organizations.`,

      manufacturing: `The manufacturing process has been designed to ensure consistent production of high-quality material. The process includes the following key steps:

1. **Raw Material Preparation**
   - Verification of starting material quality
   - Pre-processing and conditioning as required

2. **Primary Manufacturing Steps**
   - [Specific process steps to be detailed]
   - Critical process parameters monitoring

3. **Purification and Isolation**
   - [Purification methods to be described]
   - Quality control testing at each stage

4. **Final Processing**
   - Final product isolation and drying
   - Packaging under controlled conditions

Each step is performed under validated conditions with appropriate controls to ensure product quality and consistency.`,

      testing: `Quality control testing is performed using validated analytical methods to ensure product quality and compliance with specifications.

**Test Methods Include:**
- Identity testing by [method]
- Assay determination by [method]  
- Purity testing including related substances
- Physical and chemical property testing
- Microbiological testing where applicable

All testing is performed by qualified personnel using validated equipment and methods. Results are documented and reviewed according to established procedures.

**Acceptance Criteria:**
[Specific acceptance criteria to be provided based on product characteristics and regulatory requirements]`
    };

    // Select content based on title keywords
    if (title.toLowerCase().includes('nomenclature') || title.toLowerCase().includes('name')) {
      return contentTemplates.nomenclature;
    } else if (title.toLowerCase().includes('manufactur') || title.toLowerCase().includes('process')) {
      return contentTemplates.manufacturing;
    } else if (title.toLowerCase().includes('control') || title.toLowerCase().includes('test') || title.toLowerCase().includes('characteris')) {
      return contentTemplates.testing;
    } else {
      return contentTemplates.general;
    }
  }

  private generateCitations(template: Template): GeneratedCitation[] {
    const baseCitations = [
      {
        id: 1,
        text: "ICH Q6A: Specifications: Test Procedures and Acceptance Criteria for New Drug Substances and New Drug Products",
        source: "ICH Harmonised Tripartite Guideline",
        page: 15
      },
      {
        id: 2,
        text: "FDA Guidance for Industry: Q1A(R2) Stability Testing of New Drug Substances and Products",
        source: "FDA Guidance Document",
        page: 8
      },
      {
        id: 3,
        text: "ICH Q7: Good Manufacturing Practice Guide for Active Pharmaceutical Ingredients",
        source: "ICH Harmonised Tripartite Guideline",
        page: 22
      },
      {
        id: 4,
        text: "European Pharmacopoeia: General Monographs and Requirements",
        source: "Ph. Eur. 10th Edition",
        page: 145
      }
    ];

    // Add template-specific citations
    const templateSpecificCitations = [];
    if (template.name.includes('Drug Substance')) {
      templateSpecificCitations.push({
        id: 5,
        text: "ICH Q11: Development and Manufacture of Drug Substances",
        source: "ICH Harmonised Tripartite Guideline",
        page: 12
      });
    }

    if (template.name.includes('Drug Product')) {
      templateSpecificCitations.push({
        id: 6,
        text: "ICH Q8(R2): Pharmaceutical Development",
        source: "ICH Harmonised Tripartite Guideline",
        page: 28
      });
    }

    return [...baseCitations, ...templateSpecificCitations];
  }

  // Convert backend template to frontend format
  private convertBackendTemplate(backendTemplate: BackendTemplate): Template {
    return {
      id: backendTemplate.id,
      name: backendTemplate.name,
      description: backendTemplate.description || '',
      type: 'manual' as const,
      createdAt: new Date(),
      lastModified: new Date(),
      toc: this.convertBackendTOC(backendTemplate.toc),
      status: 'ready' as const
    };
  }

  // Convert frontend template to backend format
  private convertToBackendTemplate(frontendTemplate: Template): BackendTemplate {
    return {
      id: frontendTemplate.id,
      name: frontendTemplate.name,
      description: frontendTemplate.description,
      toc: this.convertFrontendTOC(frontendTemplate.toc)
    };
  }

  // Convert backend TOC to frontend format
  private convertBackendTOC(backendTOC: BackendTOCItem[]): TOCItem[] {
    return backendTOC.map((item, index) => ({
      id: item.id || `toc-${index}`,
      title: item.title,
      level: item.level || 1,
      pageNumber: index + 1,
      children: item.children ? this.convertBackendTOC(item.children) : undefined
    }));
  }

  // Convert frontend TOC to backend format
  private convertFrontendTOC(frontendTOC: TOCItem[]): BackendTOCItem[] {
    return frontendTOC.map(item => ({
      id: item.id,
      title: item.title,
      level: item.level,
      children: item.children ? this.convertFrontendTOC(item.children) : undefined
    }));
  }

  // Convert backend document to frontend format
  private convertBackendDocument(backendDoc: BackendGeneratedDocument): GeneratedDocument {
    const sections: GeneratedSection[] = backendDoc.sections.map(section => ({
      id: section.id,
      title: section.title,
      content: section.content,
      type: 'text' as const // Backend doesn't specify type, default to text
    }));

    // Generate mock citations for now (backend doesn't return citations yet)
    const citations: GeneratedCitation[] = [
      {
        id: 1,
        text: "Generated based on regulatory guidelines and best practices",
        source: "CMC Regulatory Writer AI",
        page: 1
      }
    ];

    return {
      id: backendDoc.id,
      title: backendDoc.title,
      sections,
      citations,
      templateId: backendDoc.template_id,
      generatedAt: new Date(backendDoc.generated_at)
    };
  }

  // Frontend fallback for template parsing (when backend is not available)
  private parseTemplateFromText(name: string, description: string, tocText: string): Template {
    const lines = tocText.split('\n').filter(line => line.trim());
    const toc: TOCItem[] = [];
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim();
      if (!trimmedLine) return;
      
      // Detect level based on indentation or numbering
      const level = this.detectTOCLevel(line);
      const title = this.cleanTOCTitle(trimmedLine);
      
      toc.push({
        id: `toc-${index + 1}`,
        title,
        level,
        pageNumber: index + 1
      });
    });

    return {
      id: `template-${Date.now()}`,
      name,
      description,
      type: 'manual',
      createdAt: new Date(),
      lastModified: new Date(),
      toc,
      status: 'ready'
    };
  }

  private detectTOCLevel(line: string): number {
    // Count leading spaces/tabs for indentation
    const leadingSpaces = line.length - line.trimStart().length;
    const indentLevel = Math.floor(leadingSpaces / 2) + 1;
    
    // Also check for numbering patterns
    const trimmed = line.trim();
    if (/^\d+\.\d+\.\d+/.test(trimmed)) return 3;
    if (/^\d+\.\d+/.test(trimmed)) return 2;
    if (/^\d+\./.test(trimmed)) return 1;
    
    return Math.min(indentLevel, 3); // Cap at level 3
  }

  private cleanTOCTitle(title: string): string {
    // Remove numbering and clean up title
    return title
      .replace(/^\d+(\.\d+)*\.?\s*/, '') // Remove numbering
      .replace(/^\W+/, '') // Remove leading non-word characters
      .trim();
  }

  // Generate a session ID for file management
  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Upload files to backend for a session
  async uploadFilesForSession(files: File[]): Promise<string> {
    const sessionId = this.generateSessionId();
    
    if (this.useBackend) {
      try {
        for (const file of files) {
          const formData = new FormData();
          formData.append('file', file);
          
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/files/upload/${sessionId}`, {
            method: 'POST',
            body: formData
          });
          
          if (!response.ok) {
            throw new Error(`Failed to upload file: ${file.name}`);
          }
        }
        
        return sessionId;
      } catch (error) {
        console.error('Failed to upload files to backend:', error);
        throw error;
      }
    }
    
    return sessionId; // Return session ID even if backend is disabled
  }

  // Generate document with uploaded files
  async generateDocumentWithFiles(template: Template, files: File[]): Promise<GeneratedDocument> {
    try {
      // First upload files to backend
      const sessionId = await this.uploadFilesForSession(files);
      
      if (this.useBackend) {
        // Convert frontend template to backend format
        const backendTemplate = this.convertToBackendTemplate(template);
        
        // Use the session-specific generation endpoint
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/generation/generate/${sessionId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(backendTemplate)
        });
        
        if (!response.ok) {
          throw new Error(`Generation failed: ${response.statusText}`);
        }
        
        const backendDoc = await response.json();
        return this.convertBackendDocument(backendDoc);
      }
      
      // Fallback to existing generation logic
      return await this.generateDocument(template);
    } catch (error) {
      console.error('Error generating document with files:', error);
      throw error;
    }
  }

  // Enhanced generation with files and progress callbacks
  async generateDocumentWithFilesAndProgress(
    template: Template,
    files: File[],
    callbacks?: {
      onSectionStart?: (sectionTitle: string) => void;
      onSectionComplete?: (sectionTitle: string) => void;
    }
  ): Promise<GeneratedDocument> {
    try {
      // First upload files to backend
      const sessionId = await this.uploadFilesForSession(files);
      
      if (this.useBackend) {
        // Convert frontend template to backend format
        const backendTemplate = this.convertToBackendTemplate(template);
        
        // Use the session-specific generation endpoint
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/generation/generate/${sessionId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(backendTemplate)
        });
        
        if (!response.ok) {
          throw new Error(`Generation failed: ${response.statusText}`);
        }
        
        const backendDoc = await response.json();
        
        // Simulate section-by-section progress for UX
        const sections = backendDoc.sections;
        for (let i = 0; i < sections.length; i++) {
          const section = sections[i];
          callbacks?.onSectionStart?.(section.title);
          
          // Simulate processing time
          await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
          
          callbacks?.onSectionComplete?.(section.title);
        }
        
        return this.convertBackendDocument(backendDoc);
      }
      
      // Fallback with section-by-section processing
      return await this.generateDocumentWithProgressFallback(template, callbacks);
    } catch (error) {
      console.error('Error generating document with files and progress:', error);
      throw error;
    }
  }
}

export const templateGenerationService = TemplateGenerationService.getInstance();
export type { GeneratedDocument, GeneratedSection, GeneratedCitation };
