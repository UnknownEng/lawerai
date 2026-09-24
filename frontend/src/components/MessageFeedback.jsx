import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, AlertTriangle, MessageSquare, Check, X, Send } from 'lucide-react';
import { api } from '../api';

export default function MessageFeedback({ message, sessionId }) {
  const [submitted, setSubmitted] = useState(false);
  const [feedbackType, setFeedbackType] = useState(null);
  const [showCommentInput, setShowCommentInput] = useState(false);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (message.role !== 'assistant') return null;

  const handleQuickFeedback = async (type) => {
    setFeedbackType(type);
    if (type === 'thumbs_up' || type === 'looks_fine') {
      await sendFeedback(type, 'statute_accuracy', '');
    } else {
      setShowCommentInput(true);
    }
  };

  const sendFeedback = async (type, category, textComment) => {
    setIsSubmitting(true);
    setError('');
    try {
      await api.submitFeedback({
        sessionId: sessionId || null,
        messageId: message.id && !message.id.startsWith('temp-') ? message.id : null,
        feedbackType: type,
        category: category,
        comment: textComment || null,
        queryExcerpt: (message.content || '').slice(0, 300),
        citationsFlagged: message.citations || []
      });
      setSubmitted(true);
      setShowCommentInput(false);
    } catch (err) {
      console.error('Feedback submit error:', err);
      setError(err.message || 'Failed to record feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDetailedSubmit = async (e) => {
    e.preventDefault();
    const type = feedbackType || 'comment_only';
    let category = 'general';
    if (type === 'citation_wrong') category = 'statute_accuracy';
    else if (type === 'reasoning_wrong') category = 'direction';
    else if (type === 'thumbs_down') category = 'clarity';

    await sendFeedback(type, category, comment);
  };

  if (submitted) {
    return (
      <div className="mt-2 text-[11px] text-emerald-700 bg-emerald-50 px-2 py-1 rounded inline-flex items-center gap-1 font-medium border border-emerald-200">
        <Check className="w-3 h-3 text-emerald-600" />
        <span>Feedback recorded for lawyer review</span>
      </div>
    );
  }

  return (
    <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-slate-500">
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mr-1">
          Beta Review:
        </span>

        {/* Thumbs Up */}
        <button
          type="button"
          disabled={isSubmitting}
          onClick={() => handleQuickFeedback('thumbs_up')}
          className={`px-2 py-1 rounded hover:bg-slate-100 transition inline-flex items-center gap-1 border ${
            feedbackType === 'thumbs_up' ? 'bg-emerald-50 border-emerald-300 text-emerald-700' : 'border-slate-200 text-slate-600'
          }`}
          title="Looks legally sound"
        >
          <ThumbsUp className="w-3 h-3" />
          <span className="hidden sm:inline">Sound</span>
        </button>

        {/* Citation Wrong */}
        <button
          type="button"
          disabled={isSubmitting}
          onClick={() => handleQuickFeedback('citation_wrong')}
          className={`px-2 py-1 rounded hover:bg-amber-50 transition inline-flex items-center gap-1 border ${
            feedbackType === 'citation_wrong' ? 'bg-amber-100 border-amber-400 text-amber-900 font-semibold' : 'border-slate-200 text-slate-600'
          }`}
          title="Flag inaccurate statute citation"
        >
          <AlertTriangle className="w-3 h-3 text-amber-600" />
          <span>Citation wrong</span>
        </button>

        {/* Reasoning Wrong */}
        <button
          type="button"
          disabled={isSubmitting}
          onClick={() => handleQuickFeedback('reasoning_wrong')}
          className={`px-2 py-1 rounded hover:bg-amber-50 transition inline-flex items-center gap-1 border ${
            feedbackType === 'reasoning_wrong' ? 'bg-amber-100 border-amber-400 text-amber-900 font-semibold' : 'border-slate-200 text-slate-600'
          }`}
          title="Flag flawed legal reasoning or inverted facts"
        >
          <AlertTriangle className="w-3 h-3 text-red-500" />
          <span>Reasoning wrong</span>
        </button>

        {/* Thumbs Down */}
        <button
          type="button"
          disabled={isSubmitting}
          onClick={() => handleQuickFeedback('thumbs_down')}
          className={`px-2 py-1 rounded hover:bg-slate-100 transition inline-flex items-center gap-1 border ${
            feedbackType === 'thumbs_down' ? 'bg-red-50 border-red-300 text-red-700' : 'border-slate-200 text-slate-600'
          }`}
          title="Unhelpful or unclear"
        >
          <ThumbsDown className="w-3 h-3" />
        </button>

        {/* Add Comment */}
        <button
          type="button"
          onClick={() => setShowCommentInput(!showCommentInput)}
          className="px-2 py-1 rounded hover:bg-slate-100 transition inline-flex items-center gap-1 text-slate-500 hover:text-slate-700"
          title="Add detailed comment"
        >
          <MessageSquare className="w-3 h-3" />
          <span className="hidden sm:inline">Note</span>
        </button>
      </div>

      {/* Expanded Comment Box */}
      {showCommentInput && (
        <form onSubmit={handleDetailedSubmit} className="mt-1 bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-xs space-y-2">
          <div className="flex items-center justify-between text-slate-700 font-medium">
            <span>
              {feedbackType === 'citation_wrong' && 'Flag Inaccurate Statute / Section'}
              {feedbackType === 'reasoning_wrong' && 'Flag Flawed Legal Reasoning'}
              {feedbackType === 'thumbs_down' && 'Report Unhelpful Output'}
              {(!feedbackType || feedbackType === 'comment_only') && 'Lawyer Review Note'}
            </span>
            <button
              type="button"
              onClick={() => setShowCommentInput(false)}
              className="text-slate-400 hover:text-slate-600"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Explain what was wrong (e.g. 'Should cite CPC Order 39 Rule 1 instead of Section 151', or 'Client is the landlord, not tenant')..."
            rows={2}
            className="w-full p-2 bg-white border border-slate-300 rounded text-slate-800 placeholder-slate-400 text-xs focus:ring-1 focus:ring-legal-500 focus:outline-hidden"
          />

          {error && <div className="text-red-600 text-[11px]">{error}</div>}

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowCommentInput(false)}
              className="px-2.5 py-1 text-slate-600 hover:bg-slate-200 rounded text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-3 py-1 bg-legal-800 text-white hover:bg-legal-900 rounded font-semibold text-xs inline-flex items-center gap-1 shadow-2xs"
            >
              <Send className="w-3 h-3" />
              <span>{isSubmitting ? 'Sending...' : 'Submit Feedback'}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
