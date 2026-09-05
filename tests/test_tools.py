"""
Comprehensive test suite for Kisan Dost deterministic tools.
"""
import pytest
from app.tools.agronomy.crop_advisor import recommend_crops, CropAdvisorReport
from app.tools.agronomy.fertilizer_calculator import calculate_fertilizer_needs, FertilizerCalculationResult
from app.tools.agronomy.irrigation_advisor import compute_irrigation_schedule, IrrigationSchedule
from app.tools.pest.disease_classifier import identify_disease, DiseaseDiagnosticResult
from app.tools.pest.dosage_checker import verify_pesticide_dosage, PesticideDosageCheckResult
from app.tools.market.mandi_price import get_mandi_prices, MandiPriceReport
from app.tools.market.profit_estimator import estimate_crop_profit, DetailedProfitEstimate
from app.tools.market.selling_advisor import advise_selling_strategy, SellingAdvice
from app.tools.govt.support_finder import find_government_support, GovtSupportReport
from app.tools.weather.geocoder import geocode_location, GeocodingResult
from app.tools.weather.open_meteo import fetch_weather_report, WeatherData


def test_geocoder():
    res = geocode_location("Multan")
    assert isinstance(res, GeocodingResult)
    assert res.district == "Multan"
    assert res.latitude > 25.0
    assert len(res.evidence) > 0
    assert res.evidence[0].verification_state == "verified"


def test_open_meteo_weather():
    res = fetch_weather_report("Multan")
    assert isinstance(res, WeatherData)
    assert res.temperature_c > -50.0
    assert res.et0_mm is not None
    assert len(res.evidence) > 0


def test_crop_advisor():
    res = recommend_crops(
        district="Multan",
        soil="Loam",
        season="Rabi",
        water="High",
        acreage=5.0
    )
    assert isinstance(res, CropAdvisorReport)
    assert res.district == "Multan"
    assert len(res.recommendations) > 0
    top_rec = res.recommendations[0]
    assert top_rec.net_profit_total_pkr > 0
    assert len(res.evidence) > 0


def test_fertilizer_calculator():
    res = calculate_fertilizer_needs(
        crop_name="Wheat",
        acreage=10.0,
        custom_npk="50-25-0"
    )
    assert isinstance(res, FertilizerCalculationResult)
    assert res.acreage == 10.0
    assert res.total_cost_pkr > 0
    assert len(res.bag_breakdown) >= 2
    assert len(res.evidence) > 0


def test_irrigation_advisor():
    res = compute_irrigation_schedule(
        crop_name="Wheat",
        growth_stage="Development",
        soil_type="Loam",
        et0_mm_day=4.5,
        current_moisture_percent=40.0,
        district="Multan"
    )
    assert isinstance(res, IrrigationSchedule)
    assert res.daily_water_need_mm > 0
    assert res.recommended_water_depth_mm > 0
    assert len(res.evidence) > 0


def test_disease_classifier():
    res = identify_disease(
        crop_name="Wheat",
        symptom_text="Bright yellow linear pustules on leaves with yellow powder"
    )
    assert isinstance(res, DiseaseDiagnosticResult)
    assert "Yellow" in res.disease_name or "Rust" in res.disease_name or res.match_confidence > 0.5
    assert len(res.evidence) > 0


def test_dosage_checker_verified():
    # Verified dosage case
    res = verify_pesticide_dosage(
        crop_name="Wheat",
        pest_name="Yellow Rust",
        active_ingredient="Tebuconazole + Trifloxystrobin",
        formulation="75WG",
        dosage_val=65.0,
        unit="g"
    )
    assert isinstance(res, PesticideDosageCheckResult)
    assert res.is_verified is True
    assert res.status == "VERIFIED"
    assert res.verification_state == "verified"
    assert res.warning is None
    assert len(res.evidence) > 0


def test_dosage_checker_blocked_unknown():
    # Unknown chemical must be BLOCKED and marked UNVERIFIED
    res = verify_pesticide_dosage(
        crop_name="Wheat",
        pest_name="Yellow Rust",
        active_ingredient="FakeChemical123",
        formulation="99EC",
        dosage_val=500.0,
        unit="g"
    )
    assert isinstance(res, PesticideDosageCheckResult)
    assert res.is_verified is False
    assert res.status == "UNVERIFIED"
    assert res.verification_state == "unverified"
    assert "BLOCKED" in res.recommendation
    assert res.warning is not None


def test_dosage_checker_blocked_overdosage():
    # Overdosage case must be BLOCKED
    res = verify_pesticide_dosage(
        crop_name="Wheat",
        pest_name="Yellow Rust",
        active_ingredient="Nativo",
        formulation="75WG",
        dosage_val=500.0,
        unit="g"
    )
    assert isinstance(res, PesticideDosageCheckResult)
    assert res.is_verified is False
    assert res.status == "UNVERIFIED"
    assert res.verification_state == "unverified"
    assert "EXCEEDS" in res.recommendation or "BLOCKED" in res.recommendation


def test_mandi_price():
    res = get_mandi_prices(commodity="Wheat", district="Multan")
    assert isinstance(res, MandiPriceReport)
    assert res.total_records > 0
    assert len(res.evidence) > 0


def test_profit_estimator():
    res = estimate_crop_profit(
        crop_name="Wheat",
        acreage=5.0,
        expected_yield_maunds_per_acre=40.0,
        expected_price_pkr_per_maund=4000.0
    )
    assert isinstance(res, DetailedProfitEstimate)
    assert res.gross_revenue_pkr == 800000.0
    assert res.net_profit_pkr > 0
    assert res.break_even_yield_maunds_per_acre > 0
    assert len(res.evidence) > 0


def test_selling_advisor():
    res = advise_selling_strategy(
        crop_name="Wheat",
        district="Multan",
        quantity_maunds=100.0
    )
    assert isinstance(res, SellingAdvice)
    assert res.immediate_net_revenue_pkr > 0
    assert len(res.mandi_evaluations) > 0
    assert len(res.evidence) > 0


def test_support_finder():
    res = find_government_support(
        district="Multan",
        land_acres=5.0
    )
    assert isinstance(res, GovtSupportReport)
    assert len(res.eligible_schemes) > 0
    assert len(res.evidence) > 0
