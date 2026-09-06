"""
Input Safety Guardrail for Kisan Dost.
Enforces topic relevance, jailbreak/prompt injection detection, and human medical advice blocking.
"""
import re
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class InputGuardrailResult(BaseModel):
    """
    Result of input safety evaluation.
    """
    is_allowed: bool = Field(..., description="True if prompt is safe and relevant to agriculture")
    blocked_category: Optional[str] = Field(None, description="JAILBREAK, HUMAN_MEDICAL, OFF_TOPIC, HAZARD")
    reason: str = Field(..., description="Explanation of evaluation outcome")
    sanitized_prompt: str = Field(..., description="Cleaned or original prompt text")

    @property
    def is_safe(self) -> bool:
        return self.is_allowed

    @property
    def refusal_reason(self) -> Optional[str]:
        return self.reason if not self.is_allowed else None


# Jailbreak & System Override Patterns
JAILBREAK_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s+override",
    r"you\s+are\s+now\s+dan",
    r"developer\s+mode",
    r"bypass\s+safety\s+filter",
    r"drop\s+table",
    r"sudo\s+",
    r"chmod\s+777"
]

# Human Medical Queries & Dangerous Ingestion Patterns
HUMAN_MEDICAL_PATTERNS = [
    r"\b(human|person|child|baby|infant|man|woman)\s+(fever|disease|cancer|infection|cough|headache|dose|dosage)\b",
    r"\b(cure|treat|diagnose)\s+(human|patient|person|myself|my\s+son|my\s+daughter)\b",
    r"\bparacetamol|ibuprofen|amoxicillin|insulin|aspirin\b",
    r"\b(drink|ingest|swallow|consume|take)\b.*\b(pesticide|fungicide|insecticide|poison|acid|chemical|nativo|tilt|radiant)\b",
    r"\b(person|human|man|woman|child|baby)\b.*\b(drink|ingest|swallow|consume)\b"
]

# Comprehensive Agricultural & Farming Keywords (English, Urdu, Roman Urdu)
AGRI_KEYWORDS = [
    # Crops & Plants
    "crop", "crops", "fasal", "faslon", "wheat", "gandum", "kanak", "cotton", "kapas", "phutti",
    "rice", "chawal", "dhaan", "munji", "maize", "makai", "corn", "sugarcane", "kamad", "ganna",
    "potato", "aloo", "alu", "tomato", "tamatar", "onion", "pyaz", "piaz", "chili", "mirch",
    "garlic", "lehsan", "ginger", "adrak", "mango", "aam", "citrus", "kino", "kinnow", "malta",
    "guava", "amrood", "banana", "kela", "mustard", "sarson", "raya", "canola", "toria", "taramira",
    "sunflower", "surajmukhi", "sesame", "til", "chickpea", "channa", "chana", "gram", "lentil",
    "masoor", "moong", "mash", "pulses", "daal", "dal", "fodder", "chara", "berseem", "barseem",
    "lucerne", "shaftal", "jowar", "chari", "bajra", "millet", "sorghum", "tobacco", "tambaku",
    "beej", "seed", "seeds", "seedling", "paneeri", "germination", "ugao", "variety", "varieties",
    "aqsam", "qisam", "hybrid", "cultivar", "narc", "parc",

    # Fertilizers & Soil
    "fertilizer", "fertilizers", "khaad", "khad", "urea", "dap", "npk", "potash", "sop", "mop",
    "nitrophos", "can", "ammonium", "ssp", "tsp", "zinc", "boron", "sulfur", "sulphur", "gypsum",
    "compost", "gobar", "manure", "organic", "soil", "mitti", "zameen", "zamin", "land",
    "acre", "acres", "killa", "bigha", "kanal", "marla", "loam", "mera", "clay", "chikni",
    "sandy", "raitili", "saline", "kallar", "shor", "ph", "fertility", "zarkhez", "zarkhezi",
    "nutrition", "nutrient", "deficiency", "kami", "bag", "bags", "bori", "boriyan",

    # Water, Irrigation & Weather
    "water", "pani", "paani", "irrigation", "aabpashi", "canal", "nehar", "nehri", "turn",
    "turns", "wari", "bariat", "tubewell", "tube-well", "boring", "diesel", "solar", "drip",
    "sprinkler", "flood", "furrow", "bed", "khal", "warabandi", "weather", "mausam", "rain",
    "barish", "barsat", "monsoon", "temperature", "garmi", "sardi", "darja hararat", "humidity",
    "nami", "frost", "pala", "fog", "dhund", "smog", "heatwave", "loo", "hail", "olay",
    "storm", "toofan", "forecast", "peshgoi", "et0", "evapotranspiration",

    # Pest, Diseases, Plant Protection
    "pest", "pests", "keera", "keeray", "kire", "insect", "insects", "sundi", "caterpillar",
    "bollworm", "armyworm", "pink bollworm", "gulabi", "lashkari", "whitefly", "sufaid makhi",
    "chitti makhi", "aphid", "tela", "kala tela", "sabz tela", "jassid", "thrips", "mites",
    "locust", "tidi", "fungus", "phaphundi", "rust", "kungi", "yellow rust", "peeli kungi",
    "brown rust", "blight", "jhulsaao", "early blight", "late blight", "rot", "galan",
    "root rot", "collar rot", "wilt", "murjhana", "virus", "leaf curl", "clcv", "nematode",
    "smut", "kangiari", "powdery mildew", "downy mildew", "pesticide", "pesticides", "spray",
    "zehar", "dawa", "dawayi", "fungicide", "insecticide", "weedicide", "herbicide", "jariboti",
    "ghas", "weed", "weeds", "godi", "dosage", "dose", "miqdar", "tanki", "nozzle", "dpp",

    # Market, Economics & Government Schemes
    "mandi", "market", "ghalla", "ghalla mandi", "rate", "rates", "bhaow", "bhaw", "price",
    "prices", "qeemat", "cost", "kharcha", "lagat", "profit", "munafa", "bachat", "revenue",
    "amdani", "loss", "nuqsan", "nuksan", "yield", "paidawar", "maund", "maunds", "mann",
    "kg", "kilo", "ton", "quintal", "sell", "bechna", "furrokt", "khareedna", "buy", "hold",
    "rokhna", "store", "storage", "aarth", "aarhti", "commission", "kisan card", "green tractor",
    "subsidy", "subsidies", "imdad", "scheme", "schemes", "loan", "qarz", "zarai bank", "ztbl",
    "bima", "takaful", "sarkari", "punjab agriculture", "amis",

    # Farm Operations & General Farming Terms
    "farm", "farmer", "farmers", "kisan", "kashtkar", "zamindar", "dehqan", "agriculture",
    "agricultural", "agri", "zarai", "zaraat", "khet", "field", "fields", "rabi", "kharif",
    "season", "sowing", "bohai", "bovai", "harvest", "harvesting", "katai", "cultivation",
    "kasht", "plough", "plowing", "hal", "sohaga", "leveler", "laser leveler",

    # Urdu Script (Nastaliq)
    "کسان", "زراعت", "فصل", "فصلوں", "گندم", "کپاس", "چاول", "مکئی", "کماد", "آلو", "ٹماٹر",
    "پیاز", "آم", "کھاد", "یوریا", "ڈی اے پی", "پانی", "نہری", "ٹیوب ویل", "سپرے", "کیڑا",
    "کیڑے", "سنڈی", "سفید مکھی", "تیلا", "کنگی", "جھلسائو", "منڈی", "ریٹ", "بھاؤ", "پیداوار",
    "ایکڑ", "من", "سبسڈی", "کسان کارڈ", "ٹریکٹر", "قرضہ", "بیج", "بیماری", "علاج", "نقصان",
    "منافع", "خرچہ", "بارش", "موسم", "گرمی", "زمین", "مٹی", "بوائی", "کٹائی", "زرعی"
]

