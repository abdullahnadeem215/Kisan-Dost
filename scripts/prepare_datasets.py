"""
Script to generate and populate realistic Pakistani agricultural datasets into app/data/processed/.
Covers crops, mandi prices, fertilizers, plant diseases, Punjab govt schemes, and FAOSTAT/PBS macro data.
"""
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "app" / "data" / "processed"


def prepare_crops_dataset():
    crops = [
        {
            "crop_name": "Wheat",
            "variety": "Akbar-19",
            "season": "Rabi",
            "sowing_window": "Nov 01 - Nov 30",
            "growth_duration_days": 140,
            "water_requirement_mm": 350.0,
            "optimal_temp_min_c": 10.0,
            "optimal_temp_max_c": 25.0,
            "avg_yield_maunds_per_acre": 38.0,
            "potential_yield_maunds_per_acre": 60.0,
            "recommended_npk_kg_per_acre": "50-25-0",
            "stages": [
                {"stage_name": "Crown Root Initiation", "duration_days": 21, "key_tasks": ["First irrigation", "Apply 1st split Urea"]},
                {"stage_name": "Tillering & Jointing", "duration_days": 40, "key_tasks": ["Weedicide application", "Second irrigation"]},
                {"stage_name": "Booting & Heading", "duration_days": 30, "key_tasks": ["Third irrigation", "Monitor for Rust disease"]},
                {"stage_name": "Grain Filling & Maturity", "duration_days": 49, "key_tasks": ["Final irrigation", "Harvesting prep"]}
            ]
        },
        {
            "crop_name": "Cotton",
            "variety": "FH-142",
            "season": "Kharif",
            "sowing_window": "Apr 15 - May 31",
            "growth_duration_days": 165,
            "water_requirement_mm": 700.0,
            "optimal_temp_min_c": 22.0,
            "optimal_temp_max_c": 40.0,
            "avg_yield_maunds_per_acre": 22.0,
            "potential_yield_maunds_per_acre": 40.0,
            "recommended_npk_kg_per_acre": "60-30-25",
            "stages": [
                {"stage_name": "Germination & Seedling", "duration_days": 25, "key_tasks": ["Thinning", "First weeding"]},
                {"stage_name": "Square & Flowering", "duration_days": 45, "key_tasks": ["Nitrogen top dressing", "Pest monitoring (Whitefly/Thrips)"]},
                {"stage_name": "Boll Formation", "duration_days": 55, "key_tasks": ["Potash spray", "PBW (Pink Bollworm) traps management"]},
                {"stage_name": "Boll Opening & Picking", "duration_days": 40, "key_tasks": ["Stop irrigation", "Clean picking"]}
            ]
        },
        {
            "crop_name": "Rice (Basmati)",
            "variety": "Super Basmati / PK-1121",
            "season": "Kharif",
            "sowing_window": "Jun 01 - Jul 15 (Transplanting)",
            "growth_duration_days": 125,
            "water_requirement_mm": 1200.0,
            "optimal_temp_min_c": 20.0,
            "optimal_temp_max_c": 35.0,
            "avg_yield_maunds_per_acre": 35.0,
            "potential_yield_maunds_per_acre": 55.0,
            "recommended_npk_kg_per_acre": "46-23-20",
            "stages": [
                {"stage_name": "Nursery Raising", "duration_days": 25, "key_tasks": ["Seed treatment", "Nursery care"]},
                {"stage_name": "Transplanting & Vegetative", "duration_days": 40, "key_tasks": ["Standing water maintenance", "Zinc Sulphate application"]},
                {"stage_name": "Panicle Initiation & Heading", "duration_days": 35, "key_tasks": ["Blast disease preventive spray", "Urea split"]},
                {"stage_name": "Ripening & Harvest", "duration_days": 25, "key_tasks": ["Drain field 10 days before harvest", "Combine harvesting"]}
            ]
        },
        {
            "crop_name": "Sugarcane",
            "variety": "CPF-246",
            "season": "Annual (Rabi/Kharif)",
            "sowing_window": "Feb 15 - Mar 31",
            "growth_duration_days": 330,
            "water_requirement_mm": 1600.0,
            "optimal_temp_min_c": 18.0,
            "optimal_temp_max_c": 38.0,
            "avg_yield_maunds_per_acre": 650.0,
            "potential_yield_maunds_per_acre": 1000.0,
            "recommended_npk_kg_per_acre": "90-45-45",
            "stages": [
                {"stage_name": "Germination", "duration_days": 45, "key_tasks": ["Blind hoeing", "Pre-emergence herbicide"]},
                {"stage_name": "Tillering & Formative", "duration_days": 90, "key_tasks": ["Earthing up", "Heavy fertilization"]},
                {"stage_name": "Grand Growth", "duration_days": 135, "key_tasks": ["Frequent irrigation", "Borer control"]},
                {"stage_name": "Maturity & Ripening", "duration_days": 60, "key_tasks": ["Withhold nitrogen", "Harvesting for sugar mill"]}
            ]
        },
        {
            "crop_name": "Maize",
            "variety": "Pioneer 30Y87 (Hybrid)",
            "season": "Spring / Kharif",
            "sowing_window": "Feb 01 - Mar 15 (Spring) / Jul 15 - Aug 15 (Kharif)",
            "growth_duration_days": 110,
            "water_requirement_mm": 500.0,
            "optimal_temp_min_c": 15.0,
            "optimal_temp_max_c": 35.0,
            "avg_yield_maunds_per_acre": 85.0,
            "potential_yield_maunds_per_acre": 120.0,
            "recommended_npk_kg_per_acre": "80-40-25",
            "stages": [
                {"stage_name": "Emergence & V6 Stage", "duration_days": 25, "key_tasks": ["Fall Armyworm spray", "First fertigation"]},
                {"stage_name": "Tasseling & Silking", "duration_days": 35, "key_tasks": ["Critical watering stage", "Second Urea application"]},
                {"stage_name": "Grain Filling", "duration_days": 35, "key_tasks": ["Maintain moisture", "Nutrient boost"]},
                {"stage_name": "Black Layer & Harvest", "duration_days": 15, "key_tasks": ["Grain moisture check", "Harvesting"]}
            ]
        },
        {
            "crop_name": "Potato",
            "variety": "Mozika / Asterix",
            "season": "Rabi",
            "sowing_window": "Oct 01 - Oct 25",
            "growth_duration_days": 105,
            "water_requirement_mm": 400.0,
            "optimal_temp_min_c": 12.0,
            "optimal_temp_max_c": 24.0,
            "avg_yield_maunds_per_acre": 250.0,
            "potential_yield_maunds_per_acre": 380.0,
            "recommended_npk_kg_per_acre": "100-50-60",
            "stages": [
                {"stage_name": "Sprouting & Canopy Establishment", "duration_days": 25, "key_tasks": ["Ridge making", "Initial irrigation"]},
                {"stage_name": "Tuber Initiation & Bulking", "duration_days": 50, "key_tasks": ["Potash application", "Late blight preventive fungicide"]},
                {"stage_name": "Maturation & Vine Killing", "duration_days": 30, "key_tasks": ["Haulm cutting", "Skin hardening before harvest"]}
            ]
        }
    ]
    with open(OUTPUT_DIR / "crops.json", "w", encoding="utf-8") as f:
        json.dump(crops, f, indent=2)
    print("Populated app/data/processed/crops.json")


