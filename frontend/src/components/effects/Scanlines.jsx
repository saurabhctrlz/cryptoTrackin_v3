import React from 'react';

export default function Scanlines() {
  return (
    <>
      <div
        id="scanlines"
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 1,
          pointerEvents: 'none',
          background: 'repeating-linear-gradient(to bottom, rgba(0,0,0,0) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,0.14) 3px)',
          mixBlendMode: 'overlay',
        }}
      />
      <div
        id="vignette"
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 1,
          pointerEvents: 'none',
          background: 'radial-gradient(ellipse at center, rgba(7,2,2,0) 30%, rgba(7,2,2,0.92) 100%)',
        }}
      />
    </>
  );
}
