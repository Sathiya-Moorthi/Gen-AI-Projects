"""
Configuration module for Mock Interview Chatbot.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the application."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Available interview roles
    INTERVIEW_ROLES = [
        "Software Engineer",
        "Data Scientist",
        "Product Manager",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "DevOps Engineer",
        "Machine Learning Engineer",
        "UI/UX Designer",
        "Business Analyst",
        "Project Manager",
        "Quality Assurance Engineer",
        "Gen AI Engineer"
    ]
    
    # Application Settings
    APP_TITLE = "🎯 Mock Interview Chatbot"
    APP_ICON = "🎯"
    
    @staticmethod
    def validate_config() -> tuple[bool, str]:
        """
        Validate that all required configuration is present.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not Config.OPENAI_API_KEY:
            return False, "OpenAI API key is not set. Please add it to your .env file."
        
        return True, ""
    
    @staticmethod
    def get_roles() -> List[str]:
        """Get list of available interview roles."""
        return Config.INTERVIEW_ROLES
