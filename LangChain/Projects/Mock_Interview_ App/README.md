# 🎯 Mock Interview Chatbot

An AI-powered mock interview chatbot built with **LangChain** and **Streamlit** that helps you practice for job interviews with intelligent question generation and personalized feedback.

## ✨ Features

- 🎤 **Role-Based Interviews**: Choose from 12+ different job roles
- 🤖 **AI-Powered Questions**: Dynamic question generation using GPT-4o-mini
- 💡 **Instant Feedback**: Get constructive evaluation on your answers
- 📈 **Progressive Difficulty**: Questions adapt based on your responses
- 💬 **Conversation Memory**: Context-aware follow-up questions
- 📊 **Session Tracking**: Monitor your progress with real-time statistics
- 🎨 **Modern UI**: Clean and professional Streamlit interface

## 🏗️ Architecture

The application is built with a **clean separation of concerns**:

```
Mock_Interview_App/
├── backend.py          # LangChain logic (InterviewBot class)
├── frontend.py         # Streamlit UI components
├── config.py           # Configuration and settings
├── app.py              # Main entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

### Backend (`backend.py`)
- **InterviewBot class**: Core interview logic
- **LangChain integration**: Question generation and answer evaluation
- **Conversation memory**: Maintains context throughout the session
- **Session management**: Tracks statistics and state

### Frontend (`frontend.py`)
- **Streamlit UI**: Interactive chat interface
- **Session state management**: Handles user interactions
- **Custom styling**: Professional appearance with CSS
- **Sidebar controls**: Role selection and session management

### Configuration (`config.py`)
- **Environment variables**: API key and model settings
- **Interview roles**: Predefined list of job positions
- **Validation**: Ensures proper configuration

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd "d:\Gen AI Project\Social Eagle\LangChain\Projects\Mock_Interview_ App"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     MODEL_NAME=gpt-4o-mini
     TEMPERATURE=0.7
     ```

## 🎮 Usage

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Interview Chatbot

1. **Select a Role**: Choose your target job position from the sidebar dropdown
2. **Start Interview**: Click the "🚀 Start Interview" button
3. **Answer Questions**: Type your responses in the chat input
4. **Receive Feedback**: Get instant evaluation and suggestions
5. **Continue Practice**: Answer follow-up questions to improve
6. **Reset Session**: Click "🔄 Reset Interview" to start over

### Available Roles

- Software Engineer
- Data Scientist
- Product Manager
- Frontend Developer
- Backend Developer
- Full Stack Developer
- DevOps Engineer
- Machine Learning Engineer
- UI/UX Designer
- Business Analyst
- Project Manager
- Quality Assurance Engineer

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `MODEL_NAME` | GPT model to use | `gpt-4o-mini` |
| `TEMPERATURE` | Response creativity (0.0-1.0) | `0.7` |

### Customization

You can customize the application by modifying:

- **Interview Roles**: Edit `INTERVIEW_ROLES` in `config.py`
- **Prompt Templates**: Modify prompts in `backend.py`
- **UI Styling**: Update CSS in `frontend.py`
- **Model Parameters**: Adjust temperature and model in `.env`

## 📝 How It Works

1. **Initialization**: The InterviewBot is created with your API key and model settings
2. **Question Generation**: LangChain uses GPT-4o-mini to generate contextual questions
3. **Answer Evaluation**: Your responses are analyzed for strengths and areas of improvement
4. **Conversation Flow**: Memory maintains context for relevant follow-up questions
5. **Feedback Loop**: Each answer receives constructive feedback before the next question

## 🔧 Troubleshooting

### Common Issues

**Error: "OpenAI API key is not set"**
- Solution: Ensure your `.env` file exists and contains a valid `OPENAI_API_KEY`

**Error: "ModuleNotFoundError"**
- Solution: Install all dependencies with `pip install -r requirements.txt`

**Application doesn't start**
- Solution: Check that you're in the correct directory and run `streamlit run app.py`

**Questions seem repetitive**
- Solution: Try increasing the `TEMPERATURE` value in `.env` (e.g., 0.8 or 0.9)

## 📦 Dependencies

- **streamlit**: Web application framework
- **langchain**: LLM orchestration framework
- **langchain-openai**: OpenAI integration for LangChain
- **python-dotenv**: Environment variable management
- **openai**: OpenAI API client

## 🤝 Contributing

Feel free to enhance this project by:
- Adding more interview roles
- Implementing difficulty levels
- Adding export functionality for interview transcripts
- Creating analytics dashboards
- Supporting multiple languages

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- UI powered by [Streamlit](https://streamlit.io/)
- AI capabilities from [OpenAI](https://openai.com/)

---

**Happy Interviewing! 🎯** Good luck with your interview preparation!
