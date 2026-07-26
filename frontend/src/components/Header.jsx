import React, { useState, useEffect } from 'react';
import GlitchText from './effects/GlitchText';

export default function Header() {
  const [frameIdx, setFrameIdx] = useState(0);
  const [frames, setFrames] = useState([]);

  useEffect(() => {
    fetch('/ascii-motion.js')
      .then(res => res.text())
      .then(text => {
        try {
          const arrStr = text.substring(text.indexOf('['), text.lastIndexOf(']') + 1);
          const parsed = new Function('return ' + arrStr)();
          setFrames(parsed);
        } catch (e) {
          console.error('Failed to parse ASCII motion:', e);
        }
      });
  }, []);

  useEffect(() => {
    if (frames.length === 0) return;
    const interval = setInterval(() => {
      setFrameIdx(prev => (prev + 1) % frames.length);
    }, 40);
    return () => clearInterval(interval);
  }, [frames]);

  return (
    <header>
      <div 
        style={{ 
          width: '64px', 
          height: '64px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          overflow: 'hidden',
          borderRadius: '4px',
          boxShadow: '0 0 12px rgba(57, 255, 20, 0.3)',
          border: '1px solid rgba(57, 255, 20, 0.2)',
          background: 'rgba(0, 0, 0, 0.5)'
        }}
      >
        {frames.length > 0 ? (
          <pre style={{
            fontSize: '1.2px',
            lineHeight: '0.9',
            color: '#39ff14',
            textShadow: '0 0 2px #39ff14',
            margin: 0,
            fontFamily: 'Courier New, monospace',
            userSelect: 'none',
            textAlign: 'center'
          }}>
            {frames[frameIdx]}
          </pre>
        ) : (
          <img src="/logo_hex.png" alt="CryptoTrackin logo" style={{ width: '100%', height: '100%' }} />
        )}
      </div>
      <div>
        <h1 className="wordmark">
          <GlitchText text="CryptoTrackin" />
        </h1>
        <p className="tagline">
          Blockchain Transaction Forensics &middot; <span className="credit">built by ambatron_ctrlz</span>
        </p>
      </div>
    </header>
  );
}
