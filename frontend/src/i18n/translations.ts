/**
 * Comprehensive Trilingual Dictionary for Kisan Dost:
 * - Urdu (اردو): Proper Nastaliq phrasing, RTL, respectful agricultural terms
 * - Roman Urdu: Natural colloquial Pakistani Punjabi/Urdu agricultural phrasing
 * - English: Clear agricultural domain terms
 */

export type LanguageCode = 'ur' | 'roman_urdu' | 'en';

export interface Translations {
  appName: string;
  tagline: string;
  homeTab: string;
  chatTab: string;
  faislayTab: string;
  simulatorTab: string;
  passportTab: string;
  toolsTab: string;
  chatTitle: string;
  chatSubtitle: string;
  agentThinking: string;

  // Header & Status
  liveStatus: string;
  cachedStatus: string;
  offlineStatus: string;
  acresLabel: string;
  districtLabel: string;

  // Onboarding
  welcomeTitle: string;
  welcomeSubtitle: string;
  startBtn: string;
  notSureBtn: string;
  nextBtn: string;
  backBtn: string;
  finishSetupBtn: string;
  stepNameTitle: string;
  stepNameDesc: string;
  nameLabel: string;
  namePlaceholder: string;
  phoneLabel: string;
  phonePlaceholder: string;
  stepLocationTitle: string;
  stepLocationDesc: string;
  stepAcreageTitle: string;
  stepAcreageDesc: string;
  stepWaterTitle: string;
  stepWaterDesc: string;
  stepCropTitle: string;
  stepCropDesc: string;
  stepLanguageTitle: string;
  stepLanguageDesc: string;

  // Home Screen: Aaj Ka Brief
  aajKaBrief: string;
  allNormalTitle: string;
  allNormalDesc: string;
  waterAlertTitle: string;
  waterAlertDesc: string;
  weatherAlertTitle: string;
  weatherAlertDesc: string;
  mandiAlertTitle: string;
  mandiAlertDesc: string;

  // Secondary Status Row
  healthScoreTitle: string;
  waterStatusTitle: string;
  weatherTitle: string;
  mandiRateTitle: string;
  turnsUnit: string;
  maundUnit: string;

  // Quick Action Grid (Outdoor touch targets)
  actionDiseasePhoto: string;
  actionDiseasePhotoSub: string;
  actionCropAdvisor: string;
  actionCropAdvisorSub: string;
  actionIrrigation: string;
  actionIrrigationSub: string;
  actionMandi: string;
  actionMandiSub: string;
  actionSimulator: string;
  actionSimulatorSub: string;
  actionGovtSupport: string;
  actionGovtSupportSub: string;
  actionAskQuestion: string;
  actionAskQuestionSub: string;

  // Decision Receipt
  receiptHeader: string;
  receiptIdLabel: string;
  kyunTitle: string;
  impactTitle: string;
  financialTitle: string;
  costLabel: string;
  revenueLabel: string;
  netProfitLabel: string;
  confidenceLabel: string;
  actionStepsTitle: string;
  saveDecisionBtn: string;
  savedToast: string;
  closeBtn: string;

  // History / Mere Faislay
  mereFaislayTitle: string;
  mereFaislaySubtitle: string;
  filterAll: string;
  filterCrop: string;
  filterWater: string;
  filterFertilizer: string;
  filterDisease: string;
  filterMarket: string;
  noDecisionsYet: string;

  // What-If Simulator
  simulatorTitle: string;
  simulatorSubtitle: string;
  compareButton: string;
  waterReductionLabel: string;
  recommendedOptionTitle: string;
  tradeoffsTitle: string;
  assumptionsTitle: string;
  expectedYieldLabel: string;
  waterReqLabel: string;
  waterRiskLabel: string;
  overallRiskLabel: string;

  // Disease Doctor
  diseaseTitle: string;
  diseaseSubtitle: string;
  uploadPhotoPrompt: string;
  takePhotoBtn: string;
  analyzingState: string;
  organicControlTitle: string;
  chemicalControlTitle: string;
  dosageWarning: string;
  lowConfidenceWarning: string;
  requestClearerPhoto: string;

