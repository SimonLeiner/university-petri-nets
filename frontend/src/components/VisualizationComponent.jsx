import React, { useEffect, useRef } from 'react';
import { instance } from '@viz-js/viz';
import { useAlert } from '../providers/AlertProvider';

const VizualizationComponent = ({ dotString }) => {
  const { setAlert } = useAlert();
  const containerRef = useRef(null);

  useEffect(() => {
    // Only proceed if dotString is valid
    if (!dotString) return;

    // Create a new Viz instance
    instance()
      .then((viz) => {
        return viz.renderSVGElement(dotString);
      })
      .then((svgElement) => {
        containerRef.current.innerHTML = ''; // Clear any previous content
        containerRef.current.appendChild(svgElement);
      })
      .catch((error) => {
        console.error('Error rendering the graph:', error);
      });

    // Cleanup on component unmount
    return () => {
      containerRef.current.innerHTML = '';
    };
  }, [dotString]);

  const saveSVG = () => {
    const svgElement = containerRef.current.querySelector('svg');
    if (!svgElement) {
      console.error('No Viz provided');
      setAlert('error', 'No Viz provided');
      return;
    }

    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgElement);
    const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'petri_net.svg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <section className="visualization">
      <h2>Visualizations</h2>
      <div className="visualization-area">
        <div ref={containerRef} style={{ overflow: 'auto', maxHeight: '400px', marginBottom : '10px 0'}} />
        <button onClick={saveSVG}>
          Save as SVG
        </button>
      </div>
    </section>
  );
};

export default VizualizationComponent;

