import React from 'react';
import './App.css';
import HomePage from './pages/HomePage';
import { AlertProvider } from './providers/AlertProvider';
import AlertComponent from './components/AlertComponent';

function App() {
  return (
    <div className="App">
      <AlertProvider>
        <AlertComponent/>
        <HomePage />
      </AlertProvider>

    </div>
  );
}

export default App;
