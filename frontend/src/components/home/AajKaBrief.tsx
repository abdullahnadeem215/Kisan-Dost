import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { GroundingBadge } from '../common/GroundingBadge';
import { Droplets, CheckCircle2, TrendingUp, AlertTriangle, ArrowRight, HelpCircle } from 'lucide-react';

interface AajKaBriefProps {
  onActionClick: (tool: string) => void;
}

export const AajKaBrief: React.FC<AajKaBriefProps> = ({ onActionClick }) => {
  const { t, isRtl } = useLanguage();
  const { profile, mandi, weather, updateProfile } = useFarm();

  const [dismissDataGap, setDismissDataGap] = React.useState(false);

  // Situation-driven logic
  const isIrrigationUrgent = (profile.available_water_turns ?? 2) <= 2;
  const mandiRate = mandi?.prices?.[0]?.modal_price_pkr_per_maund || 3950;
  const isMandiGood = mandiRate >= 3900;

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-bold uppercase tracking-wider text-ajrak-slate flex items-center gap-1.5">
          <span>{t.aajKaBrief}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
        </h2>
        <GroundingBadge isLive={true} state="verified" size="sm" />
      </div>

      {/* Dynamic Hero Card: Changes based on situation */}
      {isIrrigationUrgent ? (
        /* Irrigation Day / Water Hero Card (Strictly Water-Blue) */
        <div className="bg-water-surface border-2 border-water-border rounded-2xl p-5 shadow-xs relative overflow-hidden">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-white border border-water-border/80 flex items-center justify-center text-water-tone shrink-0 shadow-xs">
              <Droplets className="w-5 h-5 fill-water-tone/20" />
            </div>
            <span className="bg-white border border-water-border text-water-dark text-xs font-bold px-2.5 py-1 rounded-full num-tabular">
              {profile.available_water_turns} {t.turnsUnit}
            </span>
          </div>

          <h3 className="text-lg font-bold text-water-dark leading-snug mb-1">
            {t.waterAlertTitle}
          </h3>
          <p className="text-xs text-water-dark/80 leading-relaxed mb-4">
            {t.waterAlertDesc}
          </p>

          <button
            onClick={() => onActionClick('irrigation')}
            className="w-full py-2.5 px-4 bg-water-tone hover:bg-water-dark text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 shadow-xs transition-all"
          >
            <span>{t.actionIrrigation}</span>
            <ArrowRight className={`w-3.5 h-3.5 ${isRtl ? 'rotate-180' : ''}`} />
          </button>
        </div>
      ) : isMandiGood ? (
        /* Mandi Price Peak Hero Card */
        <div className="bg-wheat-tint border-2 border-wheat-border rounded-2xl p-5 shadow-xs">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-white border border-wheat-border flex items-center justify-center text-wheat-gold shrink-0">
              <TrendingUp className="w-5 h-5" />
            </div>
            <span className="bg-white border border-wheat-border text-wheat-dark text-xs font-bold px-2.5 py-1 rounded-full num-tabular">
              PKR {mandiRate.toLocaleString()} / Mann
            </span>
          </div>

          <h3 className="text-lg font-bold text-ajrak-black leading-snug mb-1">
            {t.mandiAlertTitle}
          </h3>
          <p className="text-xs text-earth-muted leading-relaxed mb-4">
            {t.mandiAlertDesc}
          </p>

          <button
            onClick={() => onActionClick('mandi')}
            className="w-full py-2.5 px-4 bg-wheat-gold hover:bg-wheat-dark text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 shadow-xs transition-all"
          >
            <span>{t.actionMandi}</span>
            <ArrowRight className={`w-3.5 h-3.5 ${isRtl ? 'rotate-180' : ''}`} />
          </button>
        </div>
      ) : (
        /* Normal Day: Calm, reassuring "Sab Theek Hai" status */
        <div className="bg-earth-surface border border-earth-border rounded-2xl p-5 shadow-xs">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-white border border-earth-border flex items-center justify-center text-emerald-700 shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <span className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold px-2.5 py-1 rounded-full">
              {t.allNormalTitle.split('—')[0]}
            </span>
          </div>

          <h3 className="text-lg font-bold text-ajrak-black leading-snug mb-1">
            {t.allNormalTitle}
          </h3>
          <p className="text-xs text-earth-muted leading-relaxed mb-3">
            {t.allNormalDesc}
          </p>
        </div>
      )}

      {/* In-context Progressive Data Gap Question (If soil type not yet set) */}
      {!dismissDataGap && (!profile.soil_type || profile.soil_type === 'Loam') && (
        <div className="bg-white border border-earth-border rounded-xl p-3.5 shadow-xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="text-base">🌱</span>
            <div>
              <span className="text-xs font-bold text-ajrak-black block">Mitti ki qisam kya hai?</span>
              <span className="text-[11px] text-earth-muted">Loam, Chikni (Clay) ya Raitli (Sandy)?</span>
            </div>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            <button
              onClick={() => {
                updateProfile({ soil_type: 'Clay' });
                setDismissDataGap(true);
              }}
              className="px-2 py-1 bg-earth-surface border border-earth-border rounded-lg text-xs font-semibold hover:border-wheat-gold"
            >
              Chikni
            </button>
            <button
              onClick={() => {
                updateProfile({ soil_type: 'Loam' });
                setDismissDataGap(true);
              }}
              className="px-2 py-1 bg-wheat-tint border border-wheat-border rounded-lg text-xs font-bold text-wheat-dark"
            >
              Loam
            </button>
            <button
              onClick={() => setDismissDataGap(true)}
              className="p-1 text-earth-muted hover:text-earth-dark text-xs"
              title="Not sure"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </section>
  );
};
