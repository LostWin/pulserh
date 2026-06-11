import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Sparkles, Plus, Share2, X, FileText, CheckCircle, Paperclip, Mic, Zap } from 'lucide-react';
import { assistantSuggestions } from '../../data/mockData';
import { cn } from '../../lib/utils';

/** Tiny rule-based "AI" so the chat feels alive without a backend. */
function generateReply(text) {
  const q = text.toLowerCase();
  if (q.includes('congé') || q.includes('vacance') || q.includes('rtt')) {
    return "Il vous reste **14 jours** de congés sur 25 pour l'année. Vous pouvez déposer une demande depuis l'onglet « Congés » — votre manager est notifié automatiquement et le solde se met à jour en temps réel.";
  }
  if (q.includes('télétravail') || q.includes('remote') || q.includes('distanciel')) {
    return "Votre accord prévoit jusqu'à **2 jours de télétravail par semaine**. Faites votre demande au moins 48 h à l'avance via « Congés › Télétravail ». Au-delà de 2 jours, une validation manager est requise.";
  }
  if (q.includes('paie') || q.includes('salaire') || q.includes('fiche')) {
    return "Votre fiche de paie comprend : le **brut**, les **cotisations** sociales (≈ 22 %), le **net imposable** et le **net à payer**. Vos 12 derniers bulletins sont disponibles dans « Documents ». Une ligne vous semble incorrecte ?";
  }
  if (q.includes('formation')) {
    return "Ce trimestre, 3 formations vous sont ouvertes : **React avancé**, **Communication assertive** et **RGPD pour les équipes**. Votre budget formation restant est de **800 €**. Souhaitez-vous que je pré-réserve une place ?";
  }
  if (q.includes('entretien') || q.includes('évaluation')) {
    return "Votre prochain entretien annuel est prévu le **24 juin 2026** avec votre manager. Pensez à compléter votre auto-évaluation au préalable — elle est accessible depuis vos tâches.";
  }
  if (q.includes('bonjour') || q.includes('salut') || q.includes('hello')) {
    return "Bonjour ! 👋 Je suis **Pulse AI**, votre assistante RH. Je peux vous renseigner sur vos congés, votre paie, vos formations ou vos démarches administratives. Que puis-je faire pour vous ?";
  }
  return "Bonne question ! Je n'ai pas encore la réponse exacte, mais je peux vous orienter vers le bon interlocuteur RH. En attendant, essayez l'une des suggestions ci-dessous — je gère les congés, la paie, le télétravail et les formations.";
}

