import React from 'react';

interface SpecRow {
  test: string;
  method: string;
  acceptanceCriteria: string;
}

export const SpecificationTable: React.FC = () => {
  const specifications: SpecRow[] = [
    {
      test: 'Appearance',
      method: 'Visual',
      acceptanceCriteria: 'White to off-white crystalline powder'
    },
    {
      test: 'Identity (IR)',
      method: 'Ph. Eur. 2.2.24',
      acceptanceCriteria: 'Conforms to reference spectrum'
    },
    {
      test: 'Identity (HPLC)',
      method: 'In-house method',
      acceptanceCriteria: 'RT ± 2% of reference standard'
    },
    {
      test: 'Assay (anhydrous basis)',
      method: 'HPLC',
      acceptanceCriteria: '98.0 - 102.0%'
    },
    {
      test: 'Related substances',
      method: 'HPLC',
      acceptanceCriteria: 'Individual: NMT 0.15%\nTotal: NMT 0.5%'
    },
    {
      test: 'Residual solvents',
      method: 'GC',
      acceptanceCriteria: 'ICH Q3C limits'
    },
    {
      test: 'Water content',
      method: 'Karl Fischer',
      acceptanceCriteria: 'NMT 0.5%'
    },
    {
      test: 'Residue on ignition',
      method: 'Ph. Eur. 2.4.14',
      acceptanceCriteria: 'NMT 0.1%'
    },
    {
      test: 'Heavy metals',
      method: 'ICP-MS',
      acceptanceCriteria: 'NMT 20 ppm'
    }
  ];

  return (
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
          {specifications.map((spec, index) => (
            <tr key={index}>
              <td>{spec.test}</td>
              <td>{spec.method}</td>
              <td style={{ whiteSpace: 'pre-line' }}>{spec.acceptanceCriteria}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
