import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store';
import { addMessage, setAiTyping, setNeedsConfirmation } from '../../store/chatSlice';
import { setFormData } from '../../store/interactionSlice';
import { setToolRunning, recordToolExecution } from '../../store/toolExecutionSlice';
import { crmApiService } from '../../services/api';
import { ToolExecutionBadge } from './ToolExecutionBadge';
import { Send, Bot, User, Sparkles, CheckCircle2, HelpCircle, CornerDownLeft, Mic, MicOff } from 'lucide-react';
import toast from 'react-hot-toast';

export const ChatWindow: React.FC = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef<any>(null);
  const { messages, sessionId, isAiTyping, needsConfirmation } = useSelector((state: RootState) => state.chat);
  const currentFormData = useSelector((state: RootState) => state.interaction.currentFormData);
  const dispatch = useDispatch();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isAiTyping]);

  const handleToggleRecord = () => {
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      toast.error("Web Speech API is not supported in this browser. Try Google Chrome or Edge.");
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
        toast("Listening... Speak natural interaction details now", { icon: "🎙️", duration: 3000 });
      };

      recognition.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setInputMessage(currentTranscript);
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsRecording(false);
        if (event.error !== 'no-speech') {
          toast.error(`Microphone error: ${event.error}`);
        }
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error(err);
      setIsRecording(false);
      toast.error("Could not access microphone.");
    }
  };

  const handleSendMessage = async (customMessage?: string) => {
    const textToSend = customMessage || inputMessage;
    if (!textToSend.trim() || isAiTyping) return;

    // Add user message to Redux store
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user' as const,
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    dispatch(addMessage(userMsg));
    if (!customMessage) setInputMessage('');

    // Trigger AI Typing and Tool execution state
    dispatch(setAiTyping(true));
    dispatch(setToolRunning(true));

    try {
      // Call backend FastAPI endpoint which executes LangGraph & Groq
      const response = await crmApiService.sendChatMessage({
        session_id: sessionId,
        message: textToSend,
        current_form_data: currentFormData
      });

      // Update Form Data in Redux Store
      if (response.updated_form_data) {
        dispatch(setFormData(response.updated_form_data));
      }

      // Record tool execution badge if tool ran
      if (response.tool_execution) {
        dispatch(recordToolExecution(response.tool_execution));
      } else {
        dispatch(setToolRunning(false));
      }

      // Check confirmation status
      dispatch(setNeedsConfirmation(response.needs_confirmation));

      // Add AI response message
      const aiMsg = {
        id: `ai-${Date.now()}`,
        sender: 'ai' as const,
        text: response.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        toolExecuted: response.tool_execution?.tool_name
      };
      dispatch(addMessage(aiMsg));

      if (response.saved_interaction_id) {
        toast.success(`Interaction #${response.saved_interaction_id} successfully saved to Supabase!`, {
          icon: '🎉',
          duration: 4000
        });
      }
    } catch (error: any) {
      dispatch(setToolRunning(false));
      dispatch(setAiTyping(false));
      const errorText = error.response?.data?.detail || 'Could not connect to LangGraph service. Make sure backend is running on port 8000.';
      toast.error(errorText);
      dispatch(addMessage({
        id: `err-${Date.now()}`,
        sender: 'system',
        text: `Error: ${errorText}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }));
    } finally {
      dispatch(setAiTyping(false));
    }
  };

  const handleConfirmSave = () => {
    handleSendMessage("Yes, save this interaction to Supabase.");
  };

  const handleExampleClick = (exampleText: string) => {
    handleSendMessage(exampleText);
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
      {/* Chat Header */}
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
            background: 'linear-gradient(135deg, var(--accent-purple), #6d28d9)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff'
          }}>
            <Bot size={18} />
          </div>
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Conversational AI Assistant
            </h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Powered by LangGraph Agent & Groq (`llama-3.3-70b-versatile`)
            </p>
          </div>
        </div>

        <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
          Session: <code style={{ color: 'var(--accent-primary)' }}>{sessionId.slice(-6)}</code>
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div style={{
        padding: '1.5rem',
        flex: 1,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        {/* Tool Execution Diagnostic Badge (If recently called) */}
        <ToolExecutionBadge />

        {/* Chat Messages */}
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const isSystem = msg.sender === 'system';

          return (
            <div
              key={msg.id}
              style={{
                display: 'flex',
                gap: '0.75rem',
                alignSelf: isUser ? 'flex-end' : 'flex-start',
                maxWidth: isUser ? '82%' : '90%'
              }}
            >
              {!isUser && (
                <div style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '8px',
                  backgroundColor: isSystem ? 'rgba(239, 68, 68, 0.2)' : 'rgba(139, 92, 246, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isSystem ? '#ef4444' : 'var(--accent-purple)',
                  flexShrink: 0
                }}>
                  <Bot size={16} />
                </div>
              )}

              <div style={{
                padding: '0.85rem 1.15rem',
                borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                backgroundColor: isUser
                  ? 'var(--accent-primary)'
                  : (isSystem ? 'rgba(239, 68, 68, 0.12)' : 'var(--bg-surface-secondary)'),
                color: isUser ? '#ffffff' : (isSystem ? '#f87171' : 'var(--text-primary)'),
                border: isUser ? 'none' : '1px solid var(--border-color)',
                fontSize: '0.88rem',
                lineHeight: 1.5,
                boxShadow: 'var(--shadow-sm)'
              }}>
                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'flex-end',
                  gap: '0.4rem',
                  fontSize: '0.68rem',
                  color: isUser ? 'rgba(255, 255, 255, 0.75)' : 'var(--text-tertiary)',
                  marginTop: '0.45rem'
                }}>
                  {msg.toolExecuted && (
                    <span style={{ color: 'var(--accent-success)', fontWeight: 600 }}>
                      ⚡ {msg.toolExecuted}()
                    </span>
                  )}
                  <span>{msg.timestamp}</span>
                </div>
              </div>

              {isUser && (
                <div style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '8px',
                  backgroundColor: 'rgba(59, 130, 246, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--accent-primary)',
                  flexShrink: 0
                }}>
                  <User size={16} />
                </div>
              )}
            </div>
          );
        })}

        {/* AI Typing Indicator */}
        {isAiTyping && (
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <div style={{
              width: '30px',
              height: '30px',
              borderRadius: '8px',
              backgroundColor: 'rgba(139, 92, 246, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-purple)'
            }}>
              <Bot size={16} />
            </div>
            <div style={{
              padding: '0.75rem 1.15rem',
              borderRadius: '16px',
              backgroundColor: 'var(--bg-surface-secondary)',
              border: '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}>
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        {/* Confirmation Pill Banner (Mandatory Requirement) */}
        {needsConfirmation && !isAiTyping && (
          <div style={{
            padding: '0.85rem 1.15rem',
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.25))',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            animation: 'pulse-glow 2s infinite ease-in-out'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <CheckCircle2 size={20} color="var(--accent-success)" />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Ready to Commit to Supabase Database
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  Verify the read-only form on the left, then click confirm to save.
                </div>
              </div>
            </div>

            <button
              onClick={handleConfirmSave}
              style={{
                padding: '0.55rem 1.1rem',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--accent-success)',
                color: '#ffffff',
                fontWeight: 700,
                fontSize: '0.82rem',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.35)',
                transition: 'var(--transition-fast)'
              }}
            >
              Confirm & Save
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Bar */}
      <div style={{
        padding: '0.65rem 1.5rem',
        backgroundColor: 'var(--bg-surface-secondary)',
        borderTop: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        overflowX: 'auto'
      }}>
        <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-tertiary)', flexShrink: 0, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <Sparkles size={12} /> Try Examples:
        </span>
        <button
          onClick={() => handleExampleClick("I met Dr Sharma at Apollo Hospital today. Discussed CardioPlus. Shared brochure. Doctor was interested. Schedule follow-up next Tuesday.")}
          style={{
            padding: '0.35rem 0.65rem',
            borderRadius: '999px',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            fontSize: '0.72rem',
            whiteSpace: 'nowrap',
            cursor: 'pointer',
            transition: 'var(--transition-fast)'
          }}
        >
          🩺 Log Dr Sharma (Apollo Hospital)
        </button>
        <button
          onClick={() => handleExampleClick("Search for Dr. Anjali Gupta at AIIMS")}
          style={{
            padding: '0.35rem 0.65rem',
            borderRadius: '999px',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            fontSize: '0.72rem',
            whiteSpace: 'nowrap',
            cursor: 'pointer',
            transition: 'var(--transition-fast)'
          }}
        >
          🔍 Search Dr. Gupta (AIIMS)
        </button>
        <button
          onClick={() => handleExampleClick("Show history and sentiment trend for Dr. Rakesh Sharma")}
          style={{
            padding: '0.35rem 0.65rem',
            borderRadius: '999px',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            fontSize: '0.72rem',
            whiteSpace: 'nowrap',
            cursor: 'pointer',
            transition: 'var(--transition-fast)'
          }}
        >
          📊 History & Sentiment Trend
        </button>
      </div>

      {/* Input Box */}
      <div style={{
        padding: '1rem 1.5rem',
        backgroundColor: 'var(--bg-surface)',
        borderTop: '1px solid var(--border-color)'
      }}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (isRecording && recognitionRef.current) {
              recognitionRef.current.stop();
              setIsRecording(false);
            }
            handleSendMessage();
          }}
          style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}
        >
          <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center' }}>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={isAiTyping}
              placeholder={isRecording ? "🎙️ Listening... Speak now (or watch audio waveform)..." : "Type natural language instruction (e.g. 'Met Dr. Mehta at Fortis...')..."}
              style={{
                width: '100%',
                padding: '0.85rem 1.15rem',
                borderRadius: 'var(--radius-md)',
                backgroundColor: isRecording ? 'rgba(239, 68, 68, 0.08)' : 'var(--bg-surface-secondary)',
                border: isRecording ? '1px solid #ef4444' : '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                fontSize: '0.88rem',
                outline: 'none',
                transition: 'var(--transition-fast)',
                boxShadow: isRecording ? '0 0 16px rgba(239, 68, 68, 0.25)' : 'none'
              }}
            />
            {isRecording && (
              <div style={{
                position: 'absolute',
                right: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '3px',
                pointerEvents: 'none'
              }}>
                {[1, 2, 3, 4, 5].map((i) => (
                  <span key={i} style={{
                    width: '3px',
                    backgroundColor: '#ef4444',
                    borderRadius: '2px',
                    animation: `waveform-bar 0.7s infinite ease-in-out`,
                    animationDelay: `${i * 0.12}s`
                  }} />
                ))}
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={handleToggleRecord}
            title={isRecording ? "Stop Recording Voice" : "Click to Speak (Voice-to-Text via Web Speech API)"}
            style={{
              padding: '0.85rem',
              borderRadius: 'var(--radius-md)',
              backgroundColor: isRecording ? '#ef4444' : 'var(--bg-surface-secondary)',
              color: isRecording ? '#ffffff' : 'var(--text-secondary)',
              border: isRecording ? '1px solid #ef4444' : '1px solid var(--border-color)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'var(--transition-fast)',
              animation: isRecording ? 'mic-pulse 1.5s infinite' : 'none'
            }}
          >
            {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
          </button>

          <button
            type="submit"
            disabled={!inputMessage.trim() || isAiTyping}
            style={{
              padding: '0.85rem 1.25rem',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--accent-primary)',
              color: '#ffffff',
              fontWeight: 600,
              border: 'none',
              cursor: (!inputMessage.trim() || isAiTyping) ? 'not-allowed' : 'pointer',
              opacity: (!inputMessage.trim() || isAiTyping) ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 4px 12px rgba(59, 130, 246, 0.35)',
              transition: 'var(--transition-fast)'
            }}
          >
            <span>Send</span>
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
};
