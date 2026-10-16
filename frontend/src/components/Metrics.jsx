import React from 'react';
import { FiCheck, FiTarget, FiEye, FiStar } from 'react-icons/fi';
import '../styles/Metrics.css';

function Metrics({ metrics }) {
  // Debug
  console.log('Metrics component received:', metrics);

  if (!metrics) {
    return (
      <div className="metrics-container">
        <div className="metrics-placeholder">
          <p>No metrics available yet. Send a message to see quality metrics.</p>
        </div>
      </div>
    );
  }

  const MetricBar = ({ label, value, icon: IconComponent, color }) => {
    const percentage = value ? (value * 100).toFixed(1) : 0;
    
    return (
      <div className="metric-item">
        <div className="metric-header">
          <IconComponent className="metric-icon" />
          <span className="metric-label">{label}</span>
          <span className="metric-percentage">{percentage}%</span>
        </div>
        <div className="metric-bar-container">
          <div 
            className={`metric-bar ${color}`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>
    );
  };

  const getQualityColor = (value) => {
    if (!value && value !== 0) return 'unknown';
    if (value >= 0.8) return 'excellent';
    if (value >= 0.6) return 'good';
    if (value >= 0.4) return 'fair';
    return 'poor';
  };

  return (
    <div className="metrics-container">
      <div className="metrics-header">
        <h3>Answer Quality Metrics</h3>
        <p>Evaluation based on document relevance and answer accuracy</p>
      </div>

      <div className="metrics-grid">
        <MetricBar
          label="Faithfulness"
          value={metrics.faithfulness}
          icon={FiCheck}
          color={getQualityColor(metrics.faithfulness)}
        />
        <MetricBar
          label="Answer Relevancy"
          value={metrics.answer_relevancy}
          icon={FiTarget}
          color={getQualityColor(metrics.answer_relevancy)}
        />
        <MetricBar
          label="Context Precision"
          value={metrics.context_precision}
          icon={FiEye}
          color={getQualityColor(metrics.context_precision)}
        />
        <MetricBar
          label="Overall Quality"
          value={metrics.overall}
          icon={FiStar}
          color={getQualityColor(metrics.overall)}
        />
      </div>

      {/* Info Section */}
      {(metrics.num_docs !== undefined || metrics.is_on_topic !== undefined) && (
        <div className="metrics-info">
          {metrics.num_docs !== undefined && (
            <div className="info-row">
              <span className="info-label">Documents Retrieved</span>
              <span className="info-value">{metrics.num_docs}</span>
            </div>
          )}
          {metrics.is_on_topic !== undefined && (
            <div className="info-row">
              <span className="info-label">On-Topic</span>
              <span className={`info-value ${metrics.is_on_topic ? 'on-topic' : 'off-topic'}`}>
                {metrics.is_on_topic ? 'Yes' : 'No'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="metrics-legend">
        <div className="legend-item">
          <span className="legend-dot excellent"></span>
          <span>Excellent (80-100%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot good"></span>
          <span>Good (60-80%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot fair"></span>
          <span>Fair (40-60%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot poor"></span>
          <span>Poor (&lt;40%)</span>
        </div>
      </div>
    </div>
  );
}

export default Metrics;
