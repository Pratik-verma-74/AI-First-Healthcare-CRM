import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { Cpu, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';

export const ToolExecutionBadge: React.FC = () => {
  const { lastTool, isRunning } = useSelector((state: RootState) => state.toolExecution);
  const [expanded, setExpanded] = React.useState(false);

  if (isRunning) {
    return (
      <div style={{
        padding: '0.65rem 1rem',
        borderRadius: 'var(--radius-md)',
        backgroundColor: 'rgba(139, 92, 246, 0.12)',
        border: '1px solid rgba(139, 92, 246, 0.35)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '0.85rem',
        animation: 'pulse-glow 1.5s infinite ease-in-out'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
          <Cpu size={16} color="var(--accent-purple)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            LangGraph Agent Routing Tool...
          </span>
        </div>
        <span style={{ fontSize: '0.72rem', color: 'var(--accent-purple)', fontWeight: 600 }}>
          Processing Groq LLM Output
        </span>
      </div>
    );
  }

  if (!lastTool || lastTool.tool_name === 'conversational_assistant') {
    return null;
  }

  const isSuccess = lastTool.status === 'SUCCESS';

  return (
    <div style={{
      padding: '0.75rem 1rem',
      borderRadius: 'var(--radius-md)',
      backgroundColor: isSuccess ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
      border: `1px solid ${isSuccess ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)'}`,
      marginBottom: '0.85rem',
      transition: 'var(--transition-fast)'
    }}>
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
          {isSuccess ? <CheckCircle2 size={16} color="var(--accent-success)" /> : <AlertTriangle size={16} color="#ef4444" />}
          <div>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: isSuccess ? 'var(--accent-success)' : '#ef4444' }}>
              LangGraph Tool Executed:
            </span>{' '}
            <code style={{
              fontSize: '0.8rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              backgroundColor: 'var(--bg-surface)',
              padding: '0.15rem 0.4rem',
              borderRadius: '4px'
            }}>
              {lastTool.tool_name}()
            </code>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', fontWeight: 500 }}>
            {lastTool.execution_time_ms}ms
          </span>
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
        {lastTool.tool_summary}
      </p>

      {/* Expanded Parameters Box */}
      {expanded && lastTool.parameters && Object.keys(lastTool.parameters).length > 0 && (
        <div style={{
          marginTop: '0.65rem',
          padding: '0.65rem',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-color)',
          fontSize: '0.75rem',
          fontFamily: 'monospace',
          color: 'var(--text-secondary)',
          maxHeight: '150px',
          overflowY: 'auto'
        }}>
          <div style={{ fontWeight: 700, marginBottom: '0.3rem', color: 'var(--text-tertiary)' }}>Extracted Parameters:</div>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(lastTool.parameters, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
