import React, { useState, useEffect } from 'react';
import { ShieldCheck, Sun, Moon, RefreshCw, Activity, BarChart3, MessageSquare } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store';
import { resetForm, setActiveTab } from '../../store/interactionSlice';
import { clearMessages } from '../../store/chatSlice';
import { clearToolHistory } from '../../store/toolExecutionSlice';
import toast from 'react-hot-toast';

export const Header: React.FC = () => {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const dispatch = useDispatch();
  const activeTab = useSelector((state: RootState) => state.interaction.activeTab);

  useEffect(() => {
    document.body.className = `theme-${theme}`;
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    toast.success(`Switched to ${newTheme.toUpperCase()} mode`, {
      style: {
        background: newTheme === 'dark' ? '#181d2b' : '#ffffff',
        color: newTheme === 'dark' ? '#f0f3f9' : '#0f172a',
        border: '1px solid rgba(59, 130, 246, 0.4)'
      }
    });
  };

  const handleResetSession = () => {
    dispatch(resetForm());
    dispatch(clearMessages());
    dispatch(clearToolHistory());
    toast('Started a fresh interaction session', { icon: '🔄' });
  };

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0.85rem 1.75rem',
      backgroundColor: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: 'var(--shadow-sm)'
    }}>
      {/* Brand & Module Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, var(--accent-primary), #1d4ed8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          boxShadow: '0 4px 12px rgba(59, 130, 246, 0.35)'
        }}>
          <ShieldCheck size={24} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.15rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            AI-First Healthcare CRM
          </h1>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
            HCP Interaction Module <span style={{ color: 'var(--accent-primary)' }}>• Read-Only Form & AI Assistant</span>
          </p>
        </div>
      </div>

      {/* Tab Switcher (Interaction Log vs Analytics Dashboard) */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '0.25rem',
        borderRadius: '999px',
        backgroundColor: 'var(--bg-surface-secondary)',
        border: '1px solid var(--border-color)',
        gap: '0.25rem'
      }}>
        <button
          onClick={() => dispatch(setActiveTab('interaction'))}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            padding: '0.45rem 1rem',
            borderRadius: '999px',
            backgroundColor: activeTab === 'interaction' ? 'var(--accent-primary)' : 'transparent',
            color: activeTab === 'interaction' ? '#ffffff' : 'var(--text-secondary)',
            border: 'none',
            fontSize: '0.82rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'var(--transition-fast)'
          }}
        >
          <MessageSquare size={15} />
          <span>HCP Interaction Log</span>
        </button>

        <button
          onClick={() => dispatch(setActiveTab('analytics'))}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            padding: '0.45rem 1rem',
            borderRadius: '999px',
            backgroundColor: activeTab === 'analytics' ? 'var(--accent-primary)' : 'transparent',
            color: activeTab === 'analytics' ? '#ffffff' : 'var(--text-secondary)',
            border: 'none',
            fontSize: '0.82rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'var(--transition-fast)'
          }}
        >
          <BarChart3 size={15} />
          <span>Analytics Dashboard</span>
        </button>
      </div>

      {/* Engine Status Pill */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 0.85rem',
          borderRadius: '999px',
          backgroundColor: 'var(--bg-surface-secondary)',
          border: '1px solid var(--border-color)',
          fontSize: '0.78rem',
          fontWeight: 600,
          color: 'var(--text-primary)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: 'var(--accent-success)',
            boxShadow: '0 0 8px var(--accent-success)'
          }} />
          <Activity size={14} color="var(--accent-success)" />
          <span>LangGraph + Groq (<code style={{ color: 'var(--accent-primary)', fontWeight: 700 }}>llama-3.3-70b-versatile</code>)</span>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <button
            onClick={handleResetSession}
            title="Start New Interaction"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.45rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-surface-secondary)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)',
              fontSize: '0.8rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'var(--transition-fast)'
            }}
          >
            <RefreshCw size={14} />
            <span>New Session</span>
          </button>

          <button
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '38px',
              height: '38px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-surface-secondary)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              transition: 'var(--transition-fast)'
            }}
          >
            {theme === 'dark' ? <Sun size={18} color="var(--accent-warning)" /> : <Moon size={18} color="var(--accent-purple)" />}
          </button>
        </div>
      </div>
    </header>
  );
};
