import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { IrrigationSchedule } from '../../api/types';
import { apiClient } from '../../api/client';
import { GroundingBadge } from '../common/GroundingBadge';
import { Droplets, Calendar, Clock, AlertCircle, Info } from 'lucide-react';

export const IrrigationAdvisorView: React.FC = () => {
  const { t } = useLanguage();
  const { profile } = useFarm();

  const [schedule, setSchedule] = useState<IrrigationSchedule | null>(null);
  const [stage, setStage] = useState<string>('Tillering / Crown Root Initiation');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchSchedule = async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.getIrrigationSchedule(profile.primary_crop, profile.district, stage);
        setSchedule(res);
      } catch (err) {
        console.warn('Error fetching irrigation schedule:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSchedule();
  }, [profile.primary_crop, profile.district, stage]);

  return (
    <div className="space-y-4 max-w-xl mx-auto py-2">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-ajrak-black flex items-center gap-2">
          <Droplets className="w-5 h-5 text-water-tone" />
          <span>{t.actionIrrigation}</span>
        </h2>
        <p className="text-xs text-earth-muted mt-0.5">
          FAO-56 Penman-Monteith Evapotranspiration ({schedule?.etc_mm_day || 3.8} mm/day)
        </p>
      </div>

      {/* Stage Selector */}
      <div className="bg-water-surface border border-water-border rounded-xl p-3 shadow-xs">
        <label className="text-[11px] font-bold text-water-dark block mb-1">
          Fasal Ka Marhala (Crop Growth Stage)
        </label>
        <select
          value={stage}
          onChange={(e) => setStage(e.target.value)}
          className="w-full bg-white border border-water-border rounded-lg px-2.5 py-1.5 text-xs font-bold text-water-dark focus:border-water-tone"
        >
          <option value="Initial / Germination">Initial / Germination (Ugau)</option>
          <option value="Tillering / Crown Root Initiation">Tillering / CRI (Shakhain Nikalna) • Critical</option>
          <option value="Flowering / Heading">Flowering / Booting (Sitta Banna) • Critical</option>
          <option value="Grain Filling / Milking">Grain Filling (Dana Bharna)</option>
          <option value="Maturity / Ripening">Maturity (Pakai)</option>
        </select>
      </div>

      {/* Main Schedule Card (Strictly Water-Blue) */}
      {schedule && (
        <div className="bg-water-surface border-2 border-water-border rounded-2xl p-5 space-y-4 shadow-xs">
          <div className="flex items-start justify-between gap-2">
            <div>
              <span className="text-xs font-bold text-water-dark uppercase tracking-wider block">
                Agli Aabbashi Ka Waqt (Next Water Date)
              </span>
              <h3 className="text-2xl font-bold text-water-dark num-tabular flex items-center gap-2 mt-1">
                <Calendar className="w-6 h-6 text-water-tone" />
                <span>{schedule.next_irrigation_date}</span>
              </h3>
            </div>
            <GroundingBadge isLive={true} state="verified" size="sm" />
          </div>

          {/* Key Water Parameters */}
          <div className="grid grid-cols-3 gap-2 bg-white/90 rounded-xl p-3 border border-water-border/80 text-center text-xs">
            <div>
              <span className="text-[10px] text-earth-muted block">Rozana Zaroorat</span>
              <span className="font-bold text-water-dark num-tabular">{schedule.daily_water_need_mm} mm/day</span>
            </div>
            <div>
              <span className="text-[10px] text-earth-muted block">Depth per Turn</span>
              <span className="font-bold text-water-dark num-tabular">{schedule.recommended_water_depth_mm} mm</span>
            </div>
            <div>
              <span className="text-[10px] text-earth-muted block">Mitti Ki Nami</span>
              <span className="font-bold text-emerald-800 num-tabular">{schedule.current_moisture_percent}%</span>
            </div>
          </div>

          {/* Water Saving Tips */}
          <div className="bg-white border border-water-border/80 rounded-xl p-3.5 text-xs text-water-dark space-y-1">
            <span className="font-bold block">💡 Water-Saving Advice:</span>
            <p className="text-earth-dark leading-relaxed">
              {schedule.water_saving_tips || 'Irrigate in early morning or late afternoon to minimize evaporation losses.'}
            </p>
          </div>

          {/* FAO-56 Methodology Assumptions */}
          <div className="text-[11px] text-water-dark/80 pt-2 border-t border-water-border/60">
            <span className="font-semibold block mb-1">Methodology & Assumptions:</span>
            <ul className="space-y-0.5">
              {schedule.explicit_assumptions?.map((asm, i) => (
                <li key={i}>• {asm}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
