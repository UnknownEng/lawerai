import React from 'react';
import { Scale, AlertTriangle, BookOpen, Users, LogIn, LogOut, Phone, Mail, Menu } from 'lucide-react';

export default function Header({
  language,
  setLanguage,
  onOpenLawyers,
  onOpenEmergency,
  onOpenStatutes,
  onOpenDrafter,
  onOpenAuth,
  onOpenMobileMenu,
  currentUser,
  onLogout
}) {
  const isUrdu = language === 'ur';

  return (
    <header className="bg-legal-900 text-white border-b border-legal-800 sticky top-0 z-30 shadow-md">
      {/* Persistent Legal Disclaimer Banner */}
      <div className="bg-amber-600/90 text-amber-50 px-4 py-1.5 text-xs flex items-center justify-between text-center font-medium">
        <div className="flex-1 flex items-center justify-center gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
          <span>
            {isUrdu
              ? "قانونی معلومات، قانونی مشورہ نہیں۔ عدالت میں کارروائی یا نمائندگی کے لیے بار کونسل سے رجسٹرڈ وکیل سے رجوع کریں۔"
              : "Legal information, not legal advice. Always consult a licensed Advocate of the Bar Council for formal representation."}
          </span>
        </div>
        <a
          href="tel:15"
          className="bg-red-700 hover:bg-red-800 text-white px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider ml-2 flex items-center gap-1 shadow-sm transition active:scale-95"
          aria-label="Call Police Emergency 15 immediately"
        >
          <span>Emergency 15</span>
        </a>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Clickable Logo & Brand */}
        <a
          href="/"
          className="flex items-center gap-3 group focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded-lg p-1"
          aria-label="LawerAI Home"
        >
          <div className="w-10 h-10 rounded-lg bg-legal-800 border border-legal-700 flex items-center justify-center text-emerald-400 shadow-inner group-hover:border-emerald-500 transition">
            <Scale className="w-6 h-6" aria-hidden="true" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-serif font-bold text-lg sm:text-xl tracking-tight text-emerald-50 group-hover:text-emerald-300 transition">
                LawerAI
              </h1>
              <span className="hidden sm:inline-block font-urdu text-emerald-300 text-sm">
                قانون معاون
              </span>
            </div>
            <p className="text-[11px] text-legal-300 font-sans">
              By Maverick Tech Ventures • Pakistani Legal Intelligence
            </p>
          </div>
        </a>

        {/* Navigation & Contact Utilities */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Clickable Phone (Desktop) */}
          <a
            href="tel:+923273202419"
            className="hidden xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-legal-800/60 hover:bg-legal-700 text-emerald-200 hover:text-white border border-legal-700/80 text-xs font-medium transition"
            aria-label="Call LawerAI Support at +923273202419"
          >
            <Phone className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
            <span>+92 327 3202419</span>
          </a>

          {/* Clickable Email (Desktop) */}
          <a
            href="mailto:ahmedmansoorrind1210@gmail.com"
            className="hidden 2xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-legal-800/60 hover:bg-legal-700 text-emerald-200 hover:text-white border border-legal-700/80 text-xs font-medium transition"
            aria-label="Email LawerAI Support"
          >
            <Mail className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
            <span>ahmedmansoorrind1210@gmail.com</span>
          </a>

          {/* Language Selector (Hidden on tiny screens; available in mobile menu) */}
          <div className="hidden sm:flex items-center bg-legal-800/80 rounded-lg p-0.5 border border-legal-700 text-xs">
            <button
              type="button"
              onClick={() => setLanguage('en')}
              className={`px-2.5 py-1 rounded-md transition-all font-medium ${
                language === 'en' ? 'bg-legal-600 text-white shadow-sm' : 'text-legal-300 hover:text-white'
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => setLanguage('ur')}
              className={`px-2.5 py-1 rounded-md transition-all font-urdu font-medium ${
                language === 'ur' ? 'bg-legal-600 text-white shadow-sm' : 'text-legal-300 hover:text-white'
              }`}
            >
              اردو
            </button>
            <button
              type="button"
              onClick={() => setLanguage('roman_ur')}
              className={`px-2.5 py-1 rounded-md transition-all font-medium ${
                language === 'roman_ur' ? 'bg-legal-600 text-white shadow-sm' : 'text-legal-300 hover:text-white'
              }`}
            >
              Roman
            </button>
          </div>

          {/* AI Legal Drafter Quick Trigger */}
          <button
            type="button"
            onClick={onOpenDrafter}
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs transition active:scale-95 cursor-pointer"
            title="Auto-Draft Court Petitions & Legal Notices"
          >
            <BookOpen className="w-3.5 h-3.5 text-emerald-200" aria-hidden="true" />
            <span>AI Petition Drafter</span>
          </button>

          {/* Quick Modals (Desktop) */}
          <button
            type="button"
            onClick={onOpenLawyers}
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-legal-800 hover:bg-legal-700 text-xs font-medium text-emerald-200 border border-legal-700 transition"
            title="Find a Licensed Lawyer or Legal Aid Clinic"
          >
            <Users className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Find a Lawyer</span>
          </button>

          <button
            type="button"
            onClick={onOpenStatutes}
            className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-legal-800 hover:bg-legal-700 text-xs font-medium text-emerald-200 border border-legal-700 transition"
            title="Search Pakistani Statutes"
          >
            <BookOpen className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Law Library</span>
          </button>

          {/* User Auth */}
          {currentUser ? (
            <div className="flex items-center gap-2">
              <span className="hidden sm:inline-block text-xs text-legal-200 font-medium">
                {currentUser.full_name || currentUser.email.split('@')[0]}
              </span>
              <button
                type="button"
                onClick={onLogout}
                className="p-1.5 rounded-lg bg-legal-800 hover:bg-legal-700 text-legal-300 hover:text-white border border-legal-700 transition"
                title="Sign Out"
                aria-label="Sign Out"
              >
                <LogOut className="w-4 h-4" aria-hidden="true" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenAuth}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium shadow-sm transition"
            >
              <LogIn className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Sign In</span>
            </button>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            type="button"
            onClick={onOpenMobileMenu}
            className="lg:hidden p-2 rounded-lg bg-legal-800 hover:bg-legal-700 text-emerald-300 hover:text-white border border-legal-700 transition"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </header>
  );
}
