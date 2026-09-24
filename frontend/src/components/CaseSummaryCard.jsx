import React from 'react';
import { FileText, Download, CheckCircle2, AlertCircle, MapPin, Calendar, Users, Scale, FileCheck, ExternalLink, Printer, X } from 'lucide-react';
import { api } from '../api';

export default function CaseSummaryCard({
  sessionId,
  summary,
  onSelectStatute,
  language,
  onClose
}) {
  if (!summary) return null;

  const isUrdu = language === 'ur';
  const laws = summary.applicable_laws || [];
  const steps = summary.next_steps || [];
  const evidence = summary.evidence_checklist || [];
  const docs = summary.documents_mentioned || [];

  const handlePrintDossier = () => {
    if (!sessionId) return;
    const url = api.getExportUrl(sessionId, 'html');
    window.open(url, '_blank');
  };

  const handleDownloadJson = () => {
    if (!sessionId) return;
    const url = api.getExportUrl(sessionId, 'json');
    window.open(url, '_blank');
  };

  const isReady = summary.stage === 'assessment_ready' || laws.length > 0;

  return (
    <div className="bg-white border-l border-slate-200 w-full sm:w-80 lg:w-96 flex flex-col h-full overflow-hidden shadow-xs">
      {/* Header */}
      <div className="p-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-legal-100 text-legal-800">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-xs text-slate-800 uppercase tracking-wider">
              {isUrdu ? "کیس سمری و انٹیک کارڈ" : "Live Case Summary"}
            </h3>
            <span className="text-[10px] text-slate-400">Updates dynamically during chat</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
              isReady
                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                : 'bg-amber-100 text-amber-800 border border-amber-200'
            }`}
          >
            {isReady ? 'Assessment Ready' : 'Intake In Progress'}
          </span>

          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded transition"
              title="Close Case Summary"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Body content */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 text-xs">
        {/* Issue Identification */}
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/80">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
            Primary Issue
          </div>
          <div className="font-semibold text-slate-900 text-sm">
            {summary.issue_type || 'Analyzing conversation...'}
          </div>
        </div>

        {/* Structured Case Attributes */}
        <div className="flex flex-col gap-2.5 bg-white p-2.5 rounded-lg border border-slate-100">
          <div className="flex items-start gap-2.5 text-slate-600">
            <MapPin className="w-3.5 h-3.5 mt-0.5 text-slate-400 flex-shrink-0" />
            <div>
              <span className="font-medium text-slate-500">Jurisdiction: </span>
              <span className="text-slate-800 font-semibold">{summary.location_province || 'Pending clarification'}</span>
            </div>
          </div>

          <div className="flex items-start gap-2.5 text-slate-600">
            <Users className="w-3.5 h-3.5 mt-0.5 text-slate-400 flex-shrink-0" />
            <div>
              <span className="font-medium text-slate-500">Parties: </span>
              <span className="text-slate-800">{summary.parties || 'Pending clarification'}</span>
            </div>
          </div>

          <div className="flex items-start gap-2.5 text-slate-600">
            <Calendar className="w-3.5 h-3.5 mt-0.5 text-slate-400 flex-shrink-0" />
            <div>
              <span className="font-medium text-slate-500">Timeline: </span>
              <span className="text-slate-800">{summary.dates || 'Pending clarification'}</span>
            </div>
          </div>
        </div>

        {/* Applicable Laws Grounded */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-legal-700" />
              <span>Applicable Pakistani Laws ({laws.length})</span>
            </h4>
          </div>

          {laws.length === 0 ? (
            <p className="text-slate-400 text-[11px] italic bg-slate-50 p-2.5 rounded border border-dashed border-slate-200">
              Provide more facts to identify exact statutory provisions.
            </p>
          ) : (
            <div className="flex flex-col gap-2">
              {laws.map((law, idx) => (
                <div
                  key={idx}
                  onClick={() => onSelectStatute && onSelectStatute(law)}
                  className="p-2.5 rounded-lg border border-legal-200/80 bg-legal-50/50 hover:bg-legal-100/70 cursor-pointer transition group"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-legal-900 text-xs">
                      {law.act_code} Sec. {law.section_number}
                    </span>
                    <ExternalLink className="w-3 h-3 text-legal-600 opacity-60 group-hover:opacity-100" />
                  </div>
                  <div className="text-[11px] text-legal-800 font-medium truncate mt-0.5">
                    {law.section_title}
                  </div>
                  {law.forum_court && (
                    <div className="text-[10px] text-legal-600 mt-1 truncate">
                      Forum: {law.forum_court}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Evidence & Documents */}
        <div className="flex flex-col gap-2">
          <h4 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5">
            <FileCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Evidence & Documents Checklist</span>
          </h4>

          {docs.length > 0 && (
            <div className="flex flex-col gap-1">
              <div className="text-[10px] font-semibold text-slate-400 uppercase">Attached / In Possession:</div>
              <div className="flex flex-col gap-1">
                {docs.map((d, i) => (
                  <div key={i} className="flex items-center gap-1.5 text-emerald-800 bg-emerald-50 px-2 py-1 rounded text-[11px] font-medium border border-emerald-100">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600 flex-shrink-0" />
                    <span className="truncate">{d}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {evidence.length > 0 && (
            <div className="flex flex-col gap-1">
              <div className="text-[10px] font-semibold text-slate-400 uppercase">Recommended Evidence:</div>
              <div className="flex flex-col gap-1.5">
                {evidence.map((ev, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-slate-600 text-[11px]">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-300 mt-1.5 flex-shrink-0" />
                    <span>{ev}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Next Practical Steps */}
        {steps.length > 0 && (
          <div className="flex flex-col gap-2">
            <h4 className="font-semibold text-slate-700 text-xs flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-legal-700" />
              <span>Suggested Action Plan</span>
            </h4>
            <div className="flex flex-col gap-2">
              {steps.map((st, i) => (
                <div key={i} className="flex items-start gap-2 bg-slate-50 p-2.5 rounded text-[11px] text-slate-700 border border-slate-100">
                  <span className="font-bold text-legal-800 flex-shrink-0">{i + 1}.</span>
                  <span>{st}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer / Export Actions */}
      <div className="p-3 border-t border-slate-100 bg-slate-50 flex flex-col gap-2 flex-shrink-0">
        <button
          onClick={handlePrintDossier}
          disabled={!sessionId}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-legal-800 hover:bg-legal-700 text-white font-medium text-xs shadow-xs transition active:scale-[0.99] disabled:opacity-50 cursor-pointer"
        >
          <Printer className="w-3.5 h-3.5" />
          <span>Print / PDF Legal Dossier</span>
        </button>

        <button
          onClick={handleDownloadJson}
          disabled={!sessionId}
          className="w-full flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-100 text-slate-700 font-medium text-xs border border-slate-200 shadow-2xs transition active:scale-[0.99] disabled:opacity-50 cursor-pointer"
        >
          <Download className="w-3.5 h-3.5 text-slate-500" />
          <span>Export Intake JSON</span>
        </button>

        <p className="text-[10px] text-center text-slate-400">
          Ready to present to your licensed Advocate
        </p>
      </div>
    </div>
  );
}
