import React from 'react';
import { FiMessageCircle, FiZap, FiCheck } from 'react-icons/fi';
import '../styles/Metrics.css';

function Metrics({ messages = [], getTotalTokens }) {
  const totalMessages = messages.length;
  const userMessages = messages.filter(m => m.type === 'user').length;
  const assistantMessages = messages.filter(m => m.type === 'assistant').length;

  let totalTokens = 0;
  try {
    if (typeof getTotalTokens === 'function') {
      totalTokens = getTotalTokens();
    } else if (typeof getTotalTokens === 'number') {
      totalTokens = getTotalTokens;
    }
  } catch (err) {
    console.warn('Error calculating tokens:', err);
  }

  const onTopicMessages = messages.filter(m => m.isOnTopic === true).length;
  const offTopicMessages = messages.filter(m => m.isOnTopic === false).length;
  const totalRelevance = onTopicMessages + offTopicMessages;
  const relevancePercent = totalRelevance > 0
    ? Math.round((onTopicMessages / totalRelevance) * 100)
    : 0;

  if (totalMessages === 0) {
    return (
      <div className="metrics-container empty">
        <p className="metrics-empty">No messages yet</p>
      </div>
    );
  }

  return (
    <div className="metrics-container">
      <div className="metric-card">
        <div className="metric-icon">
          <FiMessageCircle />
        </div>
        <div className="metric-content">
          <div className="metric-label">Messages</div>
          <div className="metric-value">{totalMessages}</div>
          <div className="metric-detail">
            {userMessages} you • {assistantMessages} bot
          </div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon">
          <FiZap />
        </div>
        <div className="metric-content">
          <div className="metric-label">Tokens</div>
          <div className="metric-value">{totalTokens.toLocaleString()}</div>
          <div className="metric-detail">
            {totalTokens > 0 ? `${(totalTokens / totalMessages).toFixed(0)} avg` : 'N/A'}
          </div>
        </div>
      </div>

      {totalRelevance > 0 && (
        <div className="metric-card">
          <div className="metric-icon">
            <FiCheck />
          </div>
          <div className="metric-content">
            <div className="metric-label">Relevance</div>
            <div className="metric-value">{relevancePercent}%</div>
            <div className="metric-detail">
              {onTopicMessages} on-topic • {offTopicMessages} off-topic
            </div>
            <div className="metric-bar">
              <div
                className="metric-bar-fill"
                style={{ width: `${relevancePercent}%` }}
              ></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Metrics;
