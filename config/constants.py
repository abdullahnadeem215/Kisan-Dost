"""
Constant definitions for Kisan Dost agronomy and agricultural intelligence platform.
"""

# Verification states for Evidence objects
VERIFICATION_STATES = [
    "verified",
    "unverified",
    "fallback",
    "stale",
    "partially_verified"
]

# Agro-climatic zones of Pakistan
AGRO_CLIMATIC_ZONES = [
    "Rice-Wheat Zone (Punjab)",
    "Cotton-Wheat Zone (Punjab)",
    "Mixed Crop Zone (Punjab)",
    "Barani (Rainfed) Zone (Punjab)",
    "Low Intensity Zone (Punjab)",
    "Cotton-Wheat Zone (Sindh)",
    "Rice Zone (Sindh)",
    "Desert Zone (Thar/Cholistan)",
    "Peshawar Valley (KPK)",
    "Northern Rainfed & Mountain Zone",
    "Upland Balochistan (Orchard Zone)"
]

# Supported Languages
SUPPORTED_LANGUAGES = ["ur", "en", "pnb"]  # Urdu, English, Punjabi

# Major Pakistani Crops
MAJOR_CROPS = [
    "Wheat",
    "Cotton",
    "Rice (Basmati)",
    "Rice (IRRI)",
    "Sugarcane",
    "Maize",
    "Potato",
    "Tomato",
    "Onion",
    "Citrus (Kinnow)",
    "Mango",
    "Canola / Mustard"
]

# Key Pakistani Mandi Markets
MANDI_MARKETS = [
    "Lahore",
    "Multan",
    "Faisalabad",
    "Gujranwala",
    "Rahim Yar Khan",
    "Sargodha",
    "Sahiwal",
    "Bahawalpur",
    "Rawalpindi",
    "Peshawar",
    "Karachi",
    "Quetta"
]

# Punjab Government Agricultural Schemes
PUNJAB_GOVT_SCHEMES = [
    "Kisan Card Interest-Free Loan Scheme",
    "Chief Minister Punjab Green Tractor Scheme",
    "Solarization of Agriculture Tubewells",
    "Fertilizer Subsidy Scheme (DAP/Urea)",
    "Crop Insurance (Crop Loan Takaful)",
    "High Efficiency Irrigation System (HEIS) Subsidy",
    "Wheat Seed Subsidy Program"
]

# Unit Conversions
KG_PER_MAUND = 40.0
KANAL_PER_ACRE = 8.0
MARLA_PER_KANAL = 20.0
CURRENCY = "PKR"
