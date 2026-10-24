import React, { useEffect } from 'react';
import { X, Scale, BookOpen, Users, ShieldAlert, Phone, Mail, LogIn, LogOut, FileText } from 'lucide-react';

export default function MobileMenu({
  isOpen,
  onClose,
  language,
  setLanguage,
  onOpenLawyers,
  onOpenStatutes,
  onOpenDrafter,
  onOpenEmergency,
  onOpenAuth,
  currentUser,
  onLogout
}) {
  // Close menu on ESC key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Lock body scroll when mobile menu is open to prevent background scrolling
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 lg:hidden flex">
      {/* Dark backdrop overlay */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity duration-300"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-out Menu Drawer */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Mobile Navigation"
        className="relative ml-auto w-full max-w-xs sm:max-w-sm h-full bg-slate-900 text-white z-50 shadow-2xl flex flex-col justify-between overflow-y-auto"
      >
        {/* Drawer Header */}
        <div>
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <a
              href="/"
              onClick={(e) => {
                e.preventDefault();
                onClose();
              }}
              className="flex items-center gap-2.5 text-emerald-400 group"
              aria-label="LawerAI Home"
            >
              <div className="w-8 h-8 rounded-lg bg-emerald-950 border border-emerald-700/60 flex items-center justify-center text-emerald-400 shadow-inner">
                <Scale className="w-4 h-4" aria-hidden="true" />
              </div>
              <div>
                <span className="font-serif font-bold text-base tracking-tight text-white group-hover:text-emerald-300 transition">
                  LawerAI
                </span>
                <span className="block text-[10px] text-emerald-400 font-sans">
                  By Maverick Tech Ventures
                </span>
              </div>
            </a>

            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              aria-label="Close navigation menu"
            >
              <X className="w-5 h-5" aria-hidden="true" />
            </button>
          </div>

          {/* Navigation Links */}
          <div className="p-4 space-y-2">
            <p className="text-[10px] uppercase font-bold tracking-wider text-slate-500 px-3">
              Core Legal Modules
            </p>

            <button
              type="button"
              onClick={() => {
                if (onOpenDrafter) onOpenDrafter();
                onClose();
              }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl bg-emerald-900/50 border border-emerald-700/60 hover:bg-emerald-800 text-left text-sm font-bold text-white transition cursor-pointer"
            >
              <FileText className="w-4 h-4 text-emerald-300 flex-shrink-0" aria-hidden="true" />
              <div>
                <span>AI Court Petition Drafter</span>
                <span className="block text-[10px] text-emerald-300 font-normal">Generate 22-A, 489-F & Stay notices</span>
              </div>
            </button>

            <button
              type="button"
              onClick={() => {
                onOpenStatutes();
                onClose();
              }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-slate-800 text-left text-sm font-medium text-slate-200 hover:text-emerald-400 transition"
            >
              <BookOpen className="w-4 h-4 text-emerald-400 flex-shrink-0" aria-hidden="true" />
              <span>Statutory Law Library</span>
            </button>

            <button
              type="button"
              onClick={() => {
                onOpenLawyers();
                onClose();
              }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-slate-800 text-left text-sm font-medium text-slate-200 hover:text-emerald-400 transition"
            >
              <Users className="w-4 h-4 text-emerald-400 flex-shrink-0" aria-hidden="true" />
              <span>Find a Licensed Advocate</span>
            </button>

            <button
              type="button"
              onClick={() => {
                onOpenEmergency();
                onClose();
              }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl bg-red-950/40 border border-red-900/50 hover:bg-red-950/70 text-left text-sm font-medium text-red-200 transition"
            >
              <ShieldAlert className="w-4 h-4 text-red-400 flex-shrink-0" aria-hidden="true" />
              <div>
                <span className="block font-bold">Emergency Helplines</span>
                <span className="block text-[11px] text-red-300">Police 15 • Rescue 1122</span>
              </div>
            </button>
          </div>

          {/* Language Selection */}
          <div className="p-4 border-t border-slate-800">
            <p className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-2 px-1">
              Language / زبان
            </p>
            <div className="grid grid-cols-3 gap-1.5 bg-slate-800/80 p-1 rounded-xl text-xs">
              <button
                type="button"
                onClick={() => setLanguage('en')}
                className={`py-1.5 px-2 rounded-lg font-medium transition ${
                  language === 'en' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                English
              </button>
              <button
                type="button"
                onClick={() => setLanguage('ur')}
                className={`py-1.5 px-2 rounded-lg font-urdu font-medium transition ${
                  language === 'ur' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                اردو
              </button>
              <button
                type="button"
                onClick={() => setLanguage('roman_ur')}
                className={`py-1.5 px-2 rounded-lg font-medium transition ${
                  language === 'roman_ur' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Roman
              </button>
            </div>
          </div>
        </div>

        {/* Drawer Footer: Direct Contact & Account */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60 space-y-3">
          <div className="space-y-1.5 text-xs">
            {/* Clickable Phone Number */}
            <a
              href="tel:+923273202419"
              className="flex items-center gap-2.5 p-2 rounded-lg text-slate-300 hover:text-emerald-400 hover:bg-slate-800/60 transition"
              aria-label="Call LawerAI Support at +923273202419"
            >
              <Phone className="w-4 h-4 text-emerald-400 flex-shrink-0" aria-hidden="true" />
              <span>+92 327 3202419 (Direct Support)</span>
            </a>

            {/* Clickable Email */}
            <a
              href="mailto:ahmedmansoorrind1210@gmail.com"
              className="flex items-center gap-2.5 p-2 rounded-lg text-slate-300 hover:text-emerald-400 hover:bg-slate-800/60 transition"
              aria-label="Email LawerAI at ahmedmansoorrind1210@gmail.com"
            >
              <Mail className="w-4 h-4 text-emerald-400 flex-shrink-0" aria-hidden="true" />
              <span>ahmedmansoorrind1210@gmail.com</span>
            </a>
          </div>

          {/* User Sign In / Out */}
          {currentUser ? (
            <div className="pt-2 flex items-center justify-between">
              <span className="text-xs text-slate-400 truncate">
                {currentUser.full_name || currentUser.email}
              </span>
              <button
                type="button"
                onClick={() => {
                  onLogout();
                  onClose();
                }}
                className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition"
              >
                <LogOut className="w-3.5 h-3.5" aria-hidden="true" />
                <span>Sign Out</span>
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => {
                onOpenAuth();
                onClose();
              }}
              className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-sm transition"
            >
              <LogIn className="w-4 h-4" aria-hidden="true" />
              <span>Sign In / Create Account</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
