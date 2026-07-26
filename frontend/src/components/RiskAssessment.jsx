import React from 'react';
import Panel from './Panel';

export default function RiskAssessment({ risk }) {
  if (!risk) {
    return (
      <Panel title="Risk Assessment">
        <div id="riskBox" className="muted">Trace an address to see its risk score.</div>
      </Panel>
    );
  }

  return (
    <Panel title="Risk Assessment">
      <div style={{ marginBottom: '12px' }}>
        <span className={`risk-badge risk-${risk.level}`}>{risk.level} RISK</span>
        <span className="muted" style={{ marginLeft: '10px', fontSize: '11.5px' }}>
          score {risk.score}/100
        </span>
      </div>
      {risk.flags && risk.flags.length > 0 ? (
        risk.flags.map((flag, idx) => (
          <div key={idx} className="flag-item">{flag}</div>
        ))
      ) : (
        <div className="muted" style={{ fontSize: '12px' }}>No specific flags raised.</div>
      )}
    </Panel>
  );
}