# Conversational Courtesy & Identity Patterns (Allowed simple conversational queries)
COURTESY_AND_IDENTITY_PATTERNS = [
    r"^(hi|hello|hey|salam|assalam|aoa|adab|namaste)\b",
    r"\b(kaise|kaisay|kese|kesay)\s+(ho|hain|hn)\b",
    r"\b(kya|kia)\s+(haal|hal|chal)\b",
    r"\b(how are you|how r u|theek ho|thik ho|theek hain|thik hain)\b",
    r"\b(who are you|who r u|what are you)\b",
    r"\b(aap|tum|ap)\s+(kon|kaun|kis|koun)\b",
    r"\b(kisan dost)\s+(kon|kaun|kis|koun)\b",
    r"\b(what can you do|what do you do)\b",
    r"\b(kya|kia)\s*(kar|kr)\s*(saktay|sakte|sakti|skte|skty|sktay)\b",
    r"\b(aap|tum|ap)\s+(kya|kia)\s*(kar|karte|krte|kr)\b",
    r"\b(kya|kia)\s*(madad|help)\b",
    r"\b(apna|apni)\s+(taruf|taaruf|ta'ruf|intro|introduction)\b",
    r"\b(introduce yourself|tell me about yourself)\b",
    r"\b(mera naam|my name is|main kisan|main zamindar)\b",
    r"\b(shukriya|shukria|thanks|thank you|meharbani|welcome|jazakallah)\b",
    r"^(ok|theek hai|thik hai|acha|achha|sahi hai|haan|yes|no|nahi)\b",
    r"(السلام علیکم|سلام|آداب|کیسے ہیں|کیا حال ہے|آپ کون ہیں|آپ کون ہو|کیا کر سکتے ہیں|کیا کر سکتے ہو|مدد|شکریہ|میرا نام|تعارف)"
]

