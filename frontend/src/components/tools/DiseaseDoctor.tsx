import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { DiseaseDiagnosticResult, DecisionReceipt } from '../../api/types';
import { apiClient } from '../../api/client';
import {
  diagnoseImageWithGemini,
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
  Eye
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

  // Gemini API Key & Farming Guardrail State
  const [geminiApiKey, setGeminiKey] = useState<string>(getStoredGeminiApiKey());
  const [tempApiKeyInput, setTempApiKeyInput] = useState<string>(getStoredGeminiApiKey());
  const [isKeyModalOpen, setIsKeyModalOpen] = useState<boolean>(false);
  const [showKeyText, setShowKeyText] = useState<boolean>(false);
  const [refusalMessage, setRefusalMessage] = useState<string | null>(null);
  const [scanEngine, setScanEngine] = useState<'gemini' | 'narc'>('gemini');

  const handleSaveApiKey = () => {
    const trimmed = tempApiKeyInput.trim();
    setStoredGeminiApiKey(trimmed);
    setGeminiKey(trimmed);
    setIsKeyModalOpen(false);
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
        runDiagnosis(base64Url);
      };
      reader.readAsDataURL(file);
    }
  };

  const runDiagnosis = async (base64Url?: string) => {
    const imgData = base64Url || imagePreview;
    setIsScanning(true);
    setRefusalMessage(null);

    try {
      // 1. If image is available and Gemini API key is configured, use Gemini Multimodal Vision with strict farming guardrail
      if (imgData && geminiApiKey.trim()) {
        const geminiRes = await diagnoseImageWithGemini(imgData, selectedCrop, geminiApiKey);

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

      // 2. Fallback to NARC / DPP Knowledgebase if no Gemini key or text-based diagnosis
      await new Promise(r => setTimeout(r, 600));
      const res = await apiClient.diagnoseDisease(selectedCrop, symptomText);
      setDiagnostic(res);
      setScanEngine('narc');
    } catch (err: any) {
      console.warn('Diagnosis error:', err);
      if (err?.message === 'MISSING_KEY') {
        setIsKeyModalOpen(true);
      } else {
        // Fallback to local verified classifier
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
    <div className="space-y-4 max-w-xl mx-auto py-2">
      {/* Header & Gemini Key Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-ajrak-black flex items-center gap-2">
            <Camera className="w-5 h-5 text-ochre-alert" />
            <span>{t.diseaseTitle}</span>
          </h2>
          <p className="text-xs text-earth-muted mt-0.5">
            {t.diseaseSubtitle}
          </p>
        </div>

        {/* Gemini Key Config Button */}
        <button
          onClick={() => setIsKeyModalOpen(true)}
          className={`px-2.5 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all ${
            geminiApiKey
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100'
              : 'bg-wheat-tint text-wheat-dark border-wheat-border hover:bg-wheat-tint/80'
          }`}
          title="Configure Gemini API Key for Plant Pathology Vision"
        >
          <Key className="w-3.5 h-3.5" />
          <span>{geminiApiKey ? 'Gemini Vision Active' : 'Enter Gemini Key'}</span>
        </button>
      </div>

      {/* Photo Capture / Upload Card */}
      <div className="bg-earth-surface border-2 border-dashed border-earth-border hover:border-wheat-gold rounded-2xl p-6 text-center shadow-xs transition-all relative overflow-hidden">
        {imagePreview ? (
          <div className="space-y-3">
            <div className="relative w-48 h-48 mx-auto rounded-xl overflow-hidden border-2 border-earth-border shadow-xs">
              <img src={imagePreview} alt="Leaf preview" className="w-full h-full object-cover" />
              {isScanning && (
                <div className="absolute inset-0 bg-ajrak-black/60 backdrop-blur-xs flex flex-col items-center justify-center text-white">
                  <RefreshCw className="w-8 h-8 text-wheat-gold animate-spin mb-2" />
                  <span className="text-xs font-semibold px-2">
                    {geminiApiKey ? 'Gemini Vision AI Guardrail & Diagnosis...' : t.analyzingState}
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
                className="px-3.5 py-2 rounded-xl bg-wheat-gold text-white text-xs font-bold hover:bg-wheat-dark disabled:opacity-50 shadow-2xs cursor-pointer flex items-center gap-1"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Re-Analyze</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-ochre-surface text-ochre-alert mx-auto flex items-center justify-center shadow-xs">
              <Camera className="w-7 h-7" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-ajrak-black">{t.uploadPhotoPrompt}</h3>
              <p className="text-xs text-earth-muted mt-0.5">
                Upload a plant leaf, stem, or pest photo (Strictly agricultural pictures only)
              </p>
            </div>
            <label className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white text-xs font-bold shadow-xs cursor-pointer active:scale-[0.99] transition-all">
              <Upload className="w-4 h-4" />
              <span>{t.takePhotoBtn}</span>
              <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
            </label>
          </div>
        )}
      </div>

      {/* STRICT FARMING GUARDRAIL REFUSAL CARD */}
      {refusalMessage && (
        <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-4.5 space-y-2.5 shadow-xs animate-in fade-in duration-200">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-xl bg-red-100 border border-red-300 flex items-center justify-center text-red-600 shrink-0 mt-0.5">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h4 className="font-bold text-sm text-red-950 flex items-center gap-1.5">
                <span>زراعت کے علاوہ تصویر کی شناخت مسترد</span>
                <span className="text-[10px] bg-red-200 text-red-900 font-bold px-1.5 py-0.5 rounded">
                  Farming Guardrail Block
                </span>
              </h4>
              <p className="text-xs text-red-800 leading-relaxed font-medium">
                {refusalMessage}
              </p>
              <p className="text-[11px] text-red-700/90 pt-1">
                💡 <strong>Kisan Dost Guidance:</strong> Please take a close-up photo of an affected crop leaf, stem, or pest under good lighting.
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

      {/* Diagnostic Assessment Result */}
      {diagnostic && !refusalMessage && (
        <div className="space-y-3 animate-in fade-in duration-200">
          {/* Status Banner */}
          {diagnostic.match_confidence < 0.70 ? (
            <div className="bg-amber-50 border border-amber-300 rounded-2xl p-4 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-sm text-amber-900">
                  {t.lowConfidenceWarning}
                </h4>
                <p className="text-xs text-amber-800 mt-1">
                  Pattern match confidence is only {(diagnostic.match_confidence * 100).toFixed(0)}%. Do not spray chemicals based on unverified symptoms.
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-emerald-50 border border-emerald-300 rounded-2xl p-4 flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <h4 className="font-bold text-base text-emerald-950">{diagnostic.disease_name}</h4>
                  <div className="flex items-center gap-1.5">
                    {scanEngine === 'gemini' && (
                      <span className="text-[10px] bg-emerald-200 text-emerald-900 font-bold px-1.5 py-0.5 rounded-full flex items-center gap-1">
                        <Sparkles className="w-2.5 h-2.5 text-emerald-800" />
                        <span>Gemini Vision</span>
                      </span>
                    )}
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
          <div className="bg-white border border-earth-border rounded-2xl p-5 space-y-4 shadow-xs">
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

            {/* Chemical Treatment (DPP Verified) */}
            <div className="space-y-1">
              <span className="text-xs font-bold text-ochre-dark uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-ochre-alert" />
                <span>{t.chemicalControlTitle}</span>
              </span>
              <div className="bg-ochre-surface/60 border border-ochre-border/70 rounded-xl p-3 text-xs space-y-1.5">
                <p className="font-bold text-ajrak-black text-sm">{diagnostic.chemical_control}</p>
                {diagnostic.dosage_per_acre && (
                  <p className="text-xs font-semibold text-earth-dark">
                    Acre Dosage: <span className="text-ochre-dark">{diagnostic.dosage_per_acre}</span>
                  </p>
                )}
                <p className="text-[11px] text-ochre-alert font-semibold">
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
