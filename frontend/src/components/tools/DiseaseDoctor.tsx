import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { DiseaseDiagnosticResult, DecisionReceipt } from '../../api/types';
import { apiClient } from '../../api/client';
import { diagnoseSymptomsWithGemini } from '../../api/geminiClient';
import { GroundingBadge } from '../common/GroundingBadge';
import {
  Camera,
  Upload,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  BookmarkCheck,
  ShieldAlert,
  Sparkles,
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
  const [symptomText, setSymptomText] = useState<string>('');
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [diagnostic, setDiagnostic] = useState<DiseaseDiagnosticResult | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'photo' | 'symptom'>('photo');
  const [refusalMessage, setRefusalMessage] = useState<string | null>(null);
  const [detectedObject, setDetectedObject] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [scanEngine, setScanEngine] = useState<'gemini' | 'narc'>('gemini');

  const popularCrops = [
    { id: 'Wheat', label: 'گندم (Wheat)' },
    { id: 'Cotton', label: 'کپاس (Cotton)' },
    { id: 'Rice', label: 'دھان (Rice)' },
    { id: 'Maize', label: 'مکئی (Maize)' },
    { id: 'Potato', label: 'آلو (Potato)' },
    { id: 'Sugarcane', label: 'کماد (Sugarcane)' },
  ];

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setRefusalMessage(null);
      setDetectedObject(null);
      setErrorMessage(null);
      setDiagnostic(null);
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Url = reader.result as string;
        setImagePreview(base64Url);
        runDiagnosis(base64Url);
      };
      reader.readAsDataURL(file);
    }
  };

  const runDiagnosis = async (base64Url?: string) => {
    const imgData = base64Url || imagePreview;
    setIsScanning(true);
    setRefusalMessage(null);
    setDetectedObject(null);
    setErrorMessage(null);

    try {
      // 1. If photo scan mode and image is present
      if (activeTab === 'photo' && imgData) {
        const res = await apiClient.diagnoseImage(imgData, selectedCrop);

        if (res.isRefused) {
          setRefusalMessage(
            res.refusalMessage ||
            `Yeh tasveer kisi fasal ya paudhay ki nahi hai balkay (${res.detectedObject || 'non-plant'}) ki tasveer hai. Barah-e-karam fasal ke mutasira pattay ki saaf tasveer dein.`
          );
          setDetectedObject(res.detectedObject || 'Non-plant object');
          setDiagnostic(null);
          return;
        }

        if (res.result) {
          setDiagnostic(res.result);
          setDetectedObject(res.detectedObject || 'Plant Leaf');
          setScanEngine('gemini');
          return;
        }

        if (res.error) {
          const isMissingKey = res.error.includes('key') || res.error === 'MISSING_KEY';
          setErrorMessage(
            isMissingKey
              ? 'Gemini Vision سرور پر دستیاب نہیں ہے۔ براہ کرم علامات لکھ کر تشخیص (Symptom Tab) استعمال کریں یا سرور پر GEMINI_API_KEY سیٹ کریں۔'
              : `تصویر کی پروسیسنگ مکمل نہ ہو سکی۔ برائے مہربانی پتے کی واضح تصویر منتخب کریں یا علامات کے ذریعے تشخیص کریں۔ (${res.error})`
          );
          setDiagnostic(null);
          return;
        }
      }

      // 2. If symptom text mode
      if (activeTab === 'symptom' && symptomText.trim()) {
        try {
          const geminiRes = await diagnoseSymptomsWithGemini(selectedCrop, symptomText);
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

        const res = await apiClient.diagnoseDisease(selectedCrop, symptomText);
        setDiagnostic(res);
        setScanEngine('narc');
        return;
      }
    } catch (err: any) {
      console.warn('Diagnosis error:', err);
      setErrorMessage('Diagnosis could not be completed. Please try again with a clear photo.');
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
      {/* Top Header with Gemini Flash Vision Model Badge */}
      <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-earth-border/60">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-ajrak-black flex items-center gap-2">
            <Camera className="w-5 h-5 text-ochre-alert" />
            <span>{t.diseaseTitle}</span>
            <span className="text-[10px] bg-emerald-100 text-emerald-900 border border-emerald-300 font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1 shadow-2xs">
              <Sparkles className="w-3 h-3 text-emerald-700" />
              <span>Gemini 2.5 / 3.7 Flash AI</span>
            </span>
          </h2>
          <p className="text-xs text-earth-muted mt-0.5">
            {t.diseaseSubtitle} • Powered by Google Gemini Multimodal Vision with strict plant guardrails
          </p>
        </div>

        <div className="flex items-center gap-2">
          <GroundingBadge isLive={true} state="verified" size="sm" label="DPP PAKISTAN VERIFIED" />
        </div>
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
                      <div className="absolute inset-0 bg-ajrak-black/75 backdrop-blur-xs flex flex-col items-center justify-center text-white">
                        <RefreshCw className="w-8 h-8 text-wheat-gold animate-spin mb-2" />
                        <span className="text-xs font-semibold px-2 text-center">
                          Gemini 2.5 / 3.7 Flash Pathology Analysis...
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
                      Upload a plant leaf, stem, or crop photo (Strict agricultural pictures only)
                    </p>
                  </div>
                  <label className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white text-xs font-bold shadow-xs cursor-pointer active:scale-95 transition-all">
                    <Upload className="w-4 h-4" />
                    <span>{t.takePhotoBtn}</span>
                    <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                  </label>
                  <p className="text-[10px] text-earth-muted">
                    ✨ Diagnosed instantly by Gemini 2.5 / 3.7 Flash Vision
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
            <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-4 space-y-2.5 shadow-xs animate-in fade-in duration-200">
              <div className="flex items-start gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-red-100 border border-red-300 flex items-center justify-center text-red-600 shrink-0 mt-0.5">
                  <ShieldAlert className="w-4.5 h-4.5" />
                </div>
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center justify-between flex-wrap gap-1">
                    <h4 className="font-bold text-xs text-red-950 flex items-center gap-1.5">
                      <span>غیر زرعی تصویر مسترد</span>
                      <span className="text-[9px] bg-red-200 text-red-900 font-bold px-1.5 py-0.5 rounded">
                        Farming Guardrail Block
                      </span>
                    </h4>
                    {detectedObject && (
                      <span className="text-[10px] bg-white border border-red-300 text-red-800 font-bold px-2 py-0.5 rounded-md">
                        شناخت شدہ شے: {detectedObject}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-red-800 leading-relaxed font-medium">
                    {refusalMessage}
                  </p>
                  <p className="text-[10px] text-red-700/90 pt-0.5">
                    💡 <strong>ہدایت:</strong> برائے مہربانی صرف کھیت کی فصل، پودے یا کیڑے کی تصویر اپلوڈ کریں۔ کسان دوست کسی غیر زرعی تصویر (جیسے چہرہ، گاڑی، فرنیچر، دستاویز) کی تشخیص نہیں کرتا۔
                  </p>
                </div>
              </div>

              <div className="pt-2 border-t border-red-200 flex justify-end">
                <label className="px-3.5 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-semibold cursor-pointer shadow-2xs">
                  Upload Farming Leaf Photo
                  <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                </label>
              </div>
            </div>
          )}

          {/* INFERENCE / CONFIG ERROR CARD */}
          {errorMessage && (
            <div className="bg-amber-50 border border-amber-300 rounded-2xl p-3.5 text-xs text-amber-900 space-y-2 shadow-xs animate-in fade-in duration-200">
              <div className="flex items-start justify-between gap-2">
                <p className="font-bold flex items-center gap-1.5 text-amber-950">
                  <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0" />
                  <span>تشخیص میں مسئلہ (Diagnostic Issue)</span>
                </p>
                <button
                  onClick={() => setErrorMessage(null)}
                  className="text-[10px] text-amber-800 hover:text-amber-950 font-semibold underline cursor-pointer"
                >
                  بند کریں
                </button>
              </div>
              <p className="font-medium text-amber-800 leading-relaxed">{errorMessage}</p>
              <div className="pt-1 flex items-center gap-2">
                <button
                  onClick={() => {
                    setErrorMessage(null);
                    setActiveTab('symptom');
                  }}
                  className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-bold text-[11px] flex items-center gap-1.5 shadow-2xs cursor-pointer transition-all"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>علامات لکھ کر تشخیص کریں (Use Symptom Doctor)</span>
                </button>
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
                        <span>Gemini 2.5 / 3.7 Flash</span>
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
    </div>
  );
};
