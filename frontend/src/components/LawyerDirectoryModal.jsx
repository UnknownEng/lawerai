import React, { useState, useEffect } from 'react';
import { X, Search, MapPin, Phone, Mail, Globe, ShieldCheck, Scale, Filter } from 'lucide-react';
import { api } from '../api';

export default function LawyerDirectoryModal({ isOpen, onClose }) {
  const [lawyers, setLawyers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [cityFilter, setCityFilter] = useState('');
  const [freeAidOnly, setFreeAidOnly] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadDirectory();
    }
  }, [isOpen, cityFilter, freeAidOnly]);

  const loadDirectory = async () => {
    setLoading(true);
    try {
      const data = await api.getLawyers({
        city: cityFilter || undefined,
        free_aid_only: freeAidOnly ? true : undefined,
        search: search || undefined
      });
      setLawyers(data.results || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadDirectory();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 bg-legal-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-legal-800 text-emerald-400">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Find a Licensed Advocate or Legal Aid Clinic</h2>
              <p className="text-xs text-legal-300">
                Official Pakistani Bar Councils, Free Legal Aid Societies, and Licensed Advocates
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-legal-300 hover:text-white hover:bg-legal-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter bar */}
        <div className="p-4 border-b border-slate-100 bg-slate-50 flex flex-wrap items-center gap-3">
          <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[240px] relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by specialty, name, or area (e.g. Criminal, Khula, FIR, Cheque)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-legal-600"
            />
          </form>

          <select
            value={cityFilter}
            onChange={(e) => setCityFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-legal-600"
          >
            <option value="">All Cities / Nationwide</option>
            <option value="Lahore">Lahore</option>
            <option value="Karachi">Karachi</option>
            <option value="Islamabad">Islamabad / Rawalpindi</option>
            <option value="Peshawar">Peshawar</option>
            <option value="Quetta">Quetta</option>
          </select>

          <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer font-medium select-none">
            <input
              type="checkbox"
              checked={freeAidOnly}
              onChange={(e) => setFreeAidOnly(e.target.checked)}
              className="rounded text-legal-600 focus:ring-legal-500"
            />
            <span>Free Legal Aid Only</span>
          </label>
        </div>

        {/* Content list */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              Loading legal directory...
            </div>
          ) : lawyers.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              No matching legal aid organizations or advocates found. Try adjusting your filters.
            </div>
          ) : (
            lawyers.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-xl border border-slate-200 hover:border-legal-300 bg-white hover:bg-slate-50/50 transition shadow-2xs"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-slate-900 text-sm">{item.name}</h3>
                      {item.is_free_legal_aid && (
                        <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 border border-emerald-200">
                          <ShieldCheck className="w-3 h-3 text-emerald-600" />
                          Free Legal Aid
                        </span>
                      )}
                      <span className="bg-slate-100 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded">
                        {item.type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </div>

                {/* Specialties */}
                {item.specialties && item.specialties.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {item.specialties.map((spec, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-medium bg-legal-50 text-legal-800 px-2 py-0.5 rounded-md border border-legal-100"
                      >
                        {spec}
                      </span>
                    ))}
                  </div>
                )}

                {/* Contact info grid */}
                <div className="mt-3 pt-3 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs text-slate-500">
                  <div className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    <span className="truncate">{item.address || `${item.city}, ${item.province}`}</span>
                  </div>
                  {item.phone && (
                    <div className="flex items-center gap-1.5 font-medium text-slate-700">
                      <Phone className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                      <a href={`tel:${item.phone.split('/')[0].trim()}`} className="hover:text-legal-700">
                        {item.phone}
                      </a>
                    </div>
                  )}
                  {item.email && (
                    <div className="flex items-center gap-1.5">
                      <Mail className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                      <a href={`mailto:${item.email}`} className="truncate hover:text-legal-700">
                        {item.email}
                      </a>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Bar Councils of Pakistan • Statutory Legal Representation</span>
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
