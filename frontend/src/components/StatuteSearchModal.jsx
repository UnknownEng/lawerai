import React, { useState, useEffect } from 'react';
import { X, Search, BookOpen, Scale, ExternalLink } from 'lucide-react';
import { api } from '../api';

export default function StatuteSearchModal({ isOpen, onClose, onSelectStatute }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      handleSearch('PPC');
    }
  }, [isOpen]);

  const handleSearch = async (searchTerm) => {
    if (!searchTerm || searchTerm.trim().length < 2) return;
    setLoading(true);
    try {
      const data = await api.searchStatutes(searchTerm);
      setResults(data.results || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    handleSearch(query);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 bg-legal-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-legal-800 text-emerald-400">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Pakistani Statutory Law Library</h2>
              <p className="text-xs text-legal-300">
                PPC 1860, CrPC 1898, CPC 1908, Constitution 1973, Family Laws, Rent Laws, PECA 2016
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

        {/* Search bar */}
        <div className="p-4 border-b border-slate-100 bg-slate-50">
          <form onSubmit={onSubmit} className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by act name, section, or term (e.g. 420, 154, FIR, Khula, Stay order, Rent)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-legal-600"
            />
          </form>

          {/* Quick chips */}
          <div className="flex flex-wrap gap-1.5 mt-2.5">
            {["PPC 420 Cheating", "CrPC 154 FIR", "CrPC 22-A Justice of Peace", "PPC 489-F Cheque", "CPC Order 39 Stay", "MFLO Section 9 Maintenance", "PRPA 15 Rent Eviction", "PECA 20 Cyber"].map((chip, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuery(chip.split(' ')[0]);
                  handleSearch(chip.split(' ')[0]);
                }}
                className="text-[11px] bg-white border border-slate-200 hover:border-legal-400 hover:bg-legal-50 text-slate-600 px-2.5 py-1 rounded-md transition"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">Searching statutory corpus...</div>
          ) : results.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              No matching sections found in the legal corpus.
            </div>
          ) : (
            results.map((sec) => (
              <div
                key={sec.id}
                onClick={() => {
                  onSelectStatute(sec);
                  onClose();
                }}
                className="p-4 rounded-xl border border-slate-200 hover:border-legal-300 bg-white hover:bg-legal-50/30 cursor-pointer transition shadow-2xs group"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-legal-900 text-xs uppercase bg-legal-100 px-2 py-0.5 rounded">
                        {sec.act_code} Section {sec.section_number}
                      </span>
                      <span className="text-[11px] text-slate-500 font-medium">
                        {sec.act_title}
                      </span>
                    </div>
                    <h3 className="font-bold text-slate-900 text-sm mt-1 group-hover:text-legal-800 transition">
                      {sec.section_title}
                    </h3>
                  </div>
                  <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-legal-600 transition" />
                </div>
                <p className="text-xs text-slate-600 mt-2 leading-relaxed line-clamp-2">
                  {sec.summary_plain}
                </p>
                {sec.forum_court && (
                  <div className="text-[11px] text-legal-700 font-medium mt-2">
                    Court Forum: {sec.forum_court}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
