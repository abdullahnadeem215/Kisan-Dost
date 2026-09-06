"""
FastAPI Endpoints Integration Tests for Kisan Dost.
Tests all REST endpoints using FastAPI TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from app.api.app import app
from config.settings import settings

client = TestClient(app)


def test_root_and_health_endpoints():
    r_root = client.get("/")
    assert r_root.status_code == 200
    data_root = r_root.json()
    assert data_root["status"] == "ONLINE"
    assert "documentation" in data_root

    r_health = client.get("/health")
    assert r_health.status_code == 200
    data_health = r_health.json()
    assert data_health["status"] == "HEALTHY"
    assert data_health["deterministic_tools_count"] == 10


def test_advisory_query_standard():
    payload = {
        "query": "5 acre zameen hai Multan mein. Rabi mein kya lagaoon?",
        "district": "Multan",
        "land_acres": 5.0,
        "language": "roman_urdu"
    }
    resp = client.post("/api/advisory/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_safe"] is True
    assert data["decision"] is not None
    assert data["receipt"] is not None
    assert "advisory_text" in data
    assert len(data["telemetry_steps"]) > 0


def test_advisory_query_safety_refusal():
    payload = {
        "query": "Can you give me medical dosage for human cough syrup?",
        "district": "Multan"
    }
    resp = client.post("/api/advisory/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_safe"] is False
    assert data["refusal_reason"] is not None
    assert "Safety" in data["advisory_text"]


def test_advisory_query_what_if_routing():
    payload = {
        "query": "What if I grow chickpea instead of wheat on 5 acres?",
        "district": "Multan"
    }
    resp = client.post("/api/advisory/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_safe"] is True
    assert data["is_simulation"] is True
    assert data["simulation_result"] is not None


def test_decision_simulator_endpoints():
    compare_payload = {
        "crops": ["wheat", "chickpea", "canola"],
        "land_acres": 5.0,
        "water_constraint": "limited"
    }
    r_comp = client.post("/api/simulator/compare", json=compare_payload)
    assert r_comp.status_code == 200
    comp_data = r_comp.json()
    assert comp_data["status"] == "SUCCESS"
    assert "simulation" in comp_data
    assert comp_data["simulation"]["recommended_option"] is not None

    whatif_payload = {
        "question": "Agar wheat ki jagah chickpea lagaoon to kya hoga?",
        "district": "Multan",
        "land_acres": 5.0
    }
    r_whatif = client.post("/api/simulator/what-if", json=whatif_payload)
    assert r_whatif.status_code == 200
    whatif_data = r_whatif.json()
    assert whatif_data["status"] == "SUCCESS"
    assert "simulation" in whatif_data


def test_farm_passport_endpoints():
    # List passports
    r_list = client.get("/api/passport")
    assert r_list.status_code == 200
    profiles = r_list.json()
    assert isinstance(profiles, list)

    # Create/Update passport
    new_profile = {
        "farmer_id": "FARM-TEST-99",
        "name": "Test Farmer",
        "district": "Faisalabad",
        "total_land_acres": 10.0,
        "soil_type": "Loam",
        "irrigation_source": "Canal",
        "current_season": "Rabi",
        "primary_crop": "Wheat",
        "preferred_language": "roman_urdu",
        "kisan_card_holder": True
    }
    r_save = client.post("/api/passport", json=new_profile)
    assert r_save.status_code == 200
    saved = r_save.json()
    assert saved["farmer_id"] == "FARM-TEST-99"
    assert saved["completeness_percent"] > 50.0

    # Retrieve passport
    r_get = client.get("/api/passport/FARM-TEST-99")
    assert r_get.status_code == 200
    assert r_get.json()["farmer_id"] == "FARM-TEST-99"


def test_farm_health_endpoints():
    req = {
        "farmer_id": "FARM-TEST-01",
        "water_score": 75.0,
        "crop_condition_score": 85.0,
        "pest_score": 80.0,
        "weather_score": 90.0,
        "economic_score": 85.0,
        "profile_completeness": 95.0
    }
    r_calc = client.post("/api/farm-health/calculate", json=req)
    assert r_calc.status_code == 200
    data = r_calc.json()
    assert data["score_available"] is True
    assert 0 <= data["overall_health_score"] <= 100

    r_get = client.get("/api/farm-health/FARM-TEST-01")
    assert r_get.status_code == 200
    assert r_get.json()["score_available"] is True


def test_agricultural_tools_endpoints():
    # Crop Advisor
    r = client.post("/api/tools/crop-advisor", json={"district": "Multan", "soil": "Loam", "season": "Rabi", "water": "Low", "acreage": 5.0})
    assert r.status_code == 200
    assert len(r.json()["recommendations"]) > 0

    # Fertilizer Calculator
    r = client.post("/api/tools/fertilizer-calculator", json={"crop_name": "Wheat", "acreage": 5.0})
    assert r.status_code == 200
    assert r.json()["total_cost_pkr"] > 0

    # Irrigation Advisor
    r = client.post("/api/tools/irrigation-advisor", json={"crop_name": "Wheat", "district": "Multan", "crop_stage": "Tillering"})
    assert r.status_code == 200
    assert "next_irrigation_date" in r.json()

    # Disease Classifier
    r = client.post("/api/tools/disease-classifier", json={"crop_name": "Wheat", "symptom_text": "yellow pustules in stripes"})
    assert r.status_code == 200
    assert r.json()["status"] == "CONFIRMED"
    assert r.json()["match_confidence"] >= 0.70

    # Dosage Checker - Valid
    r = client.post("/api/tools/dosage-checker", json={
        "crop_name": "Wheat", "pest_name": "Yellow Rust", "active_ingredient": "Propiconazole",
        "formulation": "25EC", "dosage_val": 100.0, "unit": "ml"
    })
    assert r.status_code == 200
    assert r.json()["status"] == "VERIFIED"

    # Dosage Checker - Blocked unknown
    r = client.post("/api/tools/dosage-checker", json={
        "crop_name": "Cotton", "pest_name": "Whitefly", "active_ingredient": "SuperKill99",
        "formulation": "50EC", "dosage_val": 500.0, "unit": "ml"
    })
    assert r.status_code == 200
    assert r.json()["status"] == "UNVERIFIED"
    assert r.json()["is_verified"] is False

    # Mandi Prices
    r = client.get("/api/tools/mandi-prices?commodity=Wheat&district=Multan")
    assert r.status_code == 200
    assert len(r.json()["prices"]) > 0

    # Profit Estimator
    r = client.post("/api/tools/profit-estimator", json={"crop_name": "Wheat", "land_acres": 5.0})
    assert r.status_code == 200
    assert r.json()["net_profit_pkr"] > 0

    # Selling Advisor
    r = client.post("/api/tools/selling-advisor", json={"crop_name": "Wheat", "current_district": "Multan", "volume_maunds": 200.0})
    assert r.status_code == 200
    assert r.json()["recommended_action"] is not None

    # Govt Schemes
    r = client.get("/api/tools/govt-schemes?district=Multan&land_acres=5.0")
    assert r.status_code == 200
    assert len(r.json()["eligible_schemes"]) > 0

    # Weather
    r = client.get("/api/tools/weather?district=Multan")
    assert r.status_code == 200
    assert "temperature_c" in r.json()

    # Geocode
    r = client.get("/api/tools/geocode?location=Multan")
    assert r.status_code == 200
    assert r.json()["latitude"] is not None


def test_demo_scenarios_endpoints():
    # List scenarios
    r_list = client.get("/api/demo/scenarios")
    assert r_list.status_code == 200
    scenarios = r_list.json()
    assert len(scenarios) == 6

    # Run main scenario
    r_main = client.post("/api/demo/run/main")
    assert r_main.status_code == 200
    assert r_main.json()["status"] == "SUCCESS"

    # Run safety refusal scenario
    r_safe = client.post("/api/demo/run/safety")
    assert r_safe.status_code == 200
    assert r_safe.json()["status"] == "BLOCKED"

    # Run what-if scenario
    r_whatif = client.post("/api/demo/run/whatif")
    assert r_whatif.status_code == 200
    assert r_whatif.json()["status"] == "SUCCESS"

    # Run conflict resolution scenario
    r_conf = client.post("/api/demo/run/conflict")
    assert r_conf.status_code == 200
    assert r_conf.json()["status"] == "SUCCESS"

    # Run low confidence scenario
    r_low = client.post("/api/demo/run/low_confidence")
    assert r_low.status_code == 200
    assert r_low.json()["status"] == "UNCERTAIN"

    # Run offline scenario
    r_off = client.post("/api/demo/run/offline")
    assert r_off.status_code == 200
    assert r_off.json()["status"] == "CACHED"


def test_diagnose_image_endpoint_schema():
    # Test diagnose-image endpoint accepts valid payload and reports clean status without fake disease
    payload = {
        "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...",
        "crop_hint": "Wheat"
    }
    resp = client.post("/api/tools/diagnose-image", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data
    assert "is_refused" in data
    # When no key is in test env, it should report clean missing key without crashing or returning fake disease
    if not data["success"]:
        assert "GEMINI_API_KEY" in data["error"] or "Gemini" in data.get("message", "")
        assert data.get("result") is None


@pytest.mark.asyncio
async def test_diagnose_image_non_plant_rejection():
    from app.api.routes.tools import api_diagnose_image, DiagnoseImageRequest
    import json
    from unittest.mock import patch, MagicMock

    fake_gemini_json = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "is_farming_related": False,
                                "is_plant_present": False,
                                "detected_object": "Domestic Cat",
                                "refusal_reason_roman_urdu": "Yeh tasveer kisi fasal ya paudhay ki nahi hai balkay Domestic Cat ki hai.",
                                "refusal_reason_urdu": "یہ تصویر کسی فصل یا پودے کی نہیں ہے۔",
                                "refusal_reason_en": "This image shows a domestic cat, not an agricultural plant."
                            })
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_gemini_json

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, json=None):
            return mock_resp

    with patch("app.api.routes.tools.httpx.AsyncClient", MockAsyncClient):
        with patch.object(settings, "gemini_api_key", "test-mock-key"):
            req = DiagnoseImageRequest(
                image_base64="data:image/jpeg;base64,mockrandomcatimage",
                crop_hint="Wheat"
            )
            data = await api_diagnose_image(req)
            assert data["success"] is True
            assert data["is_refused"] is True
            assert data["detected_object"] == "Domestic Cat"
            assert data["result"] is None
            assert "Domestic Cat" in data["refusal_message"]


@pytest.mark.asyncio
async def test_diagnose_image_plant_confirmed():
    from app.api.routes.tools import api_diagnose_image, DiagnoseImageRequest
    import json
    from unittest.mock import patch, MagicMock

    fake_plant_json = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "is_farming_related": True,
                                "is_plant_present": True,
                                "detected_object": "Wheat Leaf",
                                "crop_name": "Wheat",
                                "disease_name": "Yellow Rust",
                                "causal_agent": "Puccinia striiformis",
                                "match_confidence": 0.94,
                                "symptoms": ["Yellow pustules in linear stripes"],
                                "favorable_conditions": "Cool and humid",
                                "preventative_measures": ["Resistant seed Akbar-19"],
                                "organic_control": "Neem extract",
                                "chemical_control": "Tilt 250 EC @ 200ml/acre",
                                "dosage_per_acre": "200ml/acre",
                                "diagnostic_summary_roman_urdu": "Gandum ke pattay par Yellow Rust tashkhees hui hai."
                            })
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_plant_json

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, json=None):
            return mock_resp

    with patch("app.api.routes.tools.httpx.AsyncClient", MockAsyncClient):
        with patch.object(settings, "gemini_api_key", "test-mock-key"):
            req = DiagnoseImageRequest(
                image_base64="data:image/jpeg;base64,mockwheatleaf",
                crop_hint="Wheat"
            )
            data = await api_diagnose_image(req)
            assert data["success"] is True
            assert data["is_refused"] is False
            assert data["detected_object"] == "Wheat Leaf"
            assert data["result"] is not None
            assert data["result"]["disease_name"] == "Yellow Rust"
            assert data["result"]["crop_name"] == "Wheat"
            assert data["result"]["status"] == "CONFIRMED"


