import { useState, useRef, useEffect, useCallback } from 'react';
import { Bot, X, Maximize2, Loader2, Send, Zap, FileText, CheckCircle, Wrench } from 'lucide-react';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

function Markdownish({ text }) {
  if (!text) return null;
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**')
      ? <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>
      : <span key={i}>{part}</span>,
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="typing-dot h-1.5 w-1.5 rounded-full bg-brand-secondary/40"
          style={{ animationDelay: `${i * 0.18}s` }}
        />
      ))}
    </div>
  );
}

const ROLE_PROMPTS = {
  collaborator: [
    '📋 Mes congés restants',
    '📄 Génère une attestation de travail',
    '💰 Mon contrat actuel',
    '📊 Mes tâches en cours',
  ],
  manager: [
    '👥 Quelles sont les alertes de mon équipe ?',
    '📅 Qui est en congé aujourd\'hui ?',
    '🎯 Donne moi les infos de Walid Traoré',
  ],
  hr: [
    '🔎 Quel est le profil de Jane Doe ?',
    '📑 Combien de contrats actifs avons-nous ?',
  ],
  director: [
    '📈 Quel est le taux de turnover actuel ?',
    '💡 Quels départements sont sous surveillance ?',
  ]
};

export default function AIChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [activeConversationId, setActiveConversationId] = useState(null);
  
  const endRef = useRef(null);
  const streamRef = useRef(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streaming, isOpen]);

  const startNewConversation = () => {
    setActiveConversationId(null);
    setMessages([
      {
        from: 'bot',
        isUser: false,
        text: "Bonjour ! 👋 Je suis **Pulse AI**. Comment puis-je vous aider ?",
      },
    ]);
  };

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      startNewConversation();
    }
  }, [isOpen]);

  const send = useCallback(async (text) => {
    const content = (text || '').trim();
    if (!content || streaming) return;

    setMessages((m) => [...m, { from: 'user', isUser: true, text: content }]);
    setInput('');
    setStreaming(true);

    setMessages((m) => [
      ...m,
      { from: 'bot', isUser: false, text: '', sources: [], toolCalls: [], isStreaming: true },
    ]);

    try {
      const stream = await api.stream('/chat/stream', {
        message: content,
        conversation_id: activeConversationId,
      });
      streamRef.current = stream;

      for await (const chunk of stream.chunks()) {
        if (chunk.type === 'conversation_id') {
          setActiveConversationId(chunk.content);
        } else if (chunk.type === 'text') {
          setMessages((prev) => {
            const updated = [...prev];
            const lastBot = updated[updated.length - 1];
            if (lastBot && !lastBot.isUser) {
              updated[updated.length - 1] = {
                ...lastBot,
                text: lastBot.text + chunk.content,
              };
            }
            return updated;
          });
        } else if (chunk.type === 'source') {
          setMessages((prev) => {
            const updated = [...prev];
            const lastBot = updated[updated.length - 1];
            if (lastBot && !lastBot.isUser) {
              updated[updated.length - 1] = {
                ...lastBot,
                sources: [...(lastBot.sources || []), chunk.content],
              };
            }
            return updated;
          });
        } else if (chunk.type === 'tool_call') {
          setMessages((prev) => {
            const updated = [...prev];
            const lastBot = updated[updated.length - 1];
            if (lastBot && !lastBot.isUser) {
              updated[updated.length - 1] = {
                ...lastBot,
                toolCalls: [...(lastBot.toolCalls || []), chunk.content],
              };
            }
            return updated;
          });
        } else if (chunk.type === 'done') {
          setMessages((prev) => {
            const updated = [...prev];
            const lastBot = updated[updated.length - 1];
            if (lastBot && !lastBot.isUser) {
              updated[updated.length - 1] = {
                ...lastBot,
                isStreaming: false,
                sources: chunk.content?.sources || lastBot.sources || [],
              };
            }
            return updated;
          });
        }
      }
    } catch (e) {
      setMessages((prev) => {
        const updated = [...prev];
        const lastBot = updated[updated.length - 1];
        if (lastBot && !lastBot.isUser) {
          updated[updated.length - 1] = {
            ...lastBot,
            text: "Désolé, une erreur s'est produite.",
            isStreaming: false,
          };
        }
        return updated;
      });
    } finally {
      setStreaming(false);
      streamRef.current = null;
    }
  }, [streaming, activeConversationId]);

  // Déterminer le rôle principal
  const getPrimaryRole = () => {
    if (!user?.roles) return 'collaborator';
    if (user.roles.includes('admin')) return 'admin';
    if (user.roles.includes('director')) return 'director';
    if (user.roles.includes('hr')) return 'hr';
    if (user.roles.includes('manager')) return 'manager';
    return 'collaborator';
  };
  
  const role = getPrimaryRole();
  const quickPrompts = ROLE_PROMPTS[role] || ROLE_PROMPTS['collaborator'];

  const goToFullScreen = () => {
    setIsOpen(false);
    // Navigation vers la page Assistant du rôle courant
    const section = role === 'admin' ? 'admin' : role === 'hr' ? 'rh' : role;
    navigate(`/${section}/assistant`);
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-brand-secondary text-white shadow-lg transition-transform hover:scale-105",
          isOpen && "rotate-90 scale-0"
        )}
      >
        <Bot size={24} />
      </button>

      {/* Chat Widget Panel */}
      <div
        className={cn(
          "fixed bottom-6 right-6 z-50 flex h-[600px] w-[380px] flex-col overflow-hidden rounded-2xl border border-brand-secondary/10 bg-white shadow-2xl transition-all duration-300 origin-bottom-right",
          isOpen ? "scale-100 opacity-100" : "scale-0 opacity-0 pointer-events-none"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between bg-brand-secondary px-4 py-3 text-white">
          <div className="flex items-center gap-2">
            <Bot size={18} />
            <h3 className="font-semibold text-sm">Pulse AI</h3>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={goToFullScreen} className="text-white/80 hover:text-white" title="Ouvrir en plein écran">
              <Maximize2 size={16} />
            </button>
            <button onClick={() => setIsOpen(false)} className="text-white/80 hover:text-white" title="Fermer">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-brand-light/30">
          {messages.map((msg, i) => (
            <div key={i}>
              {msg.isUser ? (
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-brand-secondary px-3 py-2 text-sm text-white shadow-sm">
                    {msg.text}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-1.5">
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="space-y-1.5">
                      {msg.toolCalls.map((tc, ti) => (
                        <div key={ti} className="rounded-xl border border-brand-secondary/15 bg-white px-3 py-2 text-xs">
                          <div className="flex items-center gap-1.5 text-brand-secondary/70">
                            <Wrench size={10} />
                            <span>Recherche en cours...</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="flex gap-2">
                    <div className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-brand-secondary/10 text-brand-secondary">
                      <Bot size={12} />
                    </div>
                    <div className="rounded-2xl rounded-tl-sm bg-white border border-brand-secondary/10 px-3 py-2 text-sm text-brand-dark shadow-sm">
                      {msg.text ? (
                        <Markdownish text={msg.text} />
                      ) : msg.isStreaming ? (
                        <TypingDots />
                      ) : null}
                      {msg.isStreaming && msg.text && (
                        <span className="inline-block w-1 h-3 bg-brand-secondary/60 animate-pulse ml-0.5 align-text-bottom" />
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
          {streaming && messages.length > 0 && !messages[messages.length - 1]?.text && (
            <div className="flex gap-2">
              <div className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-brand-secondary/10 text-brand-secondary">
                <Bot size={12} />
              </div>
              <div className="rounded-2xl rounded-tl-sm bg-white border border-brand-secondary/10 px-3 py-2 shadow-sm">
                <TypingDots />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Composer */}
        <div className="border-t border-brand-secondary/10 bg-white p-3">
          {messages.length <= 1 && (
            <div className="flex flex-col gap-1.5 mb-3">
              {quickPrompts.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p.replace(/^[^ ]+ /, ''))}
                  className="text-left rounded-lg border border-brand-secondary/15 bg-brand-light/30 px-3 py-1.5 text-xs text-brand-secondary hover:bg-brand-secondary/5 transition-colors truncate"
                >
                  {p}
                </button>
              ))}
            </div>
          )}
          
          <form
            onSubmit={(e) => { e.preventDefault(); send(input); }}
            className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-brand-light/50 px-3 py-2"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Posez une question..."
              className="flex-1 bg-transparent text-sm text-brand-dark placeholder:text-brand-secondary/40 outline-none"
            />
            <button
              type="submit"
              disabled={!input.trim() || streaming}
              className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary text-white disabled:opacity-40"
            >
              {streaming ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
