import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { InteractionForm } from '../Form/InteractionForm';
import { ChatWindow } from '../Chat/ChatWindow';
import { AnalyticsView } from './AnalyticsView';

export const DashboardLayout: React.FC = () => {
  const activeTab = useSelector((state: RootState) => state.interaction.activeTab);

  if (activeTab === 'analytics') {
    return (
      <main style={{
        height: 'calc(100vh - 65px)',
        maxHeight: 'calc(100vh - 65px)',
        overflow: 'hidden'
      }}>
        <AnalyticsView />
      </main>
    );
  }

  return (
    <main style={{
      display: 'grid',
      gridTemplateColumns: 'minmax(480px, 1fr) minmax(500px, 1.15fr)',
      gap: '1.5rem',
      padding: '1.5rem',
      height: 'calc(100vh - 65px)',
      maxHeight: 'calc(100vh - 65px)',
      overflow: 'hidden'
    }}>
      {/* Left Pane: Read-Only Form Details */}
      <section style={{ height: '100%', overflow: 'hidden' }}>
        <InteractionForm />
      </section>

      {/* Right Pane: AI Conversational Chat Assistant */}
      <section style={{ height: '100%', overflow: 'hidden' }}>
        <ChatWindow />
      </section>
    </main>
  );
};
