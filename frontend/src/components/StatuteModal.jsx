import React, { useState, useEffect } from 'react';
import { X, BookOpen, Scale, FileText, CheckCircle2, Shield, AlertCircle } from 'lucide-react';
import { api } from '../api';

export default function StatuteModal({ statute, onClose }) {
  const [detail, setDetail] = useState(statute || null);
  const [loading, setLoading] = useState(!statute?.statutory_text);

  useEffect(() => {
    if (statute && !statute.statutory_text) {
      loadFullSection(statute.id);
    } else {
      setDetail(statute);
    }
  }, [statute]);

  const loadFullSection = async (sectionId) => {
    setLoading(true);
    try {
      const data = await api.getSectionDetail(sectionId);
      setDetail(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!statute) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 bg-legal-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-legal-800 text-emerald-400">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                  {detail?.act_code} Section {detail?.section_number}
                </span>
                <span className="text-[11px] bg-legal-800 text-slate-300 px-2 py-0.5 rounded">
                  {detail?.jurisdiction || 'Federal'}
                </span>
              </div>
              <h2 className="text-base sm:text-lg font-bold text-white mt-0.5">
                {detail?.section_title}
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-legal-300 hover:text-white hover:bg-legal-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
          {/* Classification Tags */}
          <div className="flex flex-wrap gap-2">
            {detail?.cognizable && (
              <span className="bg-slate-100 text-slate-800 px-2.5 py-1 rounded-md font-medium border border-slate-200">
                Cognizability: <strong>{detail.cognizable}</strong>
              </span>
            )}
            {detail?.bailable && (
              <span className="bg-slate-100 text-slate-800 px-2.5 py-1 rounded-md font-medium border border-slate-200">
                Bail: <strong>{detail.bailable}</strong>
              </span>
            )}
            {detail?.forum_court && (
              <span className="bg-legal-50 text-legal-900 px-2.5 py-1 rounded-md font-medium border border-legal-200">
                Court Forum: <strong>{detail.forum_court}</strong>
              </span>
            )}
          </div>

          {/* Plain Language Explanation */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-legal-700" />
              Plain-Language Explanation (English)
            </h4>
            <p className="text-slate-700 leading-relaxed text-xs">
              {detail?.summary_plain}
            </p>

            {detail?.summary_urdu && (
              <div className="mt-3 pt-3 border-t border-slate-200">
                <h4 className="font-bold text-slate-900 text-xs font-urdu mb-1">
                  آسان اردو میں مفہوم:
                </h4>
                <p className="text-slate-800 leading-loose text-xs font-urdu" dir="rtl">
                  {detail.summary_urdu}
                </p>
              </div>
            )}
          </div>

          {/* Statutory Verbatim Text */}
          {detail?.statutory_text && (
            <div className="bg-slate-900 text-slate-100 p-4 rounded-xl font-mono text-[11px] leading-relaxed border border-slate-800">
              <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-2 font-sans flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5" />
                Official Statutory Provision Text
              </div>
              <div className="whitespace-pre-wrap">{detail.statutory_text}</div>
            </div>
          )}

          {/* Penalty / Remedy */}
          {detail?.punishment && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900">
              <strong className="block font-semibold mb-0.5">Statutory Penalty / Remedy:</strong>
              <span>{detail.punishment}</span>
            </div>
          )}

          {/* Evidence Checklist */}
          {detail?.evidence_required && detail.evidence_required.length > 0 && (
            <div>
              <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                Typical Evidence Required in Pakistani Courts
              </h4>
              <ul className="space-y-1 pl-4 list-disc text-slate-600">
                {detail.evidence_required.map((ev, i) => (
                  <li key={i}>{ev}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Practical Next Steps */}
          {detail?.practical_steps && detail.practical_steps.length > 0 && (
            <div>
              <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-legal-700" />
                Recommended Procedural Steps
              </h4>
              <ol className="space-y-1.5 pl-4 list-decimal text-slate-700 font-medium">
                {detail.practical_steps.map((st, i) => (
                  <li key={i} className="leading-relaxed">{st}</li>
                ))}
              </ol>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Source: National Laws of Pakistan (Authentic Corpus)</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-legal-900 hover:bg-legal-800 text-white font-medium transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
