import React, { useState, useEffect } from 'react';

// A simple Glitch Text effect simulating the OriginKit style
export default function GlitchText({ text }) {
  const [glitching, setGlitching] = useState(false);

  useEffect(() => {
    const glitchInterval = setInterval(() => {
      if (Math.random() > 0.8) {
        setGlitching(true);
        setTimeout(() => setGlitching(false), 150);
      }
    }, 2000);
    return () => clearInterval(glitchInterval);
  }, []);

  if (!glitching) return <>{text}</>;

  return (
    <span style={{ position: 'relative', display: 'inline-block' }}>
      <span style={{ position: 'absolute', top: 0, left: '-2px', color: '#00FFFF', opacity: 0.8, zIndex: -1 }}>{text}</span>
      <span style={{ position: 'absolute', top: 0, left: '2px', color: '#FF00FF', opacity: 0.8, zIndex: -2 }}>{text}</span>
      {text}
    </span>
  );
}
