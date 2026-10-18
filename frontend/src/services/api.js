const API_BASE = '/api';

export async function sendChatMessage(query, approach = 'hybrid', conversationId = 'default_session') {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      retrieval_method: approach,
      conversation_id: conversationId,
      top_k: 5
    })
  });
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP Error ${response.status}`);
  }
  return await response.json();
}

export async function sendCompareMessage(query, conversationId = 'default_session') {
  const response = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      conversation_id: conversationId,
      top_k: 5
    })
  });
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `HTTP Error ${response.status}`);
  }
  return await response.json();
}

export async function getEvaluationResults() {
  const response = await fetch(`${API_BASE}/evaluation/results`);
  if (!response.ok) {
    throw new Error(`HTTP Error ${response.status}`);
  }
  return await response.json();
}

export async function triggerEvaluationRun() {
  const response = await fetch(`${API_BASE}/evaluation/run`, {
    method: 'POST'
  });
  if (!response.ok) {
    throw new Error(`HTTP Error ${response.status}`);
  }
  return await response.json();
}

export async function getRestaurants() {
  const response = await fetch(`${API_BASE}/restaurants`);
  if (!response.ok) {
    throw new Error(`HTTP Error ${response.status}`);
  }
  return await response.json();
}
