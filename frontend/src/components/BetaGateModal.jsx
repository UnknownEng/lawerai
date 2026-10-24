import React, { useState } from 'react';
import { ShieldCheck, KeyRound, ArrowRight, Loader2, AlertCircle, Sparkles, Check } from 'lucide-react';
import { api } from '../api';

export default function BetaGateModal({ isOpen, onSuccess }) {
  const [code, setCode] = useState('LAWERAI-2026');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e, directCode = null) => {
    if (e && e.preventDefault) e.preventDefault();
    const codeToVerify = (directCode || code || '').trim();
    if (!codeToVerify) {
      setError('Please enter a valid beta code.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await api.verifyBetaCode(codeToVerify);
      onSuccess(codeToVerify);
    } catch (err) {
      setError(err.message || 'Invalid beta invitation code. Please use LAWERAI-2026 or QANOON-BETA-2026.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickUnlock = (selectedCode) => {
    setCode(selectedCode);
    handleSubmit(null, selectedCode);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 sm:p-8 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center flex-shrink-0">
            <KeyRound className="w-6 h-6 text-emerald-700" />
          </div>
          <div>
            <span className="text-[11px] font-bold tracking-wider uppercase px-2 py-0.5 rounded bg-emerald-100 text-emerald-900">
              LawerAI Access
            </span>
            <h2 className="text-xl font-bold text-slate-900 mt-0.5">
              Enter Beta Access Code
            </h2>
          </div>
        </div>

        <p className="text-sm text-slate-600 mb-4 leading-relaxed">
          Welcome to LawerAI by Maverick Tech Ventures. To start your legal consultation, statutory analysis, or document drafting session, enter your invitation code below.
        </p>

        {/* 1-Click Instant Unlock Banner */}
        <div className="mb-5 p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900">
            <Sparkles className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>Active Beta Invitation Codes:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => handleQuickUnlock('LAWERAI-2026')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-mono text-xs font-bold transition shadow-xs active:scale-95"
            >
              <Check className="w-3.5 h-3.5" />
              <span>LAWERAI-2026 (Recommended)</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickUnlock('QANOON-BETA-2026')}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white border border-emerald-300 text-emerald-800 hover:bg-emerald-100 font-mono text-xs font-medium transition"
            >
              <span>QANOON-BETA-2026</span>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              Access Code
            </label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="LAWERAI-2026"
              className="w-full px-4 py-3 border border-slate-300 rounded-xl text-base tracking-wider font-mono uppercase focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 focus:outline-hidden transition"
              autoFocus
              required
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2.5 text-xs text-red-800">
              <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !code.trim()}
            className="w-full py-3 px-4 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition shadow-md cursor-pointer"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Verifying Access...</span>
              </>
            ) : (
              <>
                <span>Enter Legal Portal</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-5 pt-4 border-t border-slate-100 text-center text-xs text-slate-500">
          Official access code: <strong className="text-emerald-800 font-mono">LAWERAI-2026</strong>. Click the green button above to enter immediately.
        </div>
      </div>
    </div>
  );
}
