import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { SimulationResult } from '../../api/types';
import { apiClient } from '../../api/client';
import { Sparkles, Droplets, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export const WhatIfSimulator: React.FC = () => {
  const { t } = useLanguage();
  const { profile } = useFarm();

  const [waterConstraint, setWaterConstraint] = useState<string>('limited');
  const [waterReduction, setWaterReduction] = useState<number>(0);
  const [acres, setAcres] = useState<number>(profile.total_land_acres || 5.0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<SimulationResult | null>(null);

  const runSimulation = async () => {
    setIsLoading(true);
    try {
      const res = await apiClient.compareCrops(
        ['wheat', 'chickpea', 'canola'],
        acres,
        waterConstraint,
        waterReduction
      );
      setResult(res);
    } catch (err) {
      console.warn('Simulation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [waterConstraint, waterReduction, acres]);

  return (
    <div className="space-y-4 max-w-xl mx-auto py-2">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-ajrak-black flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-wheat-gold" />
          <span>{t.simulatorTitle}</span>
        </h2>
        <p className="text-xs text-earth-muted mt-0.5">
          {t.simulatorSubtitle}
        </p>
      </div>

      {/* Simulator Interactive Controls */}
      <div className="bg-earth-surface border border-earth-border rounded-2xl p-4 space-y-3.5 shadow-xs">
        {/* Acres and Water Condition */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-bold text-earth-dark block mb-1">
              Raqba (Acres)
            </label>
            <select
              value={acres}
              onChange={(e) => setAcres(Number(e.target.value))}
              className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 text-xs font-bold text-ajrak-black focus:border-wheat-gold"
            >
              <option value={2}>2 Acres</option>
              <option value={5}>5 Acres (Standard)</option>
              <option value={10}>10 Acres</option>
              <option value={20}>20 Acres</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-bold text-earth-dark block mb-1">
              Pani Ki Halat
            </label>
            <select
              value={waterConstraint}
              onChange={(e) => setWaterConstraint(e.target.value)}
              className="w-full bg-white border border-earth-border rounded-xl px-3 py-2 text-xs font-bold text-ajrak-black focus:border-wheat-gold"
            >
              <option value="limited">Limited (2 Turns) • Standard</option>
              <option value="abundant">Abundant (Tubewell + Canal)</option>
              <option value="scarce">Scarce (1 Turn / Drought)</option>
            </select>
          </div>
        </div>

        {/* Water Reduction Scenario Slider */}
        <div className="pt-2 border-t border-earth-border/60">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="font-semibold text-earth-dark flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-water-tone" />
              <span>{t.waterReductionLabel}</span>
            </span>
            <span className="font-bold text-water-dark num-tabular bg-water-surface px-2 py-0.5 rounded border border-water-border">
              -{waterReduction}% Water Cut
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={50}
            step={10}
            value={waterReduction}
            onChange={(e) => setWaterReduction(Number(e.target.value))}
            className="w-full accent-water-tone h-2 bg-white rounded-lg border border-earth-border cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-earth-muted mt-1">
            <span>0% (Full Supply)</span>
            <span>25% Cut</span>
            <span>50% Severe Cut</span>
          </div>
        </div>
      </div>

      {/* Recommended Winner Card */}
      {result && (
        <div className="bg-wheat-tint border-2 border-wheat-border rounded-2xl p-4 shadow-xs">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-bold text-wheat-dark uppercase tracking-wider">
              {t.recommendedOptionTitle}
            </span>
            <span className="text-xs font-bold bg-wheat-gold text-white px-2 py-0.5 rounded-full">
              ★ TOP CHOICE
            </span>
          </div>
          <h3 className="text-xl font-bold text-ajrak-black mb-1">
            {result.recommended_option}
          </h3>
          <p className="text-xs text-earth-dark leading-relaxed">
            {result.recommendation_reason}
          </p>
        </div>
      )}

      {/* Comparison Options Cards / Table */}
      {result && (
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-ajrak-slate">
            Faslon Ka Tafseeli Mawaazna ({acres} Acres)
          </h3>

          <div className="space-y-2.5">
            {result.options.map((opt) => {
              const isRec = opt.crop.toLowerCase() === result.recommended_option.toLowerCase();
              return (
                <div
                  key={opt.crop}
                  className={`bg-white border rounded-2xl p-4 shadow-xs transition-all ${
                    isRec ? 'border-wheat-gold ring-1 ring-wheat-gold/50' : 'border-earth-border'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-base text-ajrak-black">{opt.crop}</h4>
                        {isRec && (
                          <span className="text-[10px] font-bold bg-wheat-tint border border-wheat-border text-wheat-dark px-1.5 py-0.5 rounded">
                            Recommended
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-earth-muted">{opt.expected_yield}</span>
                    </div>

                    <div className="text-right">
                      <span className="text-[11px] text-earth-muted block">{t.netProfitLabel}</span>
                      <span className="font-bold text-sm text-emerald-800 num-tabular">
                        {opt.estimated_profit}
                      </span>
                    </div>
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-3 gap-2 bg-earth-ground rounded-xl p-2.5 text-center text-xs">
                    <div>
                      <span className="text-[10px] text-earth-muted block">{t.costLabel}</span>
                      <span className="font-semibold text-earth-dark num-tabular">{opt.input_cost}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-earth-muted block">{t.waterRiskLabel}</span>
                      <span className={`font-semibold text-[11px] ${opt.water_risk === 'LOW' ? 'text-emerald-700' : 'text-amber-700'}`}>
                        {opt.water_risk}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-earth-muted block">{t.overallRiskLabel}</span>
                      <span className="font-semibold text-[11px] text-ajrak-black">
                        {opt.overall_risk}
                      </span>
                    </div>
                  </div>

                  <p className="text-[11px] text-earth-muted mt-2">
                    💧 Water: {opt.water_requirement}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Trade-Offs & Explicit Assumptions */}
      {result && (
        <div className="bg-earth-surface border border-earth-border rounded-2xl p-4 space-y-3 text-xs">
          <div>
            <h4 className="font-bold text-ajrak-black mb-1.5 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-wheat-gold" />
              <span>{t.tradeoffsTitle}</span>
            </h4>
            <ul className="space-y-1 text-earth-dark">
              {result.tradeoffs.map((td, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-wheat-gold font-bold">•</span>
                  <span>{td}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="pt-2 border-t border-earth-border/60">
            <h4 className="font-bold text-ajrak-black mb-1.5 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-earth-muted" />
              <span>{t.assumptionsTitle}</span>
            </h4>
            <ul className="space-y-1 text-earth-muted text-[11px]">
              {result.assumptions.map((as, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span>-</span>
                  <span>{as}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
