from datetime import datetime, timezone
from typing import List, Optional
from pydantic import Field
from app.integrations.amis import AMISClient
from app.schemas.market import MandiPrice
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class MandiPriceReport(EvidentiaryDomainModel):
    """
    Summary report of wholesale mandi prices for commodities across Pakistani districts.
    Truthfully declares data freshness status: 🟢 LIVE, 🟡 CACHED, or 🔴 UNAVAILABLE.
    """
    commodity: Optional[str] = Field(None, description="Queried commodity filter")
    district: Optional[str] = Field(None, description="Queried district filter")
    total_records: int = Field(..., ge=0)
    status: str = Field(default="🟡 CACHED", description="Data status: 🟢 LIVE, 🟡 CACHED, or 🔴 UNAVAILABLE")
    is_live: bool = Field(default=False, description="True only if fetched from active live AMIS portal; never claim cached as live")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Timestamp of price reporting")
    status_notes: str = Field(default="Truthfully reported from AMIS Punjab cached dataset; not claimed as live.", description="Data freshness declaration")
    prices: List[MandiPrice] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


def get_mandi_prices(
    commodity: Optional[str] = None,
    district: Optional[str] = None
) -> MandiPriceReport:
    """
    Retrieves wholesale agricultural market rates (min, max, modal prices in PKR per maund) across Punjab mandis.
    Truthfully declares status: 🟢 LIVE, 🟡 CACHED, or 🔴 UNAVAILABLE with ISO timestamp. Never claims cached is live.
    Returns typed MandiPriceReport with attached Evidence.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    client = AMISClient()
    prices = client.get_prices(commodity=commodity, district=district)
    
    if not prices:
        ev = Evidence(
            source_id="AMIS_PRICE_UNAVAILABLE",
            source_name="AMIS Punjab Market Portal",
            verification_state="unverified",
            timestamp=datetime.now(timezone.utc),
            confidence_score=0.0,
            notes=f"Price data unavailable for commodity '{commodity}' in district '{district}'."
        )
        return MandiPriceReport(
            commodity=commodity.title() if commodity else "All Commodities",
            district=district.title() if district else "All Districts",
            total_records=0,
            status="🔴 UNAVAILABLE",
            is_live=False,
            timestamp=now_iso,
            status_notes=f"🔴 UNAVAILABLE: No market price records found for {commodity or 'All Commodities'} in {district or 'All Districts'}.",
            prices=[],
            evidence=[ev]
        )

    # Truthfully declare cached status for local AMIS dataset/benchmarks
    # Cached data must NEVER be claimed as live
    data_status = "🟡 CACHED"
    is_live = False
    status_notes = (
        f"🟡 CACHED: Wholesale rates loaded from AMIS Punjab repository. "
        f"Truthfully declared as cached historical benchmark as of {now_iso}; not claimed as live."
    )

    # Collect and update evidence from returned MandiPrice objects
    all_ev: List[Evidence] = []
    for p in prices:
        p.status = data_status
        p.is_live = is_live
        all_ev.extend(p.evidence)

    return MandiPriceReport(
        commodity=commodity.title() if commodity else "All Commodities",
        district=district.title() if district else "All Districts",
        total_records=len(prices),
        status=data_status,
        is_live=is_live,
        timestamp=now_iso,
        status_notes=status_notes,
        prices=prices,
        evidence=all_ev
    )
