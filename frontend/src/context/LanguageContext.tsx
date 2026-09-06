import React, { createContext, useContext, useState, useEffect } from 'react';
import { LanguageCode, translations, Translations } from '../i18n/translations';

interface LanguageContextType {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  t: Translations;
  isRtl: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<LanguageCode>(() => {
    const saved = localStorage.getItem('kisan_dost_lang');
    return (saved as LanguageCode) || 'roman_urdu';
  });

  const setLanguage = (lang: LanguageCode) => {
    setLanguageState(lang);
    localStorage.setItem('kisan_dost_lang', lang);
  };

  const isRtl = language === 'ur';

  useEffect(() => {
    document.documentElement.dir = isRtl ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
    if (isRtl) {
      document.body.classList.add('font-urdu');
    } else {
      document.body.classList.remove('font-urdu');
    }
  }, [language, isRtl]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t: translations[language], isRtl }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
