"""
SQLite persistent profile store and deterministic profile completeness calculator for Kisan Dost.
"""
import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.schemas.farmer import FarmerProfile
from app.schemas.evidence import Evidence

logger = logging.getLogger(__name__)


def calculate_completeness(profile: FarmerProfile) -> float:
    """
    Calculates a deterministic completeness score (0.0 to 100.0) for a farmer profile.
    
    Weights:
    - farmer_id: 10.0
    - name: 15.0
    - district: 15.0
    - agro_climatic_zone: 15.0
    - total_land_acres (>0.0): 15.0
    - irrigation_source: 10.0
    - phone_number: 10.0
    - tehsil: 5.0
    - preferred_language / kisan_card_holder: 5.0
    """
    score = 0.0

    if profile.farmer_id and profile.farmer_id.strip():
        score += 10.0
    if profile.name and profile.name.strip():
        score += 15.0
    if profile.district and profile.district.strip():
        score += 15.0
    if profile.agro_climatic_zone and profile.agro_climatic_zone.strip():
        score += 15.0
    if profile.total_land_acres is not None and profile.total_land_acres > 0.0:
        score += 15.0
    if profile.irrigation_source and profile.irrigation_source.strip():
        score += 10.0
    if profile.phone_number and profile.phone_number.strip():
        score += 10.0
    if profile.tehsil and profile.tehsil.strip():
        score += 5.0
    if profile.preferred_language and profile.preferred_language.strip():
        score += 5.0

    return min(100.0, max(0.0, score))


class FarmerProfileStore:
    """
    SQLite persistent store for farmer profiles.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS farmer_profiles (
                    farmer_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone_number TEXT,
                    district TEXT NOT NULL,
                    tehsil TEXT,
                    agro_climatic_zone TEXT NOT NULL,
                    total_land_acres REAL NOT NULL,
                    irrigation_source TEXT NOT NULL,
                    preferred_language TEXT NOT NULL,
                    kisan_card_holder INTEGER NOT NULL,
                    evidence_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_profile(self, profile: FarmerProfile) -> FarmerProfile:
        """
        Saves or updates a farmer profile in SQLite database.
        """
        now = datetime.now(timezone.utc).isoformat()
        evidence_data = [ev.model_dump(mode="json") for ev in profile.evidence]
        evidence_json = json.dumps(evidence_data)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO farmer_profiles (
                    farmer_id, name, phone_number, district, tehsil,
                    agro_climatic_zone, total_land_acres, irrigation_source,
                    preferred_language, kisan_card_holder, evidence_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(farmer_id) DO UPDATE SET
                    name = excluded.name,
                    phone_number = excluded.phone_number,
                    district = excluded.district,
                    tehsil = excluded.tehsil,
                    agro_climatic_zone = excluded.agro_climatic_zone,
                    total_land_acres = excluded.total_land_acres,
                    irrigation_source = excluded.irrigation_source,
                    preferred_language = excluded.preferred_language,
                    kisan_card_holder = excluded.kisan_card_holder,
                    evidence_json = excluded.evidence_json,
                    updated_at = excluded.updated_at
            """, (
                profile.farmer_id,
                profile.name,
                profile.phone_number,
                profile.district,
                profile.tehsil,
                profile.agro_climatic_zone,
                profile.total_land_acres,
                profile.irrigation_source,
                profile.preferred_language,
                1 if profile.kisan_card_holder else 0,
                evidence_json,
                now,
                now
            ))
            conn.commit()
        return profile

    def get_profile(self, farmer_id: str) -> Optional[FarmerProfile]:
        """
        Retrieves a farmer profile by ID.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM farmer_profiles WHERE farmer_id = ?", (farmer_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_profile(row)

    def update_profile(self, farmer_id: str, updates: Dict[str, Any]) -> Optional[FarmerProfile]:
        """
        Updates specific fields of an existing farmer profile.
        """
        existing = self.get_profile(farmer_id)
        if not existing:
            return None

        current_data = existing.model_dump()
        for field, value in updates.items():
            if field in current_data:
                current_data[field] = value

        updated_profile = FarmerProfile(**current_data)
        return self.save_profile(updated_profile)

    def delete_profile(self, farmer_id: str) -> bool:
        """
        Deletes a profile from SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM farmer_profiles WHERE farmer_id = ?", (farmer_id,))
            conn.commit()
            return cursor.rowcount > 0

    def list_profiles(self) -> List[FarmerProfile]:
        """
        Lists all registered farmer profiles.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM farmer_profiles ORDER BY name ASC")
            rows = cursor.fetchall()
            return [self._row_to_profile(row) for row in rows]

    def _row_to_profile(self, row: sqlite3.Row) -> FarmerProfile:
        evidence_list = []
        if row["evidence_json"]:
            try:
                raw_ev = json.loads(row["evidence_json"])
                evidence_list = [Evidence(**e) for e in raw_ev]
            except Exception as ex:
                logger.warning(f"Failed to parse evidence_json for {row['farmer_id']}: {ex}")

        return FarmerProfile(
            farmer_id=row["farmer_id"],
            name=row["name"],
            phone_number=row["phone_number"],
            district=row["district"],
            tehsil=row["tehsil"],
            agro_climatic_zone=row["agro_climatic_zone"],
            total_land_acres=float(row["total_land_acres"]),
            irrigation_source=row["irrigation_source"],
            preferred_language=row["preferred_language"],
            kisan_card_holder=bool(row["kisan_card_holder"]),
            evidence=evidence_list
        )