def prepare_mandi_prices_dataset():
    mandi_prices = [
        {"mandi_name": "Multan Mandi", "district": "Multan", "commodity": "Wheat", "variety": "Akbar-19", "min_price": 3850, "max_price": 4050, "modal_price": 3950, "price_date": "2026-09-05", "price_trend": "Stable"},
        {"mandi_name": "Multan Mandi", "district": "Multan", "commodity": "Cotton", "variety": "Phutti FAQ", "min_price": 7500, "max_price": 8400, "modal_price": 8000, "price_date": "2026-09-05", "price_trend": "Rising"},
        {"mandi_name": "Faisalabad Mandi", "district": "Faisalabad", "commodity": "Wheat", "variety": "Akbar-19", "min_price": 3900, "max_price": 4100, "modal_price": 4000, "price_date": "2026-09-05", "price_trend": "Stable"},
        {"mandi_name": "Faisalabad Mandi", "district": "Faisalabad", "commodity": "Maize", "variety": "Hybrid Grain", "min_price": 2200, "max_price": 2450, "modal_price": 2350, "price_date": "2026-09-05", "price_trend": "Falling"},
        {"mandi_name": "Lahore Badami Bagh", "district": "Lahore", "commodity": "Rice (Basmati)", "variety": "Super Basmati 1121", "min_price": 4800, "max_price": 5400, "modal_price": 5100, "price_date": "2026-09-05", "price_trend": "Rising"},
        {"mandi_name": "Lahore Badami Bagh", "district": "Lahore", "commodity": "Potato", "variety": "Mozika Red", "min_price": 1800, "max_price": 2300, "modal_price": 2050, "price_date": "2026-09-05", "price_trend": "Stable"},
        {"mandi_name": "Sargodha Grain Market", "district": "Sargodha", "commodity": "Citrus (Kinnow)", "variety": "Export Grade", "min_price": 2800, "max_price": 3600, "modal_price": 3200, "price_date": "2026-09-05", "price_trend": "Rising"},
        {"mandi_name": "Sahiwal Mandi", "district": "Sahiwal", "commodity": "Maize", "variety": "Hybrid Silage/Grain", "min_price": 2250, "max_price": 2480, "modal_price": 2380, "price_date": "2026-09-05", "price_trend": "Stable"},
        {"mandi_name": "Rahim Yar Khan Market", "district": "Rahim Yar Khan", "commodity": "Cotton", "variety": "Phutti Grade A", "min_price": 7800, "max_price": 8550, "modal_price": 8200, "price_date": "2026-09-05", "price_trend": "Rising"},
        {"mandi_name": "Bahawalpur Mandi", "district": "Bahawalpur", "commodity": "Wheat", "variety": "Dilkash", "min_price": 3820, "max_price": 4020, "modal_price": 3920, "price_date": "2026-09-05", "price_trend": "Stable"},
        {"mandi_name": "Rawalpindi Ganj Mandi", "district": "Rawalpindi", "commodity": "Wheat", "variety": "Standard", "min_price": 4000, "max_price": 4200, "modal_price": 4120, "price_date": "2026-09-05", "price_trend": "Stable"},
        {"mandi_name": "Peshawar Mandi", "district": "Peshawar", "commodity": "Maize", "variety": "Local Grain", "min_price": 2400, "max_price": 2650, "modal_price": 2520, "price_date": "2026-09-05", "price_trend": "Stable"}
    ]
    with open(OUTPUT_DIR / "mandi_prices.json", "w", encoding="utf-8") as f:
        json.dump(mandi_prices, f, indent=2)
    print("Populated app/data/processed/mandi_prices.json")


