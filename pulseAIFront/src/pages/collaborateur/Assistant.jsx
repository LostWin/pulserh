import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Bot, Sparkles, Plus, Share2, X, FileText, CheckCircle, Paperclip, Mic, Zap, Download, Wrench, Loader2, Trash2 } from 'lucide-react';
import { api } from '../../lib/api';
import { cn } from '../../lib/utils';

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
          className="typing-dot h-2 w-2 rounded-full bg-brand-secondary/40"
          style={{ animationDelay: `${i * 0.18}s` }}
        />
      ))}
    </div>
  );
}

const QUICK_PROMPTS = [
  '📋 Mes congés restants',
  '📄 Génère une attestation de travail',
  '💰 Mon contrat actuel',
  '📊 Mes tâches en cours',
];

export default function Assistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [loadingConversations, setLoadingConversations] = useState(true);
  const endRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streaming]);

  // Charger les conversations au montage
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoadingConversations(true);
      const data = await api.get('/chat/conversations');
      setConversations(data || []);
    } catch (e) {
      console.error('Erreur chargement conversations:', e);
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadConversationMessages = async (convId) => {
    try {
      const data = await api.get(`/chat/conversations/${convId}/messages`);
      setMessages(
        (data || []).map((m) => ({
          from: m.role === 'user' ? 'user' : 'bot',
          isUser: m.role === 'user',
          text: m.content || '',
          sources: m.sources || [],
          toolCalls: m.tool_calls || [],
        }))
      );
      setActiveConversationId(convId);
    } catch (e) {
      console.error('Erreur chargement messages:', e);
    }
  };

  const startNewConversation = () => {
    setActiveConversationId(null);
    setMessages([
      {
        from: 'bot',
        isUser: false,
        text: "Bonjour ! 👋 Je suis **Pulse AI**, votre assistante RH intelligente. Je peux vous aider avec vos congés, votre paie, vos documents et bien plus. Comment puis-je vous aider ?",
      },
    ]);
  };

  const deleteConversation = async (convId, e) => {
    e.stopPropagation();
    try {
      await api.delete(`/chat/conversations/${convId}`);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (activeConversationId === convId) {
        startNewConversation();
      }
    } catch (err) {
      console.error('Erreur suppression conversation:', err);
    }
  };

  // Initialiser avec un message de bienvenue
  useEffect(() => {
    if (messages.length === 0) {
      startNewConversation();
    }
  }, []);

  const send = useCallback(async (text) => {
    const content = (text || '').trim();
    if (!content || streaming) return;

    // Ajouter le message utilisateur
    setMessages((m) => [...m, { from: 'user', isUser: true, text: content }]);
    setInput('');
    setStreaming(true);

    // Placeholder pour la réponse en streaming
    const botMsgIndex = messages.length + 1;
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
              const finalSources = chunk.content?.sources || lastBot.sources;
              updated[updated.length - 1] = {
                ...lastBot,
                isStreaming: false,
                tokensUsed: chunk.content?.tokens_used,
                sources: finalSources || [],
              };
            }
            return updated;
          });
        }
      }
    } catch (e) {
      console.error('Erreur streaming:', e);
      setMessages((prev) => {
        const updated = [...prev];
        const lastBot = updated[updated.length - 1];
        if (lastBot && !lastBot.isUser) {
          updated[updated.length - 1] = {
            ...lastBot,
            text: "Désolé, une erreur s'est produite. Veuillez réessayer.",
            isStreaming: false,
          };
        }
        return updated;
      });
    } finally {
      setStreaming(false);
      streamRef.current = null;
      loadConversations(); // Rafraîchir la sidebar
    }
  }, [streaming, activeConversationId, messages.length]);

  return (
    <div className="animate-fade-in-up flex h-[calc(100vh-5rem)] gap-0 overflow-hidden rounded-2xl shadow-sm border border-brand-secondary/10 bg-white">

      {/* ── LEFT PANEL : Conversations ── */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-brand-secondary/10 bg-white md:flex">
        <div className="flex items-center justify-between px-4 py-4 border-b border-brand-secondary/10">
          <h2 className="text-sm font-semibold text-brand-dark">Conversations</h2>
          <button
            onClick={startNewConversation}
            className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/60 hover:text-brand-secondary transition-colors"
          >
            <Plus size={15} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-2">
          {loadingConversations ? (
            <div className="flex justify-center py-8">
              <Loader2 size={18} className="animate-spin text-brand-secondary/40" />
            </div>
          ) : conversations.length === 0 ? (
            <p className="px-4 py-6 text-xs text-brand-secondary/50 text-center">
              Aucune conversation. Commencez par envoyer un message !
            </p>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => loadConversationMessages(conv.id)}
                className={cn(
                  'w-full text-left px-4 py-3 transition-colors hover:bg-brand-light/60 group relative',
                  activeConversationId === conv.id && 'bg-brand-light',
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className={cn(
                    'text-sm font-medium truncate pr-6',
                    activeConversationId === conv.id ? 'text-brand-secondary' : 'text-brand-dark',
                  )}>
                    {conv.title || 'Nouvelle conversation'}
                  </p>
                </div>
                <p className="mt-0.5 text-xs text-brand-secondary/60 truncate">
                  {conv.message_count || 0} messages
                </p>
                <button
                  onClick={(e) => deleteConversation(conv.id, e)}
                  className="absolute right-3 top-3 opacity-0 group-hover:opacity-100 transition-opacity text-brand-secondary/40 hover:text-brand-danger"
                >
                  <Trash2 size={13} />
                </button>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* ── RIGHT PANEL : Main Chat ── */}
      <div className="flex flex-1 flex-col min-w-0">

        {/* Chat header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-brand-secondary/10 bg-white">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-brand-secondary text-white shadow-sm">
              <Bot size={18} />
            </div>
            <div>
              <h1 className="text-sm font-bold text-brand-dark">Pulse AI Assistant</h1>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[10px] font-medium text-green-600 uppercase tracking-wide">
                  {streaming ? 'Réflexion en cours...' : 'Opérationnel'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5 bg-white">
          {messages.map((msg, i) => (
            <div key={i}>
              {msg.isUser ? (
                <div className="flex justify-end">
                  <div className="max-w-[72%] rounded-2xl rounded-br-sm bg-brand-secondary px-4 py-3 text-sm leading-relaxed text-white shadow-sm">
                    <Markdownish text={msg.text} />
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  {/* Tool calls */}
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="space-y-2">
                      {msg.toolCalls.map((tc, ti) => (
                        <div key={ti} className="rounded-xl border border-brand-secondary/15 bg-brand-light px-4 py-3">
                          <div className="flex items-center gap-2 text-xs font-medium text-brand-secondary/70 mb-1.5">
                            <Wrench size={12} />
                            <span>Outil : {tc.tool?.replace(/_/g, ' ')}</span>
                          </div>
                          {tc.result?.success && (
                            <div className="flex items-center gap-1.5 rounded-lg bg-white border border-brand-secondary/15 px-2.5 py-1.5 w-fit">
                              <CheckCircle size={12} className="text-green-600" />
                              <span className="text-xs font-medium text-brand-dark">
                                {tc.result.message || 'Terminé'}
                              </span>
                            </div>
                          )}
                          {tc.result?.file_name && (
                            <div className="flex items-center gap-1.5 rounded-lg bg-white border border-brand-secondary/15 px-2.5 py-1.5 w-fit mt-1.5">
                              <FileText size={12} className="text-brand-secondary" />
                              <span className="text-xs font-medium text-brand-dark">{tc.result.file_name}</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Bot response */}
                  <div className="flex gap-3">
                    <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-brand-secondary text-white mt-0.5">
                      <Bot size={15} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="rounded-2xl rounded-tl-sm bg-brand-light px-4 py-3 text-sm leading-relaxed text-brand-dark">
                        {msg.text ? (
                          msg.text.split('\n').map((line, li) =>
                            line.startsWith('•') || line.startsWith('-') ? (
                              <div key={li} className="flex gap-2 mt-1.5">
                                <span className="text-brand-secondary mt-0.5">•</span>
                                <span><Markdownish text={line.replace(/^[•-]\s*/, '')} /></span>
                              </div>
                            ) : line ? (
                              <p key={li} className={li > 0 ? 'mt-2' : ''}><Markdownish text={line} /></p>
                            ) : null
                          )
                        ) : msg.isStreaming ? (
                          <TypingDots />
                        ) : null}
                        {msg.isStreaming && msg.text && (
                          <span className="inline-block w-1 h-4 bg-brand-secondary/60 animate-pulse ml-0.5 align-text-bottom" />
                        )}
                      </div>

                      {/* Sources */}
                      {msg.sources && msg.sources.length > 0 && !msg.isStreaming && (
                        <div className="mt-2 px-1">
                          <p className="text-[10px] uppercase font-semibold tracking-widest text-brand-secondary/40 mb-1.5">Sources</p>
                          <div className="flex flex-wrap gap-2">
                            {msg.sources.map((s, si) => (
                              <div key={si} className="flex items-center gap-1 rounded-md border border-brand-secondary/10 bg-white px-2 py-1">
                                <FileText size={10} className="text-brand-secondary/60" />
                                <span className="text-[10px] text-brand-secondary/70">{s}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          {streaming && messages.length > 0 && !messages[messages.length - 1]?.text && (
            <div className="flex gap-3">
              <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-brand-secondary text-white">
                <Bot size={15} />
              </div>
              <div className="rounded-2xl rounded-tl-sm bg-brand-light px-4 py-3">
                <TypingDots />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Composer area */}
        <div className="border-t border-brand-secondary/10 bg-white px-5 py-4">
          {/* Quick prompts */}
          {messages.length <= 1 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {QUICK_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p.replace(/^[^ ]+ /, ''))}
                  className="rounded-full border border-brand-secondary/20 bg-brand-light px-3 py-1 text-xs font-medium text-brand-secondary hover:border-brand-secondary/40 hover:bg-brand-secondary/10 transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>
          )}

          {/* Input row */}
          <form
            onSubmit={(e) => { e.preventDefault(); send(input); }}
            className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-brand-light px-3 py-2.5"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Posez une question à Pulse AI..."
              className="flex-1 bg-transparent text-sm text-brand-dark placeholder:text-brand-secondary/40 outline-none"
            />
            <div className="flex items-center gap-1 shrink-0">
              <button
                type="submit"
                disabled={!input.trim() || streaming}
                className="grid h-8 w-8 place-items-center rounded-lg bg-brand-secondary text-white shadow-sm transition-all hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-40"
              >
                {streaming ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
