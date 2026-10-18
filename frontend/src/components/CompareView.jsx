import React from 'react';
import ItemCard from './ItemCard';

export default function CompareView({ compareData }) {
  if (!compareData) return null;

  const { query, keyword, dense_rag, hybrid_rag, comparison_summary } = compareData;

  return (
    <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }} className="fade-in">
      {/* Top Banner with Query & Constraints */}
      <div style={{
        background: '#1e293b',
        border: '1px solid #ff6b35',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '20px'
      }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ff6b35', textTransform: 'uppercase', marginBottom: '4px' }}>
          COMPARE ALL MODE — SAME QUERY EXECUTION
        </div>
        <h2 style={{ fontSize: '1.2rem', color: '#f8fafc', marginBottom: '8px' }}>
          "{query}"
        </h2>
        {comparison_summary.constraints_extracted && Object.keys(comparison_summary.constraints_extracted).length > 0 && (
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {Object.entries(comparison_summary.constraints_extracted).map(([k, v], idx) => (
              <span key={idx} className="badge badge-constraint">
                {k}: {v}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 3-Column Side-by-Side Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        {/* Baseline 1: Keyword Retrieval */}
        <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#38bdf8' }}>
              1. KEYWORD RETRIEVAL
            </h3>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
              ⚡ {keyword.latency_ms} ms
            </span>
          </div>

          <div style={{ background: '#1e293b', padding: '10px', borderRadius: '8px', marginBottom: '12px', fontSize: '0.85rem', color: '#cbd5e1' }}>
            <strong>Answer:</strong> {keyword.answer}
          </div>

          <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '8px', fontWeight: 600 }}>
            Retrieved Items ({keyword.retrieved_items?.length || 0}):
          </div>
          {keyword.retrieved_items?.map((item, idx) => (
            <ItemCard key={idx} item={item} showConstraintStatus={false} />
          ))}
        </div>

        {/* Baseline 2: Conventional Dense RAG */}
        <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f43f5e' }}>
              2. CONVENTIONAL DENSE RAG
            </h3>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
              ⚡ {dense_rag.latency_ms} ms
            </span>
          </div>

          <div style={{ background: '#1e293b', padding: '10px', borderRadius: '8px', marginBottom: '12px', fontSize: '0.85rem', color: '#cbd5e1' }}>
            <strong>Answer:</strong> {dense_rag.answer}
          </div>

          <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '8px', fontWeight: 600 }}>
            Retrieved Items ({dense_rag.retrieved_items?.length || 0}):
          </div>
          {dense_rag.retrieved_items?.map((item, idx) => (
            <ItemCard key={idx} item={item} showConstraintStatus={false} />
          ))}
        </div>

        {/* Proposed: Constraint-Aware Hybrid RAG */}
        <div style={{ background: '#0f172a', border: '1px solid #10b981', borderRadius: '12px', padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#34d399' }}>
              3. CONSTRAINT-AWARE HYBRID RAG
            </h3>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
              ⚡ {hybrid_rag.latency_ms} ms
            </span>
          </div>

          <div style={{ background: '#1e293b', padding: '10px', borderRadius: '8px', marginBottom: '12px', fontSize: '0.85rem', color: '#cbd5e1' }}>
            <strong>Answer:</strong> {hybrid_rag.answer}
          </div>

          <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '8px', fontWeight: 600, display: 'flex', justifyContent: 'space-between' }}>
            <span>Retrieved Items ({hybrid_rag.retrieved_items?.length || 0}):</span>
            <span style={{ color: '#34d399' }}>CSR: {(hybrid_rag.constraint_satisfaction_rate * 100).toFixed(0)}%</span>
          </div>
          {hybrid_rag.retrieved_items?.map((item, idx) => (
            <ItemCard key={idx} item={item} showConstraintStatus={true} />
          ))}
        </div>
      </div>

      {/* Bottom Summary Metrics Table */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc', marginBottom: '12px' }}>
          📊 Quantitative Method Comparison Matrix
        </h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', color: '#cbd5e1' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #334155', textAlign: 'left' }}>
              <th style={{ padding: '8px' }}>Retrieval Metric</th>
              <th style={{ padding: '8px', color: '#38bdf8' }}>Keyword (BM25)</th>
              <th style={{ padding: '8px', color: '#f43f5e' }}>Dense RAG</th>
              <th style={{ padding: '8px', color: '#34d399' }}>Constraint Hybrid RAG</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid #1e293b' }}>
              <td style={{ padding: '8px', fontWeight: 600 }}>Constraint Satisfaction Rate</td>
              <td style={{ padding: '8px' }}>{(keyword.constraint_satisfaction_rate * 100).toFixed(0)}%</td>
              <td style={{ padding: '8px' }}>{(dense_rag.constraint_satisfaction_rate * 100).toFixed(0)}%</td>
              <td style={{ padding: '8px', fontWeight: 700, color: '#34d399' }}>{(hybrid_rag.constraint_satisfaction_rate * 100).toFixed(0)}%</td>
            </tr>
            <tr style={{ borderBottom: '1px solid #1e293b' }}>
              <td style={{ padding: '8px', fontWeight: 600 }}>Retrieval Latency</td>
              <td style={{ padding: '8px' }}>{keyword.latency_ms} ms</td>
              <td style={{ padding: '8px' }}>{dense_rag.latency_ms} ms</td>
              <td style={{ padding: '8px' }}>{hybrid_rag.latency_ms} ms</td>
            </tr>
            <tr>
              <td style={{ padding: '8px', fontWeight: 600 }}>Generation Latency</td>
              <td style={{ padding: '8px' }}>{keyword.generation_latency_ms} ms</td>
              <td style={{ padding: '8px' }}>{dense_rag.generation_latency_ms} ms</td>
              <td style={{ padding: '8px' }}>{hybrid_rag.generation_latency_ms} ms</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