def prepare_fertilizers_dataset():
    fertilizers = [
        {
            "fertilizer_id": "FERT-UREA",
            "name": "Urea (Sonam / FFC / Engro)",
            "nutrient_composition": {"N": 46.0},
            "standard_bag_weight_kg": 50.0,
            "current_price_pkr": 4650.0,
            "govt_subsidized": True,
            "subsidy_pkr_per_bag": 500.0,
            "application_method": "Top-dressing / Broadcast before irrigation"
        },
        {
            "fertilizer_id": "FERT-DAP",
            "name": "DAP (Di-Ammonium Phosphate)",
            "nutrient_composition": {"N": 18.0, "P2O5": 46.0},
            "standard_bag_weight_kg": 50.0,
            "current_price_pkr": 12800.0,
            "govt_subsidized": True,
            "subsidy_pkr_per_bag": 1000.0,
            "application_method": "Basal application at land preparation / sowing"
        },
        {
            "fertilizer_id": "FERT-SOP",
            "name": "SOP (Sulphate of Potash)",
            "nutrient_composition": {"K2O": 50.0, "S": 18.0},
            "standard_bag_weight_kg": 50.0,
            "current_price_pkr": 14500.0,
            "govt_subsidized": False,
            "subsidy_pkr_per_bag": 0.0,
            "application_method": "Fertigation or soil application at flowering/tuber bulking"
        },
        {
            "fertilizer_id": "FERT-NP",
            "name": "Nitre Phosphate (NP 22-20)",
            "nutrient_composition": {"N": 22.0, "P2O5": 20.0},
            "standard_bag_weight_kg": 50.0,
            "current_price_pkr": 8900.0,
            "govt_subsidized": True,
            "subsidy_pkr_per_bag": 400.0,
            "application_method": "Basal application or 1st irrigation split"
        },
        {
            "fertilizer_id": "FERT-ZINC",
            "name": "Zinc Sulphate (33% Monohydrate)",
            "nutrient_composition": {"Zn": 33.0, "S": 15.0},
            "standard_bag_weight_kg": 10.0,
            "current_price_pkr": 2400.0,
            "govt_subsidized": False,
            "subsidy_pkr_per_bag": 0.0,
            "application_method": "Soil application in rice/maize standing crop"
        }
    ]
    with open(OUTPUT_DIR / "fertilizers.json", "w", encoding="utf-8") as f:
        json.dump(fertilizers, f, indent=2)
    print("Populated app/data/processed/fertilizers.json")


