// Sample data for testing the DocumentEditor component

export const sampleCitations = [
  {
    id: 1,
    text: 'Manufacturing process capability study',
    source: 'Internal Report MFG-2024-001.pdf',
    page: 15
  },
  {
    id: 2, 
    text: 'ICH Q6A Specifications: Test Procedures and Acceptance Criteria for New Drug Substances and New Drug Products',
    source: 'ICH_Q6A_Guidelines.pdf',
    page: 1
  },
  {
    id: 3,
    text: 'Stability data analysis',
    source: 'Stability Report STB-2024-001.pdf',
    page: 23
  }
];

export const sampleSections = [
  {
    id: '1',
    title: '3.2.S.4.1 Specification Overview',
    content: 'The specifications for the drug substance have been established based on the manufacturing process capability [1], stability data [3], and regulatory requirements. All tests and acceptance criteria are in accordance with ICH Q6A guidelines [2] and current pharmacopeial standards.',
    type: 'text' as const
  },
  {
    id: '2',
    title: '3.2.S.4.2 Specification Table',
    content: '',
    type: 'table' as const
  },
  {
    id: '3',
    title: '3.2.S.4.3 Method Validation',
    content: 'All analytical methods have been validated according to ICH Q2(R1) guidelines [2]. The validation parameters include specificity, linearity, accuracy, precision, detection limit, quantitation limit, and robustness.',
    type: 'text' as const
  }
];
