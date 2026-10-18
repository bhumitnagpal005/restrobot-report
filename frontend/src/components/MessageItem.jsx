import React, { useState } from 'react';
import ItemCard from './ItemCard';

export default function MessageItem({ message }) {
  const [showDetails, setShowDetails] = useState(false);
  const isUser = message.role === 'user';
  const isError = message.role === 'error';

  if (isUser) {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }} className="fade-in">
        <div style={{
          background: '#3b82f6',
          color: '#ffffff',
          padding: '10px 16px',
          borderRadius: '16px 16px 2px 16px',
          maxWidth: '80%',
          fontSize: '0.93rem',
          lineHeight: '1.4'
        }}>
          {message.content}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }} className="fade-in">
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          color: '#f87171',
          padding: '12px 16px',
          borderRadius: '12px',
          maxWidth: '85%',
          fontSize: '0.88rem'
        }}>
          🚨 {message.content}
        </div>
      </div>
    );
  }

  const items = message.retrievedItems || [];
  const constraints = message.constraints || {};
  const latency = message.latency || {};
  const metadata = message.metadata || {};
  const methodLabel = message.retrievalMethod ? message.retrievalMethod.toUpperCase() : 'HYBRID RAG';

  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '20px' }} className="fade-in">
      <div style={{
        background: '#1e293b',
        border: '1px solid #334155',
        padding: '16px',
        borderRadius: '16px 16px 16px 2px',
        maxWidth: '85%',
        width: '100%'
      }}>
        {/* Method Header Badge */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            background: 'rgba(255, 107, 53, 0.15)',
            color: '#ff6b35',
            padding: '3px 8px',
            borderRadius: '4px',
            border: '1px solid rgba(255, 107, 53, 0.3)',
            letterSpacing: '0.05em'
          }}>
            METHOD: {methodLabel}
          </span>
          {latency.total_latency_ms && (
            <span style={{ fontSize: '0.73rem', color: '#94a3b8' }}>
              ⚡ Latency: {latency.total_latency_ms}ms
            </span>
          )}
        </div>

        {/* Extracted Constraints Badges */}
        {Object.keys(constraints).length > 0 && (
          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            padding: '8px 10px',
            borderRadius: '6px',
            marginBottom: '12px',
            border: '1px solid #334155'
          }}>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', display: 'block', marginBottom: '4px', fontWeight: 600 }}>
              EXTRACTED CONSTRAINTS:
            </span>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {constraints.dietary_preference && (
                <span className="badge badge-veg">Diet: {constraints.dietary_preference}</span>
              )}
              {constraints.max_price && (
                <span className="badge badge-constraint">Price ≤ ₹{constraints.max_price}</span>
              )}
              {constraints.spice_level && (
                <span className="badge badge-spice">Spice: {constraints.spice_level}</span>
              )}
              {constraints.restaurant_name && (
                <span className="badge badge-constraint">Rest: {constraints.restaurant_name}</span>
              )}
              {constraints.category && (
                <span className="badge badge-constraint">Cat: {constraints.category}</span>
              )}
            </div>
          </div>
        )}

        {/* Bot LLM Text Answer */}
        <div style={{
          fontSize: '0.93rem',
          lineHeight: '1.5',
          color: '#f8fafc',
          marginBottom: '14px',
          whiteSpace: 'pre-wrap'
        }}>
          {message.content}
        </div>

        {/* Retrieved Menu Item Cards */}
        {items.length > 0 && (
          <div style={{ marginTop: '12px' }}>
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '8px' }}>
              Retrieved Candidates ({items.length})
            </h4>
            {items.map((item, idx) => (
              <ItemCard key={idx} item={item} />
            ))}
          </div>
        )}

        {/* Expandable Details Accordion */}
        <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid #334155' }}>
          <button
            onClick={() => setShowDetails(!showDetails)}
            style={{
              background: 'none',
              border: 'none',
              color: '#38bdf8',
              fontSize: '0.78rem',
              cursor: 'pointer',
              fontWeight: 600,
              padding: 0
            }}
          >
            {showDetails ? '▲ Hide Retrieval Details' : '▼ View Retrieval Details & Scores'}
          </button>

          {showDetails && (
            <div style={{
              marginTop: '8px',
              padding: '10px',
              background: '#0f172a',
              borderRadius: '6px',
              fontSize: '0.75rem',
              color: '#cbd5e1',
              fontFamily: 'monospace'
            }}>
              <div><strong>Method:</strong> {methodLabel}</div>
              <div><strong>Retrieval Latency:</strong> {latency.retrieval_latency_ms} ms</div>
              <div><strong>Generation Latency:</strong> {latency.generation_latency_ms} ms</div>
              {metadata.weights && (
                <div><strong>Scoring Weights:</strong> α={metadata.weights.alpha}, β={metadata.weights.beta}, γ={metadata.weights.gamma}</div>
              )}
              {metadata.constraint_satisfaction_rate !== undefined && (
                <div><strong>Constraint Satisfaction Rate (CSR):</strong> {(metadata.constraint_satisfaction_rate * 100).toFixed(1)}%</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
