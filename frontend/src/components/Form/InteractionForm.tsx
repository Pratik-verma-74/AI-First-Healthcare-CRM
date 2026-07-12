import React, { useState, useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { Lock, FileText, Calendar, Clock, Users, Package, Smile, CheckCircle, ArrowRight, Sparkles, Copy, Check, Volume2, Square } from 'lucide-react';
import toast from 'react-hot-toast';

export const InteractionForm: React.FC = () => {
  const formData = useSelector((state: RootState) => state.interaction.currentFormData);
  const [copied, setCopied] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [recentlyUpdatedFields, setRecentlyUpdatedFields] = useState<Set<string>>(new Set());
  const prevFormDataRef = useRef<any>(formData);

  useEffect(() => {
    const prev = prevFormDataRef.current;
    if (!prev) {
      prevFormDataRef.current = formData;
      return;
    }
    const updated = new Set<string>();
    const fieldsToCheck = [
      'hcp_name', 'interaction_type', 'date', 'time', 'attendees',
      'topics_discussed', 'materials_shared', 'samples_distributed',
      'observed_sentiment', 'outcomes', 'follow_up_actions', 'ai_summary'
    ];
    fieldsToCheck.forEach(field => {
      if ((prev as any)[field] !== (formData as any)[field] && (formData as any)[field]) {
        updated.add(field);
      }
    });
    if (updated.size > 0) {
      setRecentlyUpdatedFields(updated);
      const timer = setTimeout(() => {
        setRecentlyUpdatedFields(new Set());
      }, 2300);
    }
    prevFormDataRef.current = formData;
  }, [formData]);

  const handleCopySummary = () => {
    if (!formData.ai_summary) return;
    navigator.clipboard.writeText(formData.ai_summary);
    setCopied(true);
    toast.success("AI Summary copied to clipboard!");
    setTimeout(() => setCopied(false), 2500);
  };

  const handleSpeakSummary = () => {
    if (!formData.ai_summary || !('speechSynthesis' in window)) {
      toast.error("Text-to-Speech is not supported or summary is empty.");
      return;
    }
    if (isPlayingAudio) {
      window.speechSynthesis.cancel();
      setIsPlayingAudio(false);
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(formData.ai_summary);
    utterance.rate = 1.0;
    utterance.onend = () => setIsPlayingAudio(false);
    utterance.onerror = () => setIsPlayingAudio(false);
    setIsPlayingAudio(true);
    window.speechSynthesis.speak(utterance);
  };

  const getFieldClass = (fieldName: string) => {
    return `form-readonly-field ${recentlyUpdatedFields.has(fieldName) ? 'field-recently-updated' : ''}`;
  };

  const renderSentimentBadge = (sentiment: string) => {
    let color = 'var(--accent-warning)';
    let bg = 'rgba(245, 158, 11, 0.15)';
    if (sentiment?.toLowerCase() === 'positive') {
      color = 'var(--accent-success)';
      bg = 'rgba(16, 185, 129, 0.15)';
    } else if (sentiment?.toLowerCase() === 'negative') {
      color = '#ef4444';
      bg = 'rgba(239, 68, 68, 0.15)';
    }
    return (
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.35rem',
        padding: '0.25rem 0.65rem',
        borderRadius: '999px',
        backgroundColor: bg,
        color: color,
        fontSize: '0.78rem',
        fontWeight: 600
      }}>
        <Smile size={14} />
        {sentiment || 'Neutral'}
      </span>
    );
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: 'var(--bg-surface)',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid var(--border-color)',
      overflow: 'hidden',
      boxShadow: 'var(--shadow-md)'
    }}>
      {/* Read-Only Header Banner */}
      <div style={{
        padding: '1rem 1.5rem',
        backgroundColor: 'var(--bg-surface-secondary)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            backgroundColor: 'rgba(59, 130, 246, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-primary)'
          }}>
            <FileText size={18} />
          </div>
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Interaction Details (Structured Form)
            </h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Medical Representative Log — Automatically synced by LangGraph AI
            </p>
          </div>
        </div>

        {/* Lock Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.35rem 0.75rem',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: '#f87171',
          fontSize: '0.75rem',
          fontWeight: 600
        }}>
          <Lock size={13} />
          <span>Read-Only Mode (AI Controlled)</span>
        </div>
      </div>

      {/* Form Content Scrollable Area */}
      <div style={{
        padding: '1.5rem',
        overflowY: 'auto',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem'
      }}>
        {/* Row 1: HCP Name & Interaction Type */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              HCP Name & Hospital
            </label>
            <input
              type="text"
              readOnly
              className={getFieldClass('hcp_name')}
              value={formData.hcp_name ? `${formData.hcp_name} (${formData.hospital || 'Hospital N/A'})` : ''}
              placeholder="Waiting for AI extraction (e.g., Dr. Sharma at Apollo)..."
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.88rem'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Interaction Type
            </label>
            <input
              type="text"
              readOnly
              className={getFieldClass('interaction_type')}
              value={formData.interaction_type || 'Meeting'}
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.88rem'
              }}
            />
          </div>
        </div>

        {/* Row 2: Date & Time */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              <Calendar size={13} /> Interaction Date
            </label>
            <input
              type="text"
              readOnly
              className={getFieldClass('date')}
              value={formData.date || ''}
              placeholder="YYYY-MM-DD"
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.88rem'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              <Clock size={13} /> Interaction Time
            </label>
            <input
              type="text"
              readOnly
              className={getFieldClass('time')}
              value={formData.time || ''}
              placeholder="12:00"
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.88rem'
              }}
            />
          </div>
        </div>

        {/* Row 3: Attendees */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
            <Users size={13} /> Attendees
          </label>
          <input
            type="text"
            readOnly
            className={getFieldClass('attendees')}
            value={formData.attendees || ''}
            placeholder="Names of participants..."
            style={{
              width: '100%',
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.88rem'
            }}
          />
        </div>

        {/* Row 4: Topics Discussed */}
        <div>
          <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
            Topics Discussed / Key Discussion Points
          </label>
          <textarea
            readOnly
            className={getFieldClass('topics_discussed')}
            rows={2}
            value={formData.topics_discussed || ''}
            placeholder="Clinical discussions, therapy benefits, dosage questions..."
            style={{
              width: '100%',
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.88rem',
              resize: 'none'
            }}
          />
        </div>

        {/* Row 5: Materials Shared & Samples Distributed */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Materials Shared
            </label>
            <input
              type="text"
              readOnly
              className={getFieldClass('materials_shared')}
              value={formData.materials_shared || ''}
              placeholder="Brochures, monographs..."
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.88rem'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              <Package size={13} /> Samples Distributed
            </label>
            <input
              type="text"
              readOnly
              className={getFieldClass('samples_distributed')}
              value={formData.samples_distributed || ''}
              placeholder="Starter kits, samples quantity..."
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.88rem'
              }}
            />
          </div>
        </div>

        {/* Row 6: Observed Sentiment & Outcomes */}
        <div style={{ display: 'grid', gridTemplateColumns: '0.8fr 1.2fr', gap: '1rem', alignItems: 'start' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Observed HCP Sentiment
            </label>
            <div className={recentlyUpdatedFields.has('observed_sentiment') ? 'field-recently-updated' : ''} style={{
              padding: '0.55rem 0.75rem',
              backgroundColor: 'var(--bg-surface-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center'
            }}>
              {renderSentimentBadge(formData.observed_sentiment)}
            </div>
          </div>

          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              <CheckCircle size={13} /> Outcomes & Agreements
            </label>
            <input
              type="text"
              readOnly
              className={getFieldClass('outcomes')}
              value={formData.outcomes || ''}
              placeholder="E.g., Doctor agreed to prescribe or participate..."
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.88rem'
              }}
            />
          </div>
        </div>

        {/* Row 7: Follow-up Actions */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
            <ArrowRight size={13} /> Follow-up Actions
          </label>
          <input
            type="text"
            readOnly
            className={getFieldClass('follow_up_actions')}
            value={formData.follow_up_actions || ''}
            placeholder="Scheduled visits, tasks, due dates..."
            style={{
              width: '100%',
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.88rem'
            }}
          />
        </div>

        {/* Row 8: AI Generated Summary */}
        <div style={{
          padding: '1.15rem',
          borderRadius: 'var(--radius-md)',
          background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.08))',
          border: '1px dashed rgba(59, 130, 246, 0.45)',
          position: 'relative'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', color: 'var(--accent-primary)' }}>
              <Sparkles size={16} />
              <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                LangGraph AI Generated Summary
              </span>
            </div>
            {formData.ai_summary && (
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  type="button"
                  onClick={handleCopySummary}
                  title="Copy Summary"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    padding: '0.3rem 0.65rem',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: copied ? 'var(--accent-success)' : 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: copied ? '#fff' : 'var(--text-secondary)',
                    fontSize: '0.74rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'var(--transition-fast)'
                  }}
                >
                  {copied ? <Check size={13} /> : <Copy size={13} />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>

                <button
                  type="button"
                  onClick={handleSpeakSummary}
                  title={isPlayingAudio ? "Stop Audio Readout" : "Listen to Summary Readout"}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    padding: '0.3rem 0.65rem',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: isPlayingAudio ? 'rgba(239, 68, 68, 0.2)' : 'var(--bg-surface)',
                    border: isPlayingAudio ? '1px solid #ef4444' : '1px solid var(--border-color)',
                    color: isPlayingAudio ? '#ef4444' : 'var(--text-secondary)',
                    fontSize: '0.74rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'var(--transition-fast)'
                  }}
                >
                  {isPlayingAudio ? <Square size={13} fill="#ef4444" /> : <Volume2 size={13} />}
                  <span>{isPlayingAudio ? 'Stop' : 'Listen'}</span>
                </button>
              </div>
            )}
          </div>
          <p className={recentlyUpdatedFields.has('ai_summary') ? 'field-recently-updated' : ''} style={{
            fontSize: '0.88rem',
            lineHeight: 1.55,
            color: formData.ai_summary ? 'var(--text-primary)' : 'var(--text-tertiary)',
            fontStyle: formData.ai_summary ? 'normal' : 'italic',
            padding: '0.35rem',
            borderRadius: 'var(--radius-sm)'
          }}>
            {formData.ai_summary || 'Summary will automatically generate here once you describe the interaction in the chat assistant.'}
          </p>
        </div>
      </div>

      {/* Form Footer Status Bar */}
      <div style={{
        padding: '0.75rem 1.5rem',
        backgroundColor: 'var(--bg-surface-secondary)',
        borderTop: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.78rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-secondary)' }}>
          <span>Current Status:</span>
          <span style={{
            fontWeight: 700,
            color: formData.status === 'Saved' ? 'var(--accent-success)' : 'var(--accent-warning)'
          }}>
            {formData.status?.toUpperCase() || 'DRAFT'}
          </span>
          {formData.id && <span style={{ color: 'var(--text-tertiary)' }}>(Database ID #{formData.id})</span>}
        </div>
        <span style={{ color: 'var(--text-tertiary)', fontSize: '0.72rem' }}>
          Sync Mode: Active via Redux Toolkit
        </span>
      </div>
    </div>
  );
};
