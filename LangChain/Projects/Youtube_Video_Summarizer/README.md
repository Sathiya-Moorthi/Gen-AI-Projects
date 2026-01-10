# 📺 YouTube Video Summarizer

An AI-powered **YouTube video summarizer** that extracts transcripts and generates concise bullet-point summaries.

## ✨ Features

- 🎬 **Multiple URL Formats**: Supports various YouTube URL formats
- 📝 **Auto Transcript Extraction**: Fetches video captions automatically
- 🤖 **AI Summarization**: Generates structured bullet-point summaries
- 👀 **Transcript Preview**: View raw transcript before summarizing
- 📥 **Download Summary**: Export summaries as `.txt` files
- ⚡ **Fast Processing**: Efficient transcript handling with truncation for long videos
- 🎨 **Modern UI**: Clean, YouTube-themed interface

## 🏗️ Architecture

```
Youtube_Video_Summarizer/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── test_*.py           # Test files
└── README.md           # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- OpenAI API key

### Setup

1. **Navigate to the project directory**
   ```bash
   cd Youtube_Video_Summarizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## 🎮 Usage

Start the application:
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### How to Use

1. Enter your OpenAI API key in the sidebar (or set in `.env`)
2. Paste a YouTube video URL
3. Click "Summarize Video"
4. View the transcript preview and AI-generated summary
5. Download the summary as a text file

### Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## ⚠️ Limitations

- **Captions Required**: Only works with videos that have captions/subtitles
- **Transcript Length**: Long videos are truncated to 10,000 characters
- **Language**: Works best with English transcripts

## 📦 Dependencies

- `streamlit` - Web application framework
- `openai` - OpenAI API client
- `youtube-transcript-api` - YouTube transcript extraction
- `python-dotenv` - Environment variable management
- `pytube` - YouTube metadata (optional)

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Built with 🦜🔗 LangChain, OpenAI & Streamlit**
