import React, { useState } from 'react';
import ScrambleText from './effects/ScrambleText';
import Panel from './Panel';

export default function SearchBar({ onSearch, status, statusType }) {
  const [address, setAddress] = useState('');

  const handleSearch = () => {
    if (!address.trim()) return;
    onSearch(address.trim());
  };

  return (
    <Panel>
      <div className="search-row">
        <input 
          type="text" 
          placeholder="Enter a BTC / ETH / LTC wallet address..." 
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch}>Trace</button>
      </div>
      {status && (
        <div id="status" className={statusType === 'err' ? 'err' : ''}>
          <ScrambleText text={status} active={statusType !== 'err'} />
        </div>
      )}
    </Panel>
  );
}
