import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { Activity, Droplets, Sun, TrendingUp } from 'lucide-react';

interface StatusRowProps {
  onTileClick: (tab: string) => void;
}

export const StatusRow: React.FC<StatusRowProps> = ({ onTileClick }) => {
  const { t } = useLanguage();
  const { healthScore, weather, mandi, profile } = useFarm();

  const healthVal = Math.round(healthScore?.overall_health_score || 84);
  const tempVal = Math.round(weather?.temperature_c || 30);
  const mandiVal = mandi?.prices?.[0]?.modal_price_pkr_per_maund || 3950;
  const turnsVal = profile.available_water_turns ?? 2;

  return (
    <section className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
      {/* 1. Farm Health Index */}
      <div
        onClick={() => onTileClick('health')}
        className="bg-earth-surface border border-earth-border rounded-xl p-3 hover:border-wheat-gold transition-all cursor-pointer shadow-xs"
      >
        <div className="flex items-center justify-between text-earth-muted mb-1">
          <span className="text-[11px] font-semibold">{t.healthScoreTitle}</span>
          <Activity className="w-3.5 h-3.5 text-emerald-700" />
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-xl font-bold num-tabular text-ajrak-black">{healthVal}</span>
          <span className="text-xs text-earth-muted">/100</span>
        </div>
        <div className="w-full bg-earth-border/60 h-1 rounded-full mt-2 overflow-hidden">
          <div className="bg-emerald-600 h-full rounded-full" style={{ width: `${healthVal}%` }} />
        </div>
      </div>

      {/* 2. Water Status (Strictly Water-Blue) */}
      <div
        onClick={() => onTileClick('irrigation')}
        className="bg-water-surface border border-water-border rounded-xl p-3 hover:border-water-tone transition-all cursor-pointer shadow-xs"
      >
        <div className="flex items-center justify-between text-water-dark/80 mb-1">
          <span className="text-[11px] font-semibold">{t.waterStatusTitle}</span>
          <Droplets className="w-3.5 h-3.5 text-water-tone fill-water-tone/20" />
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-xl font-bold num-tabular text-water-dark">{turnsVal}</span>
          <span className="text-xs text-water-dark/80">Turns</span>
        </div>
        <span className="text-[10px] text-water-dark/70 font-medium block mt-1.5 truncate">
          {profile.irrigation_source.split('+')[0]}
        </span>
      </div>

      {/* 3. Weather */}
      <div
        onClick={() => onTileClick('weather')}
        className="bg-earth-surface border border-earth-border rounded-xl p-3 hover:border-wheat-gold transition-all cursor-pointer shadow-xs"
      >
        <div className="flex items-center justify-between text-earth-muted mb-1">
          <span className="text-[11px] font-semibold">{t.weatherTitle}</span>
          <Sun className="w-3.5 h-3.5 text-amber-600" />
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-xl font-bold num-tabular text-ajrak-black">{tempVal}°C</span>
          <span className="text-xs text-earth-muted">{weather?.condition?.split('/')[0] || 'Dhoop'}</span>
        </div>
        <span className="text-[10px] text-earth-muted font-medium block mt-1.5">
          Max: {weather?.temp_max_c ? Math.round(weather.temp_max_c) : 34}°C
        </span>
      </div>

      {/* 4. Mandi Price */}
      <div
        onClick={() => onTileClick('mandi')}
        className="bg-earth-surface border border-earth-border rounded-xl p-3 hover:border-wheat-gold transition-all cursor-pointer shadow-xs"
      >
        <div className="flex items-center justify-between text-earth-muted mb-1">
          <span className="text-[11px] font-semibold">{t.mandiRateTitle}</span>
          <TrendingUp className="w-3.5 h-3.5 text-wheat-gold" />
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-base font-bold num-tabular text-ajrak-black">
            Rs {mandiVal.toLocaleString()}
          </span>
        </div>
        <span className="text-[10px] text-earth-muted font-medium block mt-1.5 truncate">
          {profile.primary_crop} (Modal)
        </span>
      </div>
    </section>
  );
};
