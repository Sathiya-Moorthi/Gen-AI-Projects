"""
WebSocket handler for live interview sessions.

Handles real-time communication between frontend and backend during interviews.
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.models.session import InterviewSession, InterviewPhase
from app.orchestration.interview_flow import InterviewFlow

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for interview sessions."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.interview_flows: Dict[str, InterviewFlow] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.interview_flows:
            del self.interview_flows[session_id]

    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send a message to a specific session."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)

    def get_flow(self, session_id: str) -> Optional[InterviewFlow]:
        """Get interview flow for a session."""
        return self.interview_flows.get(session_id)

    def set_flow(self, session_id: str, flow: InterviewFlow):
        """Store interview flow for a session."""
        self.interview_flows[session_id] = flow


manager = ConnectionManager()


ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
]


@router.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for live interview sessions.

    Client messages:
    - {"type": "start"} - Start the interview
    - {"type": "answer", "data": {"text": "..."}} - Submit answer
    - {"type": "ready"} - Ready for next question
    - {"type": "voice_toggle", "data": {"enabled": true}} - Toggle voice mode

    Server messages:
    - {"type": "intro", "data": {...}} - Interview introduction
    - {"type": "new_question", "data": {...}} - New question
    - {"type": "followup", "data": {...}} - Follow-up question
    - {"type": "score_update", "data": {...}} - Score update
    - {"type": "phase_update", "data": {...}} - Phase change
    - {"type": "time_remaining", "data": {...}} - Time update
    - {"type": "feedback", "data": {...}} - Final feedback
    - {"type": "error", "data": {...}} - Error message
    """
    # Check origin for WebSocket CORS
    origin = websocket.headers.get("origin", "")
    if origin and origin not in ALLOWED_ORIGINS:
        await websocket.close(code=4003, reason="Origin not allowed")
        return

    # Accept connection FIRST to avoid 403 errors
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for session {session_id}")

    # Validate session after accepting
    db = SessionLocal()
    try:
        # Validate session_id format
        try:
            UUID(session_id)
        except ValueError:
            logger.error(f"Invalid session ID format: {session_id}")
            await websocket.send_json({
                "type": "error",
                "data": {"message": "Invalid session ID format", "code": 4001}
            })
            await websocket.close(code=4001, reason="Invalid session ID format")
            return

        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id
        ).first()

        if not session:
            logger.error(f"Session not found: {session_id}")
            await websocket.send_json({
                "type": "error",
                "data": {"message": "Session not found", "code": 4004}
            })
            await websocket.close(code=4004, reason="Session not found")
            return

        if not session.resume_text or not session.job_description:
            logger.error(f"Session {session_id} missing resume or JD")
            await websocket.send_json({
                "type": "error",
                "data": {"message": "Upload resume and JD first", "code": 4000}
            })
            await websocket.close(code=4000, reason="Upload resume and JD first")
            return

        logger.info(f"Session {session_id} validated successfully")

        # Store connection
        manager.active_connections[session_id] = websocket

        # Create send_message callback
        async def send_message(msg: Dict[str, Any]):
            await manager.send_message(session_id, msg)

        # Send initial status
        logger.info(f"Sending connected message for session {session_id}")
        await send_message({
            "type": "connected",
            "data": {
                "session_id": session_id,
                "status": session.status,
                "phase": session.current_phase.value if session.current_phase else "setup",
                "has_resume": True,
                "has_jd": True,
                "role": session.role,
                "seniority": session.detected_seniority.value if session.detected_seniority else None
            }
        })
        logger.info(f"Connected message sent for session {session_id}")

        # Main message loop
        logger.info(f"Entering message loop for session {session_id}")
        while True:
            try:
                logger.info(f"Waiting for message from session {session_id}")
                data = await websocket.receive_json()
                msg_type = data.get("type")
                logger.info(f"Received message type '{msg_type}' from session {session_id}")

                if msg_type == "start":
                    logger.info(f"Starting interview for session {session_id}")
                    await handle_start(session_id, session, db, send_message)

                elif msg_type == "answer":
                    answer_text = data.get("data", {}).get("text", "")
                    logger.info(f"Processing answer for session {session_id}")
                    await handle_answer(session_id, answer_text, send_message)

                elif msg_type == "ready":
                    logger.info(f"Processing ready signal for session {session_id}")
                    await handle_ready(session_id, send_message)

                elif msg_type == "voice_toggle":
                    enabled = data.get("data", {}).get("enabled", False)
                    logger.info(f"Toggling voice mode for session {session_id}: {enabled}")
                    await send_message({
                        "type": "voice_mode",
                        "data": {"enabled": enabled, "message": "Voice mode toggled"}
                    })

                elif msg_type == "status":
                    flow = manager.get_flow(session_id)
                    if flow:
                        await send_message({
                            "type": "status",
                            "data": flow.get_status()
                        })

                else:
                    logger.warning(f"Unknown message type '{msg_type}' from session {session_id}")
                    await send_message({
                        "type": "error",
                        "data": {"message": f"Unknown message type: {msg_type}"}
                    })

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for session {session_id}: {e}")
                await send_message({
                    "type": "error",
                    "data": {"message": "Invalid JSON message"}
                })
            except Exception as e:
                logger.error(f"Error in message loop for session {session_id}: {e}", exc_info=True)
                await send_message({
                    "type": "error",
                    "data": {"message": f"Error: {str(e)}"}
                })

    except Exception as e:
        logger.error(f"WebSocket connection error for session {session_id}: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Connection error: {str(e)}"}
            })
        except Exception as send_error:
            logger.error(f"Failed to send error message for session {session_id}: {send_error}")
    finally:
        logger.info(f"Cleaning up WebSocket connection for session {session_id}")
        manager.disconnect(session_id)
        db.close()


