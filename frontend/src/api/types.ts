/**
 * Core Data Schemas for Kisan Dost Frontend.
 * Maps 1:1 with backend Pydantic models in app/schemas/.
 */

export interface Evidence {
  source_id: string;
  source_name: string;
  verification_state: 'verified' | 'unverified' | 'fallback' | 'stale' | 'partially_verified';
  citation_url?: string | null;
  observed_timestamp?: string | null;
  validity_window_hours?: number | null;
  methodology_notes?: string | null;
  is_live: boolean;
}

export interface FarmerProfile {
  farmer_id: string;
  name: string;
  phone_number?: string | null;
  district: string;
  tehsil?: string | null;
  agro_climatic_zone: string;
  total_land_acres: number;
  soil_type: string;
  irrigation_source: string;
  current_season: string;
  primary_crop: string;
  preferred_language: 'ur' | 'roman_urdu' | 'en';
  kisan_card_holder: boolean;
  max_budget_limit?: number | null;
  available_water_turns?: number | null;
  completeness_percent?: number;
  uncertain_fields?: string[];
}

export interface DecisionReceipt {
  receipt_id: string;
  query_summary: string;
  action_title: string;
  action_category: string;
  urgency_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  action_steps: string[];
  key_rationale: string;
  expected_impact: string;
  total_cost_pkr?: number | null;
  expected_revenue_pkr?: number | null;
  net_financial_gain_pkr?: number | null;
  overall_confidence_percent: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW' | 'CRITICAL';
  overall_verification_state: 'verified' | 'unverified' | 'fallback' | 'partially_verified';
  evidence_grounding_summary: string;
  evidence_sources: string[];
  grounded_items_count: number;
  unverified_items_count: number;
  created_at?: string;
}

export interface AdvisoryQueryResponse {
  query: string;
  is_safe: boolean;
  refusal_reason?: string | null;
  is_simulation: boolean;
  language_detected: string;
  intents_detected: string[];
  decision?: {
    action_title: string;
    action_category: string;
    action_steps: string[];
    key_rationale: string;
    expected_impact: string;
    confidence_score: number;
    evidence: Evidence[];
  };
  receipt?: DecisionReceipt;
  conflicts_resolved?: Array<{
    conflict_id: string;
    domain: string;
    description: string;
    source_a_name: string;
    source_a_value: string;
    source_b_name: string;
    source_b_value: string;
    resolved_value: string;
    resolution_strategy: string;
    reasoning: string;
  }>;
  trust_report?: {
    trust_score: number;
    trust_level: string;
    is_trusted: boolean;
    data_freshness_status: string;
  };
  risk_assessment?: {
    risk_score: number;
    risk_level: string;
    risk_factors: string[];
  };
  simulation_result?: SimulationResult;
  advisory_text: string;
  advisory_english: string;
  advisory_roman_urdu: string;
  advisory_urdu: string;
  telemetry_steps: string[];
  dashboard_metrics?: {
    category: string;
    title: string;
    source: string;
    verified: boolean;
    metrics: Array<{
      label: string;
      value: string;
      icon?: string;
      subtext?: string;
    }>;
    interactive_tool?: 'mandi' | 'irrigation' | 'disease' | 'crop' | 'govt' | 'whatif' | 'brief' | 'receipt';
    tool_button_label?: string;
  };
}

export interface SimulationOption {
  crop: string;
  expected_yield: string;
  water_requirement: string;
  input_cost: string;
  input_cost_pkr: number;
  estimated_profit: string;
  net_profit_pkr: number;
  water_risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  overall_risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  yield_maunds_per_acre: number;
}

export interface SimulationResult {
  simulation_id: string;
  scenario_name: string;
  land_acres: number;
  water_constraint: string;
  options: SimulationOption[];
  recommended_option: string;
  recommendation_reason: string;
  tradeoffs: string[];
  assumptions: string[];
}

export interface FarmHealthScore {
  farmer_id: string;
  overall_health_score: number;
  health_category: 'EXCELLENT' | 'GOOD' | 'MODERATE' | 'VULNERABLE' | 'CRITICAL';
  score_available: boolean;
  water_subscore: number;
  crop_vigor_subscore: number;
  pest_safety_subscore: number;
  weather_resilience_subscore: number;
  economic_outlook_subscore: number;
  profile_completeness_subscore: number;
  positive_drivers: string[];
  vulnerability_warnings: string[];
  data_gaps: string[];
}

export interface MandiPriceItem {
  commodity: string;
  mandi_name: string;
  district: string;
  min_price_pkr_per_maund: number;
  max_price_pkr_per_maund: number;
  modal_price_pkr_per_maund: number;
  price_trend: 'STABLE' | 'RISING' | 'FALLING';
  status: string;
  is_live: boolean;
}

export interface MandiResponse {
  commodity: string;
  district: string;
  prices: MandiPriceItem[];
  status: string;
  is_live: boolean;
  evidence: Evidence[];
}

export interface DailyWeather {
  date: string;
  temp_max: number;
  temp_min: number;
  precipitation_mm: number;
  humidity: number;
  wind_speed_kmh: number;
  condition: string;
}

export interface WeatherData {
  location: string;
  temperature_c: number;
  temp_max_c: number;
  temp_min_c: number;
  humidity_percent: number;
  precipitation_mm: number;
  wind_speed_kmh: number;
  condition: string;
  et0_mm?: number | null;
  status: string;
  is_live: boolean;
  forecast_5day: DailyWeather[];
}

export interface DiseaseDiagnosticResult {
  crop_name: string;
  disease_id: string;
  disease_name: string;
  causal_agent: string;
  symptoms: string[];
  favorable_conditions: string;
  preventative_measures: string[];
  organic_control: string;
  chemical_control: string;
  dosage_per_acre: string;
  match_confidence: number;
  status: 'CONFIRMED' | 'UNCERTAIN';
  is_uncertain: boolean;
  candidate_distribution: Array<{
    disease_id: string;
    disease_name: string;
    crop_name: string;
    confidence: number;
  }>;
  requires_clearer_image: boolean;
  image_request_message?: string | null;
  diagnostic_summary: string;
  evidence: Evidence[];
}

export interface GovtScheme {
  scheme_id: string;
  scheme_name: string;
  implementing_agency: string;
  target_audience: string;
  financial_benefit: string;
  subsidy_amount_pkr?: number | null;
  key_eligibility: string[];
  required_documents: string[];
  application_link_or_helpline: string;
  status: string;
}

export interface GovtSupportReport {
  district?: string;
  land_acres?: number;
  crop_name?: string;
  eligible_schemes: GovtScheme[];
  ineligible_schemes: Array<{ scheme_name: string; reason: string }>;
  summary: string;
}

export interface IrrigationSchedule {
  crop_name: string;
  growth_stage: string;
  soil_type: string;
  current_moisture_percent: number;
  daily_water_need_mm: number;
  recommended_water_depth_mm: number;
  next_irrigation_date: string;
  irrigation_method: string;
  water_saving_tips?: string | null;
  etc_mm_day: number;
  et0_mm_day: number;
  crop_coefficient_kc: number;
  explicit_assumptions: string[];
}
