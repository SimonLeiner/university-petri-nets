import React, { useEffect, useState } from 'react';
import InputComponent from '../components/InputComponent';
import { useAlert } from '../providers/AlertProvider';
import ConformanceComponent from '../components/ConformanceComponent';

const HomePage = () => {

  // states
  const { setAlert } = useAlert();
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [existingFiles, setExistingFiles] = useState([]);
  const [miner, setMiner] = useState(''); 
  const [noiseThreshold, setNoiseThreshold] = useState(0); 
  const [conformance, setConformance] = useState({"Alignment-based Fitness": 0, "Alignment-based Precision": 0, "Entropy-based Fitness": 0, "Entropy-based Precision": 0});

  // Reset all states
  const resetEverything = () => {
    setFile(null);
    setMiner('');
    setNoiseThreshold(0);
    setConformance({"Alignment-based Fitness": 0, "Alignment-based Precision": 0, "Entropy-based Fitness": 0, "Entropy-based Precision": 0});
    setLoading(false);
    setAlert('info', 'All states have been reset');
  };
  
  return (
    <div className="home-page">

      {/* Sidebar for file upload and settings */}
      <InputComponent
        file={file} // Pass the file state
        setFile={setFile} // Pass the setter for file state
        miner={miner} // Pass the miner state
        setMiner={setMiner} // Pass the setter for miner state
        noiseThreshold={noiseThreshold} // Pass the noise threshold state
        setNoiseThreshold={setNoiseThreshold} // Pass the setter for noise threshold
        existingFiles={existingFiles} // Pass the existing files
        setExistingFiles={setExistingFiles} // Pass the setter for existing files
        loading={loading} // Pass the loading
        setLoading={setLoading} // Pass the setter for loading
      />






      {/* Main content area for visualizations and conformance */}
      <div className="main-content">
        <header>
          <h1>Discover Petri Net</h1>
        </header>

        <main>

          {/* Visualization section */}
          <div className="divider"></div>
          <section className="visualization">
            <h2>Visualizations</h2>
            <div className="visualization-area">
              <p>This is the visualization section.</p>
            </div>
          </section>

          {/* Conformance section */}
          <div className="divider"></div>
          <ConformanceComponent conformance={conformance} />

          {/* Reset Everything Button */}
          <button onClick={resetEverything} style={{ margin: '10px 0' }}>
            Reset Everything
          </button>
        </main>
      </div>
    </div>
  );
};

export default HomePage;