def prepare_diseases_dataset():
    diseases = [
        {
            "disease_id": "DIS-WHEAT-RUST",
            "crop_name": "Wheat",
            "disease_name": "Yellow Stripe Rust (Puccinia striiformis)",
            "causal_agent": "Fungal",
            "symptoms": ["Bright yellow linear pustules on leaves", "Yellow powder on fingers when touching leaf", "Premature drying of leaf tips"],
            "favorable_conditions": "Cool temp (10-15°C), high humidity, dew on leaves in Jan-Feb",
            "preventative_measures": ["Use resistant seed varieties like Akbar-19 or Dilkash", "Avoid late sowing"],
            "organic_control": "Foliar spray of fermented neem leaf extract or sour butter-milk mixture",
            "chemical_control": "Spray Nativo (Tebuconazole + Trifloxystrobin) or Tilt (Propiconazole)",
            "dosage_per_acre": "Nativo @ 65g/acre or Tilt @ 100ml/acre in 100L water"
        },
        {
            "disease_id": "DIS-COTTON-PBW",
            "crop_name": "Cotton",
            "disease_name": "Pink Bollworm (Pectinophora gossypiella)",
            "causal_agent": "Insect Pest",
            "symptoms": ["Rosetted flowers (petals tied together)", "Entry holes in bolls sealed with frass", "Stained lint and damaged seeds inside boll"],
            "favorable_conditions": "High temperature with intermittent humidity, mid-to-late Kharif season",
            "preventative_measures": ["Install PBW Pheromone traps @ 5/acre", "Maintain PBW refuge non-Bt border"],
            "organic_control": "Release Trichogramma egg parasitoids @ 40 cards/acre",
            "chemical_control": "Spray Gamma-Cyhalothrin or Spinetoram or Triazophos",
            "dosage_per_acre": "Spinetoram 120SC @ 80ml/acre or Triazophos 40EC @ 500ml/acre"
        },
        {
            "disease_id": "DIS-RICE-BLAST",
            "crop_name": "Rice (Basmati)",
            "disease_name": "Rice Blast (Pyricularia oryzae)",
            "causal_agent": "Fungal",
            "symptoms": ["Diamond/spindle-shaped lesions with gray centers on leaves", "Blackening of neck node causing head rot"],
            "favorable_conditions": "High atmospheric humidity (>90%), night temp 20-25°C, excessive Nitrogen application",
            "preventative_measures": ["Balanced NPK application", "Seed treatment with Tricyclazole"],
            "organic_control": "Spray Garlic extract + Pseudomonas fluorescens biocontrol",
            "chemical_control": "Spray Tricyclazole 75WP (Beam) or Kasugamycin",
            "dosage_per_acre": "Tricyclazole 75WP @ 120g/acre in 100L water"
        },
        {
            "disease_id": "DIS-POTATO-BLIGHT",
            "crop_name": "Potato",
            "disease_name": "Late Blight (Phytophthora infestans)",
            "causal_agent": "Oomycete / Fungal-like",
            "symptoms": ["Water-soaked dark lesions on leaf tips", "White mildew growth on lower leaf surface under wet weather", "Rapid wilting of canopy"],
            "favorable_conditions": "Foggy humid weather with rain, temp between 12°C and 22°C",
            "preventative_measures": ["Plant disease-free certified tubers", "Prophylactic Mancozeb spray"],
            "organic_control": "Copper Oxychloride spray + Trichoderma harzianum soil treatment",
            "chemical_control": "Spray Cymoxanil + Mancozeb (Curzate M8) or Dimethomorph",
            "dosage_per_acre": "Curzate M8 @ 250g/acre in 100L water"
        },
        {
            "disease_id": "DIS-CITRUS-CANKER",
            "crop_name": "Citrus (Kinnow)",
            "disease_name": "Citrus Canker (Xanthomonas citri)",
            "causal_agent": "Bacterial",
            "symptoms": ["Raised corky brown lesions surrounded by yellow halo on leaves and fruits", "Fruit drop and blemishes"],
            "favorable_conditions": "Rainy humid weather with wind spreading bacterial inoculum",
            "preventative_measures": ["Prune affected branches after harvest", "Windbreak shelterbelts around orchard"],
            "organic_control": "Foliar spray of Copper Hydroxide / Bordeaux Mixture (1%)",
            "chemical_control": "Spray Copper Oxychloride + Streptomycin sulphate",
            "dosage_per_acre": "Copper Oxychloride @ 300g + Streptomycin @ 15g per 100L water"
        }
    ]
    with open(OUTPUT_DIR / "diseases.json", "w", encoding="utf-8") as f:
        json.dump(diseases, f, indent=2)
    print("Populated app/data/processed/diseases.json")


