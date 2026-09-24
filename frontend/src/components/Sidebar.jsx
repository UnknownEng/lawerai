import React from 'react';
import { PlusCircle, MessageSquare, Clock, ShieldAlert, BookText, ChevronRight } from 'lucide-react';

export default function Sidebar({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewSession,
  isOpen,
  onClose,
  onOpenLawyers,
  onOpenEmergency
}) {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-20 md:hidden"
        />
      )}

      <aside
        className={`fixed md:static top-0 bottom-0 left-0 w-72 bg-white border-r border-slate-200 z-20 flex flex-col flex-shrink-0 transition-transform duration-200 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* New Consultation Action */}
        <div className="p-4 border-b border-slate-100 flex-shrink-0">
          <button
            onClick={onNewSession}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-legal-900 hover:bg-legal-800 text-white font-medium text-sm shadow-sm transition active:scale-[0.99]"
          >
            <PlusCircle className="w-4 h-4 text-emerald-400" />
            <span>New Case Intake</span>
          </button>
        </div>

        {/* Previous Consultation Sessions */}
        <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-1">
          <div className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Clock className="w-3 h-3" />
            <span>Consultation History</span>
          </div>

          {sessions.length === 0 ? (
            <div className="text-center py-8 px-4 text-xs text-slate-400">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 text-slate-300 stroke-[1.5]" />
              No past consultations yet. Start by describing your situation.
            </div>
          ) : (
            sessions.map((s) => {
              const isActive = s.id === currentSessionId;
              return (
                <button
                  key={s.id}
                  onClick={() => {
                    onSelectSession(s.id);
                    onClose();
                  }}
                  className={`w-full text-left px-3 py-2.5 rounded-lg text-xs transition flex items-start gap-2.5 group ${
                    isActive
                      ? 'bg-legal-50 text-legal-900 font-semibold border border-legal-200 shadow-sm'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <MessageSquare className={`w-4 h-4 mt-0.5 flex-shrink-0 ${isActive ? 'text-legal-600' : 'text-slate-400'}`} />
                  <div className="flex-1 truncate">
                    <div className="truncate font-medium">{s.title || 'Legal Consultation'}</div>
                    <div className="text-[10px] text-slate-400 truncate mt-0.5">
                      {s.case_category || 'General Inquiry'}
                    </div>
                  </div>
                  <ChevronRight className={`w-3.5 h-3.5 self-center opacity-0 group-hover:opacity-100 transition text-slate-400 ${isActive ? 'opacity-100 text-legal-600' : ''}`} />
                </button>
              );
            })
          )}
        </div>

        {/* Quick Links & Crisis Footer */}
        <div className="p-3 border-t border-slate-100 bg-slate-50/50 flex flex-col gap-2 flex-shrink-0">
          <button
            onClick={onOpenEmergency}
            className="w-full text-left px-3 py-2 rounded-lg text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100 border border-red-200/60 flex items-center gap-2 transition"
          >
            <ShieldAlert className="w-4 h-4 text-red-600 flex-shrink-0" />
            <div className="truncate">
              <div className="font-semibold leading-tight">Emergency Helplines</div>
              <div className="text-[10px] text-red-500">15 • 1098 • 0800-22444</div>
            </div>
          </button>

          <button
            onClick={onOpenLawyers}
            className="w-full text-left px-3 py-2 rounded-lg text-xs font-medium text-legal-900 bg-white hover:bg-legal-50 border border-slate-200 flex items-center gap-2 transition shadow-2xs"
          >
            <BookText className="w-4 h-4 text-legal-600 flex-shrink-0" />
            <div className="truncate">
              <div className="font-semibold leading-tight">Legal Aid & Bar Directory</div>
              <div className="text-[10px] text-slate-500">Free Legal Clinics & Advocates</div>
            </div>
          </button>
        </div>
      </aside>
    </>
  );
}
