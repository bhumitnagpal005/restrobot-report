import React, { useRef, useEffect } from 'react';
import MessageItem from '../components/MessageItem';
import CompareView from '../components/CompareView';

export default function ChatPage({
  messages,
  isLoading,
  approach,
  compareData,
  onSend,
  inputQuery,
  setInputQuery
}) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, compareData]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputQuery.trim() && !isLoading) {
      onSend(inputQuery);
      setInputQuery('');
    }
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {approach === 'compare_all' && compareData ? (
        <CompareView compareData={compareData} />
      ) : (
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
          {messages.map((msg, idx) => (
            <MessageItem key={idx} message={msg} />
          ))}
          {isLoading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8', fontSize: '0.85rem' }}>
              <span className="fade-in">RestroBot is analyzing query & retrieving candidates...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Message Input Bar */}
      <form onSubmit={handleSubmit} style={{
        padding: '16px 20px',
        background: '#1e293b',
        borderTop: '1px solid #334155',
        display: 'flex',
        gap: '12px'
      }}>
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder={
            approach === 'compare_all'
              ? 'Enter query to run across ALL 3 retrieval methods...'
              : 'Ask RestroBot (e.g., "Show vegetarian food under ₹200")...'
          }
          disabled={isLoading}
          style={{
            flex: 1,
            background: '#0f172a',
            border: '1px solid #334155',
            color: '#f8fafc',
            padding: '12px 16px',
            borderRadius: '8px',
            fontSize: '0.92rem',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={isLoading || !inputQuery.trim()}
          className="btn btn-primary"
          style={{ padding: '0 20px', fontSize: '0.92rem' }}
        >
          {isLoading ? 'Searching...' : 'Send Query ➔'}
        </button>
      </form>
    </div>
  );
}
