import logging
import os
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
)
from livekit.plugins import openai, silero

load_dotenv()
logger = logging.getLogger("voice-agent")

class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
                ROLE: JARVIS (Iron Man Universe).
                MODE: Voice-Only Assistant.

                PERSONALITY:
                - Hyper-intelligent, Calm, Dry Wit, Loyal.
                - Address user as "Sir".

                SPEECH RULES:
                1. CONCISE: Short sentences optimized for TTS.
                2. CLEAN: STRICTLY NO emojis, markdown, lists, or code blocks.
                3. PROACTIVE: Anticipate needs.

                PROTOCOL:
                - Never mention being an AI.
                - If uncertain -> Ask clarifying question efficiently.
            """,
        )

server = AgentServer()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    logger.info("starting entrypoint")
    
    # Initialize the session with the voice pipeline components
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
    )

    # Start the session with our agent logic
    await session.start(
        agent=Assistant(),
        room=ctx.room,
    )

    # Send initial greeting
    await session.say("Hello Sir, Jarvis here. How may I be of assistance?", allow_interruptions=True)

    # Connect to the room
    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(server)
