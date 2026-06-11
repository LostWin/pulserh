import { useMemo, useRef, useState } from 'react';
import {
  Search, Upload, Download, FileText, FileCheck2,
  ShieldCheck, ReceiptText, ChevronDown, ChevronUp,
  BotMessageSquare, Sparkles, HardDrive, Bell, X,
  FileBadge, ArrowUpRight,
} from 'lucide-react';

// ─── Mock documents ──────────────────────────────────────────────────────────
const DOCUMENTS = [
  { id: 1,  name: 'Employment_Contract_2024.pdf',  type: 'Legal',      date: 'Oct 12, 2023', size: '1.2 MB',  status: 'signed'  },
  { id: 2,  name: 'Payslip_March_2024.pdf',         type: 'Financial',  date: 'Mar 28, 2024', size: '184 KB',  status: 'ok'      },
  { id: 3,  name: 'Remote_Work_Policy_V2.pdf',      type: 'Policy',     date: 'Jan 15, 2024', size: '320 KB',  status: 'ok'      },
  { id: 4,  name: 'Annual_Bonus_Statement.pdf',     type: 'Financial',  date: 'Feb 20, 2024', size: '96 KB',   status: 'ok'      },
  { id: 5,  name: 'GDPR_Consent_Form.pdf',          type: 'Compliance', date: 'Nov 05, 2023', size: '140 KB',  status: 'signed'  },
  { id: 6,  name: 'Payslip_February_2024.pdf',      type: 'Financial',  date: 'Feb 29, 2024', size: '182 KB',  status: 'ok'      },
  { id: 7,  name: 'Onboarding_Checklist.pdf',       type: 'HR',         date: 'Jan 12, 2023', size: '210 KB',  status: 'ok'      },
  { id: 8,  name: 'NDA_Agreement_2023.pdf',         type: 'Legal',      date: 'Jan 13, 2023', size: '88 KB',   status: 'signed'  },
  { id: 9,  name: 'Training_Certificate_RGPD.pdf',  type: 'Compliance', date: 'Feb 20, 2026', size: '140 KB',  status: 'ok'      },
  { id: 10, name: 'Expense_Report_Q1_2026.pdf',     type: 'Financial',  date: 'Apr 05, 2026', size: '210 KB',  status: 'pending' },
];

const TYPE_STYLES = {
  Legal:      { bg: '#dbeafe', color: '#1d4ed8' },
  Financial:  { bg: '#ede9fe', color: '#7c3aed' },
  Policy:     { bg: '#d1fae5', color: '#065f46' },
  Compliance: { bg: '#fef3c7', color: '#92400e' },
  HR:         { bg: '#fce7f3', color: '#be185d' },
};

const KPI_CARDS = [
  { label: 'TOTAL DOCUMENTS',  value: 142, sub: '+4 this month',   icon: FileText,   subColor: 'text-emerald-600 bg-emerald-50' },
  { label: 'LATEST PAYSLIPS',  value: 24,  sub: 'Updated 2d ago',  icon: ReceiptText,subColor: 'text-amber-600 bg-amber-50'    },
  { label: 'OPEN REQUESTS',    value: '07',sub: '2 Pending',       icon: FileBadge,  subColor: 'text-red-500 bg-red-50'         },
  { label: 'COMPLIANCE SCORE', value: '98%',sub: 'Optimal',        icon: ShieldCheck,subColor: 'text-emerald-600 bg-emerald-50' },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────
function downloadDocument(doc) {
  const content = [
    `============================`,
    `  PULSE RH — Document`,
    `============================`,
    ``,
    `Nom         : ${doc.name}`,
    `Type        : ${doc.type}`,
    `Date        : ${doc.date}`,
    `Taille      : ${doc.size}`,
    `Statut      : ${doc.status}`,
    ``,
    `Ce fichier est une simulation de téléchargement.`,
    `Dans un environnement de production, le vrai PDF serait fourni par l'API.`,
  ].join('\n');

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), {
    href: url,
    download: doc.name.replace(/\.pdf$/i, '.txt'),
  });
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function TypeBadge({ type }) {
  const s = TYPE_STYLES[type] || { bg: '#f1f5f9', color: '#475569' };
  return (
    <span
      className="rounded-md px-2 py-0.5 text-[11px] font-semibold"
      style={{ backgroundColor: s.bg, color: s.color }}
    >
      {type}
    </span>
  );
}