def prepare_govt_schemes_dataset():
    schemes = [
        {
            "scheme_id": "SCHEME-PUNJAB-KISAN-CARD",
            "scheme_name": "Punjab Kisan Card Interest-Free Loan Scheme",
            "department": "Punjab Agriculture Department / Bank of Punjab",
            "eligibility_criteria": [
                "Cultivator of land up to 12.5 acres in Punjab",
                "Land ownership verified via Land Records Authority (PLRA)",
                "Active mobile SIM registered on farmer's CNIC"
            ],
            "benefit_summary": "Interest-free crop production loan up to PKR 30,000 per acre (max 150,000 per farmer) for buying Urea, DAP, certified seeds, and pesticides via designated dealers.",
            "subsidy_details": "100% Interest/Markup markup subsidy borne by Punjab Govt.",
            "application_deadline": "Ongoing Open Registration 2024-2026",
            "required_documents": ["Original CNIC", "Mobile SIM registered on same CNIC", "PLRA Fard / Ownership proof"],
            "contact_helpline": "0800-17000 / SMS CNIC to 8070"
        },
        {
            "scheme_id": "SCHEME-GREEN-TRACTOR",
            "scheme_name": "Chief Minister Punjab Green Tractor Scheme",
            "department": "Punjab Agriculture Department (Field Wing)",
            "eligibility_criteria": [
                "Owner of 6 to 50 acres of agricultural land in Punjab",
                "CNIC holder, non-defaulter of state institutions"
            ],
            "benefit_summary": "Flat PKR 1,000,000 (10 Lakh) subsidy per tractor for purchasing local manufactured tractors (50 HP to 85 HP). Allocated via transparent balloting per district.",
            "subsidy_details": "PKR 10 Lakh direct subsidy per tractor unit",
            "application_deadline": "Seasonal balloting calls (Check Punjab Agri Portal)",
            "required_documents": ["CNIC", "Land Record (Fard-e-Malkiyat)", "Affidavit of non-resale within 3 years"],
            "contact_helpline": "0800-17000"
        },
        {
            "scheme_id": "SCHEME-SOLAR-TUBEWELL",
            "scheme_name": "Chief Minister Solarization of Agricultural Tubewells",
            "department": "Energy & Agriculture Department Punjab",
            "eligibility_criteria": [
                "Farmers with existing diesel or electric tube-well up to 20 HP",
                "Water table suitability in district verified by PCRWR"
            ],
            "benefit_summary": "Conversion of diesel/electric tubewells to solar system with up to 500,000 PKR subsidy per farmer.",
            "subsidy_details": "60% Government Subsidy, 40% Farmer Contribution",
            "application_deadline": "2026 Phase Application Window",
            "required_documents": ["CNIC", "Tubewell Ownership / Land Title", "Electricity Bill or Diesel Tubewell Proof"],
            "contact_helpline": "0800-17000"
        },
        {
            "scheme_id": "SCHEME-CROP-TAKAFUL",
            "scheme_name": "Crop Loan Takaful (Insurance) Scheme",
            "department": "Government of Punjab & State Bank of Pakistan",
            "eligibility_criteria": [
                "Small farmers cultivating under 12.5 acres receiving bank crop loans",
                "Crops covered: Wheat, Cotton, Rice, Sugarcane, Maize"
            ],
            "benefit_summary": "Full compensation for crop loss due to calamity, flood, drought, or pest destruction based on area yield indexes.",
            "subsidy_details": "100% Premium subsidy for small farmers paid by Punjab Govt.",
            "application_deadline": "Automatic at loan disbursement",
            "required_documents": ["Bank Agri Loan Account", "Crop declaration form"],
            "contact_helpline": "0800-17000"
        }
    ]
    with open(OUTPUT_DIR / "govt_schemes.json", "w", encoding="utf-8") as f:
        json.dump(schemes, f, indent=2)
    print("Populated app/data/processed/govt_schemes.json")


