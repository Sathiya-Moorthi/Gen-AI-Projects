import { useState } from 'react';
import { startSession, uploadResume, uploadJD } from './services/api';
import InterviewPage from './pages/InterviewPage';
import './App.css';

function App() {
  const [step, setStep] = useState('setup'); // setup, interview
  const [sessionId, setSessionId] = useState(null);
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [role, setRole] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jdSubmitted, setJdSubmitted] = useState(false);

  const handleStartSession = async () => {
    setLoading(true);
    setError(null);
    try {
      const session = await startSession();
      setSessionId(session.session_id);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  const handleResumeUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setResumeFile(file);
    if (!sessionId) return;

    setLoading(true);
    setError(null);
    try {
      const result = await uploadResume(sessionId, file);
      if (result.detected_seniority) {
        setAnalysis(result);
      }
      // If JD was already submitted, mark it so user knows they're ready
      if (jdSubmitted && result.detected_seniority) {
        // Analysis complete with both resume and JD
      }
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  const handleJDSubmit = async () => {
    if (!sessionId || !jobDescription.trim() || !role.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await uploadJD(sessionId, jobDescription, role);
      setJdSubmitted(true);

      // If resume was already uploaded, re-upload to trigger analysis
      if (resumeFile && !analysis) {
        const result = await uploadResume(sessionId, resumeFile);
        setAnalysis(result);
      }
    } catch (e) {
      setError(e.message);
      setJdSubmitted(false);
    }
    setLoading(false);
  };

  const canStartInterview = sessionId && resumeFile && jobDescription.trim() && role.trim() && jdSubmitted;

  const handleStartInterview = () => {
    if (canStartInterview) {
      setStep('interview');
    }
  };

  if (step === 'interview' && sessionId) {
    return <InterviewPage sessionId={sessionId} analysis={analysis} role={role} />;
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Agentic AI Interview Platform</h1>
        <p>Practice technical interviews with AI-powered agents</p>
      </header>

      <main className="main">
        <div className="setup-container">
          {!sessionId ? (
            <div className="card start-card">
              <h2>Start Your Interview</h2>
              <p>Begin a new mock interview session to practice and improve your technical interview skills.</p>
              <button
                className="btn-primary btn-large"
                onClick={handleStartSession}
                disabled={loading}
              >
                {loading ? 'Creating Session...' : 'Start New Session'}
              </button>
            </div>
          ) : (
            <>
              <div className="card">
                <h2>1. Upload Your Resume {resumeFile && '✓'}</h2>
                <p>Upload your resume (PDF, DOCX, or TXT)</p>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleResumeUpload}
                  disabled={loading}
                />
                {resumeFile && (
                  <p className="file-name" style={{ color: 'green' }}>✓ Selected: {resumeFile.name}</p>
                )}
              </div>

              <div className="card">
                <h2>2. Job Description {jdSubmitted && '✓'}</h2>
                <p>Paste the job description you're preparing for</p>
                <textarea
                  value={jobDescription}
                  onChange={(e) => {
                    setJobDescription(e.target.value);
                    if (jdSubmitted) setJdSubmitted(false);
                  }}
                  placeholder="Paste the job description here..."
                  rows={6}
                  disabled={loading}
                />
              </div>

              <div className="card">
                <h2>3. Target Role {jdSubmitted && '✓'}</h2>
                <p>Enter the role you're interviewing for</p>
                <input
                  type="text"
                  value={role}
                  onChange={(e) => {
                    setRole(e.target.value);
                    if (jdSubmitted) setJdSubmitted(false);
                  }}
                  placeholder="e.g., Senior Software Engineer"
                  disabled={loading}
                />
                <button
                  className="btn-secondary"
                  onClick={handleJDSubmit}
                  disabled={loading || !jobDescription.trim() || !role.trim()}
                  style={{ marginTop: '10px' }}
                >
                  {loading ? 'Analyzing...' : jdSubmitted ? '✓ Profile Analyzed' : 'Analyze Profile'}
                </button>
                {jdSubmitted && (
                  <p style={{ color: 'green', marginTop: '8px', fontSize: '14px' }}>
                    ✓ Job description and role submitted successfully
                  </p>
                )}
              </div>

              {analysis && (
                <div className="card analysis-card">
                  <h2>Profile Analysis</h2>
                  <div className="analysis-grid">
                    <div className="analysis-item">
                      <span className="label">Detected Seniority</span>
                      <span className={`badge badge-${analysis.detected_seniority}`}>
                        {analysis.detected_seniority?.toUpperCase() || 'N/A'}
                      </span>
                    </div>
                    <div className="analysis-item">
                      <span className="label">Strengths</span>
                      <ul>
                        {(analysis.strengths || []).map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="analysis-item">
                      <span className="label">Areas to Explore</span>
                      <ul>
                        {(analysis.gaps || []).map((g, i) => (
                          <li key={i}>{g}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              <div className="card action-card">
                <button
                  className="btn-primary btn-large"
                  onClick={handleStartInterview}
                  disabled={!canStartInterview || loading}
                >
                  {loading ? 'Preparing...' : 'Start Interview'}
                </button>
                {!canStartInterview && (
                  <p className="hint">
                    {!resumeFile && 'Upload your resume. '}
                    {!jdSubmitted && resumeFile && 'Fill in JD and role, then click "Analyze Profile". '}
                    {jdSubmitted && 'You\'re ready to start!'}
                  </p>
                )}
              </div>
            </>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <p>Powered by GPT-4o and AutoGen Agents</p>
      </footer>
    </div>
  );
}

export default App;
