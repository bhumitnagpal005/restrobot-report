import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatPage from './pages/ChatPage';
import EvaluationPage from './pages/EvaluationPage';
import { sendChatMessage, sendCompareMessage } from './services/api';

const WELCOME_MSG = {
  role: 'bot',
  content: "Welcome to RestroBot! 🍽️ I can help you search for restaurants and menu items using Keyword Search, Conventional Dense RAG, or Constraint-Aware Hybrid RAG.\n\nTry asking:\n• \"Show vegetarian food under ₹200\"\n• \"Find spicy non-veg rolls under ₹150\"\n• \"Show me vegetarian options from KFC under ₹200\"",
  retrievalMethod: 'hybrid',
  timestamp: Date.now()
};

export default function App() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'evaluation'
  const [approach, setApproach] = useState('hybrid'); // 'keyword', 'dense', 'hybrid', 'compare_all'
  const [conversationId] = useState(() => `session_${Math.random().toString(36).substring(2, 9)}`);
  
  const [messages, setMessages] = useState([WELCOME_MSG]);
  const [isLoading, setIsLoading] = useState(false);
  const [compareData, setCompareData] = useState(null);
  const [inputQuery, setInputQuery] = useState('');

  const handleSend = async (queryText) => {
    const query = queryText || inputQuery;
    if (!query.trim()) return;

    const userMsg = { role: 'user', content: query, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      if (approach === 'compare_all') {
        const compRes = await sendCompareMessage(query, conversationId);
        setCompareData(compRes);
      } else {
        const res = await sendChatMessage(query, approach, conversationId);
        const botMsg = {
          role: 'bot',
          content: res.answer,
          retrievalMethod: res.retrieval_method,
          retrievedItems: res.retrieved_items,
          constraints: res.constraints,
          latency: res.latency,
          metadata: res.metadata,
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, botMsg]);
        setCompareData(null);
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: `Error executing query: ${err.message}`,
        timestamp: Date.now()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([WELCOME_MSG]);
    setCompareData(null);
    setInputQuery('');
  };

  const handleSelectSample = (sampleQuery) => {
    setInputQuery(sampleQuery);
    if (activeTab !== 'chat') setActiveTab('chat');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Header activeTab={activeTab} setActiveTab={setActiveTab} currentApproach={approach} />
      
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar
          approach={approach}
          setApproach={setApproach}
          onNewChat={handleNewChat}
          onSelectSample={handleSelectSample}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#0f172a', overflow: 'hidden' }}>
          {activeTab === 'chat' ? (
            <ChatPage
              messages={messages}
              isLoading={isLoading}
              approach={approach}
              compareData={compareData}
              onSend={handleSend}
              inputQuery={inputQuery}
              setInputQuery={setInputQuery}
            />
          ) : (
            <EvaluationPage />
          )}
        </main>
      </div>
    </div>
  );
}
