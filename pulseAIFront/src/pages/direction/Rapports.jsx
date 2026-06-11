import { useState } from 'react';
import { FileSpreadsheet, Download, Plus, Calendar, Filter, X } from 'lucide-react';
import { cn } from '../../lib/utils';

const REPORTS = [
  { id: 1, name: 'Rapport d\'engagement — Mai 2026', period: 'Mai 2026', dept: 'Tous', generated: '1 juin 2026', size: '1.2 Mo', format: 'PDF' },
  { id: 2, name: 'Synthèse turnover Q2 2026', period: 'Q2 2026', dept: 'Tous', generated: '31 mai 2026', size: '890 Ko', format: 'PDF' },
  { id: 3, name: 'Analyse absentéisme — Engineering', period: 'Avril 2026', dept: 'Engineering', generated: '5 mai 2026', size: '456 Ko', format: 'PDF' },
  { id: 4, name: 'Bilan formation S1 2026', period: 'S1 2026', dept: 'Tous', generated: '30 avr. 2026', size: '2.1 Mo', format: 'PDF' },
  { id: 5, name: 'Répartition masse salariale', period: 'Juin 2026', dept: 'Finance', generated: '11 juin 2026', size: '340 Ko', format: 'XLSX' },
  { id: 6, name: 'Prévisions effectifs Q3 2026', period: 'Q3 2026', dept: 'Direction', generated: '8 juin 2026', size: '780 Ko', format: 'PDF' },
];

const FORMAT_COLORS = {
  PDF: { bg: '#fee2e2', color: '#b91c1c' },
  XLSX: { bg: '#dcfce7', color: '#15803d' },
  CSV: { bg: '#dbeafe', color: '#1d4ed8' },
};

export default function Rapports() {
  const [showModal, setShowModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [filter, setFilter] = useState('Tous');
  const [form, setForm] = useState({ name: '', period: '', dept: 'Tous', format: 'PDF' });
  const [reports, setReports] = useState(REPORTS);

  const depts = ['Tous', 'Engineering', 'Ventes', 'Marketing', 'Finance', 'Direction'];
  const filtered = reports.filter((r) => filter === 'Tous' || r.dept === filter || r.dept === 'Tous');

  const generate = () => {
    if (!form.name || !form.period) return;
    setGenerating(true);
    setTimeout(() => {
      setReports((p) => [{
        id: Date.now(), name: form.name, period: form.period, dept: form.dept,
        generated: new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }),
        size: '—', format: form.format,
      }, ...p]);
      setGenerating(false); setShowModal(false);
      setForm({ name: '', period: '', dept: 'Tous', format: 'PDF' });
    }, 2000);
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Rapports</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Accédez aux rapports stratégiques et générez des analyses personnalisées.</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors">
          <Plus size={15} />Générer un rapport
        </button>
      </div>

      {/* Filter by dept */}
      <div className="flex gap-1.5 flex-wrap">
        {depts.map((d) => (
          <button key={d} onClick={() => setFilter(d)}
            className={cn('rounded-xl px-3 py-2 text-xs font-medium transition-colors',
              filter === d ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
            {d}
          </button>
        ))}
      </div>

      {/* Reports grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((r) => {
          const fc = FORMAT_COLORS[r.format] || { bg: '#f3f4f6', color: '#374151' };
          return (
            <div key={r.id} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3 mb-4">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-brand-secondary/10">
                  <FileSpreadsheet size={18} className="text-brand-secondary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-brand-dark leading-snug">{r.name}</p>
                  <div className="flex items-center gap-1.5 mt-1">
                    <span className="rounded-full px-2 py-0.5 text-[10px] font-bold" style={{ backgroundColor: fc.bg, color: fc.color }}>{r.format}</span>
                    <span className="text-[11px] text-brand-secondary/50">{r.size}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs text-brand-secondary/60 mb-4">
                <span className="flex items-center gap-1"><Calendar size={11} />{r.period}</span>
                <span>Généré le {r.generated}</span>
              </div>
              <div className="flex gap-2">
                <button className="flex-1 flex items-center justify-center gap-1.5 rounded-xl bg-brand-secondary/10 py-2 text-xs font-medium text-brand-secondary hover:bg-brand-secondary hover:text-white transition-colors">
                  <Download size={13} />Télécharger
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-brand-dark">Générer un rapport</h2>
              <button onClick={() => setShowModal(false)} className="grid h-8 w-8 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/60"><X size={16} /></button>
            </div>
            <div className="space-y-4">
              {[
                { label: 'Titre du rapport', key: 'name', type: 'input', placeholder: 'ex: Bilan engagement T3 2026' },
                { label: 'Période', key: 'period', type: 'input', placeholder: 'ex: Q3 2026' },
              ].map((f) => (
                <div key={f.key}>
                  <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">{f.label}</label>
                  <input value={form[f.key]} onChange={(e) => setForm((p) => ({ ...p, [f.key]: e.target.value }))}
                    placeholder={f.placeholder}
                    className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary" />
                </div>
              ))}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Département</label>
                <select value={form.dept} onChange={(e) => setForm((p) => ({ ...p, dept: e.target.value }))}
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none bg-white">
                  {depts.map((d) => <option key={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Format</label>
                <div className="flex gap-2">
                  {['PDF', 'XLSX', 'CSV'].map((fmt) => (
                    <button key={fmt} onClick={() => setForm((p) => ({ ...p, format: fmt }))}
                      className={cn('flex-1 rounded-xl py-2 text-sm font-medium border transition-colors',
                        form.format === fmt ? 'bg-brand-secondary text-white border-brand-secondary' : 'border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
                      {fmt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={generate} disabled={generating}
                className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-medium text-white hover:bg-brand-dark transition-colors disabled:opacity-60">
                {generating ? 'Génération…' : 'Générer'}
              </button>
              <button onClick={() => setShowModal(false)} className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">Annuler</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
