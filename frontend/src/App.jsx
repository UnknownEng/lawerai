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
import MobileMenu from './components/MobileMenu';
import Footer from './components/Footer';
import Breadcrumbs from './components/Breadcrumbs';
import NotificationToast from './components/NotificationToast';
import NotFoundPage from './components/NotFoundPage';
import LegalDrafterModal from './components/LegalDrafterModal';
import PrecedentModal from './components/PrecedentModal';
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [is404, setIs404] = useState(window.location.pathname === '/404');

  // Modals & Beta Gate
  const [betaGateOpen, setBetaGateOpen] = useState(
    !localStorage.getItem('qanoon_beta_code') && !localStorage.getItem('qanoon_auth_token')
  );
  const [lawyerModalOpen, setLawyerModalOpen] = useState(false);
  const [emergencyModalOpen, setEmergencyModalOpen] = useState(false);
  const [statuteSearchModalOpen, setStatuteSearchModalOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [selectedStatute, setSelectedStatute] = useState(null);
  const [drafterModalOpen, setDrafterModalOpen] = useState(false);
  const [selectedPrecedent, setSelectedPrecedent] = useState(null);

  // Notification helpers
  const addNotification = (notif) => {
    const id = Date.now() + Math.random();
    setNotifications((prev) => [...prev, { id, ...notif }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 4500);
  };

  const removeNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  // Check URL params on initial load
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('open') === 'statutes') setStatuteSearchModalOpen(true);
    if (params.get('open') === 'directory') setLawyerModalOpen(true);
    if (params.get('open') === 'emergency') setEmergencyModalOpen(true);
    if (params.get('open') === 'drafter') setDrafterModalOpen(true);
    if (window.location.pathname === '/404') setIs404(true);
  }, []);

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
        loadSession(sessList[0].id || sessList[0].session_id);
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
    addNotification({
      type: 'success',
      title: 'Access Granted',
      message: 'Welcome to LawerAI by Maverick Tech Ventures.'
    });
    initApp();
  };

  const createNewSession = async (lang = language) => {
    try {
      const newSess = await api.createSession(lang);
      const sessId = newSess.session_id || newSess.id;
      setCurrentSessionId(sessId);
      loadSession(sessId);

      // Refresh list
      const list = await api.listSessions();
      setSessions(list);
      addNotification({
        type: 'success',
        title: 'New Case Initialized',
        message: 'A fresh case intake session has been created.'
      });
    } catch (e) {
      console.error("Create session error:", e);
      if (e.message && (e.message.includes('403') || e.message.includes('beta') || e.message.includes('invitation'))) {
        setBetaGateOpen(true);
      } else {
        addNotification({
          type: 'error',
          title: 'Session Error',
          message: 'Could not create new intake session. Please check your network connection.'
        });
      }
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const data = await api.getSession(sessionId);
      if (data) {
        setCurrentSessionId(sessionId);
        setCurrentSession(data);
        setMessages(data.messages || []);
        setCaseSummary(data.case_summary || null);
        if (data.language) setLanguage(data.language);
      }
    } catch (e) {
      console.error("Load session error:", e);
      addNotification({
        type: 'error',
        title: 'Load Failed',
        message: 'Failed to load case session history.'
      });
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
        addNotification({
          type: 'error',
          title: 'Emergency Detected',
          message: 'Immediate safety resources have been automatically loaded.'
        });
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
      addNotification({
        type: 'error',
        title: 'Submission Error',
        message: 'Failed to reach legal reasoning engine. Please try again.'
      });
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
      await api.uploadDocument(currentSessionId, file);
      // Reload session to reflect new document note and updated summary
      await loadSession(currentSessionId);
      addNotification({
        type: 'success',
        title: 'Document Uploaded',
        message: `${file.name} uploaded and OCR analysis completed.`
      });
    } catch (e) {
      console.error("Upload error:", e);
      addNotification({
        type: 'error',
        title: 'Upload Failed',
        message: 'Could not upload document. Please ensure it is a PDF or supported image format.'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    addNotification({
      type: 'success',
      title: 'Logged Out',
      message: 'You have been securely signed out.'
    });
    initApp();
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-100 font-sans max-w-[100vw] overflow-x-hidden">
      {/* Toast Notifications */}
      <NotificationToast notifications={notifications} onDismiss={removeNotification} />

      {/* Prominent, Persistent BETA Warning Banner */}
      <div className="bg-amber-500 text-amber-950 px-4 py-2 text-xs font-semibold flex items-center justify-center gap-2 border-b border-amber-600 shadow-xs z-40 text-center flex-wrap">
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
        }}
        onOpenLawyers={() => setLawyerModalOpen(true)}
        onOpenEmergency={() => setEmergencyModalOpen(true)}
        onOpenStatutes={() => setStatuteSearchModalOpen(true)}
        onOpenDrafter={() => setDrafterModalOpen(true)}
        onOpenAuth={() => setAuthModalOpen(true)}
        onOpenMobileMenu={() => setMobileMenuOpen(true)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {/* Visual Breadcrumb Navigation Trail */}
      <Breadcrumbs
        currentView={
          statuteSearchModalOpen
            ? 'statutes'
            : lawyerModalOpen
            ? 'directory'
            : emergencyModalOpen
            ? 'emergency'
            : 'intake'
        }
        onNavigate={(view) => {
          if (view === 'intake') {
            setIs404(false);
          }
        }}
      />

      {/* Mobile Slide-Over Menu Drawer */}
      <MobileMenu
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        language={language}
        setLanguage={setLanguage}
        onOpenLawyers={() => setLawyerModalOpen(true)}
        onOpenStatutes={() => setStatuteSearchModalOpen(true)}
        onOpenDrafter={() => setDrafterModalOpen(true)}
        onOpenEmergency={() => setEmergencyModalOpen(true)}
        onOpenAuth={() => setAuthModalOpen(true)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {/* Primary Workspace View or 404 Fallback */}
      {is404 ? (
        <NotFoundPage
          onReturnHome={() => setIs404(false)}
          onOpenStatutes={() => {
            setIs404(false);
            setStatuteSearchModalOpen(true);
          }}
          onOpenLawyers={() => {
            setIs404(false);
            setLawyerModalOpen(true);
          }}
        />
      ) : (
        <div className="flex-1 flex overflow-hidden relative min-h-[calc(100vh-210px)] h-[calc(100vh-210px)]">
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
          <main className="flex-1 flex flex-col h-full overflow-hidden relative min-w-0">
            {/* Mobile subheader toggles */}
            <div className="md:hidden bg-white border-b border-slate-200 px-4 py-2 flex items-center justify-between text-xs">
              <button
                type="button"
                onClick={() => setSidebarOpen(true)}
                className="flex items-center gap-1.5 text-slate-700 font-medium p-1 rounded hover:bg-slate-100 transition cursor-pointer"
              >
                <PanelLeft className="w-4 h-4 text-legal-700" />
                <span>History</span>
              </button>

              <button
                type="button"
                onClick={() => setSummaryPanelOpen(!summaryPanelOpen)}
                className="flex items-center gap-1.5 text-slate-700 font-medium p-1 rounded hover:bg-slate-100 transition cursor-pointer"
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
              onSelectPrecedent={(precedent) => setSelectedPrecedent(precedent)}
              onOpenDrafter={() => setDrafterModalOpen(true)}
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
                onSelectPrecedent={(precedent) => setSelectedPrecedent(precedent)}
                onOpenDrafter={() => setDrafterModalOpen(true)}
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
                aria-hidden="true"
              />
              <div className="relative ml-auto w-full max-w-sm sm:max-w-md h-full bg-white z-40 shadow-2xl flex flex-col">
                <CaseSummaryCard
                  sessionId={currentSessionId}
                  summary={caseSummary}
                  onSelectStatute={(statute) => {
                    setSelectedStatute(statute);
                  }}
                  onSelectPrecedent={(precedent) => {
                    setSelectedPrecedent(precedent);
                  }}
                  onOpenDrafter={() => setDrafterModalOpen(true)}
                  language={language}
                  onClose={() => setSummaryPanelOpen(false)}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Global Comprehensive Footer */}
      <Footer
        onOpenStatutes={() => setStatuteSearchModalOpen(true)}
        onOpenLawyers={() => setLawyerModalOpen(true)}
        onOpenEmergency={() => setEmergencyModalOpen(true)}
      />

      {/* Modals & Dialogs */}
      <LegalDrafterModal
        isOpen={drafterModalOpen}
        onClose={() => setDrafterModalOpen(false)}
        initialData={caseSummary || {}}
      />

      <PrecedentModal
        isOpen={!!selectedPrecedent}
        precedent={selectedPrecedent}
        onClose={() => setSelectedPrecedent(null)}
      />

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
        onAuthSuccess={(user) => {
          setCurrentUser(user);
          addNotification({
            type: 'success',
            title: 'Authenticated',
            message: `Welcome, ${user.full_name || user.email}!`
          });
        }}
      />

      <BetaGateModal
        isOpen={betaGateOpen}
        onSuccess={handleBetaSuccess}
      />
    </div>
  );
}
