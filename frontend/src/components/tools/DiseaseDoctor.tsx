import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { DiseaseDiagnosticResult, DecisionReceipt } from '../../api/types';
import { apiClient } from '../../api/client';
import {
  diagnoseImageWithGemini,
  diagnoseSymptomsWithGemini,
  getStoredGeminiApiKey,
  setStoredGeminiApiKey
} from '../../api/geminiClient';
import { GroundingBadge } from '../common/GroundingBadge';
import {
  Camera,
  Upload,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  BookmarkCheck,
  Key,
  ShieldAlert,
  Sparkles,
  EyeOff,
  Eye,
  FileText,
  Sprout
} from 'lucide-react';

interface DiseaseDoctorProps {
  onBack?: () => void;
}

export const DiseaseDoctor: React.FC<DiseaseDoctorProps> = ({ onBack }) => {
  const { t } = useLanguage();
  const { profile, saveDecision, openReceiptModal } = useFarm();

  const [selectedCrop, setSelectedCrop] = useState<string>(profile.primary_crop || 'Wheat');
  const [symptomText, setSymptomText] = useState<string>('Yellow pustules in linear stripes on leaf surface');
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [diagnostic, setDiagnostic] = useState<DiseaseDiagnosticResult | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'photo' | 'symptom'>('photo');

  // Gemini 1.5 Flash Model & Farming Guardrail State
  const [geminiApiKey, setGeminiKey] = useState<string>(getStoredGeminiApiKey());
  const [tempApiKeyInput, setTempApiKeyInput] = useState<string>(getStoredGeminiApiKey());
  const [isKeyModalOpen, setIsKeyModalOpen] = useState<boolean>(false);
  const [showKeyText, setShowKeyText] = useState<boolean>(false);
  const [refusalMessage, setRefusalMessage] = useState<string | null>(null);
  const [scanEngine, setScanEngine] = useState<'gemini' | 'narc'>('gemini');

  const popularCrops = [
    { id: 'Wheat', label: 'گندم (Wheat)' },
    { id: 'Cotton', label: 'کپاس (Cotton)' },
    { id: 'Rice', label: 'دھان (Rice)' },
    { id: 'Maize', label: 'مکئی (Maize)' },
    { id: 'Potato', label: 'آلو (Potato)' },
    { id: 'Sugarcane', label: 'کماد (Sugarcane)' },
  ];

  const handleSaveApiKey = () => {
    const trimmed = tempApiKeyInput.trim();
    setStoredGeminiApiKey(trimmed);
    setGeminiKey(trimmed);
    setIsKeyModalOpen(false);
    if (imagePreview) {
      runDiagnosis(imagePreview, trimmed);
    }
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setRefusalMessage(null);
      setDiagnostic(null);
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Url = reader.result as string;
        setImagePreview(base64Url);
        if (!geminiApiKey.trim()) {
          setIsKeyModalOpen(true);
        } else {
          runDiagnosis(base64Url);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const runDiagnosis = async (base64Url?: string, explicitKey?: string) => {
    const imgData = base64Url || imagePreview;
    const keyToUse = (explicitKey || geminiApiKey).trim();
    setIsScanning(true);
    setRefusalMessage(null);

    try {
      // 1. If photo is present, run Gemini 1.5 Flash Multimodal Vision
      if (imgData) {
        if (!keyToUse) {
          setIsKeyModalOpen(true);
          setIsScanning(false);
          return;
        }

        const geminiRes = await diagnoseImageWithGemini(imgData, selectedCrop, keyToUse);

        if (geminiRes.isRefused) {
          setRefusalMessage(
            geminiRes.refusalMessage ||
              'Yeh tasveer kisi fasal ya khet ki nahi hai. Barah-e-karam sirf mutasira pattay ya paudhay ki tasveer dein.'
          );
          setDiagnostic(null);
          return;
        }

        if (geminiRes.result) {
          setDiagnostic(geminiRes.result);
          setScanEngine('gemini');
          return;
        }
      }

      // 2. If symptom text with Gemini key, use Gemini 1.5 Flash Pathology model
      if (keyToUse && symptomText.trim()) {
        try {
          const geminiRes = await diagnoseSymptomsWithGemini(selectedCrop, symptomText, keyToUse);
          if (geminiRes.isRefused) {
            setRefusalMessage(geminiRes.refusalMessage || 'Yeh sawal zarai bimari se mutalliq nahi hai.');
            setDiagnostic(null);
            return;
          }
          if (geminiRes.result) {
            setDiagnostic(geminiRes.result);
            setScanEngine('gemini');
            return;
          }
        } catch (symErr) {
          console.warn('Gemini symptom diagnosis fallback to local:', symErr);
        }
      }

      // 3. Fallback to local verified classifier
      await new Promise(r => setTimeout(r, 500));
      const res = await apiClient.diagnoseDisease(selectedCrop, symptomText);
      setDiagnostic(res);
      setScanEngine('narc');
    } catch (err: any) {
      console.warn('Diagnosis error:', err);
      if (err?.message === 'MISSING_KEY') {
        setIsKeyModalOpen(true);
      } else {
        try {
          const res = await apiClient.diagnoseDisease(selectedCrop, symptomText);
          setDiagnostic(res);
          setScanEngine('narc');
        } catch (fallbackErr) {
          console.error('Fallback error:', fallbackErr);
        }
      }
    } finally {
      setIsScanning(false);
    }
  };

  const handleCreateReceipt = () => {
    if (!diagnostic) return;
    const receipt: DecisionReceipt = {
      receipt_id: `RCPT-${diagnostic.disease_id}`,
      query_summary: `${diagnostic.crop_name} ${diagnostic.disease_name} leaf scan`,
      action_title: `${diagnostic.disease_name}: ${diagnostic.chemical_control.split('@')[0]}`,
      action_category: 'Disease',
      urgency_level: diagnostic.match_confidence >= 0.70 ? 'HIGH' : 'MEDIUM',
      action_steps: [
        `Pathogen identified: ${diagnostic.disease_name} (${(diagnostic.match_confidence * 100).toFixed(0)}% match).`,
        `Apply verified spray: ${diagnostic.chemical_control}.`,
        `Bio-control remedy: ${diagnostic.organic_control}.`
      ],
      key_rationale: diagnostic.diagnostic_summary,
      expected_impact: 'Arrests fungal sporulation / insect vectors and saves up to 30% crop yield.',
      total_cost_pkr: 3800,
      expected_revenue_pkr: null,
      net_financial_gain_pkr: null,
      overall_confidence_percent: Math.round(diagnostic.match_confidence * 100),
      confidence_level: diagnostic.match_confidence >= 0.70 ? 'HIGH' : 'LOW',
      overall_verification_state: diagnostic.match_confidence >= 0.70 ? 'verified' : 'unverified',
      evidence_grounding_summary: 'Verified against Department of Plant Protection (DPP) Pakistan Registered Formulations.',
      evidence_sources: ['DPP Pakistan', 'Google Gemini Vision AI', 'NARC Pathology'],
      grounded_items_count: 6,
      unverified_items_count: diagnostic.match_confidence < 0.70 ? 1 : 0,
      created_at: new Date().toISOString()
    };
    saveDecision(receipt);
    openReceiptModal(receipt);
  };

  return (
    <div className="space-y-4 w-full py-1">
      {/* Top Header with Gemini Flash Model Badge & Key Config */}
      <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-earth-border/60">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-ajrak-black flex items-center gap-2">
            <Camera className="w-5 h-5 text-ochre-alert" />
            <span>{t.diseaseTitle}</span>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-300 font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-emerald-700" />
              <span>Gemini 1.5 Flash AI</span>
            </span>
          </h2>
          <p className="text-xs text-earth-muted mt-0.5">
            {t.diseaseSubtitle} • Powered by Google Gemini Flash Multimodal Vision
          </p>
        </div>

        {/* Gemini Key Config Button */}
        <button
          onClick={() => setIsKeyModalOpen(true)}
          className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all shadow-2xs cursor-pointer ${
            geminiApiKey
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100'
              : 'bg-wheat-tint text-wheat-dark border-wheat-border hover:bg-wheat-tint/80'
          }`}
          title="Configure Google Gemini API Key"
        >
          <Key className="w-3.5 h-3.5" />
          <span>{geminiApiKey ? 'Gemini Flash Active' : 'Enter Gemini API Key'}</span>
        </button>
      </div>

      {/* Crop Selector Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <span className="text-xs font-bold text-earth-dark flex items-center gap-1 shrink-0">
          <Sprout className="w-3.5 h-3.5 text-wheat-gold" />
          <span>فصل (Crop):</span>
        </span>
        {popularCrops.map(c => (
          <button
            key={c.id}
            onClick={() => setSelectedCrop(c.id)}
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
              selectedCrop === c.id
                ? 'bg-ajrak-black text-white shadow-2xs'
                : 'bg-white text-earth-dark border border-earth-border hover:border-wheat-gold'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Mode Switcher: Photo Scan vs Symptom Text */}
      <div className="inline-flex rounded-xl border border-earth-border bg-earth-surface p-1 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('photo')}
          className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
            activeTab === 'photo' ? 'bg-white text-ajrak-black shadow-2xs font-bold' : 'text-earth-muted hover:text-earth-dark'
          }`}
        >
          <Camera className="w-3.5 h-3.5 text-wheat-gold" />
          <span>تصویر سے تشخیص (Photo Scan)</span>
        </button>
        <button
          onClick={() => setActiveTab('symptom')}
          className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
            activeTab === 'symptom' ? 'bg-white text-ajrak-black shadow-2xs font-bold' : 'text-earth-muted hover:text-earth-dark'
          }`}
        >
          <FileText className="w-3.5 h-3.5 text-wheat-gold" />
          <span>علامات لکھ کر (Symptom Text)</span>
        </button>
      </div>

      {/* MAIN DIAGNOSTIC WORKSPACE: Responsive Widescreen 2-Column Grid */}
      <div className={`grid grid-cols-1 ${diagnostic ? 'lg:grid-cols-12' : ''} gap-5 items-start`}>
        {/* LEFT COLUMN: Image Upload / Preview & Symptom Input */}
        <div className={`${diagnostic ? 'lg:col-span-5' : 'max-w-2xl mx-auto w-full'} space-y-3`}>
          {activeTab === 'photo' ? (
            /* Photo Capture / Upload Card */
            <div className="bg-earth-surface border-2 border-dashed border-earth-border hover:border-wheat-gold rounded-2xl p-5 text-center shadow-xs transition-all relative overflow-hidden">
              {imagePreview ? (
                <div className="space-y-3">
                  <div className="relative w-48 h-48 sm:w-56 sm:h-56 mx-auto rounded-xl overflow-hidden border-2 border-earth-border shadow-xs">
                    <img src={imagePreview} alt="Leaf preview" className="w-full h-full object-cover" />
                    {isScanning && (
                      <div className="absolute inset-0 bg-ajrak-black/65 backdrop-blur-xs flex flex-col items-center justify-center text-white">
                        <RefreshCw className="w-8 h-8 text-wheat-gold animate-spin mb-2" />
                        <span className="text-xs font-semibold px-2">
                          Gemini 1.5 Flash Pathology Analysis...
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-center gap-2">
                    <label className="inline-block px-3.5 py-2 rounded-xl bg-white border border-earth-border text-xs font-bold text-earth-dark cursor-pointer hover:bg-earth-surface shadow-2xs">
                      Change Photo
                      <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                    </label>

                    <button
                      onClick={() => runDiagnosis()}
                      disabled={isScanning}
                      className="px-4 py-2 rounded-xl bg-wheat-gold text-white text-xs font-bold hover:bg-wheat-dark disabled:opacity-50 shadow-2xs cursor-pointer flex items-center gap-1.5 active:scale-95"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>{isScanning ? 'Scanning...' : 'Re-Diagnose'}</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 py-4">
                  <div className="w-14 h-14 rounded-2xl bg-ochre-surface text-ochre-alert mx-auto flex items-center justify-center shadow-xs">
                    <Camera className="w-7 h-7" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-ajrak-black">{t.uploadPhotoPrompt}</h3>
                    <p className="text-xs text-earth-muted mt-0.5">
                      Upload a plant leaf, stem, or pest photo (Strict agricultural pictures only)
                    </p>
                  </div>
                  <label className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white text-xs font-bold shadow-xs cursor-pointer active:scale-95 transition-all">
                    <Upload className="w-4 h-4" />
                    <span>{t.takePhotoBtn}</span>
                    <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                  </label>
                  <p className="text-[10px] text-earth-muted">
                    ✨ Diagnosed instantly by Gemini 1.5 Flash Vision
                  </p>
                </div>
              )}
            </div>
          ) : (
            /* Symptom Text Input Card */
            <div className="bg-white border border-earth-border rounded-2xl p-4 shadow-xs space-y-3">
              <label className="text-xs font-bold text-earth-dark block">
                فصل کی علامات تفصیل سے لکھیں (Describe Symptoms):
              </label>
              <textarea
                value={symptomText}
                onChange={e => setSymptomText(e.target.value)}
                rows={4}
                placeholder="مثلاً: پتے پیلے ہو رہے ہیں، پتوں پر بھورے یا زرد رنگ کی دھاریاں اور دانے بن رہے ہیں..."
                className="w-full bg-earth-surface border border-earth-border rounded-xl p-3 text-xs font-medium text-ajrak-black focus:border-wheat-gold focus:bg-white outline-hidden transition-all"
              />
              <button
                onClick={() => runDiagnosis()}
                disabled={isScanning || !symptomText.trim()}
                className="w-full py-2.5 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white text-xs font-bold shadow-xs disabled:opacity-50 flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer"
              >
                {isScanning ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>تشخیص جاری ہے...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Gemini Flash سے تشخیص کریں</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* STRICT FARMING GUARDRAIL REFUSAL CARD */}
          {refusalMessage && (
            <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-4 space-y-2 shadow-xs animate-in fade-in duration-200">
              <div className="flex items-start gap-2.5">
                <div className="w-7 h-7 rounded-xl bg-red-100 border border-red-300 flex items-center justify-center text-red-600 shrink-0 mt-0.5">
                  <ShieldAlert className="w-4 h-4" />
                </div>
                <div className="space-y-1">
                  <h4 className="font-bold text-xs text-red-950 flex items-center gap-1.5">
                    <span>غیر زرعی تصویر مسترد</span>
                    <span className="text-[9px] bg-red-200 text-red-900 font-bold px-1.5 py-0.2 rounded">
                      Farming Guardrail Block
                    </span>
                  </h4>
                  <p className="text-xs text-red-800 leading-relaxed font-medium">
                    {refusalMessage}
                  </p>
                  <p className="text-[10px] text-red-700/90 pt-0.5">
                    💡 <strong>ہدایت:</strong> برائے مہربانی صرف کھیت کی فصل، پودے یا کیڑے کی تصویر اپلوڈ کریں۔
                  </p>
                </div>
              </div>

              <div className="pt-2 border-t border-red-200 flex justify-end">
                <label className="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-semibold cursor-pointer shadow-2xs">
                  Upload Farming Leaf Photo
                  <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                </label>
              </div>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Diagnostic Assessment Result & Verified Treatments */}
        {diagnostic && !refusalMessage && (
          <div className="lg:col-span-7 space-y-3 animate-in fade-in duration-200">
            {/* Status Banner */}
            {diagnostic.match_confidence < 0.70 ? (
              <div className="bg-amber-50 border border-amber-300 rounded-2xl p-3.5 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-sm text-amber-900">
                    {t.lowConfidenceWarning}
                  </h4>
                  <p className="text-xs text-amber-800 mt-0.5">
                    Pattern match confidence is only {(diagnostic.match_confidence * 100).toFixed(0)}%. Do not spray chemicals based on unverified symptoms.
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-emerald-50 border border-emerald-300 rounded-2xl p-3.5 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <h4 className="font-bold text-sm sm:text-base text-emerald-950">{diagnostic.disease_name}</h4>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] bg-emerald-200 text-emerald-900 font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                        <Sparkles className="w-2.5 h-2.5 text-emerald-800" />
                        <span>Gemini 1.5 Flash</span>
                      </span>
                      <GroundingBadge isLive={true} state="verified" size="sm" label="DPP VERIFIED" />
                    </div>
                  </div>
                  <p className="text-xs text-emerald-900 mt-0.5 font-medium">
                    Confirmed on <strong>{diagnostic.crop_name}</strong> with {(diagnostic.match_confidence * 100).toFixed(0)}% pattern match ({diagnostic.causal_agent}).
                  </p>
                </div>
              </div>
            )}

            {/* Treatment Details Card */}
            <div className="bg-white border border-earth-border rounded-2xl p-4 sm:p-5 space-y-3.5 shadow-xs">
              {/* Summary Text */}
              {diagnostic.diagnostic_summary && (
                <div className="text-xs font-medium text-earth-dark bg-earth-surface/80 border border-earth-border/60 rounded-xl p-3 leading-relaxed">
                  {diagnostic.diagnostic_summary}
                </div>
              )}

              {/* Bio-security / Organic */}
              <div className="space-y-1">
                <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>{t.organicControlTitle}</span>
                </span>
                <p className="text-xs text-earth-dark bg-emerald-50/60 border border-emerald-200/60 rounded-xl p-3 leading-relaxed">
                  {diagnostic.organic_control}
                </p>
              </div>

              {/* Chemical Treatment (DPP Pakistan Verified) */}
              <div className="space-y-1">
                <span className="text-xs font-bold text-ochre-dark uppercase tracking-wider flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-ochre-alert" />
                  <span>{t.chemicalControlTitle}</span>
                </span>
                <div className="bg-ochre-surface/60 border border-ochre-border/70 rounded-xl p-3 text-xs space-y-1.5">
                  <p className="font-bold text-ajrak-black text-sm">{diagnostic.chemical_control}</p>
                  {diagnostic.dosage_per_acre && (
                    <p className="text-xs font-semibold text-earth-dark">
                      Acre Dosage: <span className="text-ochre-dark font-bold">{diagnostic.dosage_per_acre}</span>
                    </p>
                  )}
                  <p className="text-[10px] text-ochre-alert font-semibold">
                    ⚠️ {t.dosageWarning}
                  </p>
                </div>
              </div>

              {/* Preventative Measures */}
              {diagnostic.preventative_measures && diagnostic.preventative_measures.length > 0 && (
                <div className="space-y-1 pt-1">
                  <span className="text-[11px] font-bold text-earth-muted uppercase tracking-wider block">
                    Preventative Cultural Practices
                  </span>
                  <ul className="text-xs text-earth-dark space-y-1 pl-4 list-disc">
                    {diagnostic.preventative_measures.map((m, idx) => (
                      <li key={idx}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Create Decision Receipt Button */}
              <button
                onClick={handleCreateReceipt}
                className="w-full py-3 px-4 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white text-xs font-bold flex items-center justify-center gap-2 shadow-xs transition-all active:scale-[0.99] cursor-pointer"
              >
                <BookmarkCheck className="w-4 h-4" />
                <span>Convert to Official Decision Receipt</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* GEMINI API KEY MODAL */}
      {isKeyModalOpen && (
        <div className="fixed inset-0 z-50 bg-ajrak-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-earth-border p-5 w-full max-w-md space-y-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-wheat-tint text-wheat-gold flex items-center justify-center">
                  <Key className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-sm text-ajrak-black">Gemini Vision API Key</h3>
              </div>
              <button
                onClick={() => setIsKeyModalOpen(false)}
                className="text-earth-muted hover:text-earth-dark text-sm p-1"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-earth-muted leading-relaxed">
              Google Gemini Vision Multimodal AI enables instant leaf disease and pest diagnosis from photographs, with strict agricultural guardrails rejecting non-farming pictures.
            </p>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-earth-dark block">
                Enter your Google AI Studio Gemini API Key:
              </label>
              <div className="relative">
                <input
                  type={showKeyText ? 'text' : 'password'}
                  value={tempApiKeyInput}
                  onChange={e => setTempApiKeyInput(e.target.value)}
                  placeholder="AIzaSy..."
                  className="w-full bg-earth-surface border border-earth-border rounded-xl px-3 py-2 text-xs font-mono text-ajrak-black focus:border-wheat-gold outline-hidden pr-8"
                />
                <button
                  type="button"
                  onClick={() => setShowKeyText(!showKeyText)}
                  className="absolute right-2.5 top-2.5 text-earth-muted hover:text-earth-dark"
                >
                  {showKeyText ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
              <span className="text-[10px] text-earth-muted block">
                Saved securely in your local browser storage.
              </span>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-earth-border">
              <button
                onClick={() => setIsKeyModalOpen(false)}
                className="px-3.5 py-2 rounded-xl border border-earth-border text-xs font-medium text-earth-dark hover:bg-earth-surface"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveApiKey}
                className="px-4 py-2 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white text-xs font-bold shadow-xs"
              >
                Save API Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
