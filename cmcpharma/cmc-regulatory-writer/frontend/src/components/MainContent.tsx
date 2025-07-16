import React from 'react';

const MainContent: React.FC = () => {
  const specificationData = [
    {
      test: 'Appearance',
      method: 'Visual',
      criteria: 'White to off-white crystalline powder'
    },
    {
      test: 'Identity (IR)',
      method: 'Ph. Eur. 2.2.24',
      criteria: 'Conforms to reference spectrum'
    },
    {
      test: 'Identity (HPLC)',
      method: 'In-house method',
      criteria: 'RT ± 2% of reference standard'
    },
    {
      test: 'Assay (anhydrous basis)',
      method: 'HPLC',
      criteria: '98.0 - 102.0%'
    },
    {
      test: 'Related substances',
      method: 'HPLC',
      criteria: 'Individual: NMT 0.15%\nTotal: NMT 0.5%'
    },
    {
      test: 'Residual solvents',
      method: 'GC',
      criteria: 'ICH Q3C limits'
    },
    {
      test: 'Water content',
      method: 'Karl Fischer',
      criteria: 'NMT 0.5%'
    },
    {
      test: 'Residue on ignition',
      method: 'Ph. Eur. 2.4.14',
      criteria: 'NMT 0.1%'
    },
    {
      test: 'Heavy metals',
      method: 'ICP-MS',
      criteria: 'NMT 20 ppm'
    }
  ];

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
      
      <h2 className="subtitle">3.2.S.4.1 Specification</h2>
      
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Test</th>
              <th>Method</th>
              <th>Acceptance Criteria</th>
            </tr>
          </thead>
          <tbody>
            {specificationData.map((row, index) => (
              <tr key={index}>
                <td>{row.test}</td>
                <td>{row.method}</td>
                <td style={{ whiteSpace: 'pre-line' }}>{row.criteria}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
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

export default MainContent;
