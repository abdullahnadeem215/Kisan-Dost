"""
Market rates and commodity prices schema.
"""
from typing import Optional
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class MandiPrice(EvidentiaryDomainModel):
    """
    Agricultural market rate data from AMIS / provincial mandi reports.
    """
    mandi_name: str = Field(..., description="Market name (e.g. Multan Mandi, Lahore Badami Bagh)")
    district: str = Field(...)
    commodity: str = Field(..., description="Crop/Commodity name")
    variety: str = Field(default="FAQ", description="Fair Average Quality / Variety")
    min_price_pkr_per_maund: float = Field(..., ge=0.0)
    max_price_pkr_per_maund: float = Field(..., ge=0.0)
    modal_price_pkr_per_maund: float = Field(..., ge=0.0)
    price_date: str = Field(..., description="Date of price record YYYY-MM-DD")
    price_trend: str = Field(default="Stable", description="Rising, Falling, or Stable")
    status: str = Field(default="🟡 CACHED", description="Data status: 🟢 LIVE, 🟡 CACHED, or 🔴 UNAVAILABLE")
    is_live: bool = Field(default=False, description="True only if fetched from active live AMIS portal")
    evidence: list[Evidence] = Field(default_factory=list, description="Mandi price verification evidence")
