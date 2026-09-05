"""
Profile context auto-hydration module for agent conversation pipelines.
"""
import logging
from typing import Dict, Any, Optional
from app.context.farmer_profile import FarmerProfileStore, calculate_completeness
from app.context.session import SessionContext
from app.schemas.farmer import FarmerProfile
from app.schemas.evidence import Evidence

logger = logging.getLogger(__name__)


class ContextHydrator:
    """
    Utility class for session and profile hydration.
    """
    @staticmethod
    def get_default_profile(district: str = "Multan", acreage: float = 5.0) -> FarmerProfile:
        ev = Evidence(
            source_id="FARMER_REGISTRATION_PORTAL",
            source_name="Punjab Agriculture Dept Farmer Database",
            verification_state="verified"
        )
        return FarmerProfile(
            farmer_id="FARM-DEFAULT-001",
            name="Chaudhry Ahmad",
            phone_number="+923001234567",
            district=district,
            tehsil=district,
            agro_climatic_zone="Southern Irrigated Zone",
            total_land_acres=acreage,
            irrigation_source="Canal+Tubewell",
            preferred_language="ur",
            kisan_card_holder=True,
            evidence=[ev]
        )

    @staticmethod
    def hydrate_session(session: SessionContext, store: Optional[FarmerProfileStore] = None) -> SessionContext:
        if store:
            return hydrate_session_context(session, store)
        return session


def hydrate_session_context(
    session: SessionContext,
    profile_store: FarmerProfileStore
) -> SessionContext:
    """
    Hydrates session object with profile data from SQLite profile store if farmer_id is attached.
    Recalculates profile completeness deterministically.
    """
    if session.farmer_id:
        profile = profile_store.get_profile(session.farmer_id)
        if profile:
            session.farmer_profile = profile
            session.completeness_score = calculate_completeness(profile)
        else:
            logger.warning(f"Farmer ID '{session.farmer_id}' requested for session but not found in profile store.")

    elif session.farmer_profile:
        session.completeness_score = calculate_completeness(session.farmer_profile)

    return session


def build_hydrated_prompt_context(session: SessionContext) -> Dict[str, Any]:
    """
    Constructs a structured context dictionary and system prompt summary formatted for subagent models.
    """
    profile = session.farmer_profile

    if not profile:
        return {
            "is_hydrated": False,
            "completeness_score": 0.0,
            "district": "Unknown",
            "agro_climatic_zone": "Unknown",
            "land_acres": 0.0,
            "irrigation_source": "Canal",
            "language": "ur",
            "kisan_card_holder": False,
            "active_crop": session.active_crop,
            "context_summary": "Anonymous farmer context (Profile incomplete / not provided)."
        }

    completeness = calculate_completeness(profile)
    session.completeness_score = completeness

    summary_text = (
        f"Farmer Profile: {profile.name} (ID: {profile.farmer_id})\n"
        f"Location: {profile.district}" + (f", {profile.tehsil}" if profile.tehsil else "") + "\n"
        f"Agro-Climatic Zone: {profile.agro_climatic_zone}\n"
        f"Land Holding: {profile.total_land_acres} Acres | Irrigation: {profile.irrigation_source}\n"
        f"Kisan Card Holder: {'Yes' if profile.kisan_card_holder else 'No'} | Language: {profile.preferred_language}\n"
        f"Profile Completeness: {completeness:.1f}%\n"
        f"Active Crop Focus: {session.active_crop or 'Not specified'}"
    )

    return {
        "is_hydrated": True,
        "farmer_id": profile.farmer_id,
        "name": profile.name,
        "district": profile.district,
        "tehsil": profile.tehsil,
        "agro_climatic_zone": profile.agro_climatic_zone,
        "land_acres": profile.total_land_acres,
        "irrigation_source": profile.irrigation_source,
        "language": profile.preferred_language,
        "kisan_card_holder": profile.kisan_card_holder,
        "completeness_score": completeness,
        "active_crop": session.active_crop,
        "context_summary": summary_text
    }
