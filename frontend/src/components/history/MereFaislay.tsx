import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { DecisionReceiptCard } from '../decision/DecisionReceiptCard';
import { BookmarkCheck, Filter } from 'lucide-react';

export const MereFaislay: React.FC = () => {
  const { t } = useLanguage();
  const { decisions, saveDecision, openReceiptModal } = useFarm();

  const [activeFilter, setActiveFilter] = useState<string>('all');

  const filterTabs = [
    { id: 'all', label: t.filterAll },
    { id: 'crop', label: t.filterCrop },
    { id: 'water', label: t.filterWater },
    { id: 'disease', label: t.filterDisease },
    { id: 'market', label: t.filterMarket },
  ];

  const filtered = decisions.filter(d => {
    if (activeFilter === 'all') return true;
    const cat = d.action_category.toLowerCase();
    if (activeFilter === 'crop' && (cat.includes('crop') || cat.includes('agronomy'))) return true;
    if (activeFilter === 'water' && (cat.includes('water') || cat.includes('irrigation'))) return true;
    if (activeFilter === 'disease' && (cat.includes('disease') || cat.includes('pest') || cat.includes('protection'))) return true;
    if (activeFilter === 'market' && (cat.includes('market') || cat.includes('sale') || cat.includes('mandi'))) return true;
    return false;
  });

  return (
    <div className="space-y-4 max-w-xl mx-auto py-2">
      {/* Page Title */}
      <div>
        <h2 className="text-xl font-bold text-ajrak-black flex items-center gap-2">
          <BookmarkCheck className="w-5 h-5 text-wheat-gold" />
          <span>{t.mereFaislayTitle}</span>
        </h2>
        <p className="text-xs text-earth-muted mt-0.5">
          {t.mereFaislaySubtitle}
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {filterTabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveFilter(tab.id)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
              activeFilter === tab.id
                ? 'bg-ajrak-black text-white shadow-xs'
                : 'bg-earth-surface text-earth-muted border border-earth-border hover:text-earth-dark'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Decision Cards List */}
      {filtered.length === 0 ? (
        <div className="bg-earth-surface border border-earth-border rounded-2xl p-8 text-center text-earth-muted space-y-2">
          <span className="text-3xl block">📋</span>
          <p className="text-sm font-semibold text-earth-dark">{t.noDecisionsYet}</p>
          <p className="text-xs">Farm actions or queries will automatically record structured Decision Receipts here.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(receipt => (
            <DecisionReceiptCard
              key={receipt.receipt_id}
              receipt={receipt}
              compact={true}
              onOpenFull={() => openReceiptModal(receipt)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
