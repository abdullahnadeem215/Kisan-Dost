import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { MapPin, User, RefreshCw } from 'lucide-react';

interface HeaderProps {
  onOpenPassport: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenPassport }) => {
  const { language, setLanguage, t } = useLanguage();
  const { profile, isRefreshing, refreshFarmData } = useFarm();

  return (
    <header className="sticky top-0 z-30 bg-earth-ground/95 backdrop-blur-md border-b border-earth-border px-4 py-3">
      <div className="max-w-xl mx-auto flex items-center justify-between gap-3">
        {/* Logo & Identity */}
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-wheat-tint border border-wheat-border flex items-center justify-center text-xl shadow-xs">
            🌾
          </div>
          <div>
            <h1 className="font-bold text-lg text-ajrak-black tracking-tight leading-tight flex items-center gap-1.5">
              <span>{t.appName}</span>
            </h1>
            <div className="flex items-center gap-1.5 text-xs text-earth-muted">
              <span className="font-bold text-ajrak-black">{profile.name || 'Chaudhry Ahmad'}</span>
              <span>•</span>
              <MapPin className="w-3 h-3 text-wheat-gold" />
              <span>{profile.district} ({profile.total_land_acres} {t.acresLabel})</span>
            </div>
          </div>
        </div>

        {/* Right Controls: Sync, Lang Switcher, Profile */}
        <div className="flex items-center gap-2">
          {/* Refresh Data */}
          <button
            onClick={refreshFarmData}
            title="Refresh farm data"
            className={`p-2 rounded-lg border border-earth-border bg-earth-surface text-earth-dark hover:bg-wheat-tint transition-all ${isRefreshing ? 'animate-spin' : ''}`}
          >
            <RefreshCw className="w-3.5 h-3.5 text-earth-muted" />
          </button>

          {/* Language Toggle Pills */}
          <div className="inline-flex rounded-lg border border-earth-border bg-earth-surface p-0.5 text-xs font-semibold">
            <button
              onClick={() => setLanguage('ur')}
              className={`px-2 py-1 rounded-md transition-all ${language === 'ur' ? 'bg-ajrak-black text-white shadow-xs' : 'text-earth-muted hover:text-earth-dark'}`}
            >
              اردو
            </button>
            <button
              onClick={() => setLanguage('roman_urdu')}
              className={`px-2 py-1 rounded-md transition-all ${language === 'roman_urdu' ? 'bg-ajrak-black text-white shadow-xs' : 'text-earth-muted hover:text-earth-dark'}`}
            >
              Roman
            </button>
            <button
              onClick={() => setLanguage('en')}
              className={`px-2 py-1 rounded-md transition-all ${language === 'en' ? 'bg-ajrak-black text-white shadow-xs' : 'text-earth-muted hover:text-earth-dark'}`}
            >
              EN
            </button>
          </div>

          {/* Passport Button Pill */}
          <button
            onClick={onOpenPassport}
            className="flex items-center gap-1.5 py-1.5 px-2.5 rounded-lg border border-earth-border bg-earth-surface text-ajrak-black hover:border-wheat-gold hover:bg-wheat-tint transition-all text-xs font-bold"
            title="Farm Passport (SQLite Persistent)"
          >
            <User className="w-3.5 h-3.5 text-wheat-gold" />
            <span className="hidden sm:inline font-mono text-[11px] text-earth-muted">Passport</span>
          </button>
        </div>
      </div>
    </header>
  );
};
