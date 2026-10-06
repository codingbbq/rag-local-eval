import React from 'react';
import '../styles/Metrics.css';

function Metrics({ metrics }) {
  const getScoreColor = (score) => {
    if (score >= 0.8) return '#10b981'; // green
    if (score >= 0.7) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  return (
    <div className="metrics-container">
      <h3>Answer Quality Metrics</h3>
      
      <div className="metrics-grid">
        <div className="metric-item">
          <label>Faithfulness</label>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{
                width: `${metrics.faithfulness * 100}%`,
                backgroundColor: getScoreColor(metrics.faithfulness)
              }}
            />
          </div>
          <span className="metric-value">
            {(metrics.faithfulness * 100).toFixed(1)}%
          </span>
        </div>

        <div className="metric-item">
          <label>Answer Relevancy</label>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{
                width: `${metrics.answer_relevancy * 100}%`,
                backgroundColor: getScoreColor(metrics.answer_relevancy)
              }}
            />
          </div>
          <span className="metric-value">
            {(metrics.answer_relevancy * 100).toFixed(1)}%
          </span>
        </div>

        <div className="metric-item">
          <label>Context Precision</label>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{
                width: `${metrics.context_precision * 100}%`,
                backgroundColor: getScoreColor(metrics.context_precision)
              }}
            />
          </div>
          <span className="metric-value">
            {(metrics.context_precision * 100).toFixed(1)}%
          </span>
        </div>

        <div className="metric-item overall">
          <label>Overall Score</label>
          <div className="overall-score">
            {(metrics.overall * 100).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
}

export default Metrics;