// ─── Upload Modal ─────────────────────────────────────────────────────────────
function UploadModal({ onClose }) {
  const fileRef  = useRef(null);
  const [file, setFile]   = useState(null);
  const [type, setType]   = useState('Financial');
  const [done, setDone]   = useState(false);

  const handleFile = (e) => setFile(e.target.files?.[0] || null);

  const handleDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) setFile(f);
  };

  const submit = () => {
    if (!file) return;
    setDone(true);
    setTimeout(onClose, 1600);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-bold text-brand-dark">Upload Document</h3>
          <button onClick={onClose} className="grid h-8 w-8 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/60 hover:text-brand-dark transition-colors">
            <X size={16} />
          </button>
        </div>

        {done ? (
          <div className="flex flex-col items-center gap-3 py-8">
            <div className="grid h-14 w-14 place-items-center rounded-full bg-emerald-100">
              <FileCheck2 size={28} className="text-emerald-600" />
            </div>
            <p className="font-semibold text-brand-dark">Document uploaded!</p>
          </div>
        ) : (
          <>
            {/* Drop zone */}
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileRef.current?.click()}
              className="mb-4 flex cursor-pointer flex-col items-center gap-3 rounded-xl border-2 border-dashed border-brand-secondary/25 bg-brand-light/60 py-8 hover:border-brand-secondary/50 hover:bg-brand-light transition-colors"
            >
              <Upload size={28} className="text-brand-secondary/60" />
              {file ? (
                <p className="text-sm font-medium text-brand-secondary">{file.name}</p>
              ) : (
                <>
                  <p className="text-sm font-medium text-brand-dark">Drop file here or <span className="text-brand-secondary underline">browse</span></p>
                  <p className="text-xs text-brand-secondary/50">PDF, DOCX, PNG — max 20 MB</p>
                </>
              )}
              <input ref={fileRef} type="file" className="hidden" accept=".pdf,.doc,.docx,.png,.jpg" onChange={handleFile} />
            </div>

            {/* Type select */}
            <div className="mb-5">
              <label className="block mb-1.5 text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">Document type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm text-brand-dark outline-none focus:border-brand-secondary"
              >
                {Object.keys(TYPE_STYLES).map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>

            <div className="flex gap-3">
              <button onClick={onClose} className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">
                Cancel
              </button>
              <button
                onClick={submit}
                disabled={!file}
                className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-bold text-white hover:bg-brand-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Upload
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────
export default function Documents() {
  const [query,   setQuery]   = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortAsc, setSortAsc] = useState(false);
  const [uploading, setUploading]   = useState(false);
  const [aiInput,  setAiInput]  = useState('');
  const [aiResult, setAiResult] = useState('');

  const types = useMemo(() => ['all', ...Object.keys(TYPE_STYLES)], []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return DOCUMENTS
      .filter((d) =>
        (typeFilter === 'all' || d.type === typeFilter) &&
        (!q || d.name.toLowerCase().includes(q))
      )
      .sort((a, b) => sortAsc
        ? a.name.localeCompare(b.name)
        : new Date(b.date) - new Date(a.date)
      );
  }, [query, typeFilter, sortAsc]);

  const handleAI = () => {
    if (!aiInput.trim()) return;
    setAiResult(`📄 Summary for "${aiInput}":\n\nThis document appears to cover key legal or financial terms relevant to your profile. Recommended action: review clauses 3.1 and 7.2 before signing. No immediate compliance issues detected.`);
  };

  return (
    <div className="animate-fade-in-up space-y-6">

      {/* ── Header ── */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Documents</h1>
          <p className="mt-0.5 text-sm">
            <span className="text-brand-secondary font-medium">Centralized hub</span>
            <span className="text-brand-secondary/60"> for your </span>
            <span className="text-brand-secondary font-medium">professional records</span>
            <span className="text-brand-secondary/60"> and </span>
            <span className="text-brand-secondary font-medium">compliance tracking.</span>
          </p>
        </div>
        <button
          onClick={() => setUploading(true)}
          className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-brand-dark transition-colors"
        >
          <Upload size={15} />
          Upload Document
        </button>
      </div>

      {/* ── KPI cards ── */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {KPI_CARDS.map(({ label, value, sub, icon: Icon, subColor }) => (
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

      {/* ── Body grid ── */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        {/* Documents table — 2/3 */}
        <div className="lg:col-span-2 space-y-4">

          {/* Search + filters */}
          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <div className="relative flex-1">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/50" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search documents, requests…"
                  className="w-full rounded-xl border border-brand-secondary/20 bg-brand-light py-2 pl-9 pr-3 text-sm text-brand-dark outline-none focus:border-brand-secondary focus:bg-white transition"
                />
              </div>
              <div className="flex flex-wrap gap-2">
                {types.map((t) => (
                  <button
                    key={t}
                    onClick={() => setTypeFilter(t)}
                    className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                      typeFilter === t
                        ? 'border-brand-secondary bg-brand-secondary/10 text-brand-secondary'
                        : 'border-brand-secondary/20 text-brand-secondary/70 hover:bg-brand-light'
                    }`}
                  >
                    {t === 'all' ? 'All' : t}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Table */}
          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-brand-secondary/8">
              <h2 className="text-sm font-bold text-brand-dark">Recent Documents</h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSortAsc((v) => !v)}
                  className="flex items-center gap-1 rounded-lg border border-brand-secondary/15 px-2.5 py-1.5 text-xs font-medium text-brand-secondary hover:bg-brand-light transition-colors"
                >
                  {sortAsc ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                  {sortAsc ? 'A→Z' : 'Recent'}
                </button>
                <span className="text-xs text-brand-secondary/50">{filtered.length} docs</span>
              </div>
            </div>

            {/* Header row */}
            <div className="grid grid-cols-[1fr_auto_auto_auto] gap-4 px-5 py-2.5 border-b border-brand-secondary/8 text-[10px] font-bold uppercase tracking-widest text-brand-secondary/40">
              <span>Document Name</span>
              <span className="hidden sm:block">Type</span>
              <span>Date</span>
              <span>Action</span>
            </div>

            <ul className="divide-y divide-slate-50">
              {filtered.map((doc) => (
                <li
                  key={doc.id}
                  className="grid grid-cols-[1fr_auto_auto_auto] gap-4 items-center px-5 py-3.5 hover:bg-brand-light/40 transition-colors"
                >
                  {/* Name */}
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-brand-secondary/8">
                      <FileText size={16} className="text-brand-secondary" />
                    </div>
                    <span className="truncate text-sm font-medium text-brand-dark">{doc.name}</span>
                  </div>
                  {/* Type */}
                  <div className="hidden sm:block">
                    <TypeBadge type={doc.type} />
                  </div>
                  {/* Date */}
                  <span className="text-xs text-brand-secondary/60 whitespace-nowrap">{doc.date}</span>
                  {/* Download */}
                  <button
                    onClick={() => downloadDocument(doc)}
                    title={`Download ${doc.name}`}
                    className="grid h-8 w-8 place-items-center rounded-xl border border-brand-secondary/20 text-brand-secondary hover:bg-brand-secondary hover:text-white hover:border-brand-secondary transition-colors"
                  >
                    <Download size={14} />
                  </button>
                </li>
              ))}
              {filtered.length === 0 && (
                <li className="py-12 text-center text-sm text-brand-secondary/60">
                  No documents found.
                </li>
              )}
            </ul>

            <div className="px-5 py-3 border-t border-brand-secondary/8 text-center">
              <button className="flex items-center gap-1 mx-auto text-xs font-semibold text-brand-secondary hover:text-brand-dark transition-colors">
                View All Documents <ArrowUpRight size={12} />
              </button>
            </div>
          </div>
        </div>

        {/* Right panel — 1/3 */}
        <div className="space-y-5">

          {/* Pulse AI Guide */}
          <div className="rounded-2xl bg-gradient-to-br from-brand-secondary to-brand-dark border border-brand-secondary shadow-sm p-5 text-white">
            <div className="flex items-center gap-2 mb-3">
              <div className="grid h-8 w-8 place-items-center rounded-xl bg-white/15">
                <BotMessageSquare size={16} />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-widest">Pulse AI Guide</p>
                <p className="text-[10px] text-white/60">Intelligent Analysis</p>
              </div>
              <Sparkles size={14} className="ml-auto text-white/50" />
            </div>

            <p className="text-sm text-white/80 leading-relaxed mb-4">
              Need a quick overview? Drop a document here or select one from the list to get an AI-powered executive summary, key clauses, and action items.
            </p>

            {/* AI input */}
            <div className="rounded-xl bg-white/10 p-3 mb-3">
              <p className="text-[10px] font-bold uppercase tracking-widest text-white/50 mb-2">
                Summarize Document
              </p>
              <div className="flex items-center gap-2">
                <input
                  value={aiInput}
                  onChange={(e) => setAiInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAI()}
                  placeholder="Type document name…"
                  className="flex-1 rounded-lg bg-white/15 border border-white/20 px-2.5 py-1.5 text-xs text-white placeholder-white/40 outline-none focus:border-white/50"
                />
                <button
                  onClick={handleAI}
                  className="rounded-lg bg-white/20 hover:bg-white/30 px-3 py-1.5 text-xs font-bold transition-colors"
                >
                  Go
                </button>
              </div>
              {aiResult && (
                <p className="mt-2 text-[11px] text-white/80 leading-relaxed whitespace-pre-line">{aiResult}</p>
              )}
              {!aiResult && (
                <p className="mt-2 text-[10px] text-white/40">
                  Drag and drop or click to select a file from your device
                </p>
              )}
            </div>

            {/* Popular tasks */}
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-white/50 mb-2">Popular Tasks</p>
              {['Analyze policy changes', 'Extract renewal dates'].map((t) => (
                <button
                  key={t}
                  onClick={() => setAiInput(t)}
                  className="flex items-center gap-2 w-full text-left py-1 text-xs text-white/70 hover:text-white transition-colors"
                >
                  <FileText size={11} />
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Storage allocation */}
          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <HardDrive size={14} className="text-brand-secondary" />
              </div>
              <h3 className="text-sm font-bold text-brand-dark">Storage Allocation</h3>
            </div>

            {/* Bar */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs text-brand-secondary/60">Personal Records</span>
                <span className="text-xs font-bold text-brand-secondary">1.2 GB / 5 GB</span>
              </div>
              <div className="h-2.5 w-full rounded-full bg-brand-light overflow-hidden">
                <div className="h-full w-[24%] rounded-full bg-brand-secondary transition-all duration-700" />
              </div>
            </div>

            <p className="text-[11px] text-brand-secondary/60 leading-relaxed">
              You are using <strong className="text-brand-secondary">24%</strong> of your allocated secure storage.
            </p>

            <button className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-brand-secondary hover:text-brand-dark transition-colors">
              <Bell size={12} />
              Set storage alert
            </button>
          </div>
        </div>
      </div>

      {/* Upload modal */}
      {uploading && <UploadModal onClose={() => setUploading(false)} />}
    </div>
  );
}
