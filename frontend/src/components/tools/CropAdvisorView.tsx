import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { Sprout, CheckCircle2, TrendingUp, Droplets, ArrowRight } from 'lucide-react';

export const CropAdvisorView: React.FC = () => {
  const { t } = useLanguage();
  const { profile } = useFarm();

  const [season, setSeason] = useState<string>('Rabi');
  const [soil, setSoil] = useState<string>(profile.soil_type || 'Loam');
  const [water, setWater] = useState<string>('Low');

  const recommendations = [
    {
      crop: 'Wheat (Akbar-19 / Fakhar-e-Bhakkar)',
      yieldRange: '38 - 45 Maunds / Acre',
      waterNeed: '3 - 4 Irrigations',
      estProfit: 'PKR 98,000 / Acre',
      suitability: '96% Fit for Multan Loam soil',
      badge: 'High Food Security'
    },
    {
      crop: 'Chickpea / Desi Channa (Bittal-98)',
      yieldRange: '18 - 24 Maunds / Acre',
      waterNeed: '1 - 2 Irrigations (Drought Hardy)',
      estProfit: 'PKR 85,000 / Acre',
      suitability: '92% Fit for limited water turns',
      badge: 'Lowest Water Risk'
    },
    {
      crop: 'Canola / Super Raya',
      yieldRange: '22 - 28 Maunds / Acre',
      waterNeed: '2 - 3 Irrigations',
      estProfit: 'PKR 94,000 / Acre',
      suitability: '90% Fit for early Rabi sowing',
      badge: 'High Cash Value'
    }
  ];

  return (
    <div className="space-y-4 max-w-xl mx-auto py-2">
      <div>
        <h2 className="text-xl font-bold text-ajrak-black flex items-center gap-2">
          <Sprout className="w-5 h-5 text-wheat-gold" />
          <span>{t.actionCropAdvisor}</span>
        </h2>
        <p className="text-xs text-earth-muted mt-0.5">
          Agricultural Research Council Verified Varieties for {profile.district}
        </p>
      </div>

      {/* Constraints Selector */}
      <div className="grid grid-cols-3 gap-2 bg-earth-surface border border-earth-border rounded-xl p-3 shadow-xs">
        <div>
          <label className="text-[10px] font-bold text-earth-dark block mb-1">Season</label>
          <select
            value={season}
            onChange={(e) => setSeason(e.target.value)}
            className="w-full bg-white border border-earth-border rounded-lg px-2 py-1.5 text-xs font-bold text-ajrak-black"
          >
            <option value="Rabi">Rabi (Winter)</option>
            <option value="Kharif">Kharif (Summer)</option>
          </select>
        </div>
        <div>
          <label className="text-[10px] font-bold text-earth-dark block mb-1">Mitti (Soil)</label>
          <select
            value={soil}
            onChange={(e) => setSoil(e.target.value)}
            className="w-full bg-white border border-earth-border rounded-lg px-2 py-1.5 text-xs font-bold text-ajrak-black"
          >
            <option value="Loam">Loam (Mera)</option>
            <option value="Clay">Clay (Chikni)</option>
            <option value="Sandy">Sandy (Raitli)</option>
          </select>
        </div>
        <div>
          <label className="text-[10px] font-bold text-earth-dark block mb-1">Pani (Water)</label>
          <select
            value={water}
            onChange={(e) => setWater(e.target.value)}
            className="w-full bg-white border border-earth-border rounded-lg px-2 py-1.5 text-xs font-bold text-ajrak-black"
          >
            <option value="Low">Low (2 Turns)</option>
            <option value="Normal">Normal (3-4)</option>
            <option value="Abundant">Abundant (Tubewell)</option>
          </select>
        </div>
      </div>

      {/* Recommendations Cards */}
      <div className="space-y-3">
        {recommendations.map((rec, i) => (
          <div
            key={i}
            className="bg-white border border-earth-border rounded-2xl p-4 shadow-xs hover:border-wheat-gold transition-all"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <h4 className="font-bold text-base text-ajrak-black">{rec.crop}</h4>
                <span className="text-xs text-emerald-800 font-semibold">{rec.suitability}</span>
              </div>
              <span className="text-[10px] font-bold bg-wheat-tint text-wheat-dark border border-wheat-border px-2 py-0.5 rounded-full shrink-0">
                {rec.badge}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 bg-earth-ground rounded-xl p-2.5 text-xs text-earth-dark mb-3">
              <div>
                <span className="text-[10px] text-earth-muted block">Expected Yield:</span>
                <span className="font-bold num-tabular">{rec.yieldRange}</span>
              </div>
              <div>
                <span className="text-[10px] text-earth-muted block">Expected Profit:</span>
                <span className="font-bold text-emerald-800 num-tabular">{rec.estProfit}</span>
              </div>
            </div>

            <p className="text-xs text-water-dark flex items-center gap-1.5 font-medium">
              <Droplets className="w-3.5 h-3.5 text-water-tone" />
              <span>{rec.waterNeed}</span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
