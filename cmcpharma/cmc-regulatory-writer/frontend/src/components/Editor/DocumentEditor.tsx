import React from 'react';
import { SpecificationTable } from './SpecificationTable';
import { TextWithCitations } from '../Citations/TextWithCitations';

interface Section {
  id: string;
  title: string;
  content: string;
  type: 'text' | 'table';
}

interface Citation {
  id: number;
  text: string;
  source: string;
  page: number;
  sourceFileId?: string;
}

interface DocumentEditorProps {
  sections?: Section[];
  citations?: Citation[];
  isGenerating?: boolean;
}

export const DocumentEditor: React.FC<DocumentEditorProps> = ({ 
  sections = [], 
  citations = [],
  isGenerating = false
}) => {
  const defaultSections: Section[] = [
    {
      id: '1',
      title: '3.2.S.4.1 Specification',
      content: 'The specifications for the drug substance have been established based on the manufacturing process capability, stability data, and regulatory requirements [1]. All tests and acceptance criteria are in accordance with ICH Q6A guidelines [2] and current pharmacopeial standards.',
      type: 'text'
    }
  ];

  const sectionsToRender = sections.length > 0 ? sections : defaultSections;

  if (isGenerating) {
    return (
      <div className="document-editor">
        <div className="document-loading">
          <div className="loading-spinner"></div>
          <h2>Generating Document...</h2>
          <p>Creating content from template. This may take a few moments.</p>
        </div>
      </div>
    );
  }

  return (
    <main className="content">
      <div className="content-header">
        <h1 className="content-title">Drug Substance Specifications</h1>
        <div className="content-actions">
          <button className="icon-btn">↶</button>
          <button className="icon-btn">↷</button>
          <div className="toggle-container">
            <div className="toggle">
              <div className="toggle-slider"></div>
            </div>
            <span style={{ fontSize: '14px', color: '#6b7280' }}>View changes</span>
          </div>
        </div>
      </div>
      
      {sectionsToRender.map(section => (
        <div key={section.id}>
          <h2 className="subtitle">{section.title}</h2>
          {section.type === 'table' ? (
            <SpecificationTable />
          ) : (
            <TextWithCitations content={section.content} citations={citations} />
          )}
        </div>
      ))}
      
      <SpecificationTable />
      
      <p className="reference">
        Reference: <a href="#">ICH Q6A</a>
      </p>
      
      <div className="section">
        <h3 className="section-title">Justification of Specifications:</h3>
        <p className="section-content">
          The specifications for the drug substance have been established based on the manufacturing process capability, 
          stability data, and regulatory requirements. All tests and acceptance criteria are in accordance with 
          ICH Q6A guidelines and current pharmacopeial standards.
        </p>
      </div>
      
      <div className="section">
        <h3 className="section-title">Analytical Procedures:</h3>
        <ul>
          <li>Detailed analytical procedures are provided in Section 3.2.S.4.2</li>
          <li>All methods have been validated according to ICH Q2(R1)</li>
          <li>System suitability criteria are defined for each chromatographic method</li>
        </ul>
      </div>
    </main>
  );
};
