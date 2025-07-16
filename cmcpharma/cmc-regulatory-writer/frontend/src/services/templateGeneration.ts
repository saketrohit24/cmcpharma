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
}

export const templateGenerationService = TemplateGenerationService.getInstance();
export type { GeneratedDocument, GeneratedSection, GeneratedCitation };
