# 🌾 KISAN DOST (کسان دوست)
### AI Agronomy Multi-Agent Advisory, Conversational Farm Dashboard & Decision Engine

[![Tests](https://img.shields.io/badge/tests-79%20passed-brightgreen.svg)]()
[![Backend](https://img.shields.io/badge/backend-FastAPI%20REST%20API-009688.svg)]()
[![Frontend](https://img.shields.io/badge/frontend-React%2018%20%7C%20Vite%20%7C%20Tailwind-61DAFB.svg)]()
[![Framework](https://img.shields.io/badge/framework-OpenAI%20Agents%20SDK-blue.svg)]()
[![Vision](https://img.shields.io/badge/vision-Google%20Gemini%20Flash-orange.svg)]()
[![Deployed](https://img.shields.io/badge/deployed-Render-46E3B7.svg)](https://kisan-dost.onrender.com)
[![Data Provenance](https://img.shields.io/badge/data%20provenance-Verified%20%26%20Grounded-emerald.svg)]()

---

## 🌐 Live Deployment

- **Cloud Backend API**: [https://kisan-dost.onrender.com](https://kisan-dost.onrender.com)
- **Interactive OpenAPI Docs**: [https://kisan-dost.onrender.com/docs](https://kisan-dost.onrender.com/docs)
- **Health Check**: [https://kisan-dost.onrender.com/health](https://kisan-dost.onrender.com/health) (`{"status":"HEALTHY","deterministic_tools_count":10}`)

---

## 🎯 1. PRODUCT POSITIONING

> **"Kisan Dost is an evidence-grounded farm decision engine that investigates a farmer's situation, compares possible actions, validates evidence, resolves conflicting recommendations, evaluates risk and confidence, and knows when it should refuse to guess."**

### Why Kisan Dost is NOT Just Another Agricultural Chatbot:

```text
TRADITIONAL FARM CHATBOT:
Farmer Question ──► LLM Hallucination ──► Generic Plausible Answer

KISAN DOST CONVERSATIONAL DECISION ENGINE:
Farmer Situation (Name, District, Acreage, Soil, Water Quota)
      │
      ▼
Input Guardrail & Farm Passport (SQLite Persistent Context)
      │
      ▼
Multi-Intent Triage (OpenAI Agents SDK / Groq fallback)
      │
      ▼
Specialist Investigation (Agronomy • Pest Doctor • Market • Finance/Govt)
      │
      ▼
Deterministic Calculation & Evidence Aggregation (AMIS • FAO-56 • DPP • NARC)
      │
      ▼
Decision Simulator (What-If Analysis) & Conflict Resolution Engine
      │
      ▼
Independent Risk + Trust + Confidence Evaluation
      │
      ▼
Conversational Natural Output + Embedded Dashboard Stats & Interactive Tool Cards
```

---

## ⚖️ 2. NON-NEGOTIABLE ARCHITECTURAL CONTRACT

| LLM Capabilities (Allowed) | Authoritative Agricultural Facts (STRICTLY DETERMINISTIC) |
| :--- | :--- |
| • Natural language farmer understanding (Urdu / Roman Urdu / English) | • Fertilizer quantities (NFDC NPK-to-Bag conversion) |
| • Multi-intent triage & specialist routing | • Pesticide dosage & safety limits (Plant Protection DPP Registry) |
| • Contextual reasoning & trade-off explanation | • Wholesale mandi prices (AMIS Punjab API / Cache) |
| • Warm, respectful persona addressing farmer by name | • Irrigation requirements (FAO-56 Penman-Monteith \(ET_c\)) |
| • Summarization & uncertainty communication | • Profit, net margin & break-even yield calculations |
| • Refusal explanation on unverified/non-agricultural inputs | • Farm Health Index & multi-vector risk scores |

> 🚨 **Core Rule:** The LLM decides *what* needs to be calculated; deterministic tools and verified datasets perform the calculation.

---

## 🌟 3. CORE SYSTEM DIFFERENTIATORS

### 1. 🧑‍🌾 Conversational Farm Dashboard & Real-Time Farm Passport
- **Files**: `frontend/src/components/chat/ZaraiChatBot.tsx`, `frontend/src/components/onboarding/ConversationalSetup.tsx`, `app/context/farmer_profile.py`
- **Farmer Identity & Onboarding**: Captures **Farmer Full Name** (e.g. *Chaudhry Ahmad*, *Malik Farooq*), **Mobile Number**, **District**, **Acreage**, **Soil Type**, and **Water Condition**.
- **Real-Time SQLite Persistence**: Persists directly to SQLite (`farmer_profiles.db`) via `POST /api/passport` and auto-hydrates into all agent queries throughout the session.
- **Natural Language "Digital Dost" Demeanor**: Speaks warmly and respectfully, addressing the farmer by name (*"وعلیکم السلام چوہدری احمد صاحب!"*). Routine queries receive natural answers with embedded **dashboard stat boxes** (Rate, Trend, Stage, Risk), expanding full interactive tools on demand.

### 2. 🔬 Gemini Multimodal Vision with Agricultural Domain Guardrail
- **Files**: `app/api/routes/tools.py`, `frontend/src/api/client.ts`, `frontend/src/api/geminiClient.ts`, `frontend/src/components/tools/DiseaseDoctor.tsx`
- **Vision Engine**: High-resolution leaf, crop, and insect pest diagnosis using Google's latest Gemini Multimodal Vision models (`gemini-2.5-flash`, `gemini-3.7-flash` with cascade fallback to `gemini-2.0-flash` / `gemini-1.5-flash`).
- **Strict Agricultural Plant Guardrail**: The vision inspector performs explicit subject classification first. Non-agricultural pictures (humans, faces, selfies, animals, pets, cars, furniture, electronics, documents, rooms) are **strictly rejected**, identifying the detected object and returning a clear bilingual refusal:
  > *"یہ تصویر کسی فصل یا پودے کی نہیں ہے بلکہ (<detected_object>) کی ہے۔ کسان دوست صرف زراعت اور کھیتی باڑی سے متعلق پودوں اور پتوں کی تشخیص کرتا ہے۔ برائے مہربانی فصل کے متاثرہ پتے یا کیڑے کی تصویر اپلوڈ کریں۔"*
- **Zero Frontend API Key Exposure**: All vision inference is routed through the secure backend endpoint (`POST /api/tools/diagnose-image`), eliminating any exposed API keys or key input prompts on the frontend dashboard.
- **DPP Registry Grounding**: Prescriptions strictly match the **Department of Plant Protection (DPP) Pakistan** official registry (e.g. Nativo 75 WG @ 65g/acre, Tilt 250 EC @ 200ml/acre). Unregistered chemicals or off-label dosages are automatically blocked with `UNVERIFIED` status.

### 3. 🔮 Farm Decision Simulator (What-If Engine)
- **File**: `app/services/decision_simulator.py`
- Evaluates multi-crop strategies (*Wheat vs Chickpea vs Canola*) under farm constraints.
- Features an interactive water reduction slider (-10% to -40%) showing real-time trade-offs: water savings (mm / %), input costs (PKR), expected revenue, and net profit delta.
- Strictly marks scenario estimates as `is_hypothetical: True` to prevent mistaking simulation for guarantees.

### 4. ⚔️ Agent Conflict Resolution Engine
- **File**: `app/services/decision_service.py`
- Automatically detects cross-domain disagreements:
  - *Agronomy recommends 4 irrigations vs Water Monitor reports only 2 available canal turns.*
  - *Market favors high-gross crop vs Agronomy detects water stress.*
  - *Pest recommender proposes unverified chemical vs Plant Protection safety bounds.*
- Resolves conflicts using deterministic conservative agronomic precedence rules without hiding trade-offs.

### 5. 📊 Kisan Dost Farm Health Index
- **File**: `app/services/farm_health_service.py` & `app/presentation/farm_health.py`
- Composite 0-100 score tracking 6 dimensions: **Water (25%)**, **Crop Condition (20%)**, **Pest Bio-Security (20%)**, **Weather (15%)**, **Economics (10%)**, and **Profile Completeness (10%)**.
- Refuses to fabricate a score if critical evidence is absent (`score_available = False`).

### 6. 🛡️ Trust Layer & Truthful Data Freshness
- **File**: `app/services/trust_service.py`, `app/services/confidence_service.py`
- Explicitly separates **Model Confidence**, **Evidence Confidence**, and **Overall Confidence**.
- Truthfully tags all external data sources:
  - `🟢 LIVE`
  - `🟡 CACHED` (Exposes exact retrieval timestamp; never claims cached data is live)
  - `🔴 UNAVAILABLE`

### 7. 🧾 Immutable Decision Receipt
- **File**: `app/schemas/decision_receipt.py` & `app/presentation/decision_receipt.py`
- Issues a structured audit receipt for every advisory: Decision, Rationale, Action Steps, Grounding Evidence IDs, Risk Assessment, and Overall Confidence %.

### 8. 🚀 Agent Mission Control Telemetry
- **File**: `app/presentation/mission_control.py`
- Renders safe execution telemetry across agents, tools, guardrails, and conflict status **WITHOUT leaking raw LLM chain-of-thought**.

---

## 🏗️ 4. MULTI-AGENT ARCHITECTURE (OpenAI Agents SDK)

```text
                               ┌─────────────────────────┐
                               │   FARMER INPUT / QUERY  │
                               └────────────┬────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │     INPUT GUARDRAIL     │
                               └────────────┬────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │      FARM PASSPORT      │
                               │     (SQLite Context)    │
                               └────────────┬────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │      TRIAGE AGENT       │
                               └──────┬───┬───┬───┬──────┘
                                      │   │   │   │
             ┌────────────────────────┘   │   │   └────────────────────────┐
             ▼                            ▼   ▼                            ▼
   ┌───────────────────┐        ┌───────────────┐        ┌───────────────────┐
   │  AGRONOMY AGENT   │        │  PEST DOCTOR  │        │   MARKET AGENT    │
   │ • crop_advisor    │        │ • disease_cls │        │ • mandi_prices    │
   │ • fertilizer_calc │        │ • dosage_chkr │        │ • profit_estimate │
   │ • irrigation_adv  │        └───────┬───────┘        │ • selling_advisor │
   └─────────┬─────────┘                │                └─────────┬─────────┘
             │                          ▼                          │
             │                ┌───────────────────┐                │
             │                                   ▼
                   ┌─────────────────────────┐
                   │  CONVERSATIONAL CHATBOT │
                   │  + DASHBOARD STAT TILES │
                   │  + ON-DEMAND TOOL CARDS │
                   └─────────────────────────┘
```

---

## 🛠️ 5. VERIFIED DATASETS & INTEGRATIONS

| Component | Official Grounding Source | Implementation Details |
| :--- | :--- | :--- |
| **Weather & ET0** | [Open-Meteo API](https://open-meteo.com/) | Real-time 7-day temperature, precipitation, and FAO-56 Reference ET0. |
| **Mandi Rates** | [AMIS Punjab](http://www.amis.pk/) | Wholesale commodity prices across 100+ Punjab markets with live/cache tags. |
| **Pesticide Safety** | [Dept of Plant Protection](http://www.plantprotection.gov.pk/) | Official chemical registry. Blocks unverified chemicals & off-label dosages. |
| **Multimodal Vision** | [Google Gemini Vision](https://ai.google.dev/) | 1.5/2.0 Flash multimodal image diagnosis with strict agricultural guardrail. |
| **Crops & Soil** | [Kaggle Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) | N-P-K, pH, temperature, and moisture constraints tailored for Pakistan. |
| **Disease Diagnosis** | [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset) | Multi-class crop foliar pathology with strict 70% confidence safety threshold. |
| **Agri Statistics** | [FAOSTAT](https://www.fao.org/faostat/en/#country/165) & [PBS](https://www.pbs.gov.pk/) | Historical crop production, provincial yields, and input benchmarks. |
| **Govt Schemes** | [Punjab Agriculture Dept](https://www.agripunjab.gov.pk/) | Kisan Card, CM Green Tractor subsidy, Solar Tubewell, and agri-loans. |

---

## 📡 6. FASTAPI REST API SPECIFICATION

The backend exposes a fully typed REST API with interactive Swagger docs at `/docs`:

### Core Endpoints:
- `POST /api/advisory/query`: Primary multi-agent advisory endpoint with real-time profile hydration and dashboard metrics.
- `POST /api/passport`: Saves or updates the farmer profile in the persistent SQLite database.
- `GET /api/passport/{farmer_id}`: Retrieves profile and deterministic completeness score.
- `GET /api/health-index/{farmer_id}`: Calculates 6-dimensional Farm Health Index (0–100).
- `GET /api/mandi/{district}`: Live/cached wholesale commodity rates from AMIS Punjab.
- `POST /api/irrigation/schedule`: FAO-56 Penman-Monteith crop water requirement schedule.
- `POST /api/pest/diagnose`: Foliar pathology and insect pest classifier with DPP dosage verification.
- `POST /api/simulate`: Decision Simulator executing multi-crop What-If trade-off scenarios.
- `GET /api/govt/schemes`: Relevant Punjab & Federal subsidy programs (Kisan Card, Green Tractor).
- `GET /health`: Microservice health status and active tool count (`{"status":"HEALTHY","deterministic_tools_count":10}`).

---

## 💻 7. GETTING STARTED & LOCAL RUN

### 1. Backend Setup
```bash
# 1. Clone repository
git clone https://github.com/your-username/kisan-dost.git
cd kisan-dost

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Set GROQ_API_KEY, GEMINI_API_KEY, and optional OPENAI_API_KEY

# 5. Populate verified agricultural datasets
python scripts/prepare_datasets.py

# 6. Run FastAPI Server
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Set VITE_API_BASE_URL=https://kisan-dost.onrender.com/api (or http://localhost:8000/api)
# Set VITE_GEMINI_API_KEY=your_gemini_api_key

# 3. Start development server
npm run dev

# 4. Build for production
npm run build
```

---

## 🎬 8. RUNNABLE VIVA DEMO BENCHMARKS

Run any scenario directly with: `python scripts/demo.py --scenario <name>`

```bash
# 1. Primary Multi-Intent Farm Decision (Roman Urdu)
python scripts/demo.py --scenario main

# 2. Safety Attack: Unregistered Chemical / Overdosage Refusal
python scripts/demo.py --scenario safety

# 3. What-If Farm Decision Simulator (Wheat vs Chickpea vs Canola)
python scripts/demo.py --scenario whatif

# 4. Cross-Domain Agent Conflict Resolution (Agronomy vs Water Turns)
python scripts/demo.py --scenario conflict

# 5. Uncertain Pathology Diagnosis (< 70% Confidence Safety Refusal)
python scripts/demo.py --scenario low_confidence

# 6. Offline Data Fallback (Truthful Cached AMIS Market Rates)
python scripts/demo.py --scenario offline

# Run ALL 6 scenarios sequentially
python scripts/demo.py --scenario all
```

---

## 🧪 9. AUTOMATED TEST SUITE

Run all unit, integration, and safety tests with pytest:

```bash
pytest tests/ -v
```

```text
======================== 79 passed in 70.42s ========================
• tests/test_agents.py ........                                            [ 10%]
• tests/test_api.py .........                                              [ 21%]
• tests/test_foundation.py .....                                           [ 27%]
• tests/test_presentation.py ....                                          [ 32%]
• tests/test_safety_failures.py ......                                     [ 40%]
• tests/test_services.py ........                                          [ 50%]
• tests/test_signature_features.py ..........................              [ 83%]
• tests/test_tools.py .............                                        [100%]
```

---

## 📁 10. PROJECT DIRECTORY STRUCTURE

```text
kisan-dost/
├── README.md                          # Comprehensive technical documentation
├── pyproject.toml                     # Pytest and project configuration
├── requirements.txt                   # Production dependencies
├── .env.example                       # Environment configuration template
├── main.py                            # CLI entry point
│
├── config/
│   ├── settings.py                    # Pydantic v2 application settings (Gemini, Groq, OpenAI)
│   └── constants.py                   # Agro-climatic zones, Mandis, verification states
│
├── app/
│   ├── api/                           # FastAPI REST Service & Endpoints
│   │   ├── main.py                    # FastAPI application instance, CORS, middleware
│   │   └── routes/                    # advisory, passport, health_index, tools, mandi, simulate
│   │
│   ├── agents/                        # OpenAI Agents SDK Multi-Agent Handoffs
│   │   ├── base.py                    # SDK primitives, Runner & Groq fallback
│   │   ├── triage.py                  # Multi-intent routing & specialist selection
│   │   ├── agronomy.py                # Crop, fertilizer & irrigation specialist
│   │   ├── pest_doctor.py             # Disease classifier & dosage verification
│   │   ├── market.py                  # AMIS Mandi prices & selling timing
│   │   ├── finance_govt.py            # Budgeting & Punjab Govt support schemes
│   │   └── synthesis.py               # Conflict synthesis & receipt generator
│   │
│   ├── tools/                         # Deterministic Agricultural Tools
│   │   ├── agronomy/                  # crop_advisor, fertilizer_calculator, irrigation_advisor
│   │   ├── pest/                      # disease_classifier, dosage_checker
│   │   ├── market/                    # mandi_price, profit_estimator, selling_advisor
│   │   ├── govt/                      # support_finder (Kisan Card & subsidies)
│   │   └── weather/                   # open_meteo & geocoder
│   │
│   ├── integrations/                  # External API Clients
│   │   ├── gemini_client.py           # Google Gemini Multimodal Vision Client
│   │   ├── groq_client.py             # Groq Llama 3.3 fallback client
│   │   ├── amis.py                    # Punjab Agriculture Market Information System
│   │   └── open_meteo.py              # Open-Meteo weather & ET0 client
│   │
│   ├── schemas/                       # Strict Pydantic Domain Contracts with Evidence
│   │   ├── evidence.py                # Evidence & VerificationState models
│   │   ├── farmer.py                  # FarmerProfile schema
│   │   ├── simulation.py              # SimulationOption & SimulationResult schemas
│   │   ├── conflict.py                # DecisionConflict schema
│   │   ├── farm_health.py             # FarmHealthScore schema (6 dimensions)
│   │   └── decision_receipt.py        # DecisionReceipt schema
│   │
│   ├── services/                      # Deterministic Decision Intelligence Services
│   │   ├── decision_service.py        # Conflict detection & resolution engine
│   │   ├── decision_simulator.py      # What-If multi-crop scenario simulator
│   │   ├── farm_health_service.py     # Deterministic Farm Health Index calculation
│   │   ├── trust_service.py           # Unified trust & evidence distribution
│   │   ├── confidence_service.py      # Separate model, evidence, & overall confidence
│   │   ├── risk_service.py            # Multi-vector agricultural & financial risk
│   │   └── escalation_service.py      # Structured escalation states
│   │
│   ├── context/                       # SQLite Persistent Farmer Passport & Sessions
│   │   ├── farmer_profile.py          # SQLite store & deterministic completeness scoring
│   │   ├── session.py                 # Multi-turn conversation sessions
│   │   └── hydration.py               # Auto-hydration of farm context into agents
│   │
│   ├── guardrails/                    # Safety Guardrails
│   │   ├── input.py                   # Topic relevance, injection & medical block
│   │   ├── output.py                  # Financial sanity & physiological yield bounds
│   │   └── pesticide_safety.py        # Registered chemical validation & dosage bounds
│   │
│   ├── presentation/                  # Rich Terminal UI & Telemetry
│   │   ├── mission_control.py         # Safe execution telemetry panel (No raw CoT)
│   │   ├── decision_receipt.py        # Formatted decision receipt cards
│   │   ├── farm_passport.py           # Farm Passport visual card
│   │   ├── farm_health.py             # Farm Health Index card
│   │   └── terminal.py                # Interactive CLI loops
│   │
│   └── i18n/                          # Multilingual Rendering Engine
│       ├── language_detector.py       # Language classification (en, ur, roman_urdu)
│       ├── english_renderer.py        # English advisory renderer
│       ├── urdu_renderer.py           # Nastaliq/Urdu renderer
│       └── roman_urdu_renderer.py     # Natural Roman Urdu renderer
│
├── frontend/                          # React 18 + TypeScript + Tailwind Web Application
│   ├── index.html                     # Web entry point
│   ├── vite.config.ts                 # Vite bundler & API reverse proxy configuration
│   ├── src/
│   │   ├── api/                       # Typed REST client & Gemini Vision integration
│   │   │   ├── client.ts              # Talks to https://kisan-dost.onrender.com/api
│   │   │   ├── geminiClient.ts        # Multimodal Vision with farming guardrail
│   │   │   └── types.ts               # Domain types matching Pydantic backend
│   │   ├── components/
│   │   │   ├── chat/                  # Conversational Farm Dashboard Chatbot
│   │   │   │   └── ZaraiChatBot.tsx   # All-in-one conversational farm assistant
│   │   │   ├── onboarding/            # 6-step tactile onboarding with Name & Passport
│   │   │   ├── tools/                 # Expandable dashboard tools
│   │   │   │   ├── DiseaseDoctor.tsx  # Gemini camera scan, guardrail refusal & DPP dosage
│   │   │   │   ├── MandiBoard.tsx     # AMIS wholesale prices and trend tracker
│   │   │   │   ├── IrrigationPlan.tsx # FAO-56 stage-by-stage water schedule
│   │   │   │   └── WhatIfSim.tsx      # Real-time water reduction slider & trade-offs
│   │   │   └── common/                # GroundingBadges, Header, Action chips
│   │   └── context/                   # FarmContext (SQLite sync) & LanguageContext
│
├── scripts/
│   ├── prepare_datasets.py            # Verified Pakistani dataset seeder
│   └── demo.py                        # 6 executable viva demo benchmark scenarios
│
└── tests/                             # Comprehensive Automated Test Suites (79 tests)
    ├── test_agents.py                 # Multi-agent handoff & tool execution tests
    ├── test_api.py                    # FastAPI endpoint tests
    ├── test_foundation.py             # Core schemas & integration client tests
    ├── test_tools.py                  # All 10 deterministic agricultural tool tests
    ├── test_services.py               # Decision, Risk, Trust & Health service tests
    ├── test_safety_failures.py        # Failure & safety refusal tests
    └── test_signature_features.py     # All 7 signature feature benchmark tests
```

---

## 🎤 11. Why MY KISAN-DOST

**Q: Why a Multi-Agent architecture instead of a single LLM prompt?**  
> *"Because Pakistani farm decisions span multiple specialized domains — pathology, market economics, hydrology, soil agronomy, and government schemes. Separating agents creates clear single responsibilities, while deterministic tools and services prevent cross-domain hallucination."*

**Q: Where is the AI and where is the deterministic logic?**  
> *"AI handles natural-language understanding, intent triage, multi-agent orchestration, contextual reasoning, and multilingual synthesis. Deterministic logic calculates fertilizer NPK bags, pesticide safety limits, irrigation scheduling (FAO-56), profit margins, risk scores, and the Farm Health Index."*

**Q: Can the LLM guess or recommend an unknown pesticide dosage?**  
> *"No. Pesticide dosages require an exact match against the verified Department of Plant Protection registry. If an unknown chemical (e.g. 'SuperKill99') or unregistered dosage is requested, the system strictly blocks the dosage and marks it UNVERIFIED."*

**Q: How does the Gemini Vision model enforce farming-only answers?**  
> *"Before performing any pathology, the vision model checks whether the uploaded image is genuinely related to farming, agricultural plants, leaves, or field pests. If a non-farming photo (human, car, pet, document, furniture) is uploaded, it triggers a strict refusal card in Urdu and Roman Urdu, refusing to hallucinate medical or non-agricultural advice."*

**Q: How does Kisan Dost handle agent disagreements?**  
> *"The Decision Service explicitly detects cross-domain conflicts (e.g., Agronomy recommending 4 irrigations while Water Monitor caps turns at 2) and resolves them using conservative priority rules without hiding the trade-offs."*

**Q: What makes Kisan Dost unique compared to traditional AI dashboards?**  
> *"Instead of static, rigid dashboards or generic chatbots, it is an all-in-one conversational companion. It remembers the farmer by name in a persistent SQLite passport, addresses them with respect, speaks natural language, answers everyday questions concisely with embedded stats, and summons rich interactive tools only when needed."*

---

**Built with pride BY Abdullah Nadeem for Pakistani Farmers at SMIT Hackathon 🌾**

