import React from 'react';

export default function Dither({ waveColor }) {
  const [r, g, b] = waveColor || [0, 1, 1];
  
  return (
    <div 
      style={{ 
        position: 'fixed', 
        inset: 0, 
        zIndex: -1,
        background: `radial-gradient(circle at center, rgba(${r*255}, ${g*255}, ${b*255}, 0.2), transparent)`,
        backgroundImage: 'radial-gradient(rgb(0, 255, 255) 1px, transparent 1px)',
        backgroundSize: '10px 10px',
        opacity: 0.15
      }} 
    />
  );
}
