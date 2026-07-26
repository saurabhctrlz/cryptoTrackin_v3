import React from 'react';

export default function Panel({ title, children, className = '' }) {
  return (
    <div className={`panel ${className}`}>
      {title && <h3>{title}</h3>}
      {children}
    </div>
  );
}
