"""
Basic tests for the Mock Interview Chatbot backend.
Note: These tests use mocked LLM responses to avoid API calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend import InterviewBot


class TestInterviewBot:
    """Test cases for InterviewBot class."""
    
    @patch('backend.ChatOpenAI')
    def test_initialization(self, mock_chat_openai):
        """Test that InterviewBot initializes correctly."""
        bot = InterviewBot(api_key="test_key", model_name="gpt-4o-mini", temperature=0.7)
        
        assert bot.current_role is None
        assert bot.question_count == 0
        assert bot.start_time is None
        assert bot.llm is not None
        assert bot.memory is not None
    
    @patch('backend.ChatOpenAI')
    def test_start_interview(self, mock_chat_openai):
        """Test starting a new interview session."""
        # Mock the LLM response
        mock_llm = MagicMock()
        mock_response = Mock()
        mock_response.content = "What is your experience with Python?"
        mock_llm.invoke.return_value = mock_response
        
        mock_chat_openai.return_value = mock_llm
        
        bot = InterviewBot(api_key="test_key")
        result = bot.start_interview("Software Engineer")
        
        assert bot.current_role == "Software Engineer"
        assert bot.question_count == 1
        assert bot.start_time is not None
        assert "Software Engineer" in result
        assert "Welcome" in result
    
    @patch('backend.ChatOpenAI')
    def test_reset_session(self, mock_chat_openai):
        """Test resetting the interview session."""
        bot = InterviewBot(api_key="test_key")
        bot.current_role = "Data Scientist"
        bot.question_count = 5
        
        bot.reset_session()
        
        assert bot.current_role is None
        assert bot.question_count == 0
        assert bot.start_time is None
    
    @patch('backend.ChatOpenAI')
    def test_get_session_stats(self, mock_chat_openai):
        """Test retrieving session statistics."""
        bot = InterviewBot(api_key="test_key")
        bot.current_role = "Product Manager"
        bot.question_count = 3
        
        stats = bot.get_session_stats()
        
        assert stats["role"] == "Product Manager"
        assert stats["questions_asked"] == 3
        assert "elapsed_minutes" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
