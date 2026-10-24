import React from 'react';
import { X, BookOpen, Scale, ExternalLink, Bookmark, CheckCircle, Shield } from 'lucide-react';

export default function PrecedentModal({ precedent, isOpen, onClose }) {
  if (!isOpen || !precedent) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="p-5 bg-legal-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-legal-800 text-emerald-400">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700/60">
                Pakistani Case Law Precedent
              </span>
              <h2 className="text-lg font-serif font-bold text-white mt-1">
                {precedent.citation}
              </h2>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-legal-300 hover:text-white hover:bg-legal-800 transition"
            aria-label="Close Precedent Viewer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs sm:text-sm">
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Case Cause Title
            </span>
            <h3 className="text-base font-bold text-slate-900">
              {precedent.title || "Landmark Judgment of the Superior Judiciary"}
            </h3>
            <span className="text-xs text-slate-500">
              Supreme Court of Pakistan / High Court Binding Authority
            </span>
          </div>

          <div className="p-4 bg-emerald-50/70 border border-emerald-200/80 rounded-xl space-y-2">
            <span className="text-[11px] font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
              <Bookmark className="w-4 h-4 text-emerald-700" />
              <span>Ratio Decidendi (Core Legal Principle)</span>
            </span>
            <p className="text-emerald-950 leading-relaxed font-serif text-sm">
              "{precedent.ratio}"
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider">
              Legal Binding Effect & Precedential Weight
            </h4>
            <p className="text-slate-600 leading-relaxed text-xs">
              Under <strong>Article 189 of the Constitution of Pakistan (1973)</strong>, any decision of the Supreme Court shall, to the extent that it decides a question of law or is based upon or enunciates a principle of law, be binding on all other courts in Pakistan.
            </p>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs text-slate-700">
            <strong className="block text-slate-900">How to use this in your case:</strong>
            <ul className="list-disc pl-4 space-y-1 text-slate-600">
              <li>Cite this judgment in your written reply, bail petition, or plaint.</li>
              <li>Provide a copy of the reported citation from SCMR/PLD to your presiding magistrate or judge.</li>
              <li>Use the judicial ratio to substantiate lack of criminal mens rea, right to bail, or entitlement to stay.</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-emerald-600" />
            <span>Official Law Reporter Citation</span>
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-legal-900 text-white font-semibold hover:bg-legal-800 transition shadow-xs"
          >
            Close Precedent
          </button>
        </div>
      </div>
    </div>
  );
}
