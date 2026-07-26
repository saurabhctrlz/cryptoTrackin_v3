import React, { useState, useEffect } from 'react';

export default function IdleTerminal({ isDissipating }) {
  const [frameIdx, setFrameIdx] = useState(0);
  const [frames, setFrames] = useState([]);

  useEffect(() => {
    fetch('/ascii-motion.js')
      .then(res => res.text())
      .then(text => {
        try {
          const arrStr = text.substring(text.indexOf('['), text.lastIndexOf(']') + 1);
          // Using Function instead of eval for better scoping, though both are risky if data is untrusted
          // Since it's our own file, it's fine.
          const parsed = new Function('return ' + arrStr)();
          setFrames(parsed);
        } catch (e) {
          console.error('Failed to parse ASCII motion:', e);
        }
      });
  }, []);

  useEffect(() => {
    if (frames.length === 0 || isDissipating) return;
    const interval = setInterval(() => {
      setFrameIdx(prev => (prev + 1) % frames.length);
    }, 40);
    return () => clearInterval(interval);
  }, [frames, isDissipating]);

  if (!frames || frames.length === 0) return null;

  return (
    <div id="idleTerminal" className={isDissipating ? 'is-dissipating' : ''}>
      <div className="idle-terminal__header">SYSTEM STATUS: IDLE</div>
      <div className="idle-terminal__status">AWAITING INPUT...</div>
      <pre id="idleAsciiArt">{frames[frameIdx]}</pre>
    </div>
  );
}
