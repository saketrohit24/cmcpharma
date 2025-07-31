import type { Template, TOCItem } from '../components/Templates/TemplateManagerPage';
import type { GeneratedDocument } from './templateGeneration';

// LLM Service for actual content generation
export class LLMService {
  private static instance: LLMService;
  private apiKey: string | null = null;
  private apiEndpoint: string = 'https://api.openai.com/v1/chat/completions'; // Or your preferred LLM

  private constructor() {
    // Initialize with API key from environment or user input
    this.apiKey = import.meta.env.VITE_LLM_API_KEY || null;
  }

  static getInstance(): LLMService {
    if (!LLMService.instance) {
      LLMService.instance = new LLMService();
    }
    return LLMService.instance;
  }

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
  }

  async generateDocumentWithLLM(template: Template): Promise<GeneratedDocument> {
    if (!this.apiKey) {
      throw new Error('LLM API key not configured');
    }

    try {
      // Generate all sections using LLM
      const sections = await this.generateSectionsWithLLM(template.toc, template.name);
      
      // Generate citations using LLM
      const citations = await this.generateCitationsWithLLM(template.name);

      return {
        id: `doc-${Date.now()}`,
        title: `Generated ${template.name}`,
        sections,
        citations,
        templateId: template.id,
        generatedAt: new Date()
      };
    } catch (error) {
      console.error('LLM generation failed:', error);
      throw new Error('Failed to generate document with LLM');
    }
  }

  private formatTOCForPrompt(toc: TOCItem[]): string {
    return toc.map(item => {
      const indent = '  '.repeat(item.level - 1);
      return `${indent}${item.title}`;
    }).join('\n');
  }

  private async generateSectionsWithLLM(toc: TOCItem[], templateName: string) {
    const prompt = `Generate detailed CMC regulatory content for the following sections of ${templateName}:

${this.formatTOCForPrompt(toc)}

Provide comprehensive, regulatory-compliant content for each section. Return as JSON array.`;

    const response = await this.callLLM(prompt);
    
    // Parse LLM response and format as sections
    return this.parseLLMResponse(response, toc);
  }

  private async generateCitationsWithLLM(templateName: string) {
    const prompt = `Generate relevant regulatory citations for a ${templateName} document. 
    Include ICH guidelines, FDA guidance documents, and pharmacopoeial references.
    Return as JSON array with id, text, source, and page fields.`;

    const response = await this.callLLM(prompt);
    return this.parseCitationsResponse(response);
  }

  private async callLLM(prompt: string): Promise<string> {
    if (!this.apiKey) {
      throw new Error('API key not configured');
    }

    const response = await fetch(this.apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4', // Or your preferred model
        messages: [
          {
            role: 'system',
            content: 'You are an expert CMC regulatory writer with deep knowledge of pharmaceutical regulations, ICH guidelines, and FDA requirements.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 4000,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`LLM API request failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  }

  private parseLLMResponse(response: string, toc: TOCItem[]) {
    try {
      // Try to parse as JSON first
      const parsed = JSON.parse(response);
      if (parsed.sections) {
        return parsed.sections;
      }
    } catch {
      // Fallback: parse text response and map to TOC
    }

    // Fallback: create sections from TOC with LLM content
    return toc.map((item, index) => ({
      id: `section-${item.id}`,
      title: item.title,
      content: this.extractSectionContent(response, item.title, index),
      type: 'text' as const
    }));
  }

  private extractSectionContent(response: string, title: string, index: number): string {
    // Smart parsing logic to extract content for specific section
    const lines = response.split('\n');
    let content = '';
    let capturing = false;

    for (const line of lines) {
      if (line.includes(title) || line.includes(`Section ${index + 1}`)) {
        capturing = true;
        continue;
      }
      
      if (capturing && (line.trim() === '' || line.includes('Section'))) {
        if (content.length > 100) break; // End of this section
      }
      
      if (capturing && line.trim()) {
        content += line + '\n';
      }
    }

    return content || `Generated content for ${title}. This section provides comprehensive information regarding ${title.toLowerCase()} in accordance with regulatory requirements.`;
  }

  private parseCitationsResponse(response: string) {
    try {
      const parsed = JSON.parse(response);
      return parsed;
    } catch {
      // Fallback citations
      return [
        {
          id: 1,
          text: "ICH Q6A: Specifications: Test Procedures and Acceptance Criteria",
          source: "ICH Harmonised Tripartite Guideline",
          page: 15
        }
      ];
    }
  }

  async generateText(prompt: string): Promise<string> {
    return await this.callLLM(prompt);
  }
}

export const llmService = LLMService.getInstance();