function Markdownish({ text }) {
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

const RECENT_CHATS = [
  {
    id: 1,
    title: 'Remote work policy',
    preview: 'Analyzing Handbook v4.2...',
    time: '2m ago',
    active: true,
  },
  {
    id: 2,
    title: 'Paycheck query',
    preview: 'Resolved: Bonus calculation logic.',
    time: '1h ago',
    active: false,
  },
  {
    id: 3,
    title: 'Annual Leave Balance',
    preview: 'Your remaining balance is 12 days.',
    time: 'Yesterday',
    active: false,
  },
  {
    id: 4,
    title: 'Stock Option Vesting',
    preview: 'Next cliff: Oct 2024.',
    time: '3d ago',
    active: false,
  },
];

const GREETING = {
  from: 'bot',
  text: "Can you explain the current remote work policy for senior engineers in the Paris office? I need to know the specific allowance for cross-border work.",
  isUser: false,
};

const INITIAL_REPLY = {
  from: 'bot',
  isRetrieving: true,
  docs: ['Global Remote Policy v4.2.pdf', 'FR-Local-Supplement.docx'],
  text: "According to the **Pulse RH Global Remote Handbook** (Section 4.2) and the specific **France Entity Addendum**:\n\n• Senior Engineers are eligible for \"Work from Anywhere\" (WFA) status for up to **90 days per calendar year**.\n• For the Paris office, cross-border work within the EU is fully permitted with **72-hour prior notification**.\n• Cross-border work outside the EU requires a specialized tax review for durations exceeding **14 consecutive days**.",
  badge: 'POLICY COMPLIANT',
  citations: ['Remote_Handbook_2024.pdf [p. 14]', 'Tax_Nexus_FR_v2.doc [p. 3]'],
};

const QUICK_PROMPTS = [
  '❓ Summarize my benefits',
  '📅 My leave history',
  '💰 Last payslip breakdown',
];

export default function Assistant() {
  const [messages, setMessages] = useState([GREETING, INITIAL_REPLY]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const [activeChat, setActiveChat] = useState(1);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  const send = (text) => {
    const content = text.trim();
    if (!content || typing) return;
    setMessages((m) => [...m, { from: 'user', isUser: true, text: content }]);
    setInput('');
    setTyping(true);
    const delay = 700 + Math.min(content.length * 15, 800);
    setTimeout(() => {
      setMessages((m) => [...m, { from: 'bot', isUser: false, text: generateReply(content) }]);
      setTyping(false);
    }, delay);
  };

  return (
    <div className="animate-fade-in-up flex h-[calc(100vh-5rem)] gap-0 overflow-hidden rounded-2xl shadow-sm border border-brand-secondary/10 bg-white">

      {/* ── LEFT PANEL : Recent Chats ── */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-brand-secondary/10 bg-white md:flex">
        {/* Sidebar header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-brand-secondary/10">
          <h2 className="text-sm font-semibold text-brand-dark">Recent Chats</h2>
          <button className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/60 hover:text-brand-secondary transition-colors">
            <Plus size={15} />
          </button>
        </div>

        {/* Chat list */}
        <div className="flex-1 overflow-y-auto py-2">
          {RECENT_CHATS.map((chat) => (
            <button
              key={chat.id}
              onClick={() => setActiveChat(chat.id)}
              className={cn(
                'w-full text-left px-4 py-3 transition-colors hover:bg-brand-light/60 group',
                activeChat === chat.id && 'bg-brand-light',
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <p className={cn(
                  'text-sm font-medium truncate',
                  activeChat === chat.id ? 'text-brand-secondary' : 'text-brand-dark',
                )}>
                  {chat.title}
                </p>
                <span className="text-[10px] text-brand-secondary/50 shrink-0 mt-0.5">{chat.time}</span>
              </div>
              <p className="mt-0.5 text-xs text-brand-secondary/60 truncate">{chat.preview}</p>
            </button>
          ))}
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
                <span className="text-[10px] font-medium text-green-600 uppercase tracking-wide">Operational</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 rounded-lg border border-brand-secondary/20 px-3 py-1.5 text-xs font-medium text-brand-secondary hover:bg-brand-light transition-colors">
              <Share2 size={13} />
              Share Session
            </button>
            <button className="flex items-center gap-1.5 rounded-lg bg-brand-danger px-3 py-1.5 text-xs font-medium text-white hover:opacity-90 transition-opacity">
              <X size={13} />
              End Session
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5 bg-white">
          {messages.map((msg, i) => (
            <div key={i}>
              {/* User message bubble */}
              {msg.isUser ? (
                <div className="flex justify-end">
                  <div className="max-w-[72%] rounded-2xl rounded-br-sm bg-brand-secondary px-4 py-3 text-sm leading-relaxed text-white shadow-sm">
                    <Markdownish text={msg.text} />
                  </div>
                </div>
              ) : msg.isRetrieving ? (
                /* AI reply with retrieval card */
                <div className="flex flex-col gap-3">
                  {/* Retrieval card */}
                  <div className="rounded-xl border border-brand-secondary/15 bg-brand-light px-4 py-3">
                    <div className="flex items-center gap-2 text-xs font-medium text-brand-secondary/70 mb-2.5">
                      <div className="h-3 w-3 rounded-full border-2 border-brand-secondary/40 border-t-brand-secondary animate-spin" />
                      Retrieving relevant company documentation...
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {msg.docs?.map((doc) => (
                        <div key={doc} className="flex items-center gap-1.5 rounded-lg bg-white border border-brand-secondary/15 px-2.5 py-1.5">
                          <CheckCircle size={12} className="text-brand-secondary" />
                          <span className="text-xs font-medium text-brand-dark">{doc}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* AI text response */}
                  <div className="flex gap-3">
                    <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-brand-secondary text-white mt-0.5">
                      <Bot size={15} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="rounded-2xl rounded-tl-sm bg-brand-light px-4 py-3 text-sm leading-relaxed text-brand-dark">
                        {msg.text.split('\n').map((line, li) =>
                          line.startsWith('•') ? (
                            <div key={li} className="flex gap-2 mt-1.5">
                              <span className="text-brand-secondary mt-0.5">•</span>
                              <span><Markdownish text={line.slice(2)} /></span>
                            </div>
                          ) : line ? (
                            <p key={li} className={li > 0 ? 'mt-2' : ''}><Markdownish text={line} /></p>
                          ) : null
                        )}

                        {/* Policy badge */}
                        {msg.badge && (
                          <div className="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-brand-secondary/25 bg-white px-3 py-1.5">
                            <CheckCircle size={13} className="text-brand-secondary" />
                            <span className="text-xs font-semibold text-brand-secondary tracking-wide">{msg.badge}</span>
                          </div>
                        )}
                      </div>

                      {/* Source citations */}
                      {msg.citations && (
                        <div className="mt-2 px-1">
                          <p className="text-[10px] uppercase font-semibold tracking-widest text-brand-secondary/40 mb-1.5">Source Citations</p>
                          <div className="flex flex-wrap gap-2">
                            {msg.citations.map((c) => (
                              <div key={c} className="flex items-center gap-1 rounded-md border border-brand-secondary/10 bg-white px-2 py-1">
                                <FileText size={10} className="text-brand-secondary/60" />
                                <span className="text-[10px] text-brand-secondary/70">{c}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                /* Regular AI message */
                <div className="flex gap-3">
                  <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-brand-secondary text-white mt-0.5">
                    <Bot size={15} />
                  </div>
                  <div className="max-w-[72%] rounded-2xl rounded-tl-sm bg-brand-light px-4 py-3 text-sm leading-relaxed text-brand-dark">
                    <Markdownish text={msg.text} />
                  </div>
                </div>
              )}
            </div>
          ))}

          {typing && (
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

          {/* Input row */}
          <form
            onSubmit={(e) => { e.preventDefault(); send(input); }}
            className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-brand-light px-3 py-2.5"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Pulse AI about policies, payroll, or benefits..."
              className="flex-1 bg-transparent text-sm text-brand-dark placeholder:text-brand-secondary/40 outline-none"
            />
            <div className="flex items-center gap-1 shrink-0">
              <button type="button" className="grid h-7 w-7 place-items-center rounded-lg text-brand-secondary/50 hover:text-brand-secondary hover:bg-brand-secondary/10 transition-colors">
                <Paperclip size={14} />
              </button>
              <button type="button" className="grid h-7 w-7 place-items-center rounded-lg text-brand-secondary/50 hover:text-brand-secondary hover:bg-brand-secondary/10 transition-colors">
                <Mic size={14} />
              </button>
              <button
                type="submit"
                disabled={!input.trim() || typing}
                className="grid h-8 w-8 place-items-center rounded-lg bg-brand-secondary text-white shadow-sm transition-all hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Zap size={14} />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
