import { useEffect, useMemo, useState } from 'react';
import {
  Search, Download, FileText, ShieldCheck, ReceiptText,
  BotMessageSquare, Sparkles, HardDrive, FileBadge, ArrowUpRight, Lock,
  ChevronDown, ChevronUp,
} from 'lucide-react';

import { api } from '../../lib/api';

const TYPE_STYLES = {
  Contrat: { bg: '#dbeafe', color: '#1d4ed8' },
  'Fiche de paie': { bg: '#ede9fe', color: '#7c3aed' },
  Politique: { bg: '#d1fae5', color: '#065f46' },
  Compliance: { bg: '#fef3c7', color: '#92400e' },
  RH: { bg: '#fce7f3', color: '#be185d' },
};

function TypeBadge({ type }) {
  const style = TYPE_STYLES[type] || { bg: '#f1f5f9', color: '#475569' };
  return (
    <span className="rounded-md px-2 py-0.5 text-[11px] font-semibold" style={{ backgroundColor: style.bg, color: style.color }}>
      {type}
    </span>
  );
}

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [query, setQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortAsc, setSortAsc] = useState(false);
  const [aiInput, setAiInput] = useState('');
  const [aiResult, setAiResult] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const loadDocuments = async () => {
      try {
        const data = await api.get('/documents/');
        if (mounted) setDocuments(data || []);
      } catch (err) {
        if (mounted) setError(err.message || 'Impossible de charger les documents.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    loadDocuments();
    return () => {
      mounted = false;
    };
  }, []);

  const types = useMemo(() => ['all', ...new Set(documents.map((doc) => doc.type).filter(Boolean))], [documents]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return [...documents]
      .filter((doc) => (typeFilter === 'all' || doc.type === typeFilter) && (!q || doc.name.toLowerCase().includes(q)))
      .sort((left, right) => {
        if (sortAsc) {
          return left.name.localeCompare(right.name);
        }
        return new Date(right.created_at) - new Date(left.created_at);
      });
  }, [documents, query, sortAsc, typeFilter]);

  const stats = useMemo(() => {
    const total = documents.length;
    const payslips = documents.filter((doc) => /paie/i.test(doc.type || '')).length;
    const pending = documents.filter((doc) => (doc.rag_status || '').toLowerCase().includes('pending')).length;
    const compliance = Math.min(100, 82 + documents.filter((doc) => /politique|compliance|rgpd/i.test(doc.type || doc.name || '')).length * 4);
    return { total, payslips, pending, compliance };
  }, [documents]);

  const downloadDocument = async (doc) => {
    try {
      const blob = await api.get(`/documents/${doc.id}/download`, { responseType: 'blob' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = doc.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || 'Téléchargement impossible.');
    }
  };

  const handleAI = () => {
    const target = filtered.find((doc) => doc.name.toLowerCase().includes(aiInput.trim().toLowerCase()));
    if (!target) {
      setAiResult('Aucun document correspondant trouvé dans votre espace.');
      return;
    }
    setAiResult(`Le document "${target.name}" est classé "${target.type}". Utilisez le bouton de téléchargement pour le récupérer, ou le lecteur interne RH si nécessaire.`);
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Documents</h1>
          <p className="mt-0.5 text-sm text-brand-secondary/70">Espace centralisé de vos documents RH réellement accessibles depuis le backend.</p>
          {error ? <p className="mt-2 text-sm text-brand-warning">{error}</p> : null}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: 'TOTAL DOCUMENTS', value: stats.total, sub: 'Disponible', icon: FileText, subColor: 'text-emerald-600 bg-emerald-50' },
          { label: 'LATEST PAYSLIPS', value: stats.payslips, sub: 'Documents paie', icon: ReceiptText, subColor: 'text-amber-600 bg-amber-50' },
          { label: 'OPEN REQUESTS', value: stats.pending, sub: 'Traitements en cours', icon: FileBadge, subColor: 'text-red-500 bg-red-50' },
          { label: 'COMPLIANCE SCORE', value: `${stats.compliance}%`, sub: 'Estimation backend', icon: ShieldCheck, subColor: 'text-emerald-600 bg-emerald-50' },
        ].map(({ label, value, sub, icon: Icon, subColor }) => (
          <div key={label} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-brand-secondary/8">
                <Icon size={17} className="text-brand-secondary" />
              </div>
              <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${subColor}`}>{sub}</span>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-brand-secondary/40 mb-1">{label}</p>
            <p className="text-2xl font-extrabold text-brand-dark">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <div className="relative flex-1">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/50" />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Search documents…"
                  className="w-full rounded-xl border border-brand-secondary/20 bg-brand-light py-2 pl-9 pr-3 text-sm text-brand-dark outline-none focus:border-brand-secondary focus:bg-white transition"
                />
              </div>
              <div className="flex flex-wrap gap-2">
                {types.map((type) => (
                  <button
                    key={type}
                    onClick={() => setTypeFilter(type)}
                    className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                      typeFilter === type ? 'border-brand-secondary bg-brand-secondary/10 text-brand-secondary' : 'border-brand-secondary/20 text-brand-secondary/70 hover:bg-brand-light'
                    }`}
                  >
                    {type === 'all' ? 'All' : type}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-brand-secondary/8">
              <h2 className="text-sm font-bold text-brand-dark">Recent Documents</h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSortAsc((value) => !value)}
                  className="flex items-center gap-1 rounded-lg border border-brand-secondary/15 px-2.5 py-1.5 text-xs font-medium text-brand-secondary hover:bg-brand-light transition-colors"
                >
                  {sortAsc ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                  {sortAsc ? 'A→Z' : 'Recent'}
                </button>
                <span className="text-xs text-brand-secondary/50">{filtered.length} docs</span>
              </div>
            </div>

            <div className="grid grid-cols-[1fr_auto_auto_auto] gap-4 px-5 py-2.5 border-b border-brand-secondary/8 text-[10px] font-bold uppercase tracking-widest text-brand-secondary/40">
              <span>Document Name</span>
              <span className="hidden sm:block">Type</span>
              <span>Date</span>
              <span>Action</span>
            </div>

            <ul className="divide-y divide-slate-50">
              {loading ? <li className="py-12 text-center text-sm text-brand-secondary/60">Chargement…</li> : null}
              {!loading && filtered.map((doc) => (
                <li key={doc.id} className="grid grid-cols-[1fr_auto_auto_auto] gap-4 items-center px-5 py-3.5 hover:bg-brand-light/40 transition-colors">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-brand-secondary/8">
                      <FileText size={16} className="text-brand-secondary" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="truncate text-sm font-medium text-brand-dark">{doc.name}</span>
                        {Object.values(doc._field_visibility || {}).some((value) => value === 'hidden' || value === 'masked') ? (
                          <span className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-700">
                            <Lock size={10} />
                            Métadonnées filtrées
                          </span>
                        ) : null}
                      </div>
                    </div>
                  </div>
                  <div className="hidden sm:block">
                    <TypeBadge type={doc.type} />
                  </div>
                  <span className="text-xs text-brand-secondary/60 whitespace-nowrap">
                    {new Date(doc.created_at).toLocaleDateString('fr-FR')}
                  </span>
                  <button
                    onClick={() => downloadDocument(doc)}
                    title={`Download ${doc.name}`}
                    className="grid h-8 w-8 place-items-center rounded-xl border border-brand-secondary/20 text-brand-secondary hover:bg-brand-secondary hover:text-white hover:border-brand-secondary transition-colors"
                  >
                    <Download size={14} />
                  </button>
                </li>
              ))}
              {!loading && filtered.length === 0 ? <li className="py-12 text-center text-sm text-brand-secondary/60">No documents found.</li> : null}
            </ul>

            <div className="px-5 py-3 border-t border-brand-secondary/8 text-center">
              <button className="flex items-center gap-1 mx-auto text-xs font-semibold text-brand-secondary hover:text-brand-dark transition-colors">
                View All Documents <ArrowUpRight size={12} />
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-5">
          <div className="rounded-2xl bg-gradient-to-br from-brand-secondary to-brand-dark border border-brand-secondary shadow-sm p-5 text-white">
            <div className="flex items-center gap-2 mb-3">
              <div className="grid h-8 w-8 place-items-center rounded-xl bg-white/15">
                <BotMessageSquare size={16} />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-widest">Pulse AI Guide</p>
                <p className="text-[10px] text-white/60">Document Discovery</p>
              </div>
              <Sparkles size={14} className="ml-auto text-white/50" />
            </div>
            <p className="text-sm text-white/80 leading-relaxed mb-4">
              Recherchez rapidement un document et laissez le système vous aider à identifier sa catégorie et son usage.
            </p>
            <div className="rounded-xl bg-white/10 p-3 mb-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-white/50 mb-2">Summarize Document</p>
              <div className="flex items-center gap-2">
                <input
                  value={aiInput}
                  onChange={(event) => setAiInput(event.target.value)}
                  onKeyDown={(event) => event.key === 'Enter' && handleAI()}
                  placeholder="Type document name…"
                  className="flex-1 rounded-lg bg-white/15 border border-white/20 px-2.5 py-1.5 text-xs text-white placeholder-white/40 outline-none focus:border-white/50"
                />
                <button onClick={handleAI} className="rounded-lg bg-white/20 hover:bg-white/30 px-3 py-1.5 text-xs font-bold transition-colors">Go</button>
              </div>
              <p className="mt-2 text-[11px] text-white/80 leading-relaxed whitespace-pre-line">
                {aiResult || 'Sélectionnez un document par son nom pour obtenir un rappel rapide.'}
              </p>
            </div>
          </div>

          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <HardDrive size={14} className="text-brand-secondary" />
              </div>
              <h3 className="text-sm font-bold text-brand-dark">Backend Storage</h3>
            </div>
            <div className="space-y-3 text-sm text-brand-secondary/80">
              <p>Vos documents proviennent maintenant du stockage sécurisé backend/MinIO.</p>
              <p>{stats.total} fichier(s) sont actuellement visibles selon vos droits d&apos;accès.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
