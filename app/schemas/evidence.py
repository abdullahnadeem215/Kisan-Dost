"""
Evidence schema for grounding all domain models with verification state and metadata.
"""
from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field


VerificationState = Literal["verified", "unverified", "fallback", "stale", "partially_verified"]


class Evidence(BaseModel):
    """
    Metadata attached to data elements to enforce non-negotiable agronomy grounding rules.
    """
    source_id: str = Field(..., description="Unique identifier for the data source or API response")
    source_name: str = Field(..., description="Human-readable name of data provider (e.g. AMIS, Open-Meteo, PBS, PlantVillage)")
    verification_state: VerificationState = Field(
        default="unverified",
        description="Grounding verification state: verified, unverified, fallback, stale, or partially_verified"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when evidence was fetched or calculated"
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    url_or_reference: Optional[str] = Field(None, description="URL or reference document source")
    notes: Optional[str] = Field(None, description="Additional context regarding evidence retrieval or fallback reason")


class EvidentiaryDomainModel(BaseModel):
    """
    Base model that ensures all domain objects carry evidence metadata.
    """
    evidence: list[Evidence] = Field(
        default_factory=list,
        description="List of evidence items proving numerical/agronomic assertions"
    )
