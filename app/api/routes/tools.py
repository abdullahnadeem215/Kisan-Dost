"""
Deterministic Agricultural Tools API endpoints for Kisan Dost.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.tools.agronomy.crop_advisor import recommend_crops
from app.tools.agronomy.fertilizer_calculator import calculate_fertilizer_needs
from app.tools.agronomy.irrigation_advisor import compute_irrigation_schedule
from app.tools.pest.disease_classifier import identify_disease
from app.tools.pest.dosage_checker import verify_pesticide_dosage
from app.tools.market.mandi_price import get_mandi_prices
from app.tools.market.profit_estimator import estimate_crop_profit
from app.tools.market.selling_advisor import advise_selling_strategy
from app.tools.govt.support_finder import find_government_support
from app.tools.weather.open_meteo import fetch_weather_report
from app.tools.weather.geocoder import geocode_location

router = APIRouter(prefix="/tools", tags=["Agricultural Deterministic Tools"])


# Request Models
class CropAdvisorRequest(BaseModel):
    district: str = Field(default="Multan", json_schema_extra={"example": "Multan"})
    soil: str = Field(default="Loam", json_schema_extra={"example": "Loam"})
    season: str = Field(default="Rabi", json_schema_extra={"example": "Rabi"})
    water: str = Field(default="Low", json_schema_extra={"example": "Low"})
    acreage: float = Field(default=5.0, ge=0.1, json_schema_extra={"example": 5.0})


class FertilizerCalculatorRequest(BaseModel):
    crop_name: str = Field(default="Wheat", json_schema_extra={"example": "Wheat"})
    acreage: float = Field(default=5.0, ge=0.1, json_schema_extra={"example": 5.0})
    target_yield_maunds: Optional[float] = Field(None, json_schema_extra={"example": 40.0})


class IrrigationAdvisorRequest(BaseModel):
    crop_name: str = Field(default="Wheat", json_schema_extra={"example": "Wheat"})
    district: str = Field(default="Multan", json_schema_extra={"example": "Multan"})
    crop_stage: str = Field(default="Tillering / Crown Root Initiation", json_schema_extra={"example": "Tillering"})
    days_since_last_irrigation: int = Field(default=14, ge=0, json_schema_extra={"example": 14})
    soil_texture: str = Field(default="Loam", json_schema_extra={"example": "Loam"})


class DiseaseClassifierRequest(BaseModel):
    crop_name: Optional[str] = Field(default="Wheat", json_schema_extra={"example": "Wheat"})
    symptom_text: Optional[str] = Field(default="yellow pustules in linear stripes on leaf surface", json_schema_extra={"example": "yellow pustules stripes"})
    confidence_threshold: float = Field(default=0.70, ge=0.0, le=1.0)


class DosageCheckerRequest(BaseModel):
    crop_name: str = Field(..., json_schema_extra={"example": "Wheat"})
    pest_name: str = Field(..., json_schema_extra={"example": "Yellow Rust"})
    active_ingredient: str = Field(..., json_schema_extra={"example": "Propiconazole"})
    formulation: str = Field(..., json_schema_extra={"example": "25EC"})
    dosage_val: float = Field(..., ge=0.0, json_schema_extra={"example": 100.0})
    unit: str = Field(default="ml", json_schema_extra={"example": "ml"})


class ProfitEstimatorRequest(BaseModel):
    crop_name: str = Field(default="Wheat", json_schema_extra={"example": "Wheat"})
    land_acres: float = Field(default=5.0, ge=0.1, json_schema_extra={"example": 5.0})
    expected_yield_maunds: Optional[float] = Field(None, json_schema_extra={"example": 40.0})
    expected_mandi_price_pkr: Optional[float] = Field(None, json_schema_extra={"example": 3900.0})


class SellingAdvisorRequest(BaseModel):
    crop_name: str = Field(default="Wheat", json_schema_extra={"example": "Wheat"})
    current_district: str = Field(default="Multan", json_schema_extra={"example": "Multan"})
    volume_maunds: float = Field(default=200.0, ge=1.0, json_schema_extra={"example": 200.0})
    storage_capacity_months: int = Field(default=3, ge=0, json_schema_extra={"example": 3})


# Tool Endpoints
@router.post("/crop-advisor", response_model=Dict[str, Any])
async def api_crop_advisor(req: CropAdvisorRequest):
    """Recommends best crops based on soil, water, season, and district."""
    res = recommend_crops(district=req.district, soil=req.soil, season=req.season, water=req.water, acreage=req.acreage)
    return res.model_dump()


@router.post("/fertilizer-calculator", response_model=Dict[str, Any])
async def api_fertilizer_calculator(req: FertilizerCalculatorRequest):
    """Calculates NPK requirements and converts to bags of Urea/DAP with PKR costs."""
    res = calculate_fertilizer_needs(crop_name=req.crop_name, acreage=req.acreage)
    return res.model_dump()


@router.post("/irrigation-advisor", response_model=Dict[str, Any])
async def api_irrigation_advisor(req: IrrigationAdvisorRequest):
    """Calculates crop evapotranspiration (ETc) and irrigation scheduling using FAO-56."""
    res = compute_irrigation_schedule(
        crop_name=req.crop_name,
        district=req.district,
        growth_stage=req.crop_stage,
        soil_type=req.soil_texture
    )
    return res.model_dump()


@router.post("/disease-classifier", response_model=Dict[str, Any])
async def api_disease_classifier(req: DiseaseClassifierRequest):
    """Identifies disease from symptoms. If confidence < 0.70, flags UNCERTAIN and requests image."""
    res = identify_disease(crop_name=req.crop_name, symptom_text=req.symptom_text, confidence_threshold=req.confidence_threshold)
    return res.model_dump()


@router.post("/dosage-checker", response_model=Dict[str, Any])
async def api_dosage_checker(req: DosageCheckerRequest):
    """Verifies pesticide against Plant Protection registry. Unknown chemicals/dosages are strictly BLOCKED."""
    res = verify_pesticide_dosage(
        crop_name=req.crop_name,
        pest_name=req.pest_name,
        active_ingredient=req.active_ingredient,
        formulation=req.formulation,
        dosage_val=req.dosage_val,
        unit=req.unit
    )
    return res.model_dump()


@router.get("/mandi-prices", response_model=Dict[str, Any])
async def api_mandi_prices(
    commodity: Optional[str] = Query(None, description="Crop/commodity name (e.g. Wheat, Cotton, Rice)"),
    district: Optional[str] = Query(None, description="District name (e.g. Multan, Faisalabad)")
):
    """Retrieves wholesale mandi prices with truthful LIVE, CACHED, or UNAVAILABLE tags."""
    res = get_mandi_prices(commodity=commodity, district=district)
    return res.model_dump()


@router.post("/profit-estimator", response_model=Dict[str, Any])
async def api_profit_estimator(req: ProfitEstimatorRequest):
    """Computes full-season budget: input costs vs revenue, net margin, and break-even yield."""
    res = estimate_crop_profit(
        crop_name=req.crop_name,
        acreage=req.land_acres,
        expected_yield_maunds_per_acre=req.expected_yield_maunds or 40.0,
        expected_price_pkr_per_maund=req.expected_mandi_price_pkr or 3900.0
    )
    return res.model_dump()


@router.post("/selling-advisor", response_model=Dict[str, Any])
async def api_selling_advisor(req: SellingAdvisorRequest):
    """Advises optimal selling timing and target mandi considering transport and storage costs."""
    res = advise_selling_strategy(
        crop_name=req.crop_name,
        district=req.current_district,
        quantity_maunds=req.volume_maunds
    )
    return res.model_dump()


@router.get("/govt-schemes", response_model=Dict[str, Any])
async def api_govt_schemes(
    district: Optional[str] = Query(None, description="Farmer district"),
    land_acres: Optional[float] = Query(None, description="Land holding in acres")
):
    """Surfaces eligible Punjab and Federal schemes (Kisan Card, Green Tractor, Solar Tubewell)."""
    res = find_government_support(district=district, land_acres=land_acres)
    return res.model_dump()


@router.get("/weather", response_model=Dict[str, Any])
async def api_weather(
    district: str = Query(default="Multan", description="Pakistani city/district")
):
    """Fetches real-time weather and FAO-56 ET0 from Open-Meteo API."""
    res = fetch_weather_report(location=district)
    return res.model_dump()


@router.get("/geocode", response_model=Dict[str, Any])
async def api_geocode(
    location: str = Query(default="Multan", description="Location query")
):
    """Geocodes Pakistani city or district into coordinates."""
    res = geocode_location(location)
    return res.model_dump()