  // Ask Question Dialog
  askTitle: string;
  askPlaceholder: string;
  submitQuestionBtn: string;
  sampleQ1: string;
  sampleQ2: string;
  sampleQ3: string;
}

export const translations: Record<LanguageCode, Translations> = {
  ur: {
    appName: "کسان دوست",
    tagline: "حقیقی شواہد پر مبنی زرعی مشاورتی نظام",
    homeTab: "آج کا فارم",
    chatTab: "زرعی چیٹ",
    faislayTab: "میرے فیصلے",
    simulatorTab: "اگر میں...",
    passportTab: "فارم پاسپورٹ",
    toolsTab: "زرعی اوزار",
    chatTitle: "کسان دوست لائیو چیٹ بوٹ",
    chatSubtitle: "اوپن اے آئی ایجنٹس سے براہ راست منسلک",
    agentThinking: "ایجنٹس تحقیق کر رہے ہیں...",

    liveStatus: "براہِ راست (لائیو)",
    cachedStatus: "محفوظ شدہ ڈیٹا",
    offlineStatus: "آف لائن ریکارڈ",
    acresLabel: "ایکڑ",
    districtLabel: "ضلع",

    welcomeTitle: "کسان دوست میں خوش آمدید",
    welcomeSubtitle: "صرف 5 آسان سوالات میں اپنے فارم کا احوال بتائیں",
    startBtn: "شروع کریں",
    notSureBtn: "معلوم نہیں (بعد میں بتائیں)",
    nextBtn: "اگلا قدم",
    backBtn: "پیچھے",
    finishSetupBtn: "فارم بریف دیکھیں",
    stepNameTitle: "کسان کا نام اور شناختی معلومات",
    stepNameDesc: "ذاتی کسان پاسپورٹ اور ریکارڈ کے لیے اپنا نام درج کریں",
    nameLabel: "کسان کا پورا نام",
    namePlaceholder: "مثلاً چوہدری احمد، ملک فاروق...",
    phoneLabel: "موبائل نمبر (اختیاری)",
    phonePlaceholder: "0300-1234567",
    stepLocationTitle: "آپ کی زمین کس ضلع میں ہے؟",
    stepLocationDesc: "موسم اور منڈی کے ریٹ جاننے کے لیے اپنا علاقہ منتخب کریں",
    stepAcreageTitle: "آپ کے پاس کتنے ایکڑ رقبہ ہے؟",
    stepAcreageDesc: "کھاد، بیج اور پانی کے درست حساب کے لیے رقبہ بتائیں",
    stepWaterTitle: "پانی کا کیا ذریعہ اور صورتحال ہے؟",
    stepWaterDesc: "نہری باری، ٹیوب ویل یا بارش پر انحصار؟",
    stepCropTitle: "ابھی کونسی فصل زیرِ غور ہے؟",
    stepCropDesc: "اس سیزن میں آپ کیا کاشت کرنا چاہتے ہیں؟",
    stepLanguageTitle: "کس زبان میں رہنمائی چاہتے ہیں؟",
    stepLanguageDesc: "اردو، رومن اردو یا انگریزی",

    aajKaBrief: "آج کا فارم خلاصہ",
    allNormalTitle: "سب نارمل ہے — فصل کی حالت اطمینان بخش",
    allNormalDesc: "موسم اور منڈی مستحکم ہیں۔ اگلے 4 دن تک معمول کے مطابق نگرانی رکھیں۔",
    waterAlertTitle: "پانی کی باری کا وقت قریب ہے",
    waterAlertDesc: "اگلے 48 گھنٹوں میں نہری پانی کی باری متوقع ہے۔ کھیت کی نالیوں کا جائزہ لیں۔",
    weatherAlertTitle: "موسمی تغیر کا الرٹ",
    weatherAlertDesc: "آنے والے دنوں میں درجہ حرارت میں اضافہ متوقع ہے۔",
    mandiAlertTitle: "منڈی میں منصفانہ ریٹ کا موقع",
    mandiAlertDesc: "غلہ منڈی میں گندم کی اوسط قیمت 3,950 روپے فی من تک پہنچ گئی ہے۔",

    healthScoreTitle: "فارم ہیلتھ انڈیکس",
    waterStatusTitle: "پانی کی باری",
    weatherTitle: "آج کا موسم",
    mandiRateTitle: "آج کا منڈی بھاؤ",
    turnsUnit: "باریاں دستیاب",
    maundUnit: "روپے فی من",

    actionDiseasePhoto: "فصل کی بیماری کی تصویر",
    actionDiseasePhotoSub: "پتوں کی تصویر لیں اور تصدیق شدہ علاج جانیں",
    actionCropAdvisor: "فصل کا انتخاب اور مشورہ",
    actionCropAdvisorSub: "زمین اور موسم کے مطابق موزوں ترین بیج",
    actionIrrigation: "پانی اور آبپاشی کا حساب",
    actionIrrigationSub: "کب اور کتنا پانی لگانا ہے؟",
    actionMandi: "منڈی کے ریٹ اور فروخت",
    actionMandiSub: "قریبی منڈیوں کے بھاؤ اور درست وقت",
    actionSimulator: "اگر میں دوسری فصل لگاؤں؟",
    actionSimulatorSub: "گندم، چنا اور کینولا کا منافع اور پانی موازنہ",
    actionGovtSupport: "سرکاری اسکیمیں و کسان کارڈ",
    actionGovtSupportSub: "بلاسود قرض اور سبسڈی کے لیے اہلیت",
    actionAskQuestion: "سوال پوچھیں",
    actionAskQuestionSub: "کھاد، اسپرے یا فصل کے بارے میں براہِ راست سوال",

    receiptHeader: "فیصلے کی رسید",
    receiptIdLabel: "رسید نمبر",
    kyunTitle: "یہ فیصلہ کیوں؟ (وجوہات)",
    impactTitle: "متوقع پیداواری فائدہ",
    financialTitle: "مالی حساب کتاب",
    costLabel: "کل لاگت",
    revenueLabel: "متوقع آمدنی",
    netProfitLabel: "خالص منافع",
    confidenceLabel: "تصدیقی اعتماد",
    actionStepsTitle: "عملی اقدامات",
    saveDecisionBtn: "فیصلہ محفوظ کریں",
    savedToast: "فیصلہ کامیابی سے محفوظ ہوگیا!",
    closeBtn: "بند کریں",

    mereFaislayTitle: "میرے محفوظ فیصلے",
    mereFaislaySubtitle: "تمام ماضی کی تصدیقی رسیدیں اور مشورے",
    filterAll: "سب",
    filterCrop: "فصل",
    filterWater: "پانی",
    filterFertilizer: "کھاد",
    filterDisease: "بیماری",
    filterMarket: "منڈی",
    noDecisionsYet: "ابھی تک کوئی فیصلہ محفوظ نہیں کیا گیا۔",

    simulatorTitle: "فارم فیصلہ سمیلیٹر (اگر میں...)",
    simulatorSubtitle: "مختلف فصلوں کا پانی، خرچ، منافع اور رسک موازنہ",
    compareButton: "موازنہ دوبارہ کریں",
    waterReductionLabel: "پانی کی کمی کا فرضی منظرنامہ",
    recommendedOptionTitle: "بہترین انتخاب",
    tradeoffsTitle: "کھلے تضادات اور حقائق",
    assumptionsTitle: "حساب کے بنیادی مفروضات",
    expectedYieldLabel: "متوقع پیداوار",
    waterReqLabel: "پانی کی ضرورت",
    waterRiskLabel: "پانی کا خطرہ",
    overallRiskLabel: "مجموعی رسک",

    diseaseTitle: "فصل کا ڈاکٹر (تصویر سے بیماری کی تشخیص)",
    diseaseSubtitle: "پتے کی تصویر اپلوڈ کریں اور محکمہ زراعت کے رجسٹرڈ حل حاصل کریں",
    uploadPhotoPrompt: "متاثرہ پتے کی واضح تصویر منتخب کریں",
    takePhotoBtn: "تصویر لیں یا گیلری سے چنیں",
    analyzingState: "پتوں کی علامات کا تفصیلی معائنہ جاری ہے...",
    organicControlTitle: "قدرتی و دیسی طریقہ علاج",
    chemicalControlTitle: "محکمہ زراعت سے تصدیق شدہ اسپرے",
    dosageWarning: "وارننگ: تجویز کردہ مقدار سے ہرگز زیادہ نہ ڈالیں!",
    lowConfidenceWarning: "تشخیص غیر حتمی ہے (اعتماد 70٪ سے کم)۔ براہِ مہربانی دن کی روشنی میں مزید قریب سے تصویر لیں۔",
    requestClearerPhoto: "دن کی روشنی میں زیادہ واضح تصویر درکار ہے",

    askTitle: "فارم کا سوال پوچھیں",
    askPlaceholder: "مثلاً: 5 ایکڑ پر ڈی اے پی کب ڈالوں؟ یا کونسی گندم بہتر ہے؟",
    submitQuestionBtn: "مشورہ حاصل کریں",
    sampleQ1: "5 ایکڑ گندم کے لیے کھاد کا درست پلان کیا ہے؟",
    sampleQ2: "اگر نہری پانی صرف 2 بار ملے تو کیا لگاؤں؟",
    sampleQ3: "سفید مکھی کے خاتمے کا تصدیق شدہ اسپرے بتائیں"
  },

  roman_urdu: {
    appName: "Kisan Dost",
    tagline: "Saboot aur Haqaiq Par Mabni Zarai Faisla Engine",
    homeTab: "Aaj Ka Farm",
    chatTab: "Zarai Chat",
    faislayTab: "Mere Faislay",
    simulatorTab: "Agar Main...",
    passportTab: "Farm Passport",
    toolsTab: "Zarai Tools",
    chatTitle: "Kisan Dost Live ChatBot",
    chatSubtitle: "OpenAI Agents SDK network se direct connected",
    agentThinking: "Specialist Agents tehqeeq kar rahe hain...",

    liveStatus: "LIVE Data",
    cachedStatus: "CACHED Data",
    offlineStatus: "OFFLINE Record",
    acresLabel: "Acre",
    districtLabel: "Zila",

    welcomeTitle: "Kisan Dost mein Khushamdeed",
    welcomeSubtitle: "Sirf 5 aasan sawalon mein apne farm ki maloomat darj karein",
    startBtn: "Shuroo Karein",
    notSureBtn: "Maloom Nahi (Skip karein)",
    nextBtn: "Agla Qadam",
    backBtn: "Peechay",
    finishSetupBtn: "Farm Brief Dekhein",
    stepNameTitle: "Kisan Ka Naam aur Shanakht",
    stepNameDesc: "Apne zaati Farm Passport aur record ke liye apna naam darj karein",
    nameLabel: "Kisan Ka Pura Naam",
    namePlaceholder: "Maslan: Chaudhry Ahmad, Malik Farooq...",
    phoneLabel: "Mobile Number (Ikhtiari)",
    phonePlaceholder: "0300-1234567",
    stepLocationTitle: "Aap ki zameen kis zila mein hai?",
    stepLocationDesc: "Mausam aur mandi rates ke liye apna ilaaqa chunein",
    stepAcreageTitle: "Aap ke paas kul kitne acre zameen hai?",
    stepAcreageDesc: "Khad, beej aur pani ke hisab ke liye raqba zaroori hai",
    stepWaterTitle: "Pani ki kya surat-e-haal hai?",
    stepWaterDesc: "Nehri turns, tubewell ya sirf barani?",
    stepCropTitle: "Abhi konsi fasal lagana chahte hain?",
    stepCropDesc: "Rabi ya Kharif mein konsi fasal zer-e-ghor hai?",
    stepLanguageTitle: "Aap kis zaban mein baat karna chahte hain?",
    stepLanguageDesc: "Urdu Nastaliq, Roman Urdu ya English",

    aajKaBrief: "Aaj Ka Farm Brief",
    allNormalTitle: "Sab Theek Hai — Fasal Ki Halat Behtar",
    allNormalDesc: "Mausam aur mandi mustahkam hain. Aglay 4 din mamool ki nigrani karein.",
    waterAlertTitle: "Pani Ki Turn Ka Waqt Qareeb Hai",
    waterAlertDesc: "Aglay 48 ghanton mein nehri turn mutawaqqe hai. Nalian check karein.",
    weatherAlertTitle: "Mausam Ka Alert",
    weatherAlertDesc: "Aane walay dino mein dhoop aur darja-e-hararat mein izafa hoga.",
    mandiAlertTitle: "Mandi Mein Acha Rate",
    mandiAlertDesc: "Multan Ghalla Mandi mein gandum ka modal rate PKR 3,950/maund hai.",

    healthScoreTitle: "Farm Health Index",
    waterStatusTitle: "Pani Ki Turn",
    weatherTitle: "Aaj Ka Mausam",
    mandiRateTitle: "Mandi Rate",
    turnsUnit: "Turns Available",
    maundUnit: "PKR / Maund",

    actionDiseasePhoto: "Fasal Ki Bimari / Photo",
    actionDiseasePhotoSub: "Pattay ki photo lein aur verified ilaj janein",
    actionCropAdvisor: "Fasal Ka Mashwara",
    actionCropAdvisorSub: "Mitti aur pani ke mutabiq behtareen fasal",
    actionIrrigation: "Pani Aur Aabbashi",
    actionIrrigationSub: "Kab aur kitna pani lagana hai?",
    actionMandi: "Mandi Rates Aur Bechna",
    actionMandiSub: "Nearby mandis ke bhhao aur best time",
    actionSimulator: "Agar Main Doosri Fasal Lagaoon?",
    actionSimulatorSub: "Gandum vs Channa vs Canola ka munafa aur water risk",
    actionGovtSupport: "Sarkari Subsidies & Kisan Card",
    actionGovtSupportSub: "Interest-free loan aur subsidy ki eligibility",
    actionAskQuestion: "Sawal Poochein",
    actionAskQuestionSub: "Khad, spray ya fasal ke bare mein seedha sawal",

    receiptHeader: "Faislay Ki Raseed",
    receiptIdLabel: "Receipt ID",
    kyunTitle: "Yeh Faisla Kyun? (Wajohat)",
    impactTitle: "Mutawaqqe Faiyda",
    financialTitle: "Mali Hisab Kitab",
    costLabel: "Kul Kharcha",
    revenueLabel: "Mutawaqqe Aamdani",
    netProfitLabel: "Khalis Munafa",
    confidenceLabel: "Tasdeeqi Aitemad",
    actionStepsTitle: "Amli Aqdamaat",
    saveDecisionBtn: "Raseed Save Karein",
    savedToast: "Raseed 'Mere Faislay' mein save ho gayi!",
    closeBtn: "Band Karein",

    mereFaislayTitle: "Mere Faislay",
    mereFaislaySubtitle: "Aap ke tamam mehfooz shuda faislay aur raseedain",
    filterAll: "All",
    filterCrop: "Fasal",
    filterWater: "Pani",
    filterFertilizer: "Khad",
    filterDisease: "Bimari",
    filterMarket: "Mandi",
    noDecisionsYet: "Abhi tak koi faisla save nahi kiya gaya.",

    simulatorTitle: "What-If Farm Decision Simulator",
    simulatorSubtitle: "Faslon ka pani, kharcha, munafa aur risk compare karein",
    compareButton: "Dubara Compare Karein",
    waterReductionLabel: "Pani Ki Kami Ka Scenario",
    recommendedOptionTitle: "Behtareen Choice",
    tradeoffsTitle: "Trade-offs aur Haqaiq",
    assumptionsTitle: "Bunyadi Assumptions",
    expectedYieldLabel: "Expected Yield",
    waterReqLabel: "Pani Zaroorat",
    waterRiskLabel: "Water Risk",
    overallRiskLabel: "Overall Risk",

    diseaseTitle: "Pest Doctor (Photo Disease Diagnosis)",
    diseaseSubtitle: "Pattay ki photo upload karein aur verified ilaj payein",
    uploadPhotoPrompt: "Bimar pattay ki saaf photo select karein",
    takePhotoBtn: "Photo Lein / Upload Karein",
    analyzingState: "Pattay ki alamaton ka analysis ho raha hai...",
    organicControlTitle: "Desi / Organic Tareeqa",
    chemicalControlTitle: "Verified Chemical Spray",
    dosageWarning: "WARNING: Label limit se zyada dosage hargiz mat dalein!",
    lowConfidenceWarning: "Tashkhees ghair-hatmi hai (Confidence < 70%). Din ki roshni mein mazeed qareeb se photo lein.",
    requestClearerPhoto: "Saaf aur qareeb se photo required hai",

    askTitle: "Farm Ka Sawal Poochein",
    askPlaceholder: "Jaise: 5 acre par DAP kitni daloon? Ya Chickpea kaisa rahega?",
    submitQuestionBtn: "Mashwara Hasil Karein",
    sampleQ1: "5 acre Gandum ke liye balanced khad plan kya hai?",
    sampleQ2: "Agar nehri pani sirf 2 baar mile to kya lagaoon?",
    sampleQ3: "Whitefly ke khatmay ke liye safe spray konsa hai?"
  },

  en: {
    appName: "Kisan Dost",
    tagline: "Evidence-Grounded Agronomy Advisory & Farm Decision Engine",
    homeTab: "Farm Brief",
    chatTab: "Agri Chat",
    faislayTab: "My Decisions",
    simulatorTab: "What-If Simulator",
    passportTab: "Farm Passport",
    toolsTab: "Agri Tools",
    chatTitle: "Kisan Dost Live ChatBot",
    chatSubtitle: "Connected to OpenAI Agents SDK Multi-Agent Network",
    agentThinking: "Specialist agents are investigating...",

    liveStatus: "LIVE Data",
    cachedStatus: "CACHED Data",
    offlineStatus: "OFFLINE Record",
    acresLabel: "Acres",
    districtLabel: "District",

    welcomeTitle: "Welcome to Kisan Dost",
    welcomeSubtitle: "Set up your farm profile in 5 simple questions",
    startBtn: "Get Started",
    notSureBtn: "Not Sure (Skip)",
    nextBtn: "Next",
    backBtn: "Back",
    finishSetupBtn: "View Farm Brief",
    stepNameTitle: "Farmer Name & Identity",
    stepNameDesc: "Enter your full name for your personalized Farm Passport and records",
    nameLabel: "Farmer Full Name",
    namePlaceholder: "e.g. Chaudhry Ahmad, Malik Farooq...",
    phoneLabel: "Mobile Number (Optional)",
    phonePlaceholder: "0300-1234567",
    stepLocationTitle: "Which district is your land in?",
    stepLocationDesc: "Used to fetch local weather forecasts and regional mandi rates",
    stepAcreageTitle: "How much land do you cultivate?",
    stepAcreageDesc: "Required to accurately compute fertilizer bags and irrigation depth",
    stepWaterTitle: "What is your primary irrigation source?",
    stepWaterDesc: "Canal turns, tubewell, or rainfed (Barani)?",
    stepCropTitle: "Which crop are you currently planning?",
    stepCropDesc: "Wheat, Cotton, Rice, Maize, Potato, Canola, or Chickpea?",
    stepLanguageTitle: "Select your preferred language",
    stepLanguageDesc: "Urdu Nastaliq, Roman Urdu, or English",

    aajKaBrief: "Today's Farm Brief",
    allNormalTitle: "All Clear — Crop Status Stable",
    allNormalDesc: "Weather and wholesale market prices are stable. Continue standard field scouting.",
    waterAlertTitle: "Irrigation Turn Window Approaching",
    waterAlertDesc: "Canal water turn scheduled within 48 hours. Inspect watercourses.",
    weatherAlertTitle: "Weather Advisory",
    weatherAlertDesc: "Elevated temperature trend expected over the next 72 hours.",
    mandiAlertTitle: "Favorable Wholesale Market Price",
    mandiAlertDesc: "Multan wholesale wheat benchmark rate is PKR 3,950 per maund.",

    healthScoreTitle: "Farm Health Index",
    waterStatusTitle: "Water Quota",
    weatherTitle: "Local Weather",
    mandiRateTitle: "Mandi Price",
    turnsUnit: "Turns Remaining",
    maundUnit: "PKR / Maund",

    actionDiseasePhoto: "Plant Pathology / Photo",
    actionDiseasePhotoSub: "Snap leaf photo for verified diagnosis and dosage",
    actionCropAdvisor: "Crop Recommendation",
    actionCropAdvisorSub: "Best crop varieties for your soil and water",
    actionIrrigation: "Irrigation Scheduling",
    actionIrrigationSub: "FAO-56 water requirements and timing",
    actionMandi: "Mandi Prices & Selling Timing",
    actionMandiSub: "Regional prices and storage vs immediate sale advice",
    actionSimulator: "What-If Crop Simulator",
    actionSimulatorSub: "Compare Wheat vs Chickpea vs Canola trade-offs",
    actionGovtSupport: "Govt Subsidies & Kisan Card",
    actionGovtSupportSub: "Eligibility check for interest-free loans",
    actionAskQuestion: "Ask Farm Question",
    actionAskQuestionSub: "Get a grounded Decision Receipt for any query",

    receiptHeader: "Decision Receipt",
    receiptIdLabel: "Receipt ID",
    kyunTitle: "Why This Recommendation? (Key Factors)",
    impactTitle: "Expected Impact",
    financialTitle: "Financial Economics",
    costLabel: "Total Cost",
    revenueLabel: "Expected Revenue",
    netProfitLabel: "Net Profit",
    confidenceLabel: "Confidence",
    actionStepsTitle: "Actionable Steps",
    saveDecisionBtn: "Save Decision",
    savedToast: "Decision saved to 'My Decisions'!",
    closeBtn: "Close",

    mereFaislayTitle: "My Saved Decisions",
    mereFaislaySubtitle: "Complete chronological history of verified Decision Receipts",
    filterAll: "All",
    filterCrop: "Crop",
    filterWater: "Water",
    filterFertilizer: "Fertilizer",
    filterDisease: "Disease",
    filterMarket: "Market",
    noDecisionsYet: "No decision receipts saved yet.",

    simulatorTitle: "Farm Decision Simulator (What-If)",
    simulatorSubtitle: "Compare crop trade-offs under water constraints and input budgets",
    compareButton: "Re-run Comparison",
    waterReductionLabel: "Hypothetical Water Reduction",
    recommendedOptionTitle: "Recommended Choice",
    tradeoffsTitle: "Explicit Trade-Offs",
    assumptionsTitle: "Underlying Assumptions",
    expectedYieldLabel: "Expected Yield",
    waterReqLabel: "Water Need",
    waterRiskLabel: "Water Risk",
    overallRiskLabel: "Overall Risk",

    diseaseTitle: "Plant Pathology Doctor",
    diseaseSubtitle: "Upload a leaf photo for department-verified diagnosis and safe dosage limits",
    uploadPhotoPrompt: "Select a clear photo of the affected leaf",
    takePhotoBtn: "Select Photo / Camera",
    analyzingState: "Analyzing leaf visual pathology patterns...",
    organicControlTitle: "Bio-Security & Organic Protocol",
    chemicalControlTitle: "Department Verified Chemical Treatment",
    dosageWarning: "WARNING: Strict label limits apply. Never guess dosage for unverified chemicals.",
    lowConfidenceWarning: "Diagnosis uncertain (Confidence < 70%). Please provide a closer photo in daylight.",
    requestClearerPhoto: "Clear daylight photo required",

    askTitle: "Ask a Farm Decision Question",
    askPlaceholder: "e.g. 5 acres in Multan with limited water, what should I plant?",
    submitQuestionBtn: "Generate Decision Receipt",
    sampleQ1: "What is the optimal fertilizer schedule for 5 acres Wheat?",
    sampleQ2: "What if I only have 2 canal turns this Rabi season?",
    sampleQ3: "Safe verified chemical treatment for Whitefly on cotton"
  }
};
