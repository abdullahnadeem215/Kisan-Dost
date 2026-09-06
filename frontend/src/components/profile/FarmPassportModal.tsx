import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { X, Save, User, MapPin, Sprout, Droplets, CheckCircle2 } from 'lucide-react';

interface FarmPassportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const FarmPassportModal: React.FC<FarmPassportModalProps> = ({ isOpen, onClose }) => {
  const { t } = useLanguage();
  const { profile, updateProfile } = useFarm();

  const [formData, setFormData] = useState({
    name: profile.name || 'Chaudhry Ahmad',
    phone_number: profile.phone_number || '0300-1234567',
    district: profile.district || 'Multan',
    tehsil: profile.tehsil || 'Multan Saddar',
    total_land_acres: profile.total_land_acres || 5.0,
    soil_type: profile.soil_type || 'Loam',
    irrigation_source: profile.irrigation_source || 'Canal + Tubewell',
    primary_crop: profile.primary_crop || 'Wheat',
    kisan_card_holder: profile.kisan_card_holder ?? true,
    available_water_turns: profile.available_water_turns ?? 2
  });

  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateProfile(formData);
      setSavedSuccess(true);
      setTimeout(() => {
        setSavedSuccess(false);
        onClose();
      }, 700);
    } catch (err) {
      console.warn('Error saving passport:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-ajrak-black/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-earth-ground border border-earth-border rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto p-5 shadow-xl space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-earth-border">
          <div className="flex items-center gap-2">
            <span className="text-xl">📋</span>
            <div>
              <h3 className="font-bold text-base text-ajrak-black">Farm Passport (کسان پاسپورٹ)</h3>
              <span className="text-[11px] text-earth-muted font-mono">{profile.farmer_id} • SQLite Persistent</span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-earth-surface text-earth-muted">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Completeness Badge */}
        <div className="bg-wheat-tint border border-wheat-border rounded-xl p-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-wheat-dark" />
            <span className="text-xs font-bold text-ajrak-black">Profile Completeness</span>
          </div>
          <span className="text-sm font-bold text-wheat-dark num-tabular">
            {profile.completeness_percent || 92}%
          </span>
        </div>

        {/* Fields Form */}
        <div className="space-y-3 text-xs">
          <div>
            <label className="font-bold text-earth-dark block mb-1">Farmer Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(p => ({ ...p, name: e.target.value }))}
              className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 font-medium text-ajrak-black focus:border-wheat-gold"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="font-bold text-earth-dark block mb-1">District (Zila)</label>
              <input
                type="text"
                value={formData.district}
                onChange={(e) => setFormData(p => ({ ...p, district: e.target.value }))}
                className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 font-medium text-ajrak-black focus:border-wheat-gold"
              />
            </div>
            <div>
              <label className="font-bold text-earth-dark block mb-1">Tehsil</label>
              <input
                type="text"
                value={formData.tehsil}
                onChange={(e) => setFormData(p => ({ ...p, tehsil: e.target.value }))}
                className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 font-medium text-ajrak-black focus:border-wheat-gold"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="font-bold text-earth-dark block mb-1">Total Acres</label>
              <input
                type="number"
                step="0.5"
                value={formData.total_land_acres}
                onChange={(e) => setFormData(p => ({ ...p, total_land_acres: Number(e.target.value) }))}
                className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 font-bold text-ajrak-black focus:border-wheat-gold"
              />
            </div>
            <div>
              <label className="font-bold text-earth-dark block mb-1">Mitti (Soil Type)</label>
              <select
                value={formData.soil_type}
                onChange={(e) => setFormData(p => ({ ...p, soil_type: e.target.value }))}
                className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 font-bold text-ajrak-black focus:border-wheat-gold"
              >
                <option value="Loam">Loam (Mera)</option>
                <option value="Clay">Clay (Chikni)</option>
                <option value="Sandy">Sandy (Raitli)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="font-bold text-earth-dark block mb-1">Primary Crop</label>
              <input
                type="text"
                value={formData.primary_crop}
                onChange={(e) => setFormData(p => ({ ...p, primary_crop: e.target.value }))}
                className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 font-medium text-ajrak-black focus:border-wheat-gold"
              />
            </div>
            <div>
              <label className="font-bold text-earth-dark block mb-1">Water Turns (Canal)</label>
              <input
                type="number"
                value={formData.available_water_turns}
                onChange={(e) => setFormData(p => ({ ...p, available_water_turns: Number(e.target.value) }))}
                className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 font-bold text-ajrak-black focus:border-wheat-gold"
              />
            </div>
          </div>

          <div className="pt-2">
            <label className="flex items-center gap-2 font-bold text-earth-dark cursor-pointer">
              <input
                type="checkbox"
                checked={formData.kisan_card_holder}
                onChange={(e) => setFormData(p => ({ ...p, kisan_card_holder: e.target.checked }))}
                className="w-4 h-4 accent-wheat-gold rounded"
              />
              <span>Punjab Kisan Card Holder (Active)</span>
            </label>
          </div>
        </div>

        {/* Buttons */}
        <div className="pt-3 border-t border-earth-border flex gap-2">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex-1 py-3 px-4 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white font-bold text-xs flex items-center justify-center gap-2 shadow-xs transition-all"
          >
            <Save className="w-4 h-4" />
            <span>{savedSuccess ? 'Saved to SQLite!' : 'Save Farm Passport'}</span>
          </button>
          <button
            onClick={onClose}
            className="py-3 px-4 rounded-xl border border-earth-border bg-white text-earth-dark text-xs font-semibold hover:bg-earth-surface"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
