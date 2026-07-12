import React from 'react';
import { InteractionForm } from '../Form/InteractionForm';
import { ChatWindow } from '../Chat/ChatWindow';

export const DashboardLayout: React.FC = () => {
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
