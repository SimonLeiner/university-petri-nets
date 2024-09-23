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


// import React, { useEffect, useRef, useState } from 'react';
// import { instance } from '@viz-js/viz';
// import svgPanZoom from 'svg-pan-zoom';

// const VisualizationComponent = ({ dotString }) => {
//   const containerRef = useRef(null);
//   const [zoomInstance, setZoomInstance] = useState(null);

//   useEffect(() => {
//     // Only proceed if dotString is valid
//     if (!dotString) return;

//     // Create a new Viz instance
//     instance()
//       .then((viz) => {
//         return viz.renderSVGElement(dotString);
//       })
//       .then((svgElement) => {
//         // Clear previous content
//         containerRef.current.innerHTML = '';
//         containerRef.current.appendChild(svgElement);

//         // Initialize svgPanZoom
//         if (zoomInstance) {
//           zoomInstance.destroy(); // Clean up previous instance if it exists
//         }
//         const newZoomInstance = svgPanZoom(svgElement, {
//           zoomEnabled: true,
//           controlIconsEnabled: true,
//           fit: true,
//           center: true,
//           minZoom: 0.1,
//           maxZoom: 10,

//         });
//         setZoomInstance(newZoomInstance);
//       })
//       .catch((error) => {
//         console.error('Error rendering the graph:', error);
//       });

//     // Cleanup on component unmount
//     return () => {
//       if (zoomInstance) {
//         zoomInstance.destroy(); // Ensure the zoom instance is destroyed
//       }
//       containerRef.current.innerHTML = ''; // Clear content
//     };
//   }, [dotString]);

//   const resetZoom = () => {
//     if (zoomInstance) {
//       zoomInstance.reset();
//     }
//   };

//   const saveSVG = () => {
//     const svgElement = containerRef.current.querySelector('svg');
//     if (!svgElement) return;

//     const serializer = new XMLSerializer();
//     const svgString = serializer.serializeToString(svgElement);
//     const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
//     const url = URL.createObjectURL(blob);

//     const link = document.createElement('a');
//     link.href = url;
//     link.download = 'petri_net.svg';
//     document.body.appendChild(link);
//     link.click();
//     document.body.removeChild(link);
//     URL.revokeObjectURL(url);
//   };

//   return (
//     <section className="visualization">
//       <h2>Visualizations</h2>
//       <div className="visualization-area">
//         <div ref={containerRef} style={{ width: '100%', height: '100%', overflow: 'hidden' }} />
//         <button onClick={resetZoom} style={{ margin: '10px' }}>
//           Reset Zoom
//         </button>
//         <button onClick={saveSVG} style={{ margin: '10px' }}>
//           Save as SVG
//         </button>
//       </div>
//     </section>
//   );
// };

// export default VisualizationComponent;
