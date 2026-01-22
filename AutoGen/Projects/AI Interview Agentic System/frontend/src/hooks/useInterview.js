import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';

export function useInterview(sessionId) {
  const [phase, setPhase] = useState('setup');
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [scores, setScores] = useState({ technical: 0, design: 0, communication: 0 });
  const [runningScores, setRunningScores] = useState({ technical: 0, design: 0, communication: 0 });
  const [timeRemaining, setTimeRemaining] = useState(35 * 60);
  const [messages, setMessages] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [isWaiting, setIsWaiting] = useState(false);
  const [intro, setIntro] = useState(null);
  const [questionNumber, setQuestionNumber] = useState(0);

  const {
    isConnected,
    lastMessage,
    error,
    startInterview,
    submitAnswer,
    ready,
    toggleVoice
  } = useWebSocket(sessionId);

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    const { type, data } = lastMessage;

    switch (type) {
      case 'connected':
        setPhase(data.phase || 'setup');
        break;

      case 'intro':
        setPhase('intro');
        setIntro(data);
        setIsWaiting(false);
        break;

      case 'new_question':
        setPhase('questions');
        setCurrentQuestion(data);
        setQuestionNumber(data.question_number || questionNumber + 1);
        setIsWaiting(false);
        addMessage('interviewer', data.question, data.topic, data.difficulty);
        break;

      case 'followup':
        setPhase('followup');
        setCurrentQuestion({ ...currentQuestion, question: data.question, isFollowup: true });
        setIsWaiting(false);
        addMessage('interviewer', data.question, 'Follow-up', data.reason);
        break;

      case 'score_update':
        setScores(data.current_scores);
        setRunningScores(data.running_average);
        addMessage('system', `Feedback: ${data.feedback}`, null, null, data);
        break;

      case 'phase_update':
        setPhase(data.phase);
        if (data.message) {
          addMessage('system', data.message);
        }
        break;

      case 'time_remaining':
        setTimeRemaining(data.seconds);
        break;

      case 'feedback':
        setPhase('completed');
        setFeedback(data);
        setIsWaiting(false);
        break;

      case 'error':
        addMessage('error', data.message);
        setIsWaiting(false);
        break;

      default:
        break;
    }
  }, [lastMessage]);

  const addMessage = useCallback((sender, content, topic = null, extra = null, scoreData = null) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      sender,
      content,
      topic,
      extra,
      scoreData,
      timestamp: new Date().toISOString()
    }]);
  }, []);

  const handleStart = useCallback(() => {
    setIsWaiting(true);
    startInterview();
  }, [startInterview]);

  const handleSubmitAnswer = useCallback((answer) => {
    if (!answer.trim()) return;
    setIsWaiting(true);
    addMessage('candidate', answer);
    submitAnswer(answer);
  }, [submitAnswer, addMessage]);

  const handleReady = useCallback(() => {
    setIsWaiting(true);
    ready();
  }, [ready]);

  return {
    // State
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

    // Actions
    handleStart,
    handleSubmitAnswer,
    handleReady,
    toggleVoice
  };
}
