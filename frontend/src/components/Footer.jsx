import React from 'react';
import { Scale, Phone, Mail, MapPin, Shield, FileText, ExternalLink, HeartHandshake } from 'lucide-react';

export default function Footer({
  onOpenStatutes,
  onOpenLawyers,
  onOpenEmergency
}) {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900 text-slate-300 border-t border-slate-800 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 lg:py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
          {/* Brand & Purpose Column */}
          <div className="space-y-4">
            <a
              href="/"
              className="inline-flex items-center gap-2.5 text-white group"
              aria-label="LawerAI Home"
            >
              <div className="w-9 h-9 rounded-lg bg-emerald-950 border border-emerald-600/60 flex items-center justify-center text-emerald-400 shadow-inner group-hover:scale-105 transition">
                <Scale className="w-5 h-5" aria-hidden="true" />
              </div>
              <div>
                <span className="font-serif font-bold text-lg tracking-tight text-white group-hover:text-emerald-300 transition">
                  LawerAI
                </span>
                <span className="block text-[10px] text-emerald-400 font-sans uppercase tracking-wider font-semibold">
                  By Maverick Tech Ventures
                </span>
              </div>
            </a>
            <p className="text-slate-400 text-xs leading-relaxed">
              Empowering citizens, advocates, and researchers with AI-augmented Pakistani statutory jurisprudence, structured case intake, and verified legal aid directories. Developed by Maverick Tech Ventures.
            </p>
            <div className="flex items-center gap-2 text-slate-400 text-xs pt-1">
              <Shield className="w-4 h-4 text-emerald-400 flex-shrink-0" aria-hidden="true" />
              <span>AES-256 Encrypted & Bar Compliant</span>
            </div>
          </div>

          {/* Column 1: Statutory Corpus */}
          <div>
            <h4 className="font-semibold text-white uppercase tracking-wider text-[11px] mb-3.5">
              Statutory Law Corpus
            </h4>
            <ul className="space-y-2">
              <li>
                <button
                  type="button"
                  onClick={() => onOpenStatutes && onOpenStatutes()}
                  className="hover:text-emerald-400 transition text-left"
                >
                  Pakistan Penal Code (PPC 1860)
                </button>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => onOpenStatutes && onOpenStatutes()}
                  className="hover:text-emerald-400 transition text-left"
                >
                  Code of Criminal Procedure (CrPC 1898)
                </button>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => onOpenStatutes && onOpenStatutes()}
                  className="hover:text-emerald-400 transition text-left"
                >
                  Code of Civil Procedure (CPC 1908)
                </button>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => onOpenStatutes && onOpenStatutes()}
                  className="hover:text-emerald-400 transition text-left"
                >
                  Constitution of Pakistan (1973)
                </button>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => onOpenStatutes && onOpenStatutes()}
                  className="hover:text-emerald-400 transition text-left"
                >
                  Punjab / Sindh Rented Premises Acts
                </button>
              </li>
            </ul>
          </div>

          {/* Column 2: Legal Resources & Services */}
          <div>
            <h4 className="font-semibold text-white uppercase tracking-wider text-[11px] mb-3.5">
              Legal Aid & Resources
            </h4>
            <ul className="space-y-2">
              <li>
                <button
                  type="button"
                  onClick={() => onOpenLawyers && onOpenLawyers()}
                  className="hover:text-emerald-400 transition text-left flex items-center gap-1.5"
                >
                  <span>Find a Licensed Advocate</span>
                </button>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => onOpenLawyers && onOpenLawyers()}
                  className="hover:text-emerald-400 transition text-left"
                >
                  Free Legal Aid Clinics (Bar Councils)
                </button>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => onOpenEmergency && onOpenEmergency()}
                  className="hover:text-red-400 text-red-300 font-medium transition text-left flex items-center gap-1.5"
                >
                  <span>Police 15 & Crisis Helplines</span>
                </button>
              </li>
              <li>
                <a
                  href="/sitemap.xml"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-emerald-400 transition inline-flex items-center gap-1"
                >
                  <span>XML Sitemap</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" aria-hidden="true" />
                </a>
              </li>
              <li>
                <a
                  href="/robots.txt"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-emerald-400 transition inline-flex items-center gap-1"
                >
                  <span>Robots.txt Directive</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" aria-hidden="true" />
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Direct Contact Information */}
          <div>
            <h4 className="font-semibold text-white uppercase tracking-wider text-[11px] mb-3.5">
              Direct Contact & Support
            </h4>
            <div className="space-y-3">
              {/* Clickable Phone Link */}
              <div className="flex items-start gap-2.5">
                <Phone className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
                <div>
                  <span className="block text-[10px] text-slate-400">Direct Telephone</span>
                  <a
                    href="tel:+923273202419"
                    className="font-semibold text-emerald-300 hover:text-emerald-200 transition"
                    aria-label="Call LawerAI Support at +923273202419"
                  >
                    +92 327 3202419
                  </a>
                </div>
              </div>

              {/* Clickable Email Link */}
              <div className="flex items-start gap-2.5">
                <Mail className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
                <div>
                  <span className="block text-[10px] text-slate-400">Inquiry & Feedback</span>
                  <a
                    href="mailto:ahmedmansoorrind1210@gmail.com?subject=LawerAI%20Inquiry"
                    className="font-semibold text-emerald-300 hover:text-emerald-200 transition break-all"
                    aria-label="Email LawerAI Support at ahmedmansoorrind1210@gmail.com"
                  >
                    ahmedmansoorrind1210@gmail.com
                  </a>
                </div>
              </div>

              {/* Address / Jurisdiction */}
              <div className="flex items-start gap-2.5">
                <MapPin className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
                <div>
                  <span className="block text-[10px] text-slate-400">Organization</span>
                  <span className="text-slate-300">Maverick Tech Ventures • Pakistan</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar: Dynamic Copyright Year & Disclaimer */}
        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500 text-[11px]">
          <div>
            © {currentYear} LawerAI by Maverick Tech Ventures. All rights reserved.
          </div>
          <div className="flex items-center gap-4">
            <a href="/privacy" onClick={(e) => { e.preventDefault(); alert("LawerAI Privacy Policy: Developed by Maverick Tech Ventures. No intake data is sold or shared with commercial third parties. All sessions are encrypted."); }} className="hover:text-slate-400 transition">
              Privacy Policy
            </a>
            <span>•</span>
            <a href="/terms" onClick={(e) => { e.preventDefault(); alert("LawerAI Terms: Developed by Maverick Tech Ventures. LawerAI provides legal information for informational and case intake structuring purposes only, not formal legal counsel."); }} className="hover:text-slate-400 transition">
              Terms of Service
            </a>
            <span>•</span>
            <span className="text-slate-500">v1.2.0 Production</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
