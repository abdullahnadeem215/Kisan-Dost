# 🌾 KISAN DOST (کسان دوست)
### AI Agronomy Multi-Agent Advisory & Farm Decision System

[![Tests](https://img.shields.io/badge/tests-70%20passed-brightgreen.svg)]()
[![Framework](https://img.shields.io/badge/framework-OpenAI%20Agents%20SDK-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)]()
[![Data%20Status](https://img.shields.io/badge/data%20provenance-Verified%20%26%20Grounded-emerald.svg)]()

---

## 🎯 1. PRODUCT POSITIONING

> **"Kisan Dost is an evidence-grounded farm decision engine that investigates a farmer's situation, compares possible actions, validates evidence, resolves conflicting recommendations, evaluates risk and confidence, and knows when it should refuse to guess."**

### Why Kisan Dost is NOT Just Another Agricultural Chatbot:

```text
TRADITIONAL FARM CHATBOT:
Farmer Question ──► LLM Hallucination ──► Generic Plausible Answer

KISAN DOST DECISION ENGINE:
Farmer Situation
      │
      ▼
Input Guardrail & Farm Passport (SQLite Persistent Context)
      │
      ▼
Multi-Intent Triage (OpenAI Agents SDK)
      │
      ▼
Specialist Investigation (Agronomy • Pest Doctor • Market • Finance/Govt)
      │
      ▼
Deterministic Calculation & Evidence Aggregation
      │
      ▼
Decision Simulator (What-If Analysis) & Conflict Resolution
      │
      ▼
Independent Risk + Trust + Confidence Evaluation
      │
      ▼
Final Farm Decision & Immutable Decision Receipt
```

---

## ⚖️ 2. NON-NEGOTIABLE ARCHITECTURAL CONTRACT

| LLM Capabilities (Allowed) | Authoritative Agricultural Facts (STRICTLY DETERMINISTIC) |
| :--- | :--- |
| • Natural language farmer understanding (Urdu / Roman Urdu / English) | • Fertilizer quantities (NFDC NPK-to-Bag conversion) |
| • Multi-intent triage & specialist routing | • Pesticide dosage & safety limits (Plant Protection Registry) |
| • Contextual reasoning & trade-off explanation | • Wholesale mandi prices (AMIS Punjab API / Cache) |
| • Summarization & uncertainty communication | • Irrigation requirements (FAO-56 Penman-Monteith \(ET_c\)) |
| • Synthesis into structured Decision Receipts | • Profit, net margin & break-even yield calculations |
| • Refusal explanation on unverified inputs | • Farm Health Index & multi-vector risk scores |

> 🚨 **Core Rule:** The LLM decides *what* needs to be calculated; deterministic tools and verified datasets perform the calculation.

---

## 🌟 3. SEVEN SIGNATURE DIFFERENTIATORS

### 1. 🔮 Farm Decision Simulator (What-If Engine)
- File: `app/services/decision_simulator.py`
- Evaluates multi-crop strategies (*Wheat vs Chickpea vs Canola*) under farm constraints.
- Quantifies explicit trade-offs: water requirements (mm / %), input costs (PKR), expected revenue, and net profit delta.
- Strictly marks scenario estimates as `is_hypothetical: True` to prevent mistaking simulation for guarantees.

### 2. ⚔️ Agent Conflict Resolution Engine
- File: `app/services/decision_service.py`
- Automatically detects cross-domain disagreements:
  - *Agronomy recommends 4 irrigations vs Water Monitor reports only 2 available canal turns.*
  - *Market favors high-gross crop vs Agronomy detects water stress.*
  - *Pest recommender proposes unverified chemical vs Plant Protection safety bounds.*
- Resolves conflicts using deterministic conservative agronomic precedence rules without hiding trade-offs.

### 3. 🧑‍🌾 Farm Passport (SQLite Persistent Context)
- File: `app/context/farmer_profile.py` & `app/presentation/farm_passport.py`
- Remembers District, Acreage, Soil Type, Water Source, Season, Current Crop, and Language across turns.
- Features deterministic completeness scoring (0-100%).

### 4. 📊 Kisan Dost Farm Health Index
- File: `app/services/farm_health_service.py` & `app/presentation/farm_health.py`
- Composite 0-100 score tracking 6 dimensions: **Water (25%)**, **Crop Condition (20%)**, **Pest Bio-Security (20%)**, **Weather (15%)**, **Economics (10%)**, and **Profile Completeness (10%)**.
- Refuses to fabricate a score if critical evidence is absent (`score_available = False`).

### 5. 🛡️ Trust Layer & Truthful Data Freshness
- File: `app/services/trust_service.py`, `app/services/confidence_service.py`
- Explicitly separates **Model Confidence**, **Evidence Confidence**, and **Overall Confidence**.
- Truthfully tags all external data sources:
  - `🟢 LIVE`
  - `🟡 CACHED` (Exposes exact retrieval timestamp; never claims cached data is live)
  - `🔴 UNAVAILABLE`

### 6. 🧾 Immutable Decision Receipt
- File: `app/schemas/decision_receipt.py` & `app/presentation/decision_receipt.py`
- Issues a structured audit receipt for every advisory: Decision, Rationale, Action Steps, Grounding Evidence IDs, Risk Assessment, and Overall Confidence %.

### 7. 🚀 Agent Mission Control Telemetry
- File: `app/presentation/mission_control.py`
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
             │                │ FINANCE/GOVT AGNT │                │
             │                │ • govt_support    │                │
             │                │ • budget_optimizer│                │
             │                └─────────┬─────────┘                │
             │                          │                          │
             └──────────────────┬───────┴──────────────────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  DETERMINISTIC SERVICES │
                   │ • Decision Service      │
                   │ • Conflict Resolution   │
                   │ • Decision Simulator    │
                   │ • Trust & Risk Engine   │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │     SYNTHESIS AGENT     │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │    OUTPUT GUARDRAILS    │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │ 🧾 DECISION RECEIPT CARD │
                   │  + MULTILINGUAL OUTPUT  │
                   └─────────────────────────┘
```

---

## 🛠️ 5. VERIFIED DATASETS & INTEGRATIONS

| Component | Official Grounding Source | Implementation Details |
| :--- | :--- | :--- |
| **Weather & ET0** | [Open-Meteo API](https://open-meteo.com/) | Real-time 7-day temperature, precipitation, and FAO-56 Reference ET0. |
| **Mandi Rates** | [AMIS Punjab](http://www.amis.pk/) | Wholesale commodity prices across 100+ Punjab markets with live/cache tags. |
| **Pesticide Safety** | [Dept of Plant Protection](http://www.plantprotection.gov.pk/) | Official chemical registry. Blocks unverified chemicals & off-label dosages. |
| **Crops & Soil** | [Kaggle Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) | N-P-K, pH, temperature, and moisture constraints tailored for Pakistan. |
| **Disease Diagnosis** | [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset) | Multi-class crop foliar pathology with strict 70% confidence safety threshold. |
| **Agri Statistics** | [FAOSTAT](https://www.fao.org/faostat/en/#country/165) & [PBS](https://www.pbs.gov.pk/) | Historical crop production, provincial yields, and input benchmarks. |
| **Govt Schemes** | [Punjab Agriculture Dept](https://www.agripunjab.gov.pk/) | Kisan Card, CM Green Tractor subsidy, Solar Tubewell, and agri-loans. |

---

## 🎬 6. RUNNABLE VIVA DEMO BENCHMARKS

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

## 💻 7. CLI USAGE & INTERACTIVE SESSIONS

### Interactive Terminal Session
```bash
python main.py --interactive
```
*Supports natural multi-turn conversations in Roman Urdu, Urdu, and English.*

### Single Query Mode
```bash
python main.py --query "5 acre zameen hai Multan mein. Pani limited hai aur Rabi season hai. Konsi crop lagaoon aur fertilizer kitni chahiye?"
```

### Run Full Test Suite
```bash
pytest tests/
```
*(All 70 unit and integration tests pass with 100% pass rate).*

---

## 📁 8. PROJECT DIRECTORY STRUCTURE

```text
kisan-dost/
├── README.md                          # Comprehensive technical documentation
├── pyproject.toml                     # Pytest and project configuration
├── requirements.txt                   # Production dependencies
├── .env.example                       # Environment configuration template
├── main.py                            # CLI entry point
│
├── config/
│   ├── settings.py                    # Pydantic v2 application settings
│   └── constants.py                   # Agro-climatic zones, Mandis, verification states
│
├── app/
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
│   │   ├── trust_status.py            # Unified Trust Status card
│   │   └── terminal.py                # Interactive CLI loops
│   │
│   └── i18n/                          # Multilingual Rendering Engine
│       ├── language_detector.py       # Language classification (en, ur, roman_urdu)
│       ├── english_renderer.py        # English advisory renderer
│       ├── urdu_renderer.py           # Nastaliq/Urdu renderer
│       └── roman_urdu_renderer.py     # Natural Roman Urdu renderer
│
├── scripts/
│   ├── prepare_datasets.py            # Verified Pakistani dataset seeder
│   └── demo.py                        # 6 executable viva demo benchmark scenarios
│
└── tests/                             # Comprehensive Automated Test Suites (70 tests)
    ├── test_agents.py                 # Multi-agent handoff & tool execution tests
    ├── test_foundation.py             # Core schemas & integration client tests
    ├── test_tools.py                  # All 10 deterministic agricultural tool tests
    ├── test_services.py               # Decision, Risk, Trust & Health service tests
    ├── test_safety_failures.py        # Failure & safety refusal tests
    └── test_signature_features.py     # All 7 signature feature benchmark tests
```

---

## 🎤 9. VIVA EXAMINER Q&A CHEAT-SHEET

**Q: Why a Multi-Agent architecture instead of a single LLM prompt?**  
> *"Because Pakistani farm decisions span multiple specialized domains — pathology, market economics, hydrology, soil agronomy, and government schemes. Separating agents creates clear single responsibilities, while deterministic tools and services prevent cross-domain hallucination."*

**Q: Where is the AI and where is the deterministic logic?**  
> *"AI handles natural-language understanding, intent triage, multi-agent orchestration, contextual reasoning, and multilingual synthesis. Deterministic logic calculates fertilizer NPK bags, pesticide safety limits, irrigation scheduling (FAO-56), profit margins, risk scores, and the Farm Health Index."*

**Q: Can the LLM guess or recommend a pesticide dosage?**  
> *"No. Pesticide dosages require an exact match against the verified Department of Plant Protection registry. If an unknown chemical (e.g. 'SuperKill99') or unregistered dosage is requested, the system strictly blocks the dosage and marks it UNVERIFIED."*

**Q: How does Kisan Dost handle agent disagreements?**  
> *"The Decision Service explicitly detects cross-domain conflicts (e.g., Agronomy recommending 4 irrigations while Water Monitor caps turns at 2) and resolves them using conservative priority rules without hiding the trade-offs."*

**Q: What makes Kisan Dost unique?**  
> *"It is not a generic chatbot. It maintains a persistent Farm Passport, runs What-If simulations, enforces pesticide safety, exposes transparent evidence and data freshness, evaluates Farm Health, and generates verifiable Decision Receipts."*

---

**Built with pride BY Abdullah Nadeem for Pakistani Farmers at SMIT Hackathon 🌾**
