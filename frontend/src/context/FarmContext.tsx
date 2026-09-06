import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { FarmerProfile, DecisionReceipt, FarmHealthScore, WeatherData, MandiResponse } from '../api/types';
import { apiClient } from '../api/client';

interface FarmContextType {
  profile: FarmerProfile;
  isSetupComplete: boolean;
  completeSetup: (profileData: Partial<FarmerProfile>) => Promise<void>;
  updateProfile: (profileData: Partial<FarmerProfile>) => Promise<void>;
  healthScore: FarmHealthScore | null;
  weather: WeatherData | null;
  mandi: MandiResponse | null;
  decisions: DecisionReceipt[];
  saveDecision: (receipt: DecisionReceipt) => void;
  activeTab: 'home' | 'chat' | 'faislay' | 'simulator' | 'passport' | 'tools';
  setActiveTab: (tab: 'home' | 'chat' | 'faislay' | 'simulator' | 'passport' | 'tools') => void;
  isRefreshing: boolean;
  refreshFarmData: () => Promise<void>;
  openReceiptModal: (receipt: DecisionReceipt) => void;
  selectedReceipt: DecisionReceipt | null;
  closeReceiptModal: () => void;
}

const DEFAULT_PROFILE: FarmerProfile = {
  farmer_id: 'FARM-001',
  name: 'Chaudhry Ahmad',
  phone_number: '0300-1234567',
  district: 'Multan',
  tehsil: 'Multan Saddar',
  agro_climatic_zone: 'Cotton-Wheat Zone',
  total_land_acres: 5.0,
  soil_type: 'Loam',
  irrigation_source: 'Canal + Tubewell',
  current_season: 'Rabi',
  primary_crop: 'Wheat',
  preferred_language: 'roman_urdu',
  kisan_card_holder: true,
  max_budget_limit: 250000,
  available_water_turns: 2,
  completeness_percent: 92.0
};

const INITIAL_DECISIONS: DecisionReceipt[] = [
  {
    receipt_id: 'RCPT-WHEAT-01',
    query_summary: '5 acre Multan mein Rabi Gandum sowing plan',
    action_title: 'Sow High-Yielding Wheat with 2 Canal Water Turns',
    action_category: 'Crop',
    urgency_level: 'MEDIUM',
    action_steps: [
      'Sow Akbar-19 or Fakhar-e-Bhakkar certified wheat seed at 50kg/acre.',
      'Apply 5.5 bags DAP at sowing time; distribute 8.75 bags Urea in 2 canal water turns.',
      'Maintain strict water schedule aligned with 2 available canal turns.'
    ],
    key_rationale: 'Loam soil moisture retention supports wheat tillering under 2 canal applications with zero tubewell salinity risk.',
    expected_impact: 'Expected yield 40 maunds/acre; projected gross revenue PKR 790,000.',
    total_cost_pkr: 110448,
    expected_revenue_pkr: 790000,
    net_financial_gain_pkr: 679552,
    overall_confidence_percent: 92,
    confidence_level: 'HIGH',
    overall_verification_state: 'verified',
    evidence_grounding_summary: 'Verified against AMIS Punjab Mandi Rates & NARC Agro Recommendations.',
    evidence_sources: ['AMIS Mandi Portal', 'Punjab Agriculture Extension', 'FAO-56 Water Monitor'],
    grounded_items_count: 8,
    unverified_items_count: 0,
    created_at: new Date(Date.now() - 86400000 * 2).toISOString()
  },
  {
    receipt_id: 'RCPT-PEST-02',
    query_summary: 'Whitefly pest control protocol',
    action_title: 'Bio-Security First: Neem Oil / Pyriproxyfen 10EC',
    action_category: 'Disease',
    urgency_level: 'HIGH',
    action_steps: [
      'Field scouting threshold: 5 nymphs per leaf.',
      'Spray organic Neem seed extract (5ml/L) at early detection.',
      'If ETL exceeded, apply verified Pyriproxyfen 10EC @ 500ml/acre. Do not exceed 500ml label limit.'
    ],
    key_rationale: 'Department of Plant Protection verified active ingredient for whitefly vector control without killing beneficial predators.',
    expected_impact: 'Prevents leaf curl transmission and protects up to 35% crop vigor.',
    total_cost_pkr: 4200,
    expected_revenue_pkr: null,
    net_financial_gain_pkr: null,
    overall_confidence_percent: 95,
    confidence_level: 'HIGH',
    overall_verification_state: 'verified',
    evidence_grounding_summary: 'Verified from Department of Plant Protection Pakistan Registered Pesticide List.',
    evidence_sources: ['DPP Pakistan Registry', 'NARC IPM Guidelines'],
    grounded_items_count: 5,
    unverified_items_count: 0,
    created_at: new Date(Date.now() - 86400000 * 5).toISOString()
  }
];

