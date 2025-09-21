import React, { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';


interface AnalysisResult {
    upload_id: number;
    filename: string;
    message: string;
    status: string;
    analysis: {
        rows: number;
        columns: number;
        column_names: string[];
        data_types: { [key: string]: string};
        sample_data: any[];
        missing_values: { [key: string]: number};
        numeric_summary: { [key: string]: any };
    }; 
}


const FileUpload: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

// Handle drag events
const handleDrag = useCallback((e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  if (e.type === "dragenter" || e.type === "dragover") {
    setDragActive(true);
  } else if (e.type === "dragleave") {
    setDragActive(false);
  }
}, []);

// Handle file drop
const handleDrop = useCallback((e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  setDragActive(false);
  
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    uploadFile(e.dataTransfer.files[0]);
  }
}, []);

  // Handle file input change
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  // Validate file type
  const validateFile = (file: File): string | null => {
    const allowedTypes = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    if (!allowedTypes.includes(file.type)) {
      return 'Only CSV and Excel files are allowed.';
    }
    return null;
  };

// Upload file to backend
const uploadFile = async (file: File) => {
  // Reset previous state
  setError(null);
  setResult(null);

  // Validate file
  const validationError = validateFile(file);
  if (validationError) {
    setError(validationError);
    return;
  }

  setUploading(true);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      setError(data.detail || 'Upload failed');
    } else {
      setResult(data);
    }
  } catch (err) {
    setError('Failed to connect to server');
  } finally {
    setUploading(false);
  }
};

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">AI Data Analysis</h2>
      
      {/* Upload Area */}
      <div 
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-white'
        } $(uploading ? 'pointer-events-none opacity-50' : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      > 
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          Drop your CSV or Excel file here
        </p>
        <p className="text-sm text-gray-500 mb-4">or</p>
        <label className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
          <FileText className="mr-2 h-4 w-4" />
          Choose File
          <input 
            type = "file"
            className = "hidden"
            accept = ".csv,.xlsx,.xls"
            onChange = {handleFileInput}
            disabled = {uploading}
          />
        </label>
      </div>

      {/* Loading State */}
      {uploading && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center">
            <Loader2 className="animate-spin h-4 w-4 text-blue-500 mr-2" />
            <p className="text-blue-700">Processing your file...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}
            {/* Success State */}
      {result && (
        <div className="mt-6 p-6 bg-green-50 rounded-lg">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
            <h3 className="text-lg font-semibold text-green-800">Analysis Complete!</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg border">
              <p className="text-2xl font-bold text-blue-600">{result.analysis.rows.toLocaleString()}</p>
              <p className="text-sm text-gray-600">Rows</p>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <p className="text-2xl font-bold text-green-600">{result.analysis.columns}</p>
              <p className="text-sm text-gray-600">Columns</p>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <p className="text-2xl font-bold text-purple-600">
                {Object.values(result.analysis.missing_values).reduce((a, b) => a + b, 0)}
              </p>
              <p className="text-sm text-gray-600">Missing Values</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-semibold mb-2">Column Overview</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {result.analysis.column_names.map((column, index) => (
                <div key={index} className="flex justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm font-medium">{column}</span>
                  <span className="text-xs text-gray-500">
                    {result.analysis.data_types[column]}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;

function handleFileUpload(arg0: any) {
  throw new Error('Function not implemented.');
}
