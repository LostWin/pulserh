import { useState, useEffect, useRef } from 'react';
import { FileText, Download, Trash2, Upload, Search, Eye, X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';

const TYPES = ['Tous', 'Contrat', 'Fiche de paie', 'Attestation', 'Avenant'];
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
  const [docs, setDocs] = useState([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedType, setSelectedType] = useState('Contrat');
  const fileInputRef = useRef(null);

  const fetchDocs = async () => {
    try {
      const data = await api.get('/documents');
      setDocs(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const filtered = docs.filter((d) =>
    (activeType === 'Tous' || d.type === activeType) &&
    (d.name.toLowerCase().includes(search.toLowerCase()) || (d.uploaded_by && d.uploaded_by.toLowerCase().includes(search.toLowerCase())))
  );

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer ce document ?")) return;
    try {
      await api.delete(`/documents/${id}`);
      fetchDocs();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDownload = async (doc) => {
    try {
      const blob = await api.get(`/documents/${doc.id}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Erreur téléchargement", err);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', selectedType);

    try {
      await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setShowUploadModal(false);
      fetchDocs();
    } catch (err) {
      console.error(err);
      alert("Erreur lors de l'upload");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Documents RH</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Gérez les documents administratifs de tous les collaborateurs.</p>
        </div>
        <button onClick={() => setShowUploadModal(true)} disabled={uploading}
          className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors disabled:opacity-60">
          <Upload size={15} />Ajouter un document
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
                  <td className="px-5 py-3 text-brand-secondary/70">{doc.uploaded_by || 'Système'}</td>
                  <td className="px-5 py-3 text-brand-secondary/70">{new Date(doc.created_at).toLocaleDateString()}</td>
                  <td className="px-5 py-3 text-brand-secondary/70">{doc.size}</td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => handleDownload(doc)} className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary transition-colors"><Download size={14} /></button>
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

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-brand-dark/40 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl animate-fade-in-up">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-brand-dark">Ajouter un document</h3>
              <button onClick={() => setShowUploadModal(false)} className="text-brand-secondary hover:text-brand-dark">
                <X size={20} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-brand-dark mb-1">Type de document</label>
                <select 
                  value={selectedType} 
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full rounded-xl border border-brand-secondary/20 bg-white px-4 py-2.5 text-sm outline-none focus:border-brand-secondary"
                >
                  {TYPES.filter(t => t !== 'Tous').map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-brand-dark mb-1">Fichier (PDF, DOCX, etc.)</label>
                <input 
                  type="file" 
                  ref={fileInputRef}
                  onChange={handleUpload}
                  className="block w-full text-sm text-brand-secondary file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-brand-secondary/10 file:text-brand-secondary hover:file:bg-brand-secondary/20 cursor-pointer"
                />
              </div>

              {uploading && <p className="text-sm font-medium text-brand-secondary animate-pulse">Upload en cours...</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
