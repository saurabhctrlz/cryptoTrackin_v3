import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';

export default function TransactionGraph({ graphData }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    const data = {
      nodes: graphData.nodes,
      edges: graphData.edges
    };

    const options = {
      nodes: {
        shape: 'dot',
        font: {
          color: '#FFCCFF',
          face: '"JetBrains Mono", monospace',
          size: 11
        },
        borderWidth: 2
      },
      edges: {
        color: { color: 'rgba(255, 0, 255, 0.25)', highlight: '#FF1B2D' },
        width: 1,
        smooth: { type: 'continuous' },
        arrows: { to: { enabled: true, scaleFactor: 0.5 } }
      },
      physics: {
        barnesHut: {
          gravitationalConstant: -2000,
          springConstant: 0.04,
          springLength: 95
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 200
      }
    };

    const network = new Network(containerRef.current, data, options);

    return () => network.destroy();
  }, [graphData]);

  return (
    <div 
      ref={containerRef} 
      id="graph" 
      style={{ width: '100%', height: '440px' }} 
    />
  );
}
