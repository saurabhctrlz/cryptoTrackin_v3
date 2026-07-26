import React from 'react';
import Panel from './Panel';

export default function WalletStats({ data }) {
  return (
    <Panel title="Wallet Stats">
      {data ? (
        <>
          <div className="stat"><span className="muted">Chain</span><span className="val">{data.chain}</span></div>
          <div className="stat"><span className="muted">Tx count</span><span className="val">{data.n_tx}</span></div>
          <div className="stat"><span className="muted">Balance</span><span className="val">{data.final_balance_btc ?? 'n/a'}</span></div>
        </>
      ) : (
        <div className="muted">—</div>
      )}
    </Panel>
  );
}
