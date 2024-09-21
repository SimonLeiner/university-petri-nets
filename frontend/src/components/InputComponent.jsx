import React, { useEffect } from 'react';
import { useAlert } from '../providers/AlertProvider';
import axios from 'axios';

const InputComponent = ({
  file, // Receive the file state
  setFile, // Receive the setter for file state
  miner, // Receive the miner state
  setMiner, // Receive the setter for miner state
  noiseThreshold, // Receive the noise threshold state
  setNoiseThreshold, // Receive the setter for noise threshold
  existingFiles, // Receive the existing files list
  setExistingFiles, // Receive the setter for existing files
  loading, // Receive the loading state
  setLoading, // Receive the setter for loading
}) => {
  // Alerts
  const { setAlert } = useAlert();

  // Function to handle file upload
  const onFileUpload = async () => {
    if (!file) {
      setAlert('error', 'Please select a file to upload');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
      setLoading(true);
      const response = await axios.post(`${import.meta.env.VITE_PYTHON_BACKEND_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAlert('success', "File uploaded successfully");
      fetchExistingFiles(); // Refresh file list after upload
    } catch (error) {
      console.error('Error uploading file:', error);
      setAlert('error', 'Error uploading file');
    } finally {
      setLoading(false);
    }
  };

  // File selection handler
  const handleFileChange = (event) => {
    setFile(event.target.files[0]); // This should set the entire file object
  };

  // Fetch existing files on mount
  const fetchExistingFiles = async () => {
    try {
      const response = await axios.get(`${import.meta.env.VITE_PYTHON_BACKEND_URL}/files`);
      setExistingFiles(response.data.files);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  // Fetch existing files on mount
  useEffect(() => {
    fetchExistingFiles();
  }, []);

  // File selection for existing files
  const handleFileSelect = async (event) => {
    const selectedFileName = event.target.value;
    if (selectedFileName) {
      try {
        const response = await axios.get(`${import.meta.env.VITE_PYTHON_BACKEND_URL}/files/${selectedFileName}`, {
          responseType: 'blob',
        });
        const fileBlob = response.data;
        const file = new File([fileBlob], selectedFileName);
        setFile(file);
      } catch (error) {
        console.error('Error fetching the file:', error);
        setAlert('error', `Error fetching the file: ${error.message}`);
      }
    }
  };

  // Slider changes
  const handleSliderChange = (event) => {
    setNoiseThreshold(event.target.value);
  };

  // Miner changes
  const handleMinerChange = (event) => {
    setMiner(event.target.value);
  };

  return (
    <div className="input-grid-container">
      {/* Available files section */}
      <div className="grid-item">
        <h3>Available Files</h3>
        <select value={file ? file.name : ''} onChange={handleFileSelect}>
          <option value="">Select a file</option>
          {existingFiles.map((existingFile, index) => (
            <option key={index} value={existingFile}>
              {existingFile}
            </option>
          ))}
        </select>
      </div>

      {/* File upload section */}
      <div className="grid-item">
        <h3>Upload File</h3>
        <input type="file" onChange={handleFileChange} />
        <button onClick={onFileUpload}>Upload</button>
      </div>

      {/* Display selected file section */}
      <div className="grid-item">
        <h3>Selected File</h3>
        {file ? (
          <p style={{ color: 'white' }}>{file.name}</p> // Display the file name
        ) : (
          <p>No file selected.</p>
        )}
      </div>

      {/* Algorithm inputs section */}
      <div className="grid-item">
        <h3>Algorithm Input</h3>
        <label htmlFor="miner-select">
          Miner Type:
          <select id="miner-select" value={miner} onChange={handleMinerChange}>
            <option value="inductive">Inductive Miner</option>
            <option value="split">Split Miner</option>
          </select>
        </label>

        <label htmlFor="noise-threshold">
          Noise Threshold: {noiseThreshold}
          <input
            id="noise-threshold"
            type="range"
            min="0"
            max="100"
            value={noiseThreshold}
            onChange={handleSliderChange}
          />
        </label>
      </div>
    </div>
  );
};

export default InputComponent;