const FarmContext = createContext<FarmContextType | undefined>(undefined);

export const FarmProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [profile, setProfile] = useState<FarmerProfile>(() => {
    const saved = localStorage.getItem('kisan_dost_profile');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* ignore */ }
    }
    return DEFAULT_PROFILE;
  });

  const [isSetupComplete, setIsSetupComplete] = useState<boolean>(() => {
    return localStorage.getItem('kisan_dost_setup_done') === 'true';
  });

  const [healthScore, setHealthScore] = useState<FarmHealthScore | null>(null);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [mandi, setMandi] = useState<MandiResponse | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'home' | 'chat' | 'faislay' | 'simulator' | 'passport' | 'tools'>('home');
  const [selectedReceipt, setSelectedReceipt] = useState<DecisionReceipt | null>(null);

  const [decisions, setDecisions] = useState<DecisionReceipt[]>(() => {
    const saved = localStorage.getItem('kisan_dost_decisions');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* ignore */ }
    }
    return INITIAL_DECISIONS;
  });

  const refreshFarmData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [h, w, m] = await Promise.all([
        apiClient.getFarmHealth(profile.farmer_id),
        apiClient.getWeather(profile.district),
        apiClient.getMandiPrices(profile.primary_crop, profile.district)
      ]);
      setHealthScore(h);
      setWeather(w);
      setMandi(m);
    } catch (err) {
      console.warn('Error refreshing farm data:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, [profile.farmer_id, profile.district, profile.primary_crop]);

  useEffect(() => {
    refreshFarmData();
  }, [refreshFarmData]);

  const completeSetup = async (profileData: Partial<FarmerProfile>) => {
    const updated = { ...profile, ...profileData };
    setProfile(updated);
    setIsSetupComplete(true);
    localStorage.setItem('kisan_dost_profile', JSON.stringify(updated));
    localStorage.setItem('kisan_dost_setup_done', 'true');
    await apiClient.savePassport(updated);
    await refreshFarmData();
  };

  const updateProfile = async (profileData: Partial<FarmerProfile>) => {
    const updated = { ...profile, ...profileData };
    setProfile(updated);
    localStorage.setItem('kisan_dost_profile', JSON.stringify(updated));
    await apiClient.savePassport(updated);
    await refreshFarmData();
  };

  const saveDecision = (receipt: DecisionReceipt) => {
    setDecisions(prev => {
      const updated = [receipt, ...prev.filter(d => d.receipt_id !== receipt.receipt_id)];
      localStorage.setItem('kisan_dost_decisions', JSON.stringify(updated));
      return updated;
    });
  };

  const openReceiptModal = (receipt: DecisionReceipt) => {
    setSelectedReceipt(receipt);
  };

  const closeReceiptModal = () => {
    setSelectedReceipt(null);
  };

  return (
    <FarmContext.Provider
      value={{
        profile,
        isSetupComplete,
        completeSetup,
        updateProfile,
        healthScore,
        weather,
        mandi,
        decisions,
        saveDecision,
        activeTab,
        setActiveTab,
        isRefreshing,
        refreshFarmData,
        openReceiptModal,
        selectedReceipt,
        closeReceiptModal
      }}
    >
      {children}
    </FarmContext.Provider>
  );
};

export const useFarm = () => {
  const context = useContext(FarmContext);
  if (!context) {
    throw new Error('useFarm must be used within a FarmProvider');
  }
  return context;
};
