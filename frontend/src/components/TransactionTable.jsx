import React from 'react';
import Panel from './Panel';

export default function TransactionTable({ txs }) {
  return (
    <Panel title="Transactions">
      {!txs || txs.length === 0 ? (
        <div className="muted">—</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Hash</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {txs.slice(0, 8).map((tx, idx) => (
              <tr key={idx}>
                <td><code title={tx.hash}>{tx.hash}</code></td>
                <td>{tx.value_btc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}