# Explicit Out-of-Domain Block Patterns
EXPLICIT_OFF_TOPIC_PATTERNS = [
    # Politics & Non-agri Government
    r"\b(prime minister|wazir e azam|nawaz sharif|imran khan|bilawal|shehbaz|parliament|national assembly|election|elections|vote|pti|pmln|ppp|president|trump|biden|modi|politics|siyasat)\b",
    r"(سیاست|وزیر اعظم|عمران خان|نواز شریف|الیکشن)",
    # Sports & Games
    r"\b(cricket|babar azam|virat kohli|shaheen afridi|psl|ipl|world cup|football|messi|ronaldo|fifa|tennis|hockey|match score|cricket score|pubg|free fire|ludo)\b",
    r"(کرکٹ|میچ|فٹ بال|ورلڈ کپ)",
    # Entertainment, Movies, Celebrity
    r"\b(movie|film|cinema|actor|actress|song|music|drama|hollywood|bollywood|lollywood|netflix|celebrity|hero|heroine|love story|shayari|poetry|romantic)\b",
    r"(فلم|گانا|ڈرامہ|شاعری)",
    # Coding, Tech & Hacking
    r"\b(python|javascript|java|c\+\+|html|css|react|coding|programming|github|algorithm|hack|hacking|software|windows|android|iphone|laptop repair|computer repair)\b",
    # Crypto & Speculative Finance
    r"\b(bitcoin|crypto|cryptocurrency|ethereum|forex|stock exchange|stock market|trading|nft|dollar rate|currency rate)\b",
    # General non-agri trivia & science
    r"\b(quantum|black hole|capital of|speed of light|einstein|planet mars|universe|pythagoras|solve equation|essay on|recipe for cake|recipe for biryani|how to cook)\b",
    r"\b(car engine|bike repair|mobile phone price|smartphone to buy)\b"
]


class InputGuardrail:
    """
    Input validation guardrail enforcing safety, topic boundaries, and human health protection.
    """

    @classmethod
    def validate_input(cls, prompt: str) -> InputGuardrailResult:
        """
        Validates input prompt for safety violations or off-topic status.
        """
        if not prompt or not prompt.strip():
            return InputGuardrailResult(
                is_allowed=False,
                blocked_category="OFF_TOPIC",
                reason="Empty prompt provided.",
                sanitized_prompt=""
            )

        prompt_clean = prompt.strip()
        prompt_lower = prompt_clean.lower()

        # 1. Jailbreak / Prompt Injection Check
        for pattern in JAILBREAK_PATTERNS:
            if re.search(pattern, prompt_lower):
                return InputGuardrailResult(
                    is_allowed=False,
                    blocked_category="JAILBREAK",
                    reason="Security violation: Detected jailbreak or prompt override attempt.",
                    sanitized_prompt=prompt_clean
                )

        # 2. Human Medical Advice / Poison Ingestion Check
        for pattern in HUMAN_MEDICAL_PATTERNS:
            if re.search(pattern, prompt_lower):
                return InputGuardrailResult(
                    is_allowed=False,
                    blocked_category="HUMAN_MEDICAL",
                    reason="Safety violation: Kisan Dost provides agricultural intelligence only and strictly blocks human medical advice or chemical ingestion queries.",
                    sanitized_prompt=prompt_clean
                )

        # 3. Explicit Out-of-Domain Pattern Check
        for pattern in EXPLICIT_OFF_TOPIC_PATTERNS:
            if re.search(pattern, prompt_lower):
                return InputGuardrailResult(
                    is_allowed=False,
                    blocked_category="OFF_TOPIC",
                    reason="Yeh sawal zaraat aur kheti baari se mutalliq nahi hai. Kisan Dost sirf faslon, zameen, khad, bimari, mandi rates aur kisan schemes ke baray mein rehnumai faraham karta hai.",
                    sanitized_prompt=prompt_clean
                )

        # 4. Conversational Courtesy & Identity Check (Allowed for simple natural response)
        is_courtesy = any(re.search(pat, prompt_lower) for pat in COURTESY_AND_IDENTITY_PATTERNS)
        if is_courtesy:
            return InputGuardrailResult(
                is_allowed=True,
                blocked_category=None,
                reason="Input is a conversational courtesy or identity query.",
                sanitized_prompt=prompt_clean
            )

        # 5. Agricultural Topic Relevance Check
        # Check if any agri keyword or sub-word appears
        has_agri_context = any(re.search(r"\b" + re.escape(kw) + r"\b", prompt_lower) if len(kw) <= 4 else kw in prompt_lower for kw in AGRI_KEYWORDS)
        if has_agri_context:
            return InputGuardrailResult(
                is_allowed=True,
                blocked_category=None,
                reason="Input prompt passed all safety and agricultural relevance checks.",
                sanitized_prompt=prompt_clean
            )

        # 6. Fallback: If neither courtesy nor agricultural context, it is strictly out of domain!
        return InputGuardrailResult(
            is_allowed=False,
            blocked_category="OFF_TOPIC",
            reason="Yeh sawal zaraat aur kheti baari se mutalliq nahi hai. Kisan Dost sirf faslon, zameen, khad, bimari, mandi rates aur kisan schemes ke baray mein rehnumai faraham karta hai.",
            sanitized_prompt=prompt_clean
        )

    @classmethod
    def audit_input(cls, prompt: str, farmer_profile: Optional[Any] = None) -> InputGuardrailResult:
        """
        Alias for validate_input supporting optional farmer_profile context.
        """
        return cls.validate_input(prompt)