async def handle_start(
    session_id: str,
    session: InterviewSession,
    db: Session,
    send_message
):
    """Handle interview start."""
    logger.info(f"Handling start for session {session_id}")

    async def send_msg(msg):
        await send_message(msg)

    try:
        # Create interview flow
        logger.info(f"Creating interview flow for session {session_id}")
        flow = InterviewFlow(session, db, send_msg)
        manager.set_flow(session_id, flow)

        # Start the interview
        logger.info(f"Starting interview flow for session {session_id}")
        await flow.start()
        logger.info(f"Interview flow started successfully for session {session_id}")

        # Start time update task
        asyncio.create_task(time_update_loop(session_id, flow, send_message))
        logger.info(f"Time update task created for session {session_id}")
    except Exception as e:
        logger.error(f"Error in handle_start for session {session_id}: {e}", exc_info=True)
        raise


async def handle_answer(session_id: str, answer: str, send_message):
    """Handle candidate answer."""
    flow = manager.get_flow(session_id)

    if not flow:
        await send_message({
            "type": "error",
            "data": {"message": "Interview not started. Send 'start' first."}
        })
        return

    if not answer.strip():
        await send_message({
            "type": "error",
            "data": {"message": "Please provide an answer."}
        })
        return

    # Process the answer
    await flow.process_answer(answer)


async def handle_ready(session_id: str, send_message):
    """Handle ready for next question."""
    flow = manager.get_flow(session_id)

    if not flow:
        await send_message({
            "type": "error",
            "data": {"message": "Interview not started."}
        })
        return

    # Generate next question
    await flow.generate_next_question()


async def time_update_loop(session_id: str, flow: InterviewFlow, send_message):
    """Send periodic time updates."""
    while session_id in manager.active_connections:
        try:
            time_remaining = flow.orchestrator.get_time_remaining()
            await send_message({
                "type": "time_remaining",
                "data": {
                    "seconds": time_remaining,
                    "formatted": f"{time_remaining // 60}:{time_remaining % 60:02d}"
                }
            })

            # Check if time is up
            if time_remaining <= 0:
                if flow.orchestrator.current_phase not in [
                    InterviewPhase.FEEDBACK,
                    InterviewPhase.COMPLETED
                ]:
                    await flow.end_interview()
                break

            await asyncio.sleep(30)  # Update every 30 seconds

        except Exception:
            break
