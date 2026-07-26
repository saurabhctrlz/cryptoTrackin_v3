import { useState } from 'react';

export function useTracker() {
  const [status, setStatus] = useState('');
  const [statusType, setStatusType] = useState('');
  const [graphData, setGraphData] = useState(null);
  const [risk, setRisk] = useState(null);
  const [stats, setStats] = useState(null);
  const [txs, setTxs] = useState(null);

  const trace = async (address) => {
    setStatus('Tracing...');
    setStatusType('info');

    try {
      const res = await fetch('/api/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address })
      });
      const data = await res.json();

      if (data.error) {
        setStatus(`[!] ${data.error}`);
        setStatusType('err');
        return false;
      }

      if (data.easter_egg) {
        window.location.href = data.fanpage_url;
        return false;
      }

      setGraphData(data.graph);
      setRisk(data.risk);
      setStats(data.data);
      setTxs(data.data.transactions);
      
      const nTx = data.data.transactions ? data.data.transactions.length : 0;
      setStatus(`Loaded ${nTx} transactions.`);
      setStatusType('info');
      
      return true;
    } catch (e) {
      setStatus(`[!] Request failed: ${e.message}`);
      setStatusType('err');
      return false;
    }
  };

  return { trace, status, statusType, graphData, risk, stats, txs };
}
