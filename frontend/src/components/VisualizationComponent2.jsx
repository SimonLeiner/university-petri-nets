import React, { useEffect, useRef, useState } from 'react';
import svgPanZoom from 'svg-pan-zoom';

const VisualizationComponent = ({ viz }) => {
  const containerRef = useRef(null);
  const [zoomInstance, setZoomInstance] = useState(null);
  const [svgContent, setSvgContent] = useState('');

  useEffect(() => {
    // Decode and set SVG content when 'viz' changes
    if (viz) {
      const decodedSvg = atob(viz);
      setSvgContent(decodedSvg);
    }
  }, [viz]); // Only re-run when 'viz' changes

  useEffect(() => {
    if (!svgContent) return; // Skip if no SVG content

    // Render the SVG in the container
    if (containerRef.current) {
      containerRef.current.innerHTML = svgContent;

      // Clean up any previous zoom instance
      if (zoomInstance) {
        zoomInstance.destroy();
      }

      // Initialize svgPanZoom
      const newZoomInstance = svgPanZoom(containerRef.current.querySelector('svg'), {
        zoomEnabled: true,
        controlIconsEnabled: true,
        fit: true,
        center: true,
        minZoom: 0.1,
        maxZoom: 10,
      });

      // Fit and center the SVG
      newZoomInstance.fit();
      newZoomInstance.center();
      setZoomInstance(newZoomInstance);
    }

    // Cleanup when component unmounts or 'svgContent' changes
    return () => {
      if (zoomInstance) {
        zoomInstance.destroy();
      }
      if (containerRef.current) {
        containerRef.current.innerHTML = ''; // Clear the container
      }
    };
  }, [svgContent]); // Re-run when 'svgContent' changes

  // Reset zoom function
  const resetZoom = () => {
    if (zoomInstance) {
      zoomInstance.reset();
    }
  };

  // Save the current SVG content to a file
  const saveSVG = () => {
    const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'visualization.svg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <section className="visualization">
      <h2>Visualizations</h2>
      <div className="visualization-area">
        {/* Container for SVG rendering */}
        <div ref={containerRef} style={{ width: '100%', height: '100%', overflow: 'hidden' }} />

        {/* Buttons for resetting zoom and saving the SVG */}
        <button onClick={resetZoom} style={{ margin: '10px' }}>
          Reset Zoom
        </button>
        <button onClick={saveSVG} style={{ margin: '10px' }}>
          Save as SVG
        </button>
      </div>
    </section>
  );
};

export default VisualizationComponent;