/**
 * Chat Service for handling chat functionality with RAG and general Q&A
 */

import { backendApi, type ChatSession as BackendChatSession, type ChatRequest } from './backendApi';

export interface LocalChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  isTyping?: boolean;
  citations?: string[];
}

export interface ChatServiceOptions {
  useBackend?: boolean;
  useRAG?: boolean;
  sessionId?: string;
}

class ChatService {
  private static instance: ChatService;
  private useBackend: boolean = true;
  private currentSessionId: string | null = null;
  private messages: Map<string, LocalChatMessage[]> = new Map();

  private constructor() {}

  static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  setBackendMode(enabled: boolean) {
    this.useBackend = enabled;
  }

  async sendMessage(
    message: string, 
    options: ChatServiceOptions = {}
  ): Promise<LocalChatMessage> {
    const { useRAG = true, sessionId } = options;
    
    // Create user message
    const userMessage: LocalChatMessage = {
      id: `user-${Date.now()}`,
      text: message,
      sender: 'user',
      timestamp: new Date()
    };

    // Store user message
    const currentSession = sessionId || this.currentSessionId || 'default';
    this.addMessageToSession(currentSession, userMessage);

    if (this.useBackend) {
      try {
        // Send to backend
        const request: ChatRequest = {
          message,
          session_id: currentSession,
          use_rag: useRAG,
          context: undefined // Remove context for now to avoid type mismatch
        };

        console.log('Sending chat request:', request);
        const response = await backendApi.sendChatMessage(request);
        console.log('Chat response:', response);
        
        if (response.data) {
          // Convert backend response to local format
          const assistantMessage: LocalChatMessage = {
            id: response.data.message.id,
            text: response.data.message.text,
            sender: 'assistant',
            timestamp: new Date(response.data.message.timestamp),
            citations: response.data.citations || undefined
          };

          this.addMessageToSession(currentSession, assistantMessage);
          this.currentSessionId = response.data.session.id;
          
          return assistantMessage;
        } else {
          console.error('No data in chat response:', response);
          throw new Error(response.error || 'Chat request failed');
        }
      } catch (error) {
        console.warn('Backend chat failed, falling back to mock response:', error);
        return this.generateMockResponse(message, currentSession);
      }
    } else {
      // Fallback to mock response
      return this.generateMockResponse(message, currentSession);
    }
  }

