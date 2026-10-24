import React from 'react';
import { Home, Search, BookOpen, Users, ShieldAlert, ArrowLeft } from 'lucide-react';

export default function NotFoundPage({ onReturnHome, onOpenStatutes, onOpenLawyers }) {
  return (
    <div className="flex-1 flex items-center justify-center p-6 bg-slate-100 min-h-[60vh]">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-xl w-full p-8 text-center space-y-6">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-800 border border-emerald-200 shadow-inner">
          <span className="font-serif font-black text-2xl">404</span>
        </div>

        <div>
          <h2 className="text-2xl font-serif font-bold text-slate-900 mb-2">
            Legal Resource Not Found
          </h2>
          <p className="text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
            The legal section, case link, or directory route you attempted to access may have moved, been re-indexed, or is currently unavailable.
          </p>
        </div>

        {/* Quick Navigations */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
          <button
            type="button"
            onClick={onReturnHome}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition group"
          >
            <Home className="w-5 h-5 text-emerald-600 group-hover:scale-110 transition flex-shrink-0" />
            <div>
              <span className="block text-xs font-bold text-slate-900">Case Intake Hub</span>
              <span className="block text-[11px] text-slate-500">Return to active consultation</span>
            </div>
          </button>

          <button
            type="button"
            onClick={onOpenStatutes}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition group"
          >
            <BookOpen className="w-5 h-5 text-emerald-600 group-hover:scale-110 transition flex-shrink-0" />
            <div>
              <span className="block text-xs font-bold text-slate-900">Statutory Corpus</span>
              <span className="block text-[11px] text-slate-500">Search PPC, CrPC, CPC laws</span>
            </div>
          </button>

          <button
            type="button"
            onClick={onOpenLawyers}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition group"
          >
            <Users className="w-5 h-5 text-emerald-600 group-hover:scale-110 transition flex-shrink-0" />
            <div>
              <span className="block text-xs font-bold text-slate-900">Bar Directory</span>
              <span className="block text-[11px] text-slate-500">Find licensed advocates</span>
            </div>
          </button>

          <a
            href="tel:15"
            className="flex items-center gap-3 p-3.5 rounded-xl border border-red-200 bg-red-50/50 hover:bg-red-50 transition group"
          >
            <ShieldAlert className="w-5 h-5 text-red-600 group-hover:scale-110 transition flex-shrink-0" />
            <div>
              <span className="block text-xs font-bold text-red-900">Police Emergency 15</span>
              <span className="block text-[11px] text-red-600">Immediate crisis assistance</span>
            </div>
          </a>
        </div>

        <div className="pt-4 border-t border-slate-100 flex justify-center">
          <button
            type="button"
            onClick={onReturnHome}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to LawerAI Home</span>
          </button>
        </div>
      </div>
    </div>
  );
}
