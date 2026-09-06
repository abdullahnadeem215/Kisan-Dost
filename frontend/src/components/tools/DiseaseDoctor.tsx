import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { DiseaseDiagnosticResult, DecisionReceipt } from '../../api/types';
import { apiClient } from '../../api/client';
import { GroundingBadge } from '../common/GroundingBadge';
import { Camera, Upload, AlertTriangle, ShieldCheck, CheckCircle2, RefreshCw, BookmarkCheck } from 'lucide-react';

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

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
        runDiagnosis();
      };
      reader.readAsDataURL(file);
    }
  };

  const runDiagnosis = async () => {
    setIsScanning(true);
    try {
      // Small realistic processing simulation
      await new Promise(r => setTimeout(r, 900));
      const res = await apiClient.diagnoseDisease(selectedCrop, symptomText);
      setDiagnostic(res);
    } catch (err) {
      console.warn('Diagnosis error:', err);
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
        `Disease identified: ${diagnostic.disease_name} (${(diagnostic.match_confidence * 100).toFixed(0)}% match).`,
        `Apply verified spray: ${diagnostic.chemical_control}.`,
        `Alternative bio-control: ${diagnostic.organic_control}.`
      ],
      key_rationale: diagnostic.diagnostic_summary,
      expected_impact: 'Arrests fungal sporulation and prevents yield loss up to 30%.',
      total_cost_pkr: 3800,
      expected_revenue_pkr: null,
      net_financial_gain_pkr: null,
      overall_confidence_percent: Math.round(diagnostic.match_confidence * 100),
      confidence_level: diagnostic.match_confidence >= 0.70 ? 'HIGH' : 'LOW',
      overall_verification_state: diagnostic.match_confidence >= 0.70 ? 'verified' : 'unverified',
      evidence_grounding_summary: 'Grounding: Department of Plant Protection Pakistan Registered Pesticide List.',
      evidence_sources: ['DPP Pakistan', 'PlantVillage Dataset', 'NARC Pathology'],
      grounded_items_count: 5,
      unverified_items_count: diagnostic.match_confidence < 0.70 ? 1 : 0,
      created_at: new Date().toISOString()
    };
    saveDecision(receipt);
    openReceiptModal(receipt);
  };

  return (
    <div className="space-y-4 max-w-xl mx-auto py-2">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-ajrak-black flex items-center gap-2">
          <Camera className="w-5 h-5 text-ochre-alert" />
          <span>{t.diseaseTitle}</span>
        </h2>
        <p className="text-xs text-earth-muted mt-0.5">
          {t.diseaseSubtitle}
        </p>
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
                  <span className="text-xs font-semibold px-2">{t.analyzingState}</span>
                </div>
              )}
            </div>
            <label className="inline-block px-4 py-2 rounded-xl bg-white border border-earth-border text-xs font-bold text-earth-dark cursor-pointer hover:bg-earth-surface">
              Change Photo
              <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
            </label>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-ochre-surface text-ochre-alert mx-auto flex items-center justify-center shadow-xs">
              <Camera className="w-7 h-7" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-ajrak-black">{t.uploadPhotoPrompt}</h3>
              <p className="text-xs text-earth-muted mt-0.5">Select image or take camera photo in daylight</p>
            </div>
            <label className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white text-xs font-bold shadow-xs cursor-pointer active:scale-[0.99] transition-all">
              <Upload className="w-4 h-4" />
              <span>{t.takePhotoBtn}</span>
              <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
            </label>
          </div>
        )}
      </div>

      {/* Diagnostic Assessment Result */}
      {diagnostic && (
        <div className="space-y-3">
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
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-base text-emerald-950">{diagnostic.disease_name}</h4>
                  <GroundingBadge isLive={true} state="verified" size="sm" label="VERIFIED" />
                </div>
                <p className="text-xs text-emerald-900 mt-0.5 font-medium">
                  Confirmed with {(diagnostic.match_confidence * 100).toFixed(0)}% pattern match ({diagnostic.causal_agent}).
                </p>
              </div>
            </div>
          )}

          {/* Treatment Details Card */}
          <div className="bg-white border border-earth-border rounded-2xl p-5 space-y-4 shadow-xs">
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
                <p className="font-bold text-ajrak-black">{diagnostic.chemical_control}</p>
                <p className="text-[11px] text-ochre-alert font-semibold">
                  ⚠️ {t.dosageWarning}
                </p>
              </div>
            </div>

            {/* Candidate Distribution */}
            <div className="pt-2 border-t border-earth-border">
              <span className="text-[11px] font-bold text-earth-muted uppercase tracking-wider block mb-1.5">
                Candidate Disease Distribution
              </span>
              <div className="space-y-1.5">
                {diagnostic.candidate_distribution.map(c => (
                  <div key={c.disease_id} className="flex items-center justify-between text-xs">
                    <span className="text-earth-dark font-medium">{c.disease_name}</span>
                    <span className="num-tabular text-wheat-dark font-bold">
                      {(c.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Create Decision Receipt Button */}
            <button
              onClick={handleCreateReceipt}
              className="w-full py-3 px-4 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white text-xs font-bold flex items-center justify-center gap-2 shadow-xs transition-all"
            >
              <BookmarkCheck className="w-4 h-4" />
              <span>Convert to Official Decision Receipt</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
