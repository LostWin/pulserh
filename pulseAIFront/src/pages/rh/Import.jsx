import { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, XCircle, Clock, AlertTriangle, Trash2, Eye } from 'lucide-react';
import { cn } from '../../lib/utils';

const HISTORY = [
  { id: 1, file: 'employes_juin_2026.csv', date: '11 juin 2026, 09:14', status: 'success', rows: 247, user: 'I. Garcia' },
  { id: 2, file: 'contrats_Q2.xlsx', date: '5 juin 2026, 14:32', status: 'success', rows: 89, user: 'I. Garcia' },
  { id: 3, file: 'paie_mai_2026.csv', date: '1 juin 2026, 08:57', status: 'error', rows: 0, user: 'M. Dupuis' },
  { id: 4, file: 'formations_S1.xlsx', date: '28 mai 2026, 11:20', status: 'success', rows: 34, user: 'I. Garcia' },
];

const STATUS_BADGE = {
  success: 'bg-brand-secondary/10 text-brand-secondary',
  error: 'bg-brand-warning/10 text-brand-warning',
  pending: 'bg-brand-dark/10 text-brand-dark',
};
const STATUS_LABEL = { success: 'Succès', error: 'Erreur', pending: 'En attente' };
const STATUS_ICON = { success: CheckCircle, error: XCircle, pending: Clock };

export default function ImportDonnees() {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [importing, setImporting] = useState(false);
  const [done, setDone] = useState(false);
  const inputRef = useRef();

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) { setFile(f); setDone(false); setProgress(0); }
  };

  const handleFile = (e) => {
    const f = e.target.files[0];
    if (f) { setFile(f); setDone(false); setProgress(0); }
  };

  const startImport = () => {
    if (!file || importing) return;
    setImporting(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) { clearInterval(interval); setImporting(false); setDone(true); return 100; }
        return p + Math.random() * 12;
      });
    }, 200);
  };

  const reset = () => { setFile(null); setProgress(0); setDone(false); };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-dark">Import de données</h1>
        <p className="mt-1 text-sm text-brand-secondary/70">Importez des fichiers CSV ou Excel pour mettre à jour la base employés.</p>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !file && inputRef.current?.click()}
        className={cn(
          'flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed p-12 transition-colors cursor-pointer',
          dragging ? 'border-brand-secondary bg-brand-secondary/5' : 'border-brand-secondary/20 bg-white hover:border-brand-secondary/40 hover:bg-brand-light/50',
          file && 'cursor-default',
        )}
      >
        <input ref={inputRef} type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={handleFile} />
        {file ? (
          <>
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-secondary/10">
              <FileText size={28} className="text-brand-secondary" />
            </div>
            <div className="text-center">
              <p className="font-semibold text-brand-dark">{file.name}</p>
              <p className="text-sm text-brand-secondary/60">{(file.size / 1024).toFixed(1)} Ko</p>
            </div>
            {/* Progress */}
            {(importing || done) && (
              <div className="w-full max-w-sm">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-brand-secondary/70">{done ? 'Import terminé' : 'Import en cours…'}</span>
                  <span className="text-xs font-bold text-brand-secondary">{Math.round(progress)}%</span>
                </div>
                <div className="h-2 rounded-full bg-brand-light overflow-hidden">
                  <div className="h-full rounded-full bg-brand-secondary transition-all duration-200" style={{ width: `${progress}%` }} />
                </div>
              </div>
            )}
            {done && (
              <div className="flex items-center gap-2 rounded-xl bg-brand-secondary/10 px-4 py-2">
                <CheckCircle size={16} className="text-brand-secondary" />
                <span className="text-sm font-medium text-brand-secondary">Fichier importé avec succès !</span>
              </div>
            )}
            <div className="flex gap-3">
              {!importing && !done && (
                <button onClick={startImport} className="rounded-xl bg-brand-secondary px-5 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors">
                  Lancer l'import
                </button>
              )}
              <button onClick={reset} className="rounded-xl border border-brand-secondary/20 px-5 py-2 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">
                Changer de fichier
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-secondary/10">
              <Upload size={28} className="text-brand-secondary" />
            </div>
            <div className="text-center">
              <p className="font-semibold text-brand-dark">Glissez votre fichier ici</p>
              <p className="text-sm text-brand-secondary/60">ou cliquez pour parcourir · CSV, XLSX, XLS</p>
            </div>
          </>
        )}
      </div>

      {/* History */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-brand-secondary/10">
          <h2 className="font-semibold text-brand-dark">Historique des imports</h2>
          <span className="rounded-full bg-brand-light px-2.5 py-0.5 text-xs font-semibold text-brand-secondary">{HISTORY.length} imports</span>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>
              {['Fichier', 'Date', 'Lignes', 'Par', 'Statut', ''].map((h) => (
                <th key={h} className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {HISTORY.map((row) => {
              const Icon = STATUS_ICON[row.status];
              return (
                <tr key={row.id} className="hover:bg-brand-light/40 transition-colors">
                  <td className="px-5 py-3 font-medium text-brand-dark flex items-center gap-2">
                    <FileText size={14} className="text-brand-secondary/60" />{row.file}
                  </td>
                  <td className="px-5 py-3 text-brand-secondary/70">{row.date}</td>
                  <td className="px-5 py-3 text-brand-secondary/70">{row.rows > 0 ? row.rows : '—'}</td>
                  <td className="px-5 py-3 text-brand-secondary/70">{row.user}</td>
                  <td className="px-5 py-3">
                    <span className={cn('inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold', STATUS_BADGE[row.status])}>
                      <Icon size={11} />{STATUS_LABEL[row.status]}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-1">
                      <button className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary transition-colors"><Eye size={14} /></button>
                      <button className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-warning/10 text-brand-secondary/50 hover:text-brand-warning transition-colors"><Trash2 size={14} /></button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
