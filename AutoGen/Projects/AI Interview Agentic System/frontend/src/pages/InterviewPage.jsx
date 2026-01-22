import { useState } from 'react';
import { useInterview } from '../hooks/useInterview';
import './InterviewPage.css';

function InterviewPage({ sessionId, analysis, role }) {
  const [answer, setAnswer] = useState('');
  const [voiceEnabled, setVoiceEnabled] = useState(false);

  const {
    phase,
    currentQuestion,
    scores,
    runningScores,
    timeRemaining,
    messages,
    feedback,
    isWaiting,
    intro,
    questionNumber,
    isConnected,
    error,
    handleStart,
    handleSubmitAnswer,
    handleReady,
    toggleVoice
  } = useInterview(sessionId);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSubmit = (e) => {
    e.preventDefault();
    if (answer.trim() && !isWaiting) {
      handleSubmitAnswer(answer);
      setAnswer('');
    }
  };

  const handleVoiceToggle = () => {
    const newValue = !voiceEnabled;
    setVoiceEnabled(newValue);
    toggleVoice(newValue);
  };

  if (feedback) {
    return (
      <div className="interview-page">
        <header className="interview-header">
          <h1>Interview Complete</h1>
          <div className="header-info">
            <span className="role">{role}</span>
          </div>
        </header>

        <main className="feedback-main">
          <div className="feedback-container">
            <div className="card scores-final">
              <h2>Final Scores</h2>
              <div className="score-grid">
                <div className="score-item">
                  <span className="score-label">Technical</span>
                  <span className="score-value">{feedback.final_scores?.technical || 0}/10</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Design</span>
                  <span className="score-value">{feedback.final_scores?.design || 0}/10</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Communication</span>
                  <span className="score-value">{feedback.final_scores?.communication || 0}/10</span>
                </div>
              </div>
              <div className={`recommendation recommendation-${feedback.recommendation?.toLowerCase().replace('-', '')}`}>
                <span>Recommendation:</span>
                <strong>{feedback.recommendation}</strong>
              </div>
            </div>

            <div className="card report-card">
              <h2>Feedback Report</h2>
              <div className="report-content" dangerouslySetInnerHTML={{
                __html: feedback.report?.replace(/\n/g, '<br/>').replace(/## /g, '<h3>').replace(/\*\*/g, '')
              }} />
            </div>

            {feedback.skill_roadmap?.length > 0 && (
              <div className="card roadmap-card">
                <h2>Learning Roadmap</h2>
                <ul className="roadmap-list">
                  {feedback.skill_roadmap.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="interview-page">
      <header className="interview-header">
        <div className="header-left">
          <h1>Technical Interview</h1>
          <span className="role">{role}</span>
        </div>
        <div className="header-right">
          <div className="timer">
            <span className="timer-icon">⏱</span>
            <span className={`timer-value ${timeRemaining < 300 ? 'timer-warning' : ''}`}>
              {formatTime(timeRemaining)}
            </span>
          </div>
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </header>

      <div className="interview-main">
        <aside className="sidebar">
          <div className="card phase-card">
            <h3>Interview Phase</h3>
            <div className="phase-indicator">
              <div className={`phase-step ${['setup', 'intro', 'questions', 'followup', 'evaluation', 'feedback', 'completed'].indexOf(phase) >= 0 ? 'active' : ''}`}>Setup</div>
              <div className={`phase-step ${['intro', 'questions', 'followup', 'evaluation', 'feedback', 'completed'].indexOf(phase) >= 0 ? 'active' : ''}`}>Intro</div>
              <div className={`phase-step ${['questions', 'followup', 'evaluation', 'feedback', 'completed'].indexOf(phase) >= 0 ? 'active' : ''}`}>Questions</div>
              <div className={`phase-step ${['evaluation', 'feedback', 'completed'].indexOf(phase) >= 0 ? 'active' : ''}`}>Evaluation</div>
              <div className={`phase-step ${['feedback', 'completed'].indexOf(phase) >= 0 ? 'active' : ''}`}>Feedback</div>
            </div>
          </div>

          <div className="card scores-card">
            <h3>Live Scores</h3>
            <div className="score-bars">
              <div className="score-bar">
                <label>Technical</label>
                <div className="bar-container">
                  <div className="bar-fill" style={{ width: `${runningScores.technical * 10}%` }}></div>
                </div>
                <span>{runningScores.technical}/10</span>
              </div>
              <div className="score-bar">
                <label>Design</label>
                <div className="bar-container">
                  <div className="bar-fill" style={{ width: `${runningScores.design * 10}%` }}></div>
                </div>
                <span>{runningScores.design}/10</span>
              </div>
              <div className="score-bar">
                <label>Communication</label>
                <div className="bar-container">
                  <div className="bar-fill" style={{ width: `${runningScores.communication * 10}%` }}></div>
                </div>
                <span>{runningScores.communication}/10</span>
              </div>
            </div>
          </div>

          <div className="card question-card">
            <h3>Question {questionNumber || '-'}</h3>
            {currentQuestion && (
              <>
                <span className={`difficulty difficulty-${currentQuestion.difficulty}`}>
                  {currentQuestion.difficulty}
                </span>
                <span className="topic">{currentQuestion.topic}</span>
              </>
            )}
          </div>

          <button
            className={`btn-voice ${voiceEnabled ? 'active' : ''}`}
            onClick={handleVoiceToggle}
          >
            {voiceEnabled ? '🎤 Voice On' : '🔇 Voice Off'}
          </button>
        </aside>

        <main className="chat-area">
          {phase === 'setup' && (
            <div className="start-prompt">
              <h2>Ready to Begin?</h2>
              <p>Your profile has been analyzed. Click below to start your mock interview.</p>
              {analysis && (
                <div className="quick-info">
                  <span>Seniority: <strong>{analysis.detected_seniority?.toUpperCase()}</strong></span>
                </div>
              )}
              <button
                className="btn-primary btn-large"
                onClick={handleStart}
                disabled={isWaiting || !isConnected}
              >
                {isWaiting ? 'Starting...' : 'Begin Interview'}
              </button>
            </div>
          )}

          {intro && phase === 'intro' && (
            <div className="intro-message">
              <div className="message interviewer">
                <div className="message-header">
                  <span className="avatar">🤖</span>
                  <span className="name">Interviewer</span>
                </div>
                <div className="message-content" style={{ whiteSpace: 'pre-wrap' }}>
                  {intro.message}
                </div>
              </div>
              <button
                className="btn-primary"
                onClick={handleReady}
                disabled={isWaiting}
              >
                {isWaiting ? 'Preparing question...' : "I'm Ready - Let's Start!"}
              </button>
            </div>
          )}

          {(phase === 'questions' || phase === 'followup') && (
            <div className="chat-container">
              <div className="messages">
                {messages.map((msg) => (
                  <div key={msg.id} className={`message ${msg.sender}`}>
                    <div className="message-header">
                      <span className="avatar">
                        {msg.sender === 'interviewer' ? '🤖' : msg.sender === 'candidate' ? '👤' : 'ℹ️'}
                      </span>
                      <span className="name">
                        {msg.sender === 'interviewer' ? 'Interviewer' : msg.sender === 'candidate' ? 'You' : 'System'}
                      </span>
                      {msg.topic && <span className="msg-topic">{msg.topic}</span>}
                    </div>
                    <div className="message-content">{msg.content}</div>
                    {msg.scoreData && (
                      <div className="inline-scores">
                        <span>T: {msg.scoreData.current_scores.technical}</span>
                        <span>D: {msg.scoreData.current_scores.design}</span>
                        <span>C: {msg.scoreData.current_scores.communication}</span>
                      </div>
                    )}
                  </div>
                ))}
                {isWaiting && (
                  <div className="message system">
                    <div className="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                )}
              </div>

              <form className="answer-form" onSubmit={handleAnswerSubmit}>
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer here..."
                  disabled={isWaiting}
                  rows={3}
                />
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={!answer.trim() || isWaiting}
                >
                  {isWaiting ? 'Processing...' : 'Submit Answer'}
                </button>
              </form>
            </div>
          )}

          {(phase === 'evaluation' || phase === 'generating_feedback') && (
            <div className="processing-message">
              <div className="spinner"></div>
              <h3>Generating your feedback report...</h3>
              <p>This may take a moment.</p>
            </div>
          )}

          {error && (
            <div className="error-banner">
              {error}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default InterviewPage;
