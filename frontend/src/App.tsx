import React, { useEffect, useState } from 'react';
import FileUpload from './components/FileUpload';
import { healthCheck } from './services/api';
import './App.css';

function App() {
  const [backendStatus, setBackendStatus] = useState<string>('Checking...');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await healthCheck();
        setBackendStatus(response.data.status);
      } catch (error) {
        setBackendStatus('error - backend not running');
      } 
    };
    checkBackend();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
        <header className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <h1 className="text-3xl font-bold text-gray-900">AI Business Platform</h1>
                <p className="text-sm text-gray-500">Backend Status: {backendStatus}</p>
            </div>
        </header>

        <main className="py-8">
            <FileUpload />
        </main>
    </div>
  );
}

export default App;