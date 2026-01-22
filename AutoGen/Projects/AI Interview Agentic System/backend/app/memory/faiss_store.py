"""
FAISS Vector Store for semantic search of interview Q&A.

Stores embeddings of questions and answers for:
- Finding similar past questions
- Identifying areas of weakness
- Enabling continuity across sessions
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import faiss

from app.core.config import settings
from app.services.llm_service import get_embedding


class FAISSStore:
    """
    FAISS-based vector store for interview memory.

    Stores embeddings with metadata for semantic search.
    Only persists data when user opts in.
    """

    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        self.metadata_path = f"{self.index_path}_metadata.json"
        self.dimension = 1536  # text-embedding-3-small dimension

        # Initialize or load index
        self.index = self._load_or_create_index()
        self.metadata: List[Dict] = self._load_metadata()

    def _load_or_create_index(self) -> faiss.IndexFlatL2:
        """Load existing index or create new one."""
        index_file = f"{self.index_path}.faiss"

        if os.path.exists(index_file):
            try:
                return faiss.read_index(index_file)
            except Exception:
                pass

        # Create new index
        return faiss.IndexFlatL2(self.dimension)

    def _load_metadata(self) -> List[Dict]:
        """Load metadata from file."""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save(self):
        """Persist index and metadata to disk."""
        os.makedirs(os.path.dirname(self.index_path) or '.', exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, f"{self.index_path}.faiss")

        # Save metadata
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)

    def add_embedding(self, text: str, metadata: Dict[str, Any]) -> int:
        """
        Add text with metadata to the store.

        Args:
            text: Text to embed and store
            metadata: Associated metadata (session_id, scores, topic, etc.)

        Returns:
            Index of the added vector
        """
        # Get embedding
        embedding = get_embedding(text)
        vector = np.array([embedding], dtype=np.float32)

        # Add to index
        self.index.add(vector)

        # Store metadata
        entry = {
            "text": text,
            **metadata
        }
        self.metadata.append(entry)

        # Persist
        self._save()

        return len(self.metadata) - 1

    def search_similar(
        self,
        query: str,
        k: int = 5,
        session_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar Q&A entries.

        Args:
            query: Search query
            k: Number of results to return
            session_filter: Optional session_id to filter results

        Returns:
            List of matching entries with metadata
        """
        if self.index.ntotal == 0:
            return []

        # Get query embedding
        query_embedding = get_embedding(query)
        query_vector = np.array([query_embedding], dtype=np.float32)

        # Search
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_vector, k)

        # Build results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                entry = self.metadata[idx].copy()
                entry["distance"] = float(distances[0][i])

                # Apply session filter if specified
                if session_filter and entry.get("session_id") != session_filter:
                    continue

                results.append(entry)

        return results

    def get_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all entries for a specific session."""
        return [
            entry for entry in self.metadata
            if entry.get("session_id") == session_id
        ]

    def delete_session(self, session_id: str):
        """
        Delete all entries for a session.

        Note: FAISS doesn't support deletion, so we rebuild the index.
        """
        # Filter out entries for this session
        remaining = [
            (i, entry) for i, entry in enumerate(self.metadata)
            if entry.get("session_id") != session_id
        ]

        if len(remaining) == len(self.metadata):
            return  # Nothing to delete

        # Rebuild index
        new_index = faiss.IndexFlatL2(self.dimension)
        new_metadata = []

        for old_idx, entry in remaining:
            text = entry.get("text", "")
            if text:
                embedding = get_embedding(text)
                vector = np.array([embedding], dtype=np.float32)
                new_index.add(vector)
                new_metadata.append(entry)

        self.index = new_index
        self.metadata = new_metadata
        self._save()

    def clear(self):
        """Clear all data from the store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self._save()
