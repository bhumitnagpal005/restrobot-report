import React from 'react';

export default function Header({ activeTab, setActiveTab, currentApproach }) {
  return (
    <header style={{
      height: '60px',
      background: '#1e293b',
      borderBottom: '1px solid #334155',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      zIndex: 10
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ fontSize: '1.5rem' }}>🍽️</span>
        <div>
          <h1 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.02em' }}>
            RESTROBOT
          </h1>
          <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Conversational Restaurant Information Retrieval
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <button
          className={`btn ${activeTab === 'chat' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat Interface
        </button>
        <button
          className={`btn ${activeTab === 'evaluation' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('evaluation')}
        >
          📊 Research Dashboard
        </button>
      </div>
    </header>
  );
}
