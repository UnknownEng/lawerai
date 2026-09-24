import React, { useState } from 'react';
import { ShieldCheck, KeyRound, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../api';

export default function BetaGateModal({ isOpen, onSuccess }) {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!code.trim()) {
      setError('Please enter a valid beta code.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await api.verifyBetaCode(code.trim());
      onSuccess(code.trim());
    } catch (err) {
      setError(err.message || 'Invalid beta invitation code. Please check with your invite administrator.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 sm:p-8 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center flex-shrink-0">
            <KeyRound className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-bold tracking-wider uppercase px-2 py-0.5 rounded bg-amber-100 text-amber-900">
              Private Legal Beta
            </span>
            <h2 className="text-xl font-bold text-slate-900 mt-0.5">
              Enter Beta Invite Code
            </h2>
          </div>
        </div>

        <p className="text-sm text-slate-600 mb-6 leading-relaxed">
          Qanoon Sahayak is currently in closed evaluation with qualified Pakistani advocates and researchers. 
          Enter your invitation code to access the consultation portal.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              Beta Access Code
            </label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="e.g. QANOON-BETA-2026"
              className="w-full px-4 py-3 border border-slate-300 rounded-xl text-base tracking-wider font-mono uppercase focus:ring-2 focus:ring-legal-600 focus:border-legal-600 focus:outline-hidden transition"
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
            className="w-full py-3 px-4 bg-legal-900 hover:bg-legal-800 disabled:opacity-50 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition shadow-md"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Verifying Invitation...</span>
              </>
            ) : (
              <>
                <span>Enter Beta Consultation</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-100 text-center text-xs text-slate-500">
          Need an invite code? Qualified advocates can request access via the repository maintainers.
        </div>
      </div>
    </div>
  );
}
