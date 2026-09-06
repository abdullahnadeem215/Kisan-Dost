import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { LanguageCode } from '../../i18n/translations';
import { User, MapPin, Sprout, Droplets, Globe, Check, ArrowRight, HelpCircle } from 'lucide-react';

interface SetupState {
  name: string;
  phone_number: string;
  district: string;
  total_land_acres: number;
  irrigation_source: string;
  primary_crop: string;
  preferred_language: LanguageCode;
  uncertain_fields: string[];
}

export const ConversationalSetup: React.FC = () => {
  const { t, setLanguage, isRtl } = useLanguage();
  const { completeSetup } = useFarm();

  const [step, setStep] = useState<number>(1);
  const [data, setData] = useState<SetupState>({
    name: 'Chaudhry Ahmad',
    phone_number: '0300-1234567',
    district: 'Multan',
    total_land_acres: 5.0,
    irrigation_source: 'Canal + Tubewell',
    primary_crop: 'Wheat',
    preferred_language: 'roman_urdu',
    uncertain_fields: []
  });

  const popularNames = ['Chaudhry Ahmad', 'Malik Farooq', 'Mian Tariq', 'Haji Rasheed'];

  const districts = [
    { id: 'Multan', nameUrdu: 'ملتان', nameRoman: 'Multan', desc: 'Cotton-Wheat Zone' },
    { id: 'Khanewal', nameUrdu: 'خانیوال', nameRoman: 'Khanewal', desc: 'Central Punjab' },
    { id: 'Lodhran', nameUrdu: 'لودھراں', nameRoman: 'Lodhran', desc: 'South Punjab' },
    { id: 'Faisalabad', nameUrdu: 'فیصل آباد', nameRoman: 'Faisalabad', desc: 'Mixed Cropping' },
    { id: 'Bahawalpur', nameUrdu: 'بہاولپور', nameRoman: 'Bahawalpur', desc: 'Cotton Zone' },
    { id: 'Sargodha', nameUrdu: 'سرگودھا', nameRoman: 'Sargodha', desc: 'Citrus & Wheat' },
    { id: 'Sahiwal', nameUrdu: 'ساہیوال', nameRoman: 'Sahiwal', desc: 'Maize & Potato' },
    { id: 'Rahim Yar Khan', nameUrdu: 'رحیم یار خان', nameRoman: 'Rahim Yar Khan', desc: 'Cotton & Sugarcane' },
  ];

  const acreageOptions = [
    { value: 2.0, label: '1 - 2 Acre', descUrdu: 'چھوٹا کاشتکار', descRoman: 'Smallholder' },
    { value: 5.0, label: '3 - 5 Acre', descUrdu: 'درمیانہ رقبہ', descRoman: 'Medium Farm (Standard)' },
    { value: 10.0, label: '6 - 12 Acre', descUrdu: 'بڑا فارم', descRoman: 'Progressive Farmer' },
    { value: 20.0, label: '15+ Acre', descUrdu: 'وسیع اراضی', descRoman: 'Commercial Scale' },
  ];

  const waterOptions = [
    { id: 'Canal + Tubewell', labelUrdu: 'نہری باری + ٹیوب ویل', labelRoman: 'Canal + Tubewell (Behtar)', turns: 3 },
    { id: 'Canal Only', labelUrdu: 'صرف نہری پانی (محدود باریاں)', labelRoman: 'Canal Only (Limited Turns)', turns: 2 },
    { id: 'Tubewell Only', labelUrdu: 'صرف ٹیوب ویل کا پانی', labelRoman: 'Tubewell Only (Groundwater)', turns: 4 },
    { id: 'Rainfed (Barani)', labelUrdu: 'بارانی (صرف بارش پر انحصار)', labelRoman: 'Rainfed / Barani', turns: 0 },
  ];

  const cropOptions = [
    { id: 'Wheat', nameUrdu: 'گندم', nameRoman: 'Wheat (Gandum)', season: 'Rabi' },
    { id: 'Cotton', nameUrdu: 'کپاس', nameRoman: 'Cotton (Kapas)', season: 'Kharif' },
    { id: 'Rice', nameUrdu: 'دھان / چاول', nameRoman: 'Rice / Basmati', season: 'Kharif' },
    { id: 'Maize', nameUrdu: 'مکئی', nameRoman: 'Maize (Makai)', season: 'Both' },
    { id: 'Potato', nameUrdu: 'آلو', nameRoman: 'Potato (Aalo)', season: 'Rabi' },
    { id: 'Canola', nameUrdu: 'کینولا / رایا', nameRoman: 'Canola (Raye)', season: 'Rabi' },
    { id: 'Chickpea', nameUrdu: 'چنا', nameRoman: 'Chickpea (Channa)', season: 'Rabi' },
  ];

  const handleNext = () => {
    if (step < 6) {
      setStep(step + 1);
    } else {
      completeSetup({
        ...data,
        name: data.name.trim() || 'Chaudhry Ahmad',
        phone_number: data.phone_number.trim() || '0300-1234567',
        available_water_turns: data.irrigation_source === 'Canal Only' ? 2 : (data.irrigation_source === 'Rainfed (Barani)' ? 0 : 3)
      });
    }
  };

  const handleSkip = (fieldName: string) => {
    setData(prev => ({
      ...prev,
      uncertain_fields: [...prev.uncertain_fields, fieldName]
    }));
    handleNext();
  };

  return (
    <div className="min-h-screen bg-earth-ground flex flex-col justify-between p-4 sm:p-6 max-w-lg mx-auto">
      {/* Top Brand & Progress Indicator */}
      <div className="pt-4 pb-2">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🌾</span>
            <span className="font-bold text-lg text-ajrak-black">{t.appName}</span>
          </div>
          <span className="text-xs font-semibold text-wheat-dark px-2.5 py-1 bg-wheat-tint border border-wheat-border rounded-full">
            Step {step} of 6
          </span>
        </div>

        {/* Tactile 6-Bar Step Indicator */}
        <div className="grid grid-cols-6 gap-1.5 h-1.5 w-full bg-earth-border/40 rounded-full overflow-hidden">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div
              key={i}
              className={`h-full transition-all duration-300 ${
                i <= step ? 'bg-wheat-gold' : 'bg-transparent'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Center Question View */}
      <div className="my-auto py-6">
        {/* STEP 1: Farmer Name & Identity */}
        {step === 1 && (
          <div className="space-y-4">
            <div>
              <div className="w-10 h-10 rounded-xl bg-wheat-tint text-wheat-gold flex items-center justify-center mb-3">
                <User className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-bold text-ajrak-black leading-tight mb-1">
                {t.stepNameTitle}
              </h2>
              <p className="text-xs text-earth-muted">
                {t.stepNameDesc}
              </p>
            </div>

            <div className="space-y-3.5 pt-2">
              <div>
                <label className="block text-xs font-bold text-earth-dark mb-1.5">
                  {t.nameLabel}
                </label>
                <input
                  type="text"
                  value={data.name}
                  onChange={(e) => setData(p => ({ ...p, name: e.target.value }))}
                  placeholder={t.namePlaceholder}
                  className="w-full p-3.5 rounded-xl border border-earth-border bg-earth-surface text-ajrak-black font-semibold text-sm focus:border-wheat-gold focus:bg-white transition-all outline-hidden"
                />
              </div>

              {/* Quick Name Suggestions */}
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                <span className="text-[10px] text-earth-muted font-medium">Quick Pick:</span>
                {popularNames.map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => setData(p => ({ ...p, name: n }))}
                    className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
                      data.name === n
                        ? 'bg-wheat-gold text-white border-wheat-gold font-bold'
                        : 'bg-white border-earth-border text-earth-dark hover:border-wheat-border'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>

              <div className="pt-2">
                <label className="block text-xs font-bold text-earth-dark mb-1.5">
                  {t.phoneLabel}
                </label>
                <input
                  type="text"
                  value={data.phone_number}
                  onChange={(e) => setData(p => ({ ...p, phone_number: e.target.value }))}
                  placeholder={t.phonePlaceholder}
                  className="w-full p-3.5 rounded-xl border border-earth-border bg-earth-surface text-ajrak-black font-semibold text-sm focus:border-wheat-gold focus:bg-white transition-all outline-hidden font-mono"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: District */}
        {step === 2 && (
          <div className="space-y-4">
            <div>
              <div className="w-10 h-10 rounded-xl bg-wheat-tint text-wheat-gold flex items-center justify-center mb-3">
                <MapPin className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-bold text-ajrak-black leading-tight mb-1">
                {t.stepLocationTitle}
              </h2>
              <p className="text-xs text-earth-muted">
                {t.stepLocationDesc}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2.5 pt-2">
              {districts.map(d => (
                <button
                  key={d.id}
                  onClick={() => setData(p => ({ ...p, district: d.id }))}
                  className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between min-h-[72px] ${
                    data.district === d.id
                      ? 'bg-wheat-tint border-wheat-gold text-ajrak-black shadow-xs font-bold'
                      : 'bg-earth-surface border-earth-border text-earth-dark hover:border-wheat-border'
                  }`}
                >
                  <span className="text-sm font-semibold">{d.nameRoman}</span>
                  <span className="text-xs text-earth-muted">{d.nameUrdu}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* STEP 3: Acreage */}
        {step === 3 && (
          <div className="space-y-4">
            <div>
              <div className="w-10 h-10 rounded-xl bg-wheat-tint text-wheat-gold flex items-center justify-center mb-3">
                <Sprout className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-bold text-ajrak-black leading-tight mb-1">
                {t.stepAcreageTitle}
              </h2>
              <p className="text-xs text-earth-muted">
                {t.stepAcreageDesc}
              </p>
            </div>

            <div className="space-y-2.5 pt-2">
              {acreageOptions.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setData(p => ({ ...p, total_land_acres: opt.value }))}
                  className={`w-full p-4 rounded-xl border transition-all flex items-center justify-between min-h-[58px] ${
                    data.total_land_acres === opt.value
                      ? 'bg-wheat-tint border-wheat-gold text-ajrak-black font-bold shadow-xs'
                      : 'bg-earth-surface border-earth-border text-earth-dark hover:border-wheat-border'
                  }`}
                >
                  <div>
                    <span className="text-base font-bold num-tabular block">{opt.label}</span>
                    <span className="text-xs text-earth-muted">{opt.descRoman} • {opt.descUrdu}</span>
                  </div>
                  {data.total_land_acres === opt.value && (
                    <div className="w-5 h-5 rounded-full bg-wheat-gold text-white flex items-center justify-center">
                      <Check className="w-3.5 h-3.5 stroke-[3]" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* STEP 4: Water Availability */}
        {step === 4 && (
          <div className="space-y-4">
            <div>
              <div className="w-10 h-10 rounded-xl bg-water-surface text-water-tone flex items-center justify-center mb-3">
                <Droplets className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-bold text-ajrak-black leading-tight mb-1">
                {t.stepWaterTitle}
              </h2>
              <p className="text-xs text-earth-muted">
                {t.stepWaterDesc}
              </p>
            </div>

            <div className="space-y-2.5 pt-2">
              {waterOptions.map(w => (
                <button
                  key={w.id}
                  onClick={() => setData(p => ({ ...p, irrigation_source: w.id }))}
                  className={`w-full p-4 rounded-xl border transition-all flex items-center justify-between min-h-[58px] ${
                    data.irrigation_source === w.id
                      ? 'bg-water-surface border-water-border text-water-dark font-bold shadow-xs'
                      : 'bg-earth-surface border-earth-border text-earth-dark hover:border-wheat-border'
                  }`}
                >
                  <div>
                    <span className="text-sm font-semibold block">{w.labelRoman}</span>
                    <span className="text-xs text-earth-muted">{w.labelUrdu}</span>
                  </div>
                  {data.irrigation_source === w.id && (
                    <div className="w-5 h-5 rounded-full bg-water-tone text-white flex items-center justify-center">
                      <Check className="w-3.5 h-3.5 stroke-[3]" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* STEP 5: Primary Crop */}
        {step === 5 && (
          <div className="space-y-4">
            <div>
              <div className="w-10 h-10 rounded-xl bg-wheat-tint text-wheat-gold flex items-center justify-center mb-3">
                <Sprout className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-bold text-ajrak-black leading-tight mb-1">
                {t.stepCropTitle}
              </h2>
              <p className="text-xs text-earth-muted">
                {t.stepCropDesc}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2.5 pt-2">
              {cropOptions.map(c => (
                <button
                  key={c.id}
                  onClick={() => setData(p => ({ ...p, primary_crop: c.id }))}
                  className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between min-h-[72px] ${
                    data.primary_crop === c.id
                      ? 'bg-wheat-tint border-wheat-gold text-ajrak-black shadow-xs font-bold'
                      : 'bg-earth-surface border-earth-border text-earth-dark hover:border-wheat-border'
                  }`}
                >
                  <span className="text-sm font-semibold">{c.nameRoman}</span>
                  <span className="text-xs text-earth-muted">{c.nameUrdu} ({c.season})</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* STEP 6: Preferred Language */}
        {step === 6 && (
          <div className="space-y-4">
            <div>
              <div className="w-10 h-10 rounded-xl bg-wheat-tint text-wheat-gold flex items-center justify-center mb-3">
                <Globe className="w-5 h-5" />
              </div>
              <h2 className="text-2xl font-bold text-ajrak-black leading-tight mb-1">
                {t.stepLanguageTitle}
              </h2>
              <p className="text-xs text-earth-muted">
                {t.stepLanguageDesc}
              </p>
            </div>

            <div className="space-y-3 pt-2">
              <button
                onClick={() => {
                  setData(p => ({ ...p, preferred_language: 'ur' }));
                  setLanguage('ur');
                }}
                className={`w-full p-4 rounded-xl border transition-all flex items-center justify-between ${
                  data.preferred_language === 'ur'
                    ? 'bg-wheat-tint border-wheat-gold text-ajrak-black font-bold shadow-xs'
                    : 'bg-earth-surface border-earth-border text-earth-dark'
                }`}
              >
                <div>
                  <span className="text-lg font-bold block font-urdu">اردو (نستعلیق)</span>
                  <span className="text-xs text-earth-muted">روایتی رسم الخط برائے پنجاب</span>
                </div>
                {data.preferred_language === 'ur' && <Check className="w-5 h-5 text-wheat-gold" />}
              </button>

              <button
                onClick={() => {
                  setData(p => ({ ...p, preferred_language: 'roman_urdu' }));
                  setLanguage('roman_urdu');
                }}
                className={`w-full p-4 rounded-xl border transition-all flex items-center justify-between ${
                  data.preferred_language === 'roman_urdu'
                    ? 'bg-wheat-tint border-wheat-gold text-ajrak-black font-bold shadow-xs'
                    : 'bg-earth-surface border-earth-border text-earth-dark'
                }`}
              >
                <div>
                  <span className="text-base font-bold block">Roman Urdu</span>
                  <span className="text-xs text-earth-muted">Aasan Roman Urdu alfaz</span>
                </div>
                {data.preferred_language === 'roman_urdu' && <Check className="w-5 h-5 text-wheat-gold" />}
              </button>

              <button
                onClick={() => {
                  setData(p => ({ ...p, preferred_language: 'en' }));
                  setLanguage('en');
                }}
                className={`w-full p-4 rounded-xl border transition-all flex items-center justify-between ${
                  data.preferred_language === 'en'
                    ? 'bg-wheat-tint border-wheat-gold text-ajrak-black font-bold shadow-xs'
                    : 'bg-earth-surface border-earth-border text-earth-dark'
                }`}
              >
                <div>
                  <span className="text-base font-bold block">English</span>
                  <span className="text-xs text-earth-muted">Agronomic technical phrasing</span>
                </div>
                {data.preferred_language === 'en' && <Check className="w-5 h-5 text-wheat-gold" />}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Button Bar */}
      <div className="space-y-2 pt-4 border-t border-earth-border">
        <button
          onClick={handleNext}
          className="w-full py-4 px-6 rounded-xl bg-wheat-gold hover:bg-wheat-dark text-white font-bold text-base flex items-center justify-center gap-2 shadow-xs transition-all active:scale-[0.99]"
        >
          <span>{step === 6 ? t.finishSetupBtn : t.nextBtn}</span>
          <ArrowRight className={`w-4 h-4 ${isRtl ? 'rotate-180' : ''}`} />
        </button>

        {step > 1 && step < 6 && (
          <button
            onClick={() => handleSkip(step === 2 ? 'district' : (step === 3 ? 'acres' : (step === 4 ? 'water' : 'crop')))}
            className="w-full py-2.5 px-4 text-xs font-semibold text-earth-muted hover:text-earth-dark flex items-center justify-center gap-1.5 transition-colors"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>{t.notSureBtn}</span>
          </button>
        )}
      </div>
    </div>
  );
};