  async sendMessageStream(
    message: string,
    onChunk: (chunk: string, messageId: string) => void,
    onComplete: (fullMessage: LocalChatMessage, session?: BackendChatSession) => void,
    onError: (error: string) => void,
    options: ChatServiceOptions = {}
  ): Promise<void> {
    const { sessionId } = options;
    
    try {
      const request: ChatRequest = {
        message,
        session_id: sessionId || this.currentSessionId || undefined,
        use_rag: options.useRAG !== undefined ? options.useRAG : true,
        context: undefined // Remove context for now to avoid type mismatch
      };

      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/chat/message/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let messageId = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'user_message') {
                  // User message received, update session if needed
                  if (data.message.session_id) {
                    this.currentSessionId = data.message.session_id;
                  }
                } else if (data.type === 'chunk') {
                  // Stream chunk received
                  messageId = data.message_id;
                  onChunk(data.chunk, messageId);
                } else if (data.type === 'complete') {
                  // Stream complete
                  const assistantMessage: LocalChatMessage = {
                    id: data.message.id,
                    text: data.message.text,
                    sender: 'assistant',
                    timestamp: new Date(data.message.timestamp),
                    citations: data.citations || undefined
                  };
                  
                  if (data.message.session_id) {
                    this.currentSessionId = data.message.session_id;
                  }
                  
                  onComplete(assistantMessage, data.session);
                } else if (data.type === 'error') {
                  onError(data.error);
                  return;
                }
              } catch {
                // Ignore JSON parse errors for non-data lines
                continue;
              }
            }
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Unknown error occurred');
    }
  }

  private async generateMockResponse(message: string, sessionId: string): Promise<LocalChatMessage> {
    // Simulate thinking delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    let response = '';
    const lowerMessage = message.toLowerCase();

    // RAG/CMC specific responses
    if (lowerMessage.includes('specification') || lowerMessage.includes('spec')) {
      response = `I can help you create specifications for pharmaceutical products. Here's a basic structure:

**Analytical Specifications typically include:**
- Identity tests (IR, HPLC, etc.)
- Assay determination
- Related substances/impurities
- Physical properties (particle size, moisture, etc.)
- Microbiological limits (if applicable)

Would you like me to help you develop a specific type of specification?`;

    } else if (lowerMessage.includes('protocol')) {
      response = `I can assist with various validation protocols. Common types include:

**Analytical Method Validation:**
- Accuracy and precision studies
- Linearity and range
- Specificity and selectivity
- Robustness testing

**Process Validation:**
- Installation Qualification (IQ)
- Operational Qualification (OQ)
- Performance Qualification (PQ)

What type of protocol are you looking to develop?`;

    } else if (lowerMessage.includes('stability')) {
      response = `For stability studies, I can help with:

**ICH Stability Guidelines:**
- Q1A(R2): Stability testing requirements
- Q1B: Photostability testing
- Q1C: Stability testing for new dosage forms

**Study Design:**
- Storage conditions (25°C/60% RH, 30°C/65% RH, 40°C/75% RH)
- Testing intervals (0, 3, 6, 9, 12, 18, 24 months)
- Sample sizes and statistical considerations

What specific aspect of stability would you like to explore?`;

    } else if (lowerMessage.includes('impurity') || lowerMessage.includes('degradation')) {
      response = `Impurity profiling is crucial for drug safety. I can help with:

**ICH Q3A/Q3B Guidelines:**
- Identification thresholds
- Qualification thresholds
- Reporting thresholds

**Types of Impurities:**
- Process-related impurities
- Degradation products
- Residual solvents
- Elemental impurities (ICH Q3D)

Which type of impurity assessment do you need assistance with?`;

    } else if (lowerMessage.includes('method') && lowerMessage.includes('validation')) {
      response = `Method validation follows ICH Q2(R1) guidelines. Key parameters include:

**Analytical Performance Parameters:**
- Accuracy: Recovery studies, reference standards
- Precision: Repeatability, intermediate precision, reproducibility
- Specificity: Interference testing, forced degradation
- Linearity: Correlation coefficient ≥0.999
- Range: 80-120% of target concentration
- Detection/Quantitation limits: Signal-to-noise ratio approach

Would you like detailed guidance on any specific validation parameter?`;

    } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      response = `Hello! I'm your CMC regulatory writing assistant. I can help you with:

🔬 **Analytical Methods & Validation**
📋 **Specifications & Protocols** 
📊 **Stability Studies**
🧪 **Impurity Assessment**
📝 **Regulatory Documentation**
❓ **General CMC Questions**

I have access to regulatory guidelines, industry best practices, and can provide both general answers and document-specific insights. What would you like to work on today?`;

    } else if (lowerMessage.includes('thank')) {
      response = `You're welcome! I'm here to help with any CMC or regulatory questions you have. Feel free to ask about analytical methods, specifications, validation protocols, or any other pharmaceutical development topics.`;

    } else if (lowerMessage.includes('what') && (lowerMessage.includes('cmc') || lowerMessage.includes('regulatory'))) {
      response = `CMC (Chemistry, Manufacturing, and Controls) is a critical section of regulatory submissions that covers:

**Key CMC Elements:**
📋 **Drug Substance & Product Specifications**
🔬 **Analytical Methods & Validation**  
🏭 **Manufacturing Process & Controls**
📊 **Stability Data & Studies**
🧪 **Impurity Profiles & Control**
📝 **Quality Control Procedures**

I can help you develop any of these elements. What specific area would you like to focus on?`;

    } else if (lowerMessage.includes('help') || lowerMessage.includes('what can you do')) {
      response = `I'm your AI-powered CMC regulatory writing assistant! Here's how I can help:

**📋 Document Generation**
- Specifications for drug substances/products
- Validation protocols and reports  
- Stability study designs and reports
- Regulatory submission sections

**🔍 Expert Guidance**
- ICH guideline interpretation (Q1-Q14)
- FDA/EMA regulatory requirements
- Industry best practices
- Method development strategies

**📊 Data Analysis Support**
- Statistical evaluation of results
- Trend analysis recommendations
- Out-of-specification investigations

**💬 Interactive Q&A**
- Answer specific technical questions
- Provide regulatory guidance
- Suggest documentation approaches

Just ask me about any CMC topic or upload documents for analysis!`;

    } else if (lowerMessage.includes('how') && lowerMessage.includes('work')) {
      response = `I work in multiple ways to assist with your CMC regulatory needs:

**🤖 AI-Powered Analysis**
- Advanced language models trained on regulatory guidelines
- Document parsing and content extraction
- Intelligent template generation

**📚 Knowledge Base**
- ICH guidelines (Q1A-Q14)
- FDA/EMA guidance documents
- Industry standards and best practices
- Pharmaceutical development principles

**🔄 Interactive Features**
- Real-time Q&A on any CMC topic
- Document-specific analysis (RAG)
- Template-based generation
- Multi-format export capabilities

You can ask me questions directly, upload documents for analysis, or request specific document generation. What would you like to try first?`;

    // General knowledge questions
    } else if (lowerMessage.includes('president') || lowerMessage.includes('1st president') || lowerMessage.includes('first president')) {
      response = `George Washington was the first President of the United States, serving from 1789 to 1797. He was a key leader during the American Revolutionary War and is often called the "Father of His Country."

**Key Facts about George Washington:**
• Born: February 22, 1732, in Virginia
• Served: 1789-1797 (two terms)
• Previous role: Commander-in-Chief of Continental Army
• Major achievements: Led Continental Army to victory, established many presidential precedents
• Died: December 14, 1799, at Mount Vernon

While I'm primarily designed to help with CMC regulatory writing, I'm happy to answer general questions too! Is there anything else you'd like to know, or would you like help with any pharmaceutical documentation?`;

    } else if (lowerMessage.includes('artificial intelligence') || lowerMessage.includes(' ai ')) {
      response = `Artificial Intelligence (AI) refers to computer systems that can perform tasks that typically require human intelligence, such as learning, reasoning, problem-solving, and understanding language.

**Types of AI:**
• **Machine Learning**: Systems that learn from data
• **Natural Language Processing**: Understanding and generating human language
• **Computer Vision**: Interpreting visual information
• **Robotics**: Physical AI systems that interact with the world

**Applications:**
• Healthcare diagnostics and drug discovery
• Autonomous vehicles and transportation
• Virtual assistants and chatbots
• Financial analysis and fraud detection

I'm an example of AI specialized in regulatory writing and pharmaceutical documentation. How can I help you with your CMC or regulatory needs today?`;

    } else if (lowerMessage.includes('weather') || lowerMessage.includes('temperature')) {
      response = `I don't have access to current weather data or real-time information. For accurate weather information, I'd recommend checking weather apps or local forecasts.

However, I can help you with pharmaceutical stability studies that involve controlled temperature and humidity conditions! For example:
• ICH stability testing conditions (25°C/60% RH, 40°C/75% RH)
• Environmental monitoring for manufacturing
• Storage condition specifications

Would you like assistance with any stability-related regulatory documentation?`;

    } else if (lowerMessage.includes('time') || lowerMessage.includes('date') || lowerMessage.includes('today')) {
      response = `I don't have access to real-time information, so I can't tell you the current time or date. Check your device's clock for current time and date.

However, I can help you with time-related aspects of pharmaceutical documentation:
• Stability study timelines and schedules
• Method validation timeframes
• Regulatory submission deadlines
• Shelf-life determinations

Is there anything related to pharmaceutical timelines or regulatory scheduling I can help you with?`;

    } else if (lowerMessage.includes('math') || lowerMessage.includes('calculate')) {
      response = `I can help with basic mathematical concepts and pharmaceutical calculations!

**General Math Topics:**
• Basic arithmetic and algebra
• Statistical concepts (mean, standard deviation, RSD)
• Percentage calculations
• Unit conversions

**Pharmaceutical Calculations:**
• Assay calculations and recoveries
• Dilution and concentration calculations  
• Statistical analysis of analytical data
• Limits and specifications calculations

What specific calculation would you like help with? If it's pharmaceutical-related, I can provide detailed guidance with examples!`;

    } else {
      // General response with CMC context
      response = `I understand you're asking about "${message}". 

As your CMC regulatory assistant, I can provide guidance on:
- Analytical method development and validation
- Pharmaceutical specifications and testing
- Stability study design and analysis  
- Impurity assessment and control strategies
- Regulatory submission requirements
- Quality control procedures

Could you provide more specific details about what you'd like to know? For example, are you looking for:
- Specific regulatory guidelines?
- Method development strategies?
- Documentation templates?
- Technical troubleshooting advice?`;
    }

    const assistantMessage: LocalChatMessage = {
      id: `assistant-${Date.now()}`,
      text: response,
      sender: 'assistant',
      timestamp: new Date()
    };

    this.addMessageToSession(sessionId, assistantMessage);
    return assistantMessage;
  }

  private addMessageToSession(sessionId: string, message: LocalChatMessage) {
    const sessionMessages = this.messages.get(sessionId) || [];
    sessionMessages.push(message);
    this.messages.set(sessionId, sessionMessages);
  }

  private getRecentContext(sessionId: string, maxMessages: number = 5): string {
    const sessionMessages = this.messages.get(sessionId) || [];
    const recentMessages = sessionMessages.slice(-maxMessages);
    
    return recentMessages
      .map(msg => `${msg.sender}: ${msg.text}`)
      .join('\n');
  }

  getSessionMessages(sessionId?: string): LocalChatMessage[] {
    const currentSession = sessionId || this.currentSessionId || 'default';
    return this.messages.get(currentSession) || [];
  }

  clearSession(sessionId?: string) {
    const currentSession = sessionId || this.currentSessionId || 'default';
    this.messages.delete(currentSession);
  }

  getCurrentSessionId(): string | null {
    return this.currentSessionId;
  }

  setCurrentSessionId(sessionId: string) {
    this.currentSessionId = sessionId;
  }
}

export const chatService = ChatService.getInstance();
export type { BackendChatSession as ChatSession };