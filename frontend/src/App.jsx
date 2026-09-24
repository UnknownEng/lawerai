import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import CaseSummaryCard from './components/CaseSummaryCard';
import LawyerDirectoryModal from './components/LawyerDirectoryModal';
import EmergencyModal from './components/EmergencyModal';
import StatuteModal from './components/StatuteModal';
import StatuteSearchModal from './components/StatuteSearchModal';
import AuthModal from './components/AuthModal';
import BetaGateModal from './components/BetaGateModal';
import { api } from './api';
import { PanelLeft, PanelRight, ShieldAlert } from 'lucide-react';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [caseSummary, setCaseSummary] = useState(null);
  const [language, setLanguage] = useState('en');
  const [currentUser, setCurrentUser] = useState(null);

  // UI state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [summaryPanelOpen, setSummaryPanelOpen] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // Modals & Beta Gate
  const [betaGateOpen, setBetaGateOpen] = useState(
    !localStorage.getItem('qanoon_beta_code') && !localStorage.getItem('qanoon_auth_token')
  );
  const [lawyerModalOpen, setLawyerModalOpen] = useState(false);
  const [emergencyModalOpen, setEmergencyModalOpen] = useState(false);
  const [statuteSearchModalOpen, setStatuteSearchModalOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [selectedStatute, setSelectedStatute] = useState(null);

  // Initialize app
  useEffect(() => {
    if (!betaGateOpen) {
      initApp();
    }
  }, [betaGateOpen]);

  const initApp = async () => {
    try {
      // 1. Check user auth
      const user = await api.getMe();
      if (user) setCurrentUser(user);

      // 2. Load sessions list
      const sessList = await api.listSessions();
      setSessions(sessList);

      if (sessList && sessList.length > 0) {
        loadSession(sessList[0].id);
      } else {
        await createNewSession('en');
      }
    } catch (e) {
      console.error("Init error:", e);
      if (e.message && (e.message.includes('403') || e.message.includes('beta'))) {
        setBetaGateOpen(true);
      } else {
        createNewSession('en');
      }
    }
  };

  const handleBetaSuccess = (code) => {
    setBetaGateOpen(false);
    initApp();
  };

  const createNewSession = async (lang = language) => {
    try {
      const newSess = await api.createSession(lang);
      setCurrentSessionId(newSess.session_id);
      loadSession(newSess.session_id);

      // Refresh list
      const list = await api.listSessions();
      setSessions(list);
    } catch (e) {
      console.error("Create session error:", e);
      if (e.message && (e.message.includes('403') || e.message.includes('beta') || e.message.includes('invitation'))) {
        setBetaGateOpen(true);
      }
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const data = await api.getSession(sessionId);
      setCurrentSessionId(sessionId);
      setCurrentSession(data);
      setMessages(data.messages || []);
      setCaseSummary(data.case_summary || null);
      if (data.language) setLanguage(data.language);
    } catch (e) {
      console.error("Load session error:", e);
    }
  };

  const handleSendMessage = async (content) => {
    if (!currentSessionId || isSending) return;
    setIsSending(true);

    // Optimistic user message addition
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const data = await api.sendMessage(currentSessionId, content, language);

      // If backend detected an active emergency, trigger emergency modal automatically!
      if (data.is_emergency) {
        setEmergencyModalOpen(true);
      }

      // Update state with assistant response
      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => m.id !== tempUserMsg.id);
        return [...withoutTemp, data.user_message, data.assistant_message];
      });

      if (data.case_summary) {
        setCaseSummary(data.case_summary);
      }

      // Refresh session title in list
      const list = await api.listSessions();
      setSessions(list);
    } catch (e) {
      console.error("Send message error:", e);
      // Fallback message
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: "I apologize, but there was an error processing your query. Please verify your connection or try again."
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleUploadDocument = async (file) => {
    if (!currentSessionId || isUploading) return;
    setIsUploading(true);

    try {
      const res = await api.uploadDocument(currentSessionId, file);
      // Reload session to reflect new document note and updated summary
      await loadSession(currentSessionId);
    } catch (e) {
      console.error("Upload error:", e);
      alert("Failed to upload document. Please ensure it is a PDF or image.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    initApp();
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-100 font-sans">
      {/* Prominent, Persistent BETA Warning Banner */}
      <div className="bg-amber-500 text-amber-950 px-4 py-2 text-xs font-semibold flex items-center justify-center gap-2 border-b border-amber-600 shadow-xs z-50 text-center flex-wrap">
        <span className="bg-amber-950 text-amber-100 text-[10px] uppercase font-black px-1.5 py-0.5 rounded tracking-wider shadow-2xs">
          BETA
        </span>
        <span>
          Under legal review. Do not rely on this system for actual legal proceedings without independent verification from a qualified advocate.
        </span>
      </div>

      {/* Top Navbar Header */}
      <Header
        language={language}
        setLanguage={(l) => {
          setLanguage(l);
          if (currentSessionId) {
            // update language for current consultation
          }
        }}
        onOpenLawyers={() => setLawyerModalOpen(true)}
        onOpenEmergency={() => setEmergencyModalOpen(true)}
        onOpenStatutes={() => setStatuteSearchModalOpen(true)}
        onOpenAuth={() => setAuthModalOpen(true)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar: Case History */}
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={loadSession}
          onNewSession={() => createNewSession(language)}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onOpenLawyers={() => setLawyerModalOpen(true)}
          onOpenEmergency={() => setEmergencyModalOpen(true)}
        />

        {/* Center: Live Chat Stream */}
        <main className="flex-1 flex flex-col h-full overflow-hidden relative">
          {/* Mobile subheader toggles */}
          <div className="md:hidden bg-white border-b border-slate-200 px-4 py-2 flex items-center justify-between text-xs">
            <button
              onClick={() => setSidebarOpen(true)}
              className="flex items-center gap-1.5 text-slate-700 font-medium p-1 rounded hover:bg-slate-100"
            >
              <PanelLeft className="w-4 h-4 text-legal-700" />
              <span>History</span>
            </button>

            <button
              onClick={() => setSummaryPanelOpen(!summaryPanelOpen)}
              className="flex items-center gap-1.5 text-slate-700 font-medium p-1 rounded hover:bg-slate-100"
            >
              <span>Case Dossier</span>
              <PanelRight className="w-4 h-4 text-legal-700" />
            </button>
          </div>

          <ChatArea
            session={currentSession}
            messages={messages}
            onSendMessage={handleSendMessage}
            onUploadDocument={handleUploadDocument}
            onSelectStatute={(statute) => setSelectedStatute(statute)}
            onOpenEmergency={() => setEmergencyModalOpen(true)}
            language={language}
            isSending={isSending}
            isUploading={isUploading}
          />
        </main>

        {/* Right Sidebar: Live Structured Case Summary Panel (Desktop) */}
        {summaryPanelOpen && (
          <aside className="hidden lg:block h-full flex-shrink-0">
            <CaseSummaryCard
              sessionId={currentSessionId}
              summary={caseSummary}
              onSelectStatute={(statute) => setSelectedStatute(statute)}
              language={language}
            />
          </aside>
        )}

        {/* Mobile Case Dossier Drawer (< lg) */}
        {summaryPanelOpen && (
          <div className="lg:hidden fixed inset-0 z-30 flex">
            <div
              className="fixed inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
              onClick={() => setSummaryPanelOpen(false)}
            />
            <div className="relative ml-auto w-full max-w-sm sm:max-w-md h-full bg-white z-40 shadow-2xl flex flex-col">
              <CaseSummaryCard
                sessionId={currentSessionId}
                summary={caseSummary}
                onSelectStatute={(statute) => {
                  setSelectedStatute(statute);
                }}
                language={language}
                onClose={() => setSummaryPanelOpen(false)}
              />
            </div>
          </div>
        )}
      </div>

      {/* Modals & Drawers */}
      <LawyerDirectoryModal
        isOpen={lawyerModalOpen}
        onClose={() => setLawyerModalOpen(false)}
      />

      <EmergencyModal
        isOpen={emergencyModalOpen}
        onClose={() => setEmergencyModalOpen(false)}
      />

      <StatuteSearchModal
        isOpen={statuteSearchModalOpen}
        onClose={() => setStatuteSearchModalOpen(false)}
        onSelectStatute={(statute) => setSelectedStatute(statute)}
      />

      <StatuteModal
        statute={selectedStatute}
        onClose={() => setSelectedStatute(null)}
      />

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={(user) => setCurrentUser(user)}
      />

      <BetaGateModal
        isOpen={betaGateOpen}
        onSuccess={handleBetaSuccess}
      />
    </div>
  );
}
