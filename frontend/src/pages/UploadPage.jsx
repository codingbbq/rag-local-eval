import React, { useState, useRef } from 'react';
import '../styles/UploadPage.css';

function UploadPage() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processedInfo, setProcessedInfo] = useState(null);
  const [error, setError] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    chunk_size: 1000,
    chunk_overlap: 200,
    retrieve_k: 5
  });
  const fileInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setUploadedFiles(data.file_names);
      setError(null);
    } catch (err) {
      setError(`Upload error: ${err.message}`);
    } finally {
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
  };

  const handleDragLeave = (e) => {
    e.currentTarget.classList.remove('drag-over');
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files);
    
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setUploadedFiles(data.file_names);
      setError(null);
    } catch (err) {
      setError(`Upload error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    if (uploadedFiles.length === 0) {
      setError('No files uploaded');
      return;
    }

    setLoading(true);
    setError(null);
    setProcessedInfo(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      });

      if (!response.ok) {
        throw new Error('Processing failed');
      }

      const data = await response.json();
      setProcessedInfo(data);
      setUploadedFiles([]);
    } catch (err) {
      setError(`Processing error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClearUploads = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/uploads/clear', {
        method: 'DELETE'
      });
      setUploadedFiles([]);
      setError(null);
    } catch (err) {
      setError(`Clear error: ${err.message}`);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <h1>📚 Upload & Index Documents</h1>
        <p className="subtitle">Add PDF or TXT files to train your RAG system</p>

        {/* Upload Area */}
        <div
          className="upload-area"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-content">
            <div className="upload-icon">📄</div>
            <h3>Drag and drop files here</h3>
            <p>or click to browse</p>
            <p className="file-types">Supported: PDF, TXT</p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.md"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <div className="uploaded-files">
            <h3>✓ Uploaded Files ({uploadedFiles.length})</h3>
            <ul>
              {uploadedFiles.map((file, idx) => (
                <li key={idx}>📄 {file}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Settings Section */}
        <div className="settings-section">
          <button
            className="settings-toggle"
            onClick={() => setShowSettings(!showSettings)}
          >
            {showSettings ? '▼' : '▶'} Advanced Settings
          </button>

          {showSettings && (
            <div className="settings-panel">
              <div className="setting-item">
                <label>Chunk Size (characters)</label>
                <input
                  type="number"
                  value={settings.chunk_size}
                  onChange={(e) =>
                    setSettings({ ...settings, chunk_size: parseInt(e.target.value) })
                  }
                  min="100"
                  max="5000"
                />
                <small>Recommended: 500-1500</small>
              </div>

              <div className="setting-item">
                <label>Chunk Overlap (characters)</label>
                <input
                  type="number"
                  value={settings.chunk_overlap}
                  onChange={(e) =>
                    setSettings({ ...settings, chunk_overlap: parseInt(e.target.value) })
                  }
                  min="0"
                  max="500"
                />
                <small>Recommended: 100-300</small>
              </div>

              <div className="setting-item">
                <label>Retrieval K (documents)</label>
                <input
                  type="number"
                  value={settings.retrieve_k}
                  onChange={(e) =>
                    setSettings({ ...settings, retrieve_k: parseInt(e.target.value) })
                  }
                  min="1"
                  max="20"
                />
                <small>Recommended: 3-10</small>
              </div>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Processing documents...</p>
            <p className="loading-details">
              {uploadedFiles.length > 0
                ? '📄 Creating embeddings...'
                : '💾 Saving to FAISS index...'}
            </p>
          </div>
        )}

        {/* Success State */}
        {processedInfo && (
          <div className="success-message">
            <h3>✅ Processing Complete!</h3>
            <div className="success-details">
              <p>📄 Documents processed: <strong>{processedInfo.documents_processed}</strong></p>
              <p>🔪 Chunks created: <strong>{processedInfo.chunks_created}</strong></p>
              <p>🧠 Embeddings created: <strong>{processedInfo.embeddings_created}</strong></p>
              <p>💾 Total vectors in index: <strong>{processedInfo.total_vectors_in_index}</strong></p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="button-group">
          <button
            className="btn btn-primary"
            onClick={handleProcess}
            disabled={uploadedFiles.length === 0 || loading}
          >
            {loading ? '⏳ Processing...' : '🚀 Process & Index'}
          </button>

          {uploadedFiles.length > 0 && (
            <button
              className="btn btn-secondary"
              onClick={handleClearUploads}
              disabled={loading}
            >
              🗑️ Clear Files
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
