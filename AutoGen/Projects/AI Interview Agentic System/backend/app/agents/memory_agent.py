from typing import Dict, Any, List, Optional
from app.memory.faiss_store import FAISSStore
from app.memory.session_store import SessionStore


class MemoryAgent:
    """
    Memory Agent handles persistence of interview data.

    - FAISS: Stores embeddings for semantic search of past Q&A
    - Postgres: Stores metadata, scores, and session history

    Only stores data if user has opted in (memory_opt_in=True).
    """

    def __init__(self, session_id: str, db_session):
        self.session_id = session_id
        self.db_session = db_session
        self.faiss_store = FAISSStore()
        self.session_store = SessionStore(db_session)

    async def store_qa(
        self,
        question: str,
        answer: str,
        scores: Dict[str, int],
        feedback: str,
        topic: str,
        memory_opt_in: bool
    ) -> bool:
        """
        Store a Q&A pair with evaluation.

        Only stores to FAISS if memory_opt_in is True.
        Always updates session in Postgres for current interview.
        """
        # Always update session with Q&A for current interview
        qa_item = {
            "question": question,
            "answer": answer,
            "score": scores,
            "feedback": feedback,
            "topic": topic
        }

        self.session_store.add_qa_to_session(self.session_id, qa_item)

        # Only store to FAISS if opted in
        if memory_opt_in:
            text_to_embed = f"Q: {question}\nA: {answer}\nTopic: {topic}"
            metadata = {
                "session_id": self.session_id,
                "scores": scores,
                "topic": topic
            }
            self.faiss_store.add_embedding(text_to_embed, metadata)

        return True

    async def get_past_weaknesses(
        self,
        focus_areas: List[str],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve past Q&A where candidate showed weakness.

        Used to inform question generation for returning candidates.
        """
        weaknesses = []

        for area in focus_areas:
            results = self.faiss_store.search_similar(area, k=limit)
            for result in results:
                # Filter for low scores (weakness indicators)
                if result.get("scores", {}).get("technical", 10) < 6:
                    weaknesses.append(result)

        return weaknesses[:limit]

    async def update_session_scores(self, scores: Dict[str, float]):
        """Update running average scores in session."""
        self.session_store.update_scores(self.session_id, scores)

    async def finalize_session(
        self,
        final_report: str,
        recommendation: str,
        skill_roadmap: List[str]
    ):
        """Finalize session with report and recommendation."""
        self.session_store.finalize_session(
            self.session_id,
            final_report=final_report,
            recommendation=recommendation,
            skill_roadmap=skill_roadmap
        )
