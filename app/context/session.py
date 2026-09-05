"""
Session management module for tracking active agent sessions and farmer conversations.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.schemas.farmer import FarmerProfile


class SessionContext(BaseModel):
    """
    State container for an active user/agent session.
    """
    session_id: str = Field(default_factory=lambda: f"SESS-{uuid.uuid4().hex[:8].upper()}")
    farmer_id: Optional[str] = Field(None, description="Associated farmer ID if logged in")
    farmer_profile: Optional[FarmerProfile] = Field(None, description="Hydrated farmer profile")
    completeness_score: float = Field(0.0, ge=0.0, le=100.0, description="Farmer profile completeness score")
    active_crop: Optional[str] = Field(None, description="Crop currently in focus (e.g. Wheat)")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation turn history")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session extra variables")


class SessionManager:
    """
    In-memory session manager for managing multi-turn agent sessions.
    """

    def __init__(self):
        self._sessions: Dict[str, SessionContext] = {}

    def create_session(
        self,
        farmer_id: Optional[str] = None,
        farmer_profile: Optional[FarmerProfile] = None,
        active_crop: Optional[str] = None
    ) -> SessionContext:
        """
        Creates and stores a new active session.
        """
        session = SessionContext(
            farmer_id=farmer_id,
            farmer_profile=farmer_profile,
            active_crop=active_crop
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieves a session by ID.
        """
        return self._sessions.get(session_id)

    def update_session(self, session: SessionContext) -> SessionContext:
        """
        Updates session state in manager.
        """
        session.updated_at = datetime.now(timezone.utc)
        self._sessions[session.session_id] = session
        return session

    def close_session(self, session_id: str) -> bool:
        """
        Closes and removes a session.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
