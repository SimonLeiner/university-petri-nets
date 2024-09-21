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
  const [dotString, setDotString] = useState('');
  const [miner, setMiner] = useState(''); 
  const [noiseThreshold, setNoiseThreshold] = useState(0); 
  const [conformance, setConformance] = useState({"Alignment-based Fitness": 0, "Alignment-based Precision": 0, "Entropy-based Fitness": 0, "Entropy-based Precision": 0});

  // Call Algorithm
  const applyAlgorithm = async () => {
    if (!file) {
      setAlert('error', 'Please select a file.');
      return;
    }
    if (!miner) {
      setAlert('error', 'Please select a miner.');
      return;
    }
    if (!noiseThreshold) {
      setAlert('error', 'Please select a noise threshold.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    formData.append('miner', miner);
    if (miner === 'inductive') {
      formData.append('noiseThreshold', noiseThreshold);
    }
    try {
      setLoading(true);
      const response = await axios.post(`${import.meta.env.VITE_PYTHON_BACKEND_URL}/discover`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'text',
        timeout: 10000000000,
        withCredentials: true,
      });
      const jsonData = JSON.parse(response.data); 
      const parsedDotString = parsePnmlToDot(jsonData.net);
      setDotString(parsedDotString);
      setConformance(jsonData.conformance)
      setLoading(false);
    } catch (error) {
      console.error('Error applying algorithm:', error);
      setAlert('error', 'Error applying algorithm');
    } finally {
      setLoading(false);
    }
  }

  // Reset all states
  const resetEverything = () => {
    setFile(null);
    setDotString('');
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

        <button onClick={applyAlgorithm} disabled={loading}>
          Start Calculation
        </button>

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
