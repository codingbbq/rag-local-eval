import React, { useState } from 'react';
import '../styles/UploadPage.css';

function UploadPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [chunkSize, setChunkSize] = useState(1000);
  const [chunkOverlap, setChunkOverlap] = useState(200);
  const [retrievalK, setRetrievalK] = useState(5);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    const validFiles = droppedFiles.filter(file => 
      file.name.endsWith('.pdf') || 
      file.name.endsWith('.txt') || 
      file.name.endsWith('.md')
    );

    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles]);
      setMessage({ type: 'success', text: `Added ${validFiles.length} file(s)` });
    } else {
      setMessage({ type: 'error', text: 'Only PDF, TXT, and MD files are supported' });
    }
  };

  const handleFileInput = (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (selectedFiles.length > 0) {
      setFiles(prev => [...prev, ...selectedFiles]);
      setMessage({ type: 'success', text: `Added ${selectedFiles.length} file(s)` });
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setMessage({ type: 'error', text: 'Please select files first' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      // Upload files
      const uploadResponse = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        body: formData
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }

      // Process uploaded files
      const processResponse = await fetch('http://localhost:8000/api/v1/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          chunk_size: parseInt(chunkSize),
          chunk_overlap: parseInt(chunkOverlap),
          retrieval_k: parseInt(retrievalK)
        })
      });

      if (!processResponse.ok) {
        throw new Error('Processing failed');
      }

      setMessage({ 
        type: 'success', 
        text: `Successfully uploaded and processed ${files.length} file(s)` 
      });
      setFiles([]);

    } catch (error) {
      console.error('Upload error:', error);
      setMessage({ 
        type: 'error', 
        text: error.message || 'An error occurred during upload' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = () => {
    if (window.confirm('Clear all uploaded files?')) {
      fetch('http://localhost:8000/api/v1/uploads/clear', {
        method: 'DELETE'
      })
        .then(() => {
          setMessage({ type: 'success', text: 'Uploads cleared' });
        })
        .catch(error => {
          console.error('Clear error:', error);
          setMessage({ type: 'error', text: 'Failed to clear uploads' });
        });
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-content">
        <h1 className="upload-title">Upload Documents</h1>
        <p className="upload-subtitle">
          Add PDF, TXT, or MD files to your knowledge base. They'll be automatically processed and indexed.
        </p>

        {/* Messages */}
        {message && (
          <div className={`status-message status-${message.type}`}>
            {message.text}
          </div>
        )}

        {/* Drop Zone */}
        <div 
          className="drop-zone"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="drop-zone-content">
            <div className="drop-zone-icon">📄</div>
            <div className="drop-text">Drag files here or click to browse</div>
            <div className="drop-hint">PDF, TXT, or MD files (up to 50MB each)</div>
          </div>
          <input
            type="file"
            className="file-input"
            multiple
            accept=".pdf,.txt,.md"
            onChange={handleFileInput}
            onClick={(e) => {
              const input = e.target;
              input.click();
            }}
            id="file-input"
          />
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="file-list">
            <div className="file-list-title">
              Selected Files ({files.length})
            </div>
            {files.map((file, index) => (
              <div key={index} className="file-item">
                <div>
                  <div className="file-name">{file.name}</div>
                  <div className="file-size">
                    {(file.size / 1024).toFixed(2)} KB
                  </div>
                </div>
                <button
                  className="file-remove-btn"
                  onClick={() => removeFile(index)}
                  title="Remove file"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Settings */}
        <div className="upload-settings">
          <div className="settings-title">⚙️ Processing Settings</div>

          <div className="setting-group">
            <label className="setting-label">Chunk Size</label>
            <input
              type="number"
              value={chunkSize}
              onChange={(e) => setChunkSize(e.target.value)}
              className="setting-input"
              min="100"
              max="5000"
              step="100"
            />
            <div className="setting-hint">
              Size of text chunks (higher = fewer chunks, lower = more granular)
            </div>
          </div>

          <div className="setting-group">
            <label className="setting-label">Chunk Overlap</label>
            <input
              type="number"
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(e.target.value)}
              className="setting-input"
              min="0"
              max="500"
              step="50"
            />
            <div className="setting-hint">
              Characters to overlap between chunks (helps maintain context)
            </div>
          </div>

          <div className="setting-group">
            <label className="setting-label">Retrieval K</label>
            <input
              type="number"
              value={retrievalK}
              onChange={(e) => setRetrievalK(e.target.value)}
              className="setting-input"
              min="1"
              max="20"
              step="1"
            />
            <div className="setting-hint">
              Number of documents to retrieve per query
            </div>
          </div>
        </div>

        {/* Buttons */}
        <div className="button-group">
          <button
            className="btn-primary"
            onClick={handleUpload}
            disabled={loading || files.length === 0}
          >
            {loading ? 'Uploading...' : 'Upload & Process'}
          </button>
          <button
            className="btn-secondary"
            onClick={handleClearAll}
            disabled={loading}
          >
            Clear All
          </button>
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
