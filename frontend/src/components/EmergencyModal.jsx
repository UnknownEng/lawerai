import React, { useState, useEffect } from 'react';
import { X, PhoneCall, ShieldAlert, HeartHandshake, AlertCircle } from 'lucide-react';
import { api } from '../api';

export default function EmergencyModal({ isOpen, onClose }) {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadEmergencies();
    }
  }, [isOpen]);

  const loadEmergencies = async () => {
    setLoading(true);
    try {
      const data = await api.getEmergencyResources();
      setResources(data.resources || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden border-2 border-red-500/20">
        {/* Urgent Header */}
        <div className="p-5 bg-red-600 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-red-700 text-white">
              <ShieldAlert className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Emergency & Crisis Helplines — Pakistan</h2>
              <p className="text-xs text-red-100">
                Immediate police, medical, domestic violence, and mental health support
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-red-200 hover:text-white hover:bg-red-700 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Priority Banner */}
        <div className="p-4 bg-red-50 border-b border-red-100 flex items-start gap-3 text-xs text-red-900">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="font-bold">Are you in immediate physical danger?</strong>
            <p className="mt-0.5 text-red-800">
              Do not wait for legal advice. Call <strong>Police Emergency 15</strong> or <strong>Rescue 1122</strong> immediately.
            </p>
          </div>
        </div>

        {/* Helplines list */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          {loading ? (
            <div className="py-8 text-center text-slate-400 text-sm">Loading helplines...</div>
          ) : (
            resources.map((item) => (
              <div
                key={item.id}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-red-300 bg-white hover:bg-red-50/20 transition flex items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-slate-900 text-sm">{item.name}</h3>
                    <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                      {item.hours}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{item.description}</p>
                </div>

                <a
                  href={`tel:${item.short_code || item.phone}`}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-xs transition active:scale-95 flex-shrink-0"
                >
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>Call {item.short_code || item.phone}</span>
                </a>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>All toll-free calls are confidential and free of charge</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
