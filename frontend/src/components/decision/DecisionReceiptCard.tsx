import React from 'react';
import { DecisionReceipt } from '../../api/types';
import { useLanguage } from '../../context/LanguageContext';
import { GroundingBadge } from '../common/GroundingBadge';
import { CheckCircle2, AlertTriangle, ShieldCheck, Sparkles, Share2, BookmarkCheck, ArrowRight, ExternalLink } from 'lucide-react';

interface DecisionReceiptCardProps {
  receipt: DecisionReceipt;
  onSave?: () => void;
  isSaved?: boolean;
  compact?: boolean;
  onOpenFull?: () => void;
}

export const DecisionReceiptCard: React.FC<DecisionReceiptCardProps> = ({
  receipt,
  onSave,
  isSaved = false,
  compact = false,
  onOpenFull
}) => {
  const { t, isRtl } = useLanguage();

  const getUrgencyBadge = () => {
    switch (receipt.urgency_level) {
      case 'CRITICAL':
        return <span className="bg-ochre-surface text-ochre-dark border border-ochre-border text-xs font-bold px-2 py-0.5 rounded">ZAROORI / CRITICAL</span>;
      case 'HIGH':
        return <span className="bg-amber-100 text-amber-900 border border-amber-300 text-xs font-semibold px-2 py-0.5 rounded">HIGH PRIORITY</span>;
      case 'MEDIUM':
        return <span className="bg-earth-surface text-earth-dark border border-earth-border text-xs font-medium px-2 py-0.5 rounded">MEDIUM</span>;
      default:
        return <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-medium px-2 py-0.5 rounded">NORMAL</span>;
    }
  };

  const handleShare = () => {
    const text = `🌾 *Kisan Dost Faisla Raseed (${receipt.receipt_id})*\n\n📌 *${receipt.action_title}*\n\n💡 *Kyun?*\n${receipt.key_rationale}\n\n📊 *Impact:* ${receipt.expected_impact}\n\n🔗 Grounding: ${receipt.evidence_grounding_summary}`;
    if (navigator.share) {
      navigator.share({ title: receipt.action_title, text }).catch(() => {});
    } else {
      window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
    }
  };

  if (compact) {
    return (
      <div
        onClick={onOpenFull}
        className="bg-earth-surface border border-earth-border rounded-xl p-4 hover:border-wheat-gold transition-all cursor-pointer shadow-xs hover:shadow-sm"
      >
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-1.5">
            {getUrgencyBadge()}
            <span className="text-xs text-earth-muted font-mono">{receipt.receipt_id}</span>
          </div>
          <GroundingBadge state={receipt.overall_verification_state} size="sm" />
        </div>

        <h3 className="font-bold text-base text-ajrak-black leading-snug mb-1.5">
          {receipt.action_title}
        </h3>

        <p className="text-xs text-earth-muted line-clamp-2 mb-3">
          {receipt.key_rationale}
        </p>

        <div className="flex items-center justify-between pt-2 border-t border-earth-border/60 text-xs text-earth-dark font-medium">
          <span className="text-wheat-dark font-semibold num-tabular">
            {receipt.overall_confidence_percent}% {t.confidenceLabel}
          </span>
          <span className="text-wheat-gold flex items-center gap-1">
            <span>Tafseel</span>
            <ArrowRight className={`w-3.5 h-3.5 ${isRtl ? 'rotate-180' : ''}`} />
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#FAF8F5] border-2 border-earth-border rounded-2xl shadow-sm overflow-hidden text-earth-dark">
      {/* Receipt Top Header */}
      <div className="bg-earth-surface/80 border-b border-earth-border px-5 py-3.5 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">🧾</span>
          <div>
            <span className="text-xs font-bold text-ajrak-black uppercase tracking-wider block">
              {t.receiptHeader}
            </span>
            <span className="text-[11px] text-earth-muted font-mono">
              {receipt.receipt_id}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {getUrgencyBadge()}
          <GroundingBadge state={receipt.overall_verification_state} size="sm" />
        </div>
      </div>

      <div className="p-5 space-y-4">
        {/* Action Title */}
        <div>
          <span className="text-xs font-semibold text-wheat-dark uppercase tracking-wider block mb-1">
            {receipt.action_category} • Recommendation
          </span>
          <h2 className="text-xl font-bold text-ajrak-black leading-tight">
            {receipt.action_title}
          </h2>
        </div>

        {/* Action Steps */}
        {receipt.action_steps && receipt.action_steps.length > 0 && (
          <div className="bg-white border border-earth-border/80 rounded-xl p-3.5">
            <h4 className="text-xs font-bold text-ajrak-black uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
              <span>{t.actionStepsTitle}</span>
            </h4>
            <ul className="space-y-2 text-xs text-earth-dark">
              {receipt.action_steps.map((step, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="w-4 h-4 rounded-full bg-wheat-tint text-wheat-dark flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="leading-relaxed">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Why this recommendation? (Concrete bullet factors) */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-bold text-ajrak-black uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-wheat-gold" />
            <span>{t.kyunTitle}</span>
          </h4>
          <div className="bg-earth-surface/50 border border-earth-border/70 rounded-xl p-3 text-xs leading-relaxed text-earth-dark">
            {receipt.key_rationale}
          </div>
        </div>

        {/* Financial Economics (If available) */}
        {(receipt.total_cost_pkr !== null && receipt.total_cost_pkr !== undefined) && (
          <div className="bg-earth-surface/60 border border-earth-border rounded-xl p-3 grid grid-cols-3 gap-2 text-center">
            <div className="border-r border-earth-border/80 pr-2">
              <span className="text-[11px] text-earth-muted block">{t.costLabel}</span>
              <span className="font-bold text-xs num-tabular text-earth-dark">
                PKR {receipt.total_cost_pkr?.toLocaleString()}
              </span>
            </div>
            <div className="border-r border-earth-border/80 px-2">
              <span className="text-[11px] text-earth-muted block">{t.revenueLabel}</span>
              <span className="font-bold text-xs num-tabular text-earth-dark">
                {receipt.expected_revenue_pkr ? `PKR ${receipt.expected_revenue_pkr?.toLocaleString()}` : '—'}
              </span>
            </div>
            <div className="pl-2">
              <span className="text-[11px] text-emerald-800 font-semibold block">{t.netProfitLabel}</span>
              <span className="font-bold text-xs num-tabular text-emerald-800">
                {receipt.net_financial_gain_pkr ? `+ PKR ${receipt.net_financial_gain_pkr?.toLocaleString()}` : '—'}
              </span>
            </div>
          </div>
        )}

        {/* Expected Impact */}
        <div className="text-xs text-earth-dark flex items-start gap-2 bg-emerald-50/70 border border-emerald-200/80 rounded-xl p-3">
          <ShieldCheck className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-emerald-900 block mb-0.5">{t.impactTitle}:</span>
            <span className="text-emerald-950 leading-relaxed">{receipt.expected_impact}</span>
          </div>
        </div>

        {/* Grounding & Evidence Footer */}
        <div className="pt-2 border-t border-dashed border-earth-border text-xs text-earth-muted space-y-1">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-earth-dark">
              {t.confidenceLabel}: <span className="num-tabular text-wheat-dark">{receipt.overall_confidence_percent}%</span>
            </span>
            <span>
              {receipt.grounded_items_count} Verified Factors
            </span>
          </div>
          <p className="text-[11px] text-earth-muted leading-tight">
            {receipt.evidence_grounding_summary}
          </p>
        </div>

        {/* Card Action Buttons */}
        <div className="pt-2 flex items-center gap-2">
          {onSave && (
            <button
              onClick={onSave}
              className={`flex-1 py-2.5 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                isSaved
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                  : 'bg-wheat-gold hover:bg-wheat-dark text-white border-transparent shadow-xs'
              }`}
            >
              <BookmarkCheck className="w-3.5 h-3.5" />
              <span>{isSaved ? t.savedToast : t.saveDecisionBtn}</span>
            </button>
          )}

          <button
            onClick={handleShare}
            className="py-2.5 px-3.5 rounded-xl border border-earth-border bg-white text-earth-dark hover:bg-earth-surface text-xs font-semibold flex items-center justify-center gap-1.5 transition-all"
            title="Share"
          >
            <Share2 className="w-3.5 h-3.5 text-earth-muted" />
            <span>Share</span>
          </button>
        </div>
      </div>
    </div>
  );
};
