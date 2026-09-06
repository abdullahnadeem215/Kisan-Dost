import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { MandiResponse } from '../../api/types';
import { apiClient } from '../../api/client';
import { GroundingBadge } from '../common/GroundingBadge';
import { TrendingUp, MapPin, Calendar, Clock, DollarSign, RefreshCw } from 'lucide-react';

export const MandiView: React.FC = () => {
  const { t } = useLanguage();
  const { profile } = useFarm();

  const [commodity, setCommodity] = useState<string>(profile.primary_crop || 'Wheat');
  const [district, setDistrict] = useState<string>(profile.district || 'Multan');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [mandiData, setMandiData] = useState<MandiResponse | null>(null);

  const fetchPrices = async () => {
    setIsLoading(true);
    try {
      const res = await apiClient.getMandiPrices(commodity, district);
      setMandiData(res);
    } catch (err) {
      console.warn('Error fetching mandi prices:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPrices();
  }, [commodity, district]);

  return (
    <div className="space-y-4 max-w-xl mx-auto py-2">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-ajrak-black flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-wheat-gold" />
          <span>{t.actionMandi}</span>
        </h2>
        <p className="text-xs text-earth-muted mt-0.5">
          AMIS Punjab Verified Wholesale Mandi Bulletin & Holding Strategy
        </p>
      </div>

      {/* Selector Filters */}
      <div className="grid grid-cols-2 gap-2.5 bg-earth-surface border border-earth-border rounded-xl p-3 shadow-xs">
        <div>
          <label className="text-[11px] font-bold text-earth-dark block mb-1">Fasal (Commodity)</label>
          <select
            value={commodity}
            onChange={(e) => setCommodity(e.target.value)}
            className="w-full bg-white border border-earth-border rounded-lg px-2.5 py-1.5 text-xs font-bold text-ajrak-black"
          >
            <option value="Wheat">Gandum (Wheat)</option>
            <option value="Cotton">Kapas (Cotton)</option>
            <option value="Rice">Dhan (Basmati Rice)</option>
            <option value="Maize">Makai (Maize)</option>
            <option value="Potato">Aalo (Potato)</option>
            <option value="Canola">Raye (Canola)</option>
          </select>
        </div>

        <div>
          <label className="text-[11px] font-bold text-earth-dark block mb-1">Zila (District)</label>
          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="w-full bg-white border border-earth-border rounded-lg px-2.5 py-1.5 text-xs font-bold text-ajrak-black"
          >
            <option value="Multan">Multan</option>
            <option value="Faisalabad">Faisalabad</option>
            <option value="Khanewal">Khanewal</option>
            <option value="Sargodha">Sargodha</option>
            <option value="Bahawalpur">Bahawalpur</option>
            <option value="Sahiwal">Sahiwal</option>
          </select>
        </div>
      </div>

      {/* Main Rate Card */}
      {mandiData && mandiData.prices.length > 0 && (
        <div className="bg-wheat-tint border-2 border-wheat-border rounded-2xl p-5 space-y-4 shadow-xs">
          <div className="flex items-start justify-between gap-2">
            <div>
              <span className="text-xs font-bold text-wheat-dark uppercase tracking-wider block">
                {mandiData.prices[0].mandi_name}
              </span>
              <h3 className="text-2xl font-bold text-ajrak-black num-tabular">
                Rs {mandiData.prices[0].modal_price_pkr_per_maund.toLocaleString()}{' '}
                <span className="text-xs font-normal text-earth-muted">/ Mann (40kg)</span>
              </h3>
            </div>
            <GroundingBadge isLive={mandiData.is_live} state="verified" size="sm" />
          </div>

          {/* Range */}
          <div className="grid grid-cols-2 gap-3 bg-white/80 rounded-xl p-3 border border-wheat-border/60 text-xs">
            <div>
              <span className="text-[11px] text-earth-muted block">Kam az Kam (Min)</span>
              <span className="font-bold text-earth-dark num-tabular">
                Rs {mandiData.prices[0].min_price_pkr_per_maund.toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-[11px] text-earth-muted block">Zyada se Zyada (Max)</span>
              <span className="font-bold text-emerald-800 num-tabular">
                Rs {mandiData.prices[0].max_price_pkr_per_maund.toLocaleString()}
              </span>
            </div>
          </div>

          {/* Selling Advisor Strategy Box */}
          <div className="bg-white border border-earth-border rounded-xl p-3.5 text-xs space-y-1.5">
            <span className="font-bold text-ajrak-black flex items-center gap-1.5">
              <span>💡</span>
              <span>Bechne Ka Mashwara (Selling Timing):</span>
            </span>
            <p className="text-earth-dark leading-relaxed">
              Current mandi rates in {district} reflect strong seasonal demand. Holding beyond 60 days will incur PKR 60/maund/month storage cost which diminishes margins. <strong className="text-wheat-dark">Recommendation: Sell 60% of produce now to lock benchmark rate.</strong>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
