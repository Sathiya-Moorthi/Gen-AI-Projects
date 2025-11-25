"""
Backend module for Mock Interview Chatbot using LangChain.
Handles interview question generation, answer evaluation, and conversation management.
"""

from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, List, Optional
import os
from datetime import datetime


class InterviewBot:
    """Main class for managing mock interview sessions."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initialize the InterviewBot with LangChain components.
        
        Args:
            api_key: OpenAI API key
            model_name: Name of the model to use (default: gpt-4o-mini)
            temperature: Temperature for response generation (default: 0.7)
        """
        self.llm = ChatOpenAI(
            api_key=api_key,
            model_name=model_name,
            temperature=temperature
        )
        
        self.chat_history = ChatMessageHistory()
        
        self.current_role = None
        self.question_count = 0
        self.start_time = None
        
        # Prompt template for generating interview questions
        self.question_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an experienced technical interviewer conducting a mock interview. 
Your role is to ask relevant, challenging, and progressive interview questions based on the candidate's role.

Guidelines:
- Ask one question at a time
- Start with easier questions and gradually increase difficulty
- Ask follow-up questions based on previous answers
- Cover different aspects of the role (technical skills, problem-solving, behavioral)
- Keep questions clear and concise
- Be professional and encouraging

For custom roles: Pay special attention to the job description provided and tailor questions accordingly."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", """Generate the next interview question for this role: {role}
{role_description}

Question number: {question_number}

Please generate a relevant question that aligns with the role requirements and description.""")
        ])
        
        # Prompt template for evaluating answers
        self.evaluation_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an experienced interviewer evaluating a candidate's answer.

Provide constructive feedback that includes:
1. Strengths of the answer
2. Areas for improvement
3. A brief rating (Excellent/Good/Fair/Needs Improvement)
4. Specific suggestions for better answers

Be encouraging but honest. Keep feedback concise and actionable."""),
            ("human", """Question: {question}
Candidate's Answer: {answer}

Please evaluate this answer and provide feedback.""")
        ])
        
        self.question_chain = self.question_prompt | self.llm
        self.evaluation_chain = self.evaluation_prompt | self.llm
    
    def start_interview(self, role: str) -> str:
        """
        Start a new interview session for a specific role.
        
        Args:
            role: The job role/position for the interview (may include description)
            
        Returns:
            Welcome message with the first question
        """
        self.current_role = role
        self.question_count = 0
        self.start_time = datetime.now()
        self.chat_history.clear()
        
        # Extract role name and description if provided
        if " - " in role:
            role_name, role_description = role.split(" - ", 1)
        else:
            role_name = role
            role_description = ""
        
        # Generate first question
        first_question = self.generate_question(role_name, role_description)
        
        welcome_message = f"""Welcome to your mock interview for the **{role_name}** position! 

I'll be asking you a series of questions to help you practice. Take your time to think through your answers, and I'll provide feedback after each response.

Let's begin with your first question:

{first_question}"""
        
        return welcome_message
    
    def generate_question(self, role_name: str = None, role_description: str = "") -> str:
        """
        Generate the next interview question based on conversation history.
        
        Args:
            role_name: The role name (optional, uses current_role if not provided)
            role_description: The role description for custom roles
            
        Returns:
            The generated interview question
        """
        self.question_count += 1
        
        # Use current role if not provided
        if role_name is None:
            if " - " in self.current_role:
                role_name, role_description = self.current_role.split(" - ", 1)
            else:
                role_name = self.current_role
                role_description = ""
        
        # Get chat history
        chat_history = self.chat_history.messages
        
        # Generate question
        response = self.question_chain.invoke({
            "role": role_name,
            "role_description": role_description,
            "question_number": self.question_count,
            "chat_history": chat_history
        })
        
        question = response.content
        
        # Save question to chat history
        self.chat_history.add_ai_message(question)
        
        return question
    
    def evaluate_answer(self, question: str, answer: str) -> Dict[str, str]:
        """
        Evaluate the user's answer and provide feedback.
        
        Args:
            question: The interview question that was asked
            answer: The user's answer to evaluate
            
        Returns:
            Dictionary containing feedback and the next question
        """
        # Save user's answer to chat history
        self.chat_history.add_user_message(answer)
        
        # Generate evaluation
        evaluation_response = self.evaluation_chain.invoke({
            "question": question,
            "answer": answer
        })
        
        feedback = evaluation_response.content
        
        # Generate next question with role information
        if " - " in self.current_role:
            role_name, role_description = self.current_role.split(" - ", 1)
        else:
            role_name = self.current_role
            role_description = ""
        
        next_question = self.generate_question(role_name, role_description)
        
        return {
            "feedback": feedback,
            "next_question": next_question
        }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Retrieve the conversation history.
        
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        messages = self.chat_history.messages
        
        formatted_history = []
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted_history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                formatted_history.append({"role": "assistant", "content": message.content})
        
        return formatted_history
    
    def reset_session(self):
        """Clear conversation memory and reset session state."""
        self.chat_history.clear()
        self.current_role = None
        self.question_count = 0
        self.start_time = None
    
    def get_session_stats(self) -> Dict[str, any]:
        """
        Get statistics about the current interview session.
        
        Returns:
            Dictionary containing session statistics
        """
        elapsed_time = None
        if self.start_time:
            elapsed_time = (datetime.now() - self.start_time).seconds // 60  # in minutes
        
        return {
            "role": self.current_role,
            "questions_asked": self.question_count,
            "elapsed_minutes": elapsed_time
        }
