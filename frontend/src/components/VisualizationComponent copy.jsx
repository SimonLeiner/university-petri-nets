import React from 'react';

// TODO: Implement the VizualizationComponent
const VizualizationComponent = ( {dotString}) => {
  return (
    <section className="visualization">
            <h2>Visualizations</h2>
            <div className="visualization-area">
              <p>This is the visualization section.</p>
              <div style={{ overflow: 'auto', maxHeight: '400px' }}>
              </div>
            </div>
          </section>
  );
};

export default VizualizationComponent;
