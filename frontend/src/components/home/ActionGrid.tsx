import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { Camera, Sprout, Droplets, TrendingUp, Sparkles, Building2, HelpCircle } from 'lucide-react';

interface ActionGridProps {
  onAction: (action: string) => void;
}

export const ActionGrid: React.FC<ActionGridProps> = ({ onAction }) => {
  const { t } = useLanguage();

  const actions = [
    {
      id: 'disease',
      icon: Camera,
      title: t.actionDiseasePhoto,
      subtitle: t.actionDiseasePhotoSub,
      accent: 'border-ochre-border/70 hover:border-ochre-alert bg-white text-ochre-dark',
      iconBg: 'bg-ochre-surface text-ochre-alert',
      badge: 'Photo / Camera'
    },
    {
      id: 'crop',
      icon: Sprout,
      title: t.actionCropAdvisor,
      subtitle: t.actionCropAdvisorSub,
      accent: 'border-earth-border hover:border-wheat-gold bg-white',
      iconBg: 'bg-wheat-tint text-wheat-gold',
      badge: 'Rabi / Kharif'
    },
    {
      id: 'irrigation',
      icon: Droplets,
      title: t.actionIrrigation,
      subtitle: t.actionIrrigationSub,
      accent: 'border-water-border/80 hover:border-water-tone bg-white',
      iconBg: 'bg-water-surface text-water-tone',
      badge: 'FAO-56 Water'
    },
    {
      id: 'mandi',
      icon: TrendingUp,
      title: t.actionMandi,
      subtitle: t.actionMandiSub,
      accent: 'border-earth-border hover:border-wheat-gold bg-white',
      iconBg: 'bg-wheat-tint text-wheat-gold',
      badge: 'Ghalla Mandi'
    },
    {
      id: 'simulator',
      icon: Sparkles,
      title: t.actionSimulator,
      subtitle: t.actionSimulatorSub,
      accent: 'border-earth-border hover:border-wheat-gold bg-white',
      iconBg: 'bg-earth-surface text-ajrak-black',
      badge: 'What-If Engine'
    },
    {
      id: 'govt',
      icon: Building2,
      title: t.actionGovtSupport,
      subtitle: t.actionGovtSupportSub,
      accent: 'border-earth-border hover:border-wheat-gold bg-white',
      iconBg: 'bg-emerald-50 text-emerald-700',
      badge: 'Kisan Card'
    },
    {
      id: 'ask',
      icon: HelpCircle,
      title: t.actionAskQuestion,
      subtitle: t.actionAskQuestionSub,
      accent: 'border-wheat-border hover:border-wheat-gold bg-wheat-tint/40 col-span-full',
      iconBg: 'bg-wheat-gold text-white',
      badge: 'Decision Receipt'
    }
  ];

  return (
    <section className="space-y-2.5">
      <h2 className="text-xs font-bold uppercase tracking-wider text-ajrak-slate">
        Zarai Rehnumai • Direct Actions
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {actions.map(act => {
          const Icon = act.icon;
          return (
            <button
              key={act.id}
              onClick={() => onAction(act.id)}
              className={`p-4 rounded-2xl border text-left transition-all active:scale-[0.99] flex items-start gap-3.5 shadow-xs hover:shadow-sm ${act.accent}`}
            >
              <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 shadow-xs ${act.iconBg}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1 mb-0.5">
                  <h3 className="font-bold text-sm text-ajrak-black leading-snug truncate">
                    {act.title}
                  </h3>
                  <span className="text-[10px] font-semibold text-earth-muted px-1.5 py-0.5 bg-earth-surface border border-earth-border rounded shrink-0">
                    {act.badge}
                  </span>
                </div>
                <p className="text-xs text-earth-muted leading-tight line-clamp-2">
                  {act.subtitle}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
};