def prepare_faostat_pbs_stats_dataset():
    stats = {
        "faostat_crop_production": {
            "Wheat": {
                "area_harvested_ha": 8900000,
                "production_tonnes": 28200000,
                "yield_kg_ha": 3168.0,
                "note": "FAOSTAT official 2022-2023 estimate for Pakistan"
            },
            "Cotton": {
                "area_harvested_ha": 2140000,
                "production_tonnes": 4800000,
                "yield_kg_ha": 2242.0,
                "note": "Raw seed cotton production"
            },
            "Rice": {
                "area_harvested_ha": 3470000,
                "production_tonnes": 9300000,
                "yield_kg_ha": 2680.0,
                "note": "Combined Basmati and IRRI coarse rice"
            },
            "Sugarcane": {
                "area_harvested_ha": 1260000,
                "production_tonnes": 88000000,
                "yield_kg_ha": 69841.0,
                "note": "Cane fresh weight"
            },
            "Maize": {
                "area_harvested_ha": 1720000,
                "production_tonnes": 10100000,
                "yield_kg_ha": 5872.0,
                "note": "High hybrid adoption driving yields"
            }
        },
        "pbs_district_census": {
            "Multan": {
                "total_farms": 142000,
                "cultivated_area_acres": 720000,
                "canal_irrigated_percent": 62.0,
                "tubewell_irrigated_percent": 38.0,
                "major_crops": ["Cotton", "Wheat", "Mango", "Fodder"]
            },
            "Faisalabad": {
                "total_farms": 185000,
                "cultivated_area_acres": 1150000,
                "canal_irrigated_percent": 70.0,
                "tubewell_irrigated_percent": 30.0,
                "major_crops": ["Wheat", "Sugarcane", "Maize", "Vegetables"]
            },
            "Sargodha": {
                "total_farms": 160000,
                "cultivated_area_acres": 980000,
                "canal_irrigated_percent": 65.0,
                "tubewell_irrigated_percent": 35.0,
                "major_crops": ["Citrus (Kinnow)", "Wheat", "Sugarcane"]
            },
            "Sahiwal": {
                "total_farms": 128000,
                "cultivated_area_acres": 690000,
                "canal_irrigated_percent": 58.0,
                "tubewell_irrigated_percent": 42.0,
                "major_crops": ["Maize", "Potato", "Wheat", "Cotton"]
            },
            "Rahim Yar Khan": {
                "total_farms": 175000,
                "cultivated_area_acres": 1220000,
                "canal_irrigated_percent": 75.0,
                "tubewell_irrigated_percent": 25.0,
                "major_crops": ["Cotton", "Sugarcane", "Wheat"]
            }
        }
    }
    with open(OUTPUT_DIR / "faostat_pbs_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print("Populated app/data/processed/faostat_pbs_stats.json")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Preparing datasets in {OUTPUT_DIR}...")
    prepare_crops_dataset()
    prepare_mandi_prices_dataset()
    prepare_fertilizers_dataset()
    prepare_diseases_dataset()
    prepare_govt_schemes_dataset()
    prepare_faostat_pbs_stats_dataset()
    print("All Pakistani agricultural datasets successfully generated and saved.")


if __name__ == "__main__":
    main()
