import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Scale, ShieldAlert, Sparkles, Loader2, FileUp, CheckCircle2, ChevronRight, Mic, Info } from 'lucide-react';
import MessageFeedback from './MessageFeedback';

export default function ChatArea({
  session,
  messages,
  onSendMessage,
  onUploadDocument,
  onSelectStatute,
  onOpenEmergency,
  language,
  isSending,
  isUploading
}) {
  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const isUrdu = language === 'ur';

  // Detect RTL if user types Arabic/Urdu script
  const isRTLText = (text) => /[\u0600-\u06FF]/.test(text);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSend = (e) => {
    e.preventDefault();
    if ((!input.trim() && !selectedFile) || isSending) return;

    if (selectedFile) {
      onUploadDocument(selectedFile);
      setSelectedFile(null);
    }

    if (input.trim()) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const quickPrompts = [
    { label: "Cheque Dishonour (PPC 489-F)", text: "A client gave me a cheque of 450,000 PKR which bounced due to insufficient funds. What are my legal remedies?" },
    { label: "Police Refused FIR (CrPC 22-A)", text: "I went to the police station to report theft of my motorbike, but the SHO refused to register an FIR. What should I do?" },
    { label: "Urgent Stay Order (CPC O.39)", text: "My neighbor has started illegal construction and encroaching on my inherited plot in Lahore. How can I get an urgent stay order?" },
    { label: "Tenant Eviction (Rent Laws)", text: "My tenant in Lahore has not paid rent for 4 months and his tenancy agreement has expired. How can I evict him legally?" },
    { label: "Khula & Child Maintenance", text: "I want to apply for Khula from my husband and claim monthly maintenance for my two minor children." },
    { label: "Cyber Harassment (PECA 2016)", text: "Someone created a fake Facebook account with my photos and is blackmailing me on WhatsApp. How do I report this to FIA?" }
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#fcfbf9] overflow-hidden">
      {/* Session Title Header */}
      <div className="px-6 py-3 border-b border-slate-200/80 bg-white/80 backdrop-blur-xs flex items-center justify-between">
        <div className="flex items-center gap-2.5 truncate">
          <div className="p-1.5 rounded-md bg-legal-50 text-legal-800 border border-legal-200/60">
            <Scale className="w-4 h-4" />
          </div>
          <div className="truncate">
            <h2 className="text-sm font-bold text-slate-800 truncate">
              {session?.title || "Legal Consultation"}
            </h2>
            <div className="text-[11px] text-slate-400 truncate">
              {session?.case_category || "Initial Legal Intake"}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-medium text-slate-500 hidden sm:inline-block">
            One-question intake interview
          </span>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 flex flex-col gap-6">
        {messages.map((msg, index) => {
          const isUser = msg.role === 'user';
          const isUrduMsg = isRTLText(msg.content);

          return (
            <div
              key={msg.id || index}
              className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold shadow-2xs ${
                  isUser
                    ? 'bg-slate-700 text-white'
                    : 'bg-legal-900 text-emerald-300 border border-legal-700'
                }`}
              >
                {isUser ? 'You' : 'QS'}
              </div>

              {/* Message Content Bubble */}
              <div
                className={`rounded-2xl px-5 py-4 text-xs sm:text-sm leading-relaxed shadow-xs transition-all ${
                  isUser
                    ? 'bg-slate-800 text-white rounded-tr-none'
                    : msg.is_emergency
                    ? 'bg-red-50 text-red-950 border-2 border-red-300 rounded-tl-none'
                    : 'bg-white text-slate-800 border border-slate-200/90 rounded-tl-none'
                }`}
                dir={isUrduMsg ? 'rtl' : 'ltr'}
              >
                {/* Emergency Header if applicable */}
                {msg.is_emergency && (
                  <div className="flex items-center gap-2 text-red-700 font-bold mb-3 pb-2 border-b border-red-200">
                    <ShieldAlert className="w-4 h-4 animate-pulse flex-shrink-0" />
                    <span>EMERGENCY ALERT — IMMEDIATE SAFETY PRIORITY</span>
                  </div>
                )}

                {/* Formatted Text */}
                <div
                  className={`prose-legal whitespace-pre-wrap ${
                    isUrduMsg ? 'font-urdu text-sm sm:text-base leading-loose' : 'font-sans'
                  }`}
                >
                  {msg.content}
                </div>

                {/* Statutory Citations Pills */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center gap-1.5">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mr-1">
                      Citations:
                    </span>
                    {msg.citations.map((c, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => onSelectStatute(c)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-legal-50 hover:bg-legal-100 text-legal-900 border border-legal-200/80 transition shadow-2xs"
                      >
                        <Scale className="w-3 h-3 text-legal-700" />
                        <span>{c.act_code} Sec. {c.section_number}</span>
                      </button>
                    ))}
                  </div>
                )}

                {/* Beta Feedback Actions (Thumbs up/down, Citation Wrong, Reasoning Wrong, Comment) */}
                {!isUser && (
                  <MessageFeedback message={msg} sessionId={session?.id} />
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isSending && (
          <div className="flex gap-3 max-w-xl mr-auto">
            <div className="w-8 h-8 rounded-full bg-legal-900 text-emerald-300 flex items-center justify-center flex-shrink-0 text-xs font-bold border border-legal-700">
              QS
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-2 text-slate-500 text-xs shadow-xs">
              <Loader2 className="w-4 h-4 animate-spin text-legal-700" />
              <span>Analyzing Pakistani statutory corpus & preparing intake questions...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Strip (shown when conversation is new) */}
      {messages.length <= 2 && (
        <div className="px-6 py-2 bg-slate-50/70 border-t border-slate-100 overflow-x-auto flex gap-2">
          {quickPrompts.map((p, i) => (
            <button
              key={i}
              onClick={() => onSendMessage(p.text)}
              className="text-[11px] whitespace-nowrap bg-white border border-slate-200 hover:border-legal-400 hover:bg-legal-50/50 text-slate-700 px-3 py-1.5 rounded-lg transition shadow-2xs flex-shrink-0"
            >
              {p.label}
            </button>
          ))}
        </div>
      )}

      {/* Input Bar */}
      <div className="p-4 bg-white border-t border-slate-200">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto space-y-2">
          {/* Selected File Chip */}
          {selectedFile && (
            <div className="flex items-center justify-between p-2 bg-emerald-50 text-emerald-900 rounded-lg text-xs border border-emerald-200">
              <div className="flex items-center gap-2 truncate">
                <Paperclip className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                <span className="font-semibold truncate">{selectedFile.name}</span>
                <span className="text-[10px] text-emerald-700">({(selectedFile.size / 1024).toFixed(1)} KB) — Ready for OCR</span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                className="text-emerald-700 hover:text-emerald-900 font-bold ml-2"
              >
                ✕
              </button>
            </div>
          )}

          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus-within:ring-2 focus-within:ring-legal-600 focus-within:bg-white transition">
            {/* File Upload Trigger */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.png,.jpg,.jpeg,.txt"
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-1.5 text-slate-400 hover:text-legal-800 transition rounded-lg hover:bg-slate-100"
              title="Attach FIR copy, bounced cheque, contract, or screenshot"
            >
              <Paperclip className="w-5 h-5" />
            </button>

            {/* Main Text Input */}
            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(e);
                }
              }}
              placeholder={
                isUrdu
                  ? "اپنا قانونی مسئلہ یہاں بیان کریں (مثلاً چیک باؤنس، پولیس کا ایف آئی آر درج نہ کرنا، کرایہ داری)..."
                  : "Describe your situation in plain English, Urdu, or Roman Urdu (e.g. cheque bounced, police refused FIR, stay order)..."
              }
              dir={isRTLText(input) ? 'rtl' : 'ltr'}
              className={`flex-1 bg-transparent border-0 focus:outline-none text-xs sm:text-sm text-slate-800 resize-none max-h-32 ${
                isRTLText(input) ? 'font-urdu text-sm' : ''
              }`}
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={(!input.trim() && !selectedFile) || isSending}
              className="p-2 rounded-lg bg-legal-900 hover:bg-legal-800 text-white disabled:opacity-40 disabled:hover:bg-legal-900 transition flex-shrink-0 active:scale-95 shadow-2xs"
            >
              {isSending ? (
                <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400 px-1">
            <span>Press Enter to send, Shift + Enter for new line</span>
            <span className="text-slate-400">Attach FIR, Cheques, or Contracts for instant OCR</span>
          </div>
        </form>
      </div>
    </div>
  );
}
