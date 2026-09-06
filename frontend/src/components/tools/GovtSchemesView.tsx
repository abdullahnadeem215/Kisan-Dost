import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useFarm } from '../../context/FarmContext';
import { GovtSupportReport } from '../../api/types';
import { apiClient } from '../../api/client';
import { Building2, CheckCircle2, XCircle, Phone, FileText, ExternalLink } from 'lucide-react';

export const GovtSchemesView: React.FC = () => {
  const { t } = useLanguage();
  const { profile } = useFarm();

  const [report, setReport] = useState<GovtSupportReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchSchemes = async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.getGovtSchemes(profile.district, profile.total_land_acres);
        setReport(res);
      } catch (err) {
        console.warn('Error loading govt schemes:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSchemes();
  }, [profile.district, profile.total_land_acres]);

  return (
    <div className="space-y-4 max-w-xl mx-auto py-2">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-ajrak-black flex items-center gap-2">
          <Building2 className="w-5 h-5 text-emerald-700" />
          <span>{t.actionGovtSupport}</span>
        </h2>
        <p className="text-xs text-earth-muted mt-0.5">
          Punjab Agriculture Department & Federal Certified Schemes for {profile.total_land_acres} Acres in {profile.district}
        </p>
      </div>

      {/* Eligible Schemes List */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-700" />
          <span>Aap Ki Zameen Ke Liye Qabil-e-Amal (Eligible Schemes)</span>
        </h3>

        {report?.eligible_schemes?.map(scheme => (
          <div
            key={scheme.scheme_id}
            className="bg-white border-2 border-emerald-200/80 rounded-2xl p-4 space-y-3 shadow-xs"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <h4 className="font-bold text-base text-ajrak-black leading-snug">
                  {scheme.scheme_name}
                </h4>
                <span className="text-xs text-emerald-800 font-semibold block mt-0.5">
                  {scheme.implementing_agency}
                </span>
              </div>
              <span className="text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-300 px-2 py-0.5 rounded-full shrink-0">
                ELIGIBLE
              </span>
            </div>

            <div className="bg-emerald-50/60 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-950 font-medium">
              💰 Financial Benefit: <span className="font-bold text-emerald-900">{scheme.financial_benefit}</span>
            </div>

            {/* Key Requirements & Documents */}
            <div className="text-xs space-y-1.5 text-earth-dark">
              <span className="font-bold text-earth-dark block">Zaroori Asnaad (Documents):</span>
              <ul className="space-y-1 text-[11px] text-earth-muted">
                {scheme.required_documents.map((doc, idx) => (
                  <li key={idx} className="flex items-center gap-1.5">
                    <FileText className="w-3 h-3 text-emerald-700 shrink-0" />
                    <span>{doc}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Helpline / Link */}
            <div className="pt-2 border-t border-earth-border/60 flex items-center justify-between text-xs">
              <span className="text-earth-muted font-medium flex items-center gap-1.5">
                <Phone className="w-3.5 h-3.5 text-emerald-700" />
                <span>Helpline: 0800-17000</span>
              </span>
              <span className="text-wheat-gold font-bold flex items-center gap-1">
                <span>Direct Apply</span>
                <ExternalLink className="w-3 h-3" />
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Ineligible Schemes (if any) */}
      {report && report.ineligible_schemes?.length > 0 && (
        <div className="space-y-2 pt-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-earth-muted flex items-center gap-1.5">
            <XCircle className="w-3.5 h-3.5 text-earth-muted" />
            <span>Ghair-Ahil (Ineligible) Schemes</span>
          </h3>
          {report.ineligible_schemes.map((ine, i) => (
            <div key={i} className="bg-earth-surface/50 border border-earth-border rounded-xl p-3 text-xs text-earth-muted">
              <span className="font-bold text-earth-dark block">{ine.scheme_name}</span>
              <span>{ine.reason}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
