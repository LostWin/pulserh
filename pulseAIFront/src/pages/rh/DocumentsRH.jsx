import { useState } from 'react';
import { FileText, Download, Trash2, Upload, Search, Eye } from 'lucide-react';
import { cn } from '../../lib/utils';

const TYPES = ['Tous', 'Contrat', 'Fiche de paie', 'Attestation', 'Avenant'];
const INITIAL_DOCS = [
  { id: 1, name: 'Contrat CDI — Alex Dupont', type: 'Contrat', employee: 'Alex Dupont', date: '12 jan. 2023', size: '234 Ko' },
  { id: 2, name: 'Bulletin de paie — Mai 2026', type: 'Fiche de paie', employee: 'Alex Dupont', date: '31 mai 2026', size: '89 Ko' },
  { id: 3, name: 'Attestation employeur — Camille Laurent', type: 'Attestation', employee: 'Camille Laurent', date: '8 juin 2026', size: '45 Ko' },
  { id: 4, name: 'Avenant télétravail — Yanis Moreau', type: 'Avenant', employee: 'Yanis Moreau', date: '2 juin 2026', size: '112 Ko' },
  { id: 5, name: 'Bulletin de paie — Avril 2026', type: 'Fiche de paie', employee: 'Sofia Nguyen', date: '30 avr. 2026', size: '91 Ko' },
  { id: 6, name: 'Contrat CDD — Lucas Bernard', type: 'Contrat', employee: 'Lucas Bernard', date: '15 mars 2026', size: '198 Ko' },
];
const TYPE_COLORS = {
  'Contrat': { bg: '#dbeafe', color: '#1d4ed8' },
  'Fiche de paie': { bg: '#dcfce7', color: '#15803d' },
  'Attestation': { bg: '#ede9fe', color: '#7c3aed' },
  'Avenant': { bg: '#ffedd5', color: '#c2410c' },
};

export default function DocumentsRH() {
  const [search, setSearch] = useState('');
  const [activeType, setActiveType] = useState('Tous');
  const [uploading, setUploading] = useState(false);
  const [docs, setDocs] = useState(INITIAL_DOCS);

  const filtered = docs.filter((d) =>
    (activeType === 'Tous' || d.type === activeType) &&
    (d.name.toLowerCase().includes(search.toLowerCase()) || d.employee.toLowerCase().includes(search.toLowerCase()))
  );

  const handleDelete = (id) => setDocs((prev) => prev.filter((d) => d.id !== id));

  const simulateUpload = () => {
    setUploading(true);
    setTimeout(() => {
      setDocs((prev) => [{
        id: Date.now(), name: 'Nouveau document.pdf', type: 'Attestation', employee: 'Tous',
        date: new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }), size: '—',
      }, ...prev]);
      setUploading(false);
    }, 1500);
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Documents RH</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Gérez les documents administratifs de tous les collaborateurs.</p>
        </div>
        <button onClick={simulateUpload} disabled={uploading}
          className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors disabled:opacity-60">
          <Upload size={15} />{uploading ? 'Upload…' : 'Ajouter un document'}
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/50" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher par nom ou collaborateur…"
            className="w-full rounded-xl border border-brand-secondary/20 bg-white pl-9 pr-4 py-2.5 text-sm outline-none focus:border-brand-secondary" />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {TYPES.map((t) => (
            <button key={t} onClick={() => setActiveType(t)}
              className={cn('rounded-xl px-3 py-2 text-xs font-medium transition-colors',
                activeType === t ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>{['Document', 'Type', 'Collaborateur', 'Date', 'Taille', 'Actions'].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {filtered.map((doc) => {
              const tc = TYPE_COLORS[doc.type] || { bg: '#f3f4f6', color: '#374151' };
              return (
                <tr key={doc.id} className="hover:bg-brand-light/40 transition-colors">
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2.5">
                      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-brand-secondary/10">
                        <FileText size={14} className="text-brand-secondary" />
                      </div>
                      <span className="font-medium text-brand-dark">{doc.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <span className="rounded-full px-2.5 py-1 text-xs font-semibold" style={{ backgroundColor: tc.bg, color: tc.color }}>{doc.type}</span>
                  </td>
                  <td className="px-5 py-3 text-brand-secondary/70">{doc.employee}</td>
                  <td className="px-5 py-3 text-brand-secondary/70">{doc.date}</td>
                  <td className="px-5 py-3 text-brand-secondary/70">{doc.size}</td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-1">
                      <button className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary transition-colors"><Eye size={14} /></button>
                      <button className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary transition-colors"><Download size={14} /></button>
                      <button onClick={() => handleDelete(doc.id)} className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-warning/10 text-brand-secondary/50 hover:text-brand-warning transition-colors"><Trash2 size={14} /></button>
                    </div>
                  </td>
                </tr>
              );
            })}
            {filtered.length === 0 && (
              <tr><td colSpan={6} className="px-5 py-12 text-center text-sm text-brand-secondary/50">Aucun document trouvé.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
