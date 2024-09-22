import React, { useState } from 'react';
import InputComponent from '../components/InputComponent';
import { useAlert } from '../providers/AlertProvider';
import ConformanceComponent from '../components/ConformanceComponent';
import VizualizationComponent from '../components/VisualizationComponent copy';
import axios from 'axios';
import { convertPnmlToDot } from '../converter/DotStringConverter';

const HomePage = () => {

  // states
  const { setAlert } = useAlert();
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [existingFiles, setExistingFiles] = useState([]);
  const [dotString, setDotString] = useState('');
  const [miner, setMiner] = useState(''); 
  const [interfacePattern, setInterfacePattern] = useState('');
  const [noiseThreshold, setNoiseThreshold] = useState(0); 
  const [conformance, setConformance] = useState({"Alignment-based Fitness": 0, "Alignment-based Precision": 0, "Entropy-based Fitness": 0, "Entropy-based Precision": 0});

  // Call Algorithm
  const applyAlgorithm = async () => {
    if (!file) {
      setAlert('error', 'Please select a file.');
      return;
    }
    if (!interfacePattern) {
      setAlert('error', 'Please select a interface pattern.');
      return;
    }
    if (!miner) {
      setAlert('error', 'Please select a miner.');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('miner', miner);
    formData.append('interfacePattern', interfacePattern);
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
      const parsedDotString = convertPnmlToDot(jsonData.net);
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

      {/* Title page */}
      <header>
        <h1>Discover Petri Net</h1>
      </header>

      {/* Main content area for visualizations and conformance */}
      <div className="main-content">

        {/* Main Part */}
        <main>

          {/* Sidebar for file upload and settings */}
          <InputComponent
            file={file} // Pass the file state
            setFile={setFile} // Pass the setter for file state
            miner={miner} // Pass the miner state
            setMiner={setMiner} // Pass the setter for miner state
            interfacePattern={interfacePattern} // Pass the interface pattern state
            setInterfacePattern={setInterfacePattern} // Pass the setter for interface pattern
            noiseThreshold={noiseThreshold} // Pass the noise threshold state
            setNoiseThreshold={setNoiseThreshold} // Pass the setter for noise threshold
            existingFiles={existingFiles} // Pass the existing files
            setExistingFiles={setExistingFiles} // Pass the setter for existing files
            loading={loading} // Pass the loading
            setLoading={setLoading} // Pass the setter for loading
          />

          {/* Visualization section */}
          <div className="divider"></div>
          <VizualizationComponent dotString={dotString} />

          {/* Conformance section */}
          <div className="divider"></div>
          <ConformanceComponent conformance={conformance} />

          {/* Reset Everything Button */}
          <div className="divider"></div>
          <button onClick={resetEverything} style={{ margin: '10px 0' }}>
            Reset Everything
          </button>
        </main>
      </div>

      {/* Footer */}
      <div className="divider"></div>
      <footer className="footer">
        <div className="footer-content">
          <p>&copy; {new Date().getFullYear()} Discovering architecture-aware and sound process models of multi-agent systems: a composition approach by Simon Leiner.</p>
          <p>
            <a href="https://data.niaid.nih.gov/resources?id=zenodo_5830862" target="_blank">Research Paper</a>
          </p>
        </div>
      </footer>

    </div>
  );
};

export default HomePage;
