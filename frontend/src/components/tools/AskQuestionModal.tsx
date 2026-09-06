import React, { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { apiClient } from '../../api/client';
import { DecisionReceiptCard } from '../decision/DecisionReceiptCard';
import { DecisionReceipt } from '../../api/types';
import { HelpCircle, Send, X, RefreshCw } from 'lucide-react';

interface AskQuestionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AskQuestionModal: React.FC<AskQuestionModalProps> = ({ isOpen, onClose }) => {
  const { t } = useLanguage();
  const { profile, saveDecision, openReceiptModal } = useFarm();

  const [query, setQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [receipt, setReceipt] = useState<DecisionReceipt | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (queryText: string) => {
    const q = (queryText || query).trim();
    if (!q) return;

    setIsLoading(true);
    setReceipt(null);
    try {
      const res = await apiClient.queryAdvisory(q, profile);
      if (res.receipt) {
        setReceipt(res.receipt);
        saveDecision(res.receipt);
      }
    } catch (err) {
      console.warn('Error querying advisory:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const sampleQuestions = [
    t.sampleQ1,
    t.sampleQ2,
    t.sampleQ3,
  ];

  return (
    <div className="fixed inset-0 z-50 bg-ajrak-black/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-earth-ground border border-earth-border rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-5 shadow-lg space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-earth-border">
          <div className="flex items-center gap-2">
            <span className="text-xl">💬</span>
            <h3 className="font-bold text-base text-ajrak-black">{t.askTitle}</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-earth-surface text-earth-muted">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Text Input */}
        <div className="space-y-2">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t.askPlaceholder}
            rows={3}
            className="w-full p-3.5 bg-white border border-earth-border rounded-xl text-xs font-medium text-ajrak-black focus:border-wheat-gold resize-none"
          />

          {/* Sample Chips */}
          <div className="flex flex-wrap gap-1.5">
            {sampleQuestions.map((sq, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(sq);
                  handleSubmit(sq);
                }}
                className="text-[11px] font-medium text-earth-dark bg-earth-surface hover:bg-wheat-tint hover:text-wheat-dark border border-earth-border rounded-full px-2.5 py-1 transition-colors text-left"
              >
                {sq}
              </button>
            ))}
          </div>

          <button
            onClick={() => handleSubmit(query)}
            disabled={isLoading || !query.trim()}
            className="w-full py-3 px-4 rounded-xl bg-wheat-gold hover:bg-wheat-dark disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-xs transition-all"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Multi-Agent Engine Investigating...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>{t.submitQuestionBtn}</span>
              </>
            )}
          </button>
        </div>

        {/* Resulting Decision Receipt */}
        {receipt && (
          <div className="pt-2">
            <DecisionReceiptCard
              receipt={receipt}
              isSaved={true}
              onSave={() => saveDecision(receipt)}
            />
          </div>
        )}
      </div>
    </div>
  );
};
