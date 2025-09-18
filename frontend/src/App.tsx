import React, { useEffect, useState } from 'react';
import { healthCheck } from './services/api';
import './App.css';

function App() {
  const [backendstatus, setBackendStatus] = useState<string>('Checking...');
  
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await healthCheck();
        setBackendStatus(response.data.status);
      } catch (error) {
        setBackendStatus('Error connecting to backend'); 
      }
    };
    checkBackend();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Business Platform</h1>
        <p>Backend Status: {backendstatus}</p>
        <p>Frontend Connected Successfully!</p>
      </header>
    </div>
  );
}

export default App;