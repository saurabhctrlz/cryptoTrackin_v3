import React, { useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import TransactionGraph from './components/TransactionGraph';
import RiskAssessment from './components/RiskAssessment';
import WalletStats from './components/WalletStats';
import TransactionTable from './components/TransactionTable';
import Scanlines from './components/effects/Scanlines';
import BlackHole from './components/backgrounds/BlackHole';
import Dither from './components/backgrounds/Dither';
import Panel from './components/Panel';
import { useTracker } from './hooks/useTracker';

function App() {
  const { trace, status, statusType, graphData, risk, stats, txs } = useTracker();
  const [hasTraced, setHasTraced] = useState(false);

  const handleSearch = async (address) => {
    const success = await trace(address);
    if (success) {
      setHasTraced(true);
    }
  };

  return (
    <>
      {/* Background Layers */}
      <Dither waveColor={[0, 1, 1]} />
      <BlackHole />
      <Scanlines />

      {/* Main Content */}
      <div className="app">
        <Header />
        
        <SearchBar onSearch={handleSearch} status={status} statusType={statusType} />

        <div id="resultsSection" className={`layout ${hasTraced ? 'show' : 'hidden'}`}>
          <div className="main">
            <Panel title="Transaction Flow">
              <TransactionGraph graphData={graphData} />
            </Panel>
          </div>

          <div className="sidebar">
            <RiskAssessment risk={risk} />
            <WalletStats data={stats} />
            <TransactionTable txs={txs} />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
