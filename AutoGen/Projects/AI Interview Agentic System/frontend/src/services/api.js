const API_BASE = 'http://127.0.0.1:8000';

export async function startSession() {
  const response = await fetch(`${API_BASE}/session/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!response.ok) throw new Error('Failed to start session');
  return response.json();
}

export async function uploadResume(sessionId, file) {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload/resume`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload resume');
  }
  return response.json();
}

export async function uploadJD(sessionId, jobDescription, role) {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('job_description', jobDescription);
  formData.append('role', role);

  const response = await fetch(`${API_BASE}/upload/jd`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload JD');
  }
  return response.json();
}

export async function optInMemory(sessionId, optIn) {
  const response = await fetch(`${API_BASE}/interview/opt-in-memory?session_id=${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ opt_in: optIn })
  });
  if (!response.ok) throw new Error('Failed to update memory preference');
  return response.json();
}

export async function getReport(sessionId) {
  const response = await fetch(`${API_BASE}/interview/report/${sessionId}`);
  if (!response.ok) throw new Error('Failed to get report');
  return response.json();
}

export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!response.ok) throw new Error('Session not found');
  return response.json();
}
