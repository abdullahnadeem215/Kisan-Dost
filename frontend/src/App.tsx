import React, { useState } from 'react';
import { useFarm } from './context/FarmContext';
import { Header } from './components/common/Header';
import { ConversationalSetup } from './components/onboarding/ConversationalSetup';
import { ZaraiChatBot } from './components/chat/ZaraiChatBot';
import { FarmPassportModal } from './components/profile/FarmPassportModal';
import { DecisionReceiptCard } from './components/decision/DecisionReceiptCard';
import { X } from 'lucide-react';

export const App: React.FC = () => {
  const {
    isSetupComplete,
    selectedReceipt,
    closeReceiptModal,
    saveDecision
  } = useFarm();

  const [isPassportOpen, setIsPassportOpen] = useState<boolean>(false);

  // If first-time user, render Conversational Progressive Setup (with Farmer Name & SQLite save)
  if (!isSetupComplete) {
    return <ConversationalSetup />;
  }

  return (
    <div className="h-dvh flex flex-col bg-earth-ground text-earth-dark selection:bg-wheat-gold selection:text-white overflow-hidden">
      {/* Sticky Top Header */}
      <Header onOpenPassport={() => setIsPassportOpen(true)} />

      {/* Main Conversational Farm Dashboard: Full-Height, Zero Overlap */}
      <main className="flex-1 w-full max-w-2xl mx-auto flex flex-col min-h-0 overflow-hidden px-2 sm:px-4 py-2">
        <ZaraiChatBot />
      </main>

      {/* Farm Passport SQLite Viewer / Editor Modal */}
      <FarmPassportModal
        isOpen={isPassportOpen}
        onClose={() => setIsPassportOpen(false)}
      />

      {/* Decision Receipt Full Detail Modal */}
      {selectedReceipt && (
        <div className="fixed inset-0 z-50 bg-ajrak-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-lg max-h-[88vh] overflow-y-auto space-y-2 pb-6">
            <div className="flex justify-end">
              <button
                onClick={closeReceiptModal}
                className="p-1.5 rounded-full bg-white text-ajrak-black hover:bg-earth-surface shadow-md cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <DecisionReceiptCard
              receipt={selectedReceipt}
              isSaved={true}
              onSave={() => saveDecision(selectedReceipt)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

