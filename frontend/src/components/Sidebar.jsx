import React from 'react';

const SAMPLE_QUERIES = [
  "Show vegetarian food under ₹200",
  "Find spicy non-veg rolls under ₹150",
  "Which restaurants serve biryani?",
  "Show me vegetarian options from KFC under ₹200",
  "Find pizza under ₹300 near Delhi",
  "Which restaurants offer spicy vegetarian food?"
];

export default function Sidebar({ approach, setApproach, onNewChat, onSelectSample, activeTab, setActiveTab }) {
  const methods = [
    { id: 'keyword', label: 'Keyword Retrieval (BM25)', desc: 'Pure lexical matching baseline' },
    { id: 'dense', label: 'Conventional Dense RAG', desc: 'SBERT + FAISS semantic search' },
    { id: 'hybrid', label: 'Constraint-Aware Hybrid RAG', desc: 'Proposed research approach', badge: 'PROPOSED' },
    { id: 'compare_all', label: 'Compare All Mode', desc: 'Side-by-side comparison on same query', badge: 'BENCHMARK' }
  ];

  return (
    <aside style={{
      width: '280px',
      background: '#0f172a',
      borderRight: '1px solid #334155',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px',
      gap: '16px',
      overflowY: 'auto'
    }}>
      <button className="btn btn-primary" onClick={onNewChat} style={{ justifyContent: 'center', width: '100%', padding: '10px' }}>
        ➕ New Conversation
      </button>

      <div>
        <h3 style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.05em', marginBottom: '10px' }}>
          Retrieval Method
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {methods.map(m => (
            <div
              key={m.id}
              onClick={() => {
                setApproach(m.id);
                if (activeTab !== 'chat') setActiveTab('chat');
              }}
              style={{
                padding: '10px 12px',
                borderRadius: '8px',
                background: approach === m.id ? '#1e293b' : 'transparent',
                border: approach === m.id ? '1px solid #ff6b35' : '1px solid #1e293b',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
                <span style={{ fontSize: '0.88rem', fontWeight: 600, color: approach === m.id ? '#ff6b35' : '#f8fafc' }}>
                  {m.label}
                </span>
                {m.badge && (
                  <span style={{
                    fontSize: '0.65rem',
                    background: m.badge === 'PROPOSED' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(139, 92, 246, 0.2)',
                    color: m.badge === 'PROPOSED' ? '#34d399' : '#c084fc',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontWeight: 700
                  }}>
                    {m.badge}
                  </span>
                )}
              </div>
              <p style={{ fontSize: '0.73rem', color: '#94a3b8' }}>{m.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.05em', marginBottom: '10px' }}>
          Sample Test Queries
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {SAMPLE_QUERIES.map((q, idx) => (
            <div
              key={idx}
              onClick={() => onSelectSample(q)}
              style={{
                padding: '8px 10px',
                background: '#1e293b',
                borderRadius: '6px',
                fontSize: '0.8rem',
                color: '#cbd5e1',
                cursor: 'pointer',
                border: '1px solid #334155',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = '#ff6b35'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = '#334155'}
            >
              "{q}"
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid #1e293b' }}>
        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
          RestroBot v1.0 • Academic Research RAG Platform
        </div>
      </div>
    </aside>
  );
}
