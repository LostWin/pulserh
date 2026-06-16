import { useEffect, useState } from 'react';
import { Download, FileSpreadsheet, Plus, X } from 'lucide-react';

import { api } from '../../lib/api';

export default function Rapports() {
  const [reports, setReports] = useState([]);
  const [departments, setDepartments] = useState(['Tous']);
  const [filter, setFilter] = useState('Tous');
  const [showModal, setShowModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [form, setForm] = useState({ name: '', period: '', dept: 'Tous', format: 'PDF' });
  const [error, setError] = useState('');

  const load = async () => {
    const data = await api.get('/reports');
    setReports(data.items || []);
    setDepartments(data.available_departments || ['Tous']);
  };

  useEffect(() => {
    load().catch((err) => setError(err.message || 'Impossible de charger les rapports.'));
  }, []);

  const filtered = reports.filter((report) => filter === 'Tous' || report.dept === filter || report.dept === 'Tous');

  const generate = async () => {
    if (!form.name || !form.period) return;
    setGenerating(true);
    try {
      await api.post('/reports/generate', form);
      await load();
      setShowModal(false);
      setForm({ name: '', period: '', dept: 'Tous', format: 'PDF' });
    } catch (err) {
      setError(err.message || 'Impossible de générer le rapport.');
    } finally {
      setGenerating(false);
    }
  };

  const download = async (report) => {
    const blob = await api.get(`/reports/${report.id}/download`, { responseType: 'blob' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${report.name}.${report.format.toLowerCase()}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Rapports</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Accédez aux rapports stratégiques et générez des analyses personnalisées.</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors">
          <Plus size={15} /> Générer un rapport
        </button>
      </div>
      {error ? <div className="rounded-xl bg-white p-4 text-sm text-brand-warning">{error}</div> : null}

      <div className="flex gap-1.5 flex-wrap">
        {departments.map((department) => (
          <button key={department} onClick={() => setFilter(department)} className={`rounded-xl px-3 py-2 text-xs font-medium transition-colors ${filter === department ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40'}`}>
            {department}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((report) => (
          <div key={report.id} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5 hover:shadow-md transition-shadow">
            <div className="mb-4 flex items-start gap-3">
              <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-brand-secondary/10">
                <FileSpreadsheet size={18} className="text-brand-secondary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-brand-dark leading-snug">{report.name}</p>
                <div className="mt-1 flex items-center gap-1.5">
                  <span className="rounded-full bg-brand-light px-2 py-0.5 text-[10px] font-bold text-brand-secondary">{report.format}</span>
                  <span className="text-[11px] text-brand-secondary/50">{report.size}</span>
                </div>
              </div>
            </div>
            <div className="mb-4 flex items-center justify-between text-xs text-brand-secondary/60">
              <span>{report.period}</span>
              <span>Généré le {report.generated}</span>
            </div>
            <button onClick={() => download(report)} className="flex w-full items-center justify-center gap-1.5 rounded-xl bg-brand-secondary/10 py-2 text-xs font-medium text-brand-secondary hover:bg-brand-secondary hover:text-white transition-colors">
              <Download size={13} /> Télécharger
            </button>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-lg font-bold text-brand-dark">Générer un rapport</h2>
              <button onClick={() => setShowModal(false)} className="grid h-8 w-8 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/60"><X size={16} /></button>
            </div>
            <div className="space-y-4">
              <input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} placeholder="Titre du rapport" className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm" />
              <input value={form.period} onChange={(event) => setForm((current) => ({ ...current, period: event.target.value }))} placeholder="Période" className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm" />
              <select value={form.dept} onChange={(event) => setForm((current) => ({ ...current, dept: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm bg-white">
                {departments.map((department) => <option key={department}>{department}</option>)}
              </select>
              <div className="flex gap-2">
                {['PDF', 'CSV', 'XLSX'].map((format) => (
                  <button key={format} onClick={() => setForm((current) => ({ ...current, format }))} className={`flex-1 rounded-xl py-2 text-sm font-medium border transition-colors ${form.format === format ? 'bg-brand-secondary text-white border-brand-secondary' : 'border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40'}`}>
                    {format}
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button onClick={generate} disabled={generating} className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-medium text-white disabled:opacity-60">{generating ? 'Génération…' : 'Générer'}</button>
              <button onClick={() => setShowModal(false)} className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light">Annuler</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
