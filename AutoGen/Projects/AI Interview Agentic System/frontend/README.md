# Agentic AI Interview Platform - Frontend

React frontend for the AI-powered mock interview system.

## Features

- Single-page interview flow
- Real-time WebSocket communication
- Live score display
- Timer countdown
- Phase indicators
- Feedback report view

## Quick Start

### Prerequisites

- Node.js 18+

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

### Production Build

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── pages/           # Page components
│   └── InterviewPage.jsx
├── components/      # Reusable components
├── hooks/           # Custom React hooks
│   ├── useWebSocket.js
│   └── useInterview.js
├── services/        # API services
│   └── api.js
├── App.jsx          # Main app component
└── main.jsx         # Entry point
```

## Interview Flow

1. **Setup**: Upload resume, paste JD, enter role
2. **Analysis**: AI analyzes profile and detects seniority
3. **Interview**: Answer questions with real-time scoring
4. **Feedback**: Receive comprehensive report

## Configuration

The frontend expects the backend to be running at `http://localhost:8000`. This can be changed in:

- `vite.config.js` - Proxy settings
- `src/services/api.js` - API base URL
- `src/hooks/useWebSocket.js` - WebSocket URL

## Tech Stack

- React 18
- Vite
- WebSocket API
- CSS (no frameworks)
