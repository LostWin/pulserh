import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { FileText, Download, Trash2, Upload, Search, Eye, X, Plus, ShieldCheck, History, LoaderCircle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';

const TYPES = ['Tous', 'Contrat', 'Fiche de paie', 'Attestation', 'Avenant'];
const TYPE_COLORS = {
  'Contrat': { bg: '#dbeafe', color: '#1d4ed8' },
  'Fiche de paie': { bg: '#dcfce7', color: '#15803d' },
  'Attestation': { bg: '#ede9fe', color: '#7c3aed' },
  'Avenant': { bg: '#ffedd5', color: '#c2410c' },
};
const ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.odt', '.ott', '.rtf', '.pages'];
const DOCUMENT_ACCEPT = ALLOWED_DOCUMENT_EXTENSIONS.join(',');
const ROLE_OPTIONS = [
  { key: 'collaborator', label: 'Collaborateur' },
  { key: 'manager', label: 'Manager' },
  { key: 'hr', label: 'RH' },
  { key: 'director', label: 'Direction' },
  { key: 'admin', label: 'Admin' },
];
const ACCESS_ACTION_LABELS = {
  view: 'Consultation',
  download: 'Téléchargement',
  permissions_update: 'Mise à jour des accès',
  rag_sync: 'Ingestion RAG',
  rag_sync_error: 'Erreur d’ingestion',
  rag_disable: 'Désactivation RAG',
};

export default function DocumentsRH() {
  const [search, setSearch] = useState('');
  const [activeType, setActiveType] = useState('Tous');
  const [uploading, setUploading] = useState(false);
  const [docs, setDocs] = useState([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedType, setSelectedType] = useState('Contrat');
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [viewerDoc, setViewerDoc] = useState(null);
  const [viewerUrl, setViewerUrl] = useState('');
  const [viewerLoading, setViewerLoading] = useState(false);
  const [viewerError, setViewerError] = useState('');
  const [drawerDoc, setDrawerDoc] = useState(null);
  const [accessHistory, setAccessHistory] = useState([]);
  const [settingsState, setSettingsState] = useState({ allowed_roles: ['hr', 'admin'], rag_enabled: false, rag_status: 'disabled', rag_error: null, rag_last_synced_at: null, can_preview: false });
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [settingsSaving, setSettingsSaving] = useState(false);
  const fileInputRef = useRef(null);
  const overlayRoot = typeof document !== 'undefined' ? document.body : null;

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        if (viewerDoc) closeViewer();
        if (drawerDoc) closeDrawer();
        if (showUploadModal) setShowUploadModal(false);
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [viewerDoc, drawerDoc, showUploadModal, viewerUrl]);

  const fetchDocs = async () => {
    try {
      const data = await api.get('/documents/');
      setDocs(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  useEffect(() => () => {
    if (viewerUrl) {
      window.URL.revokeObjectURL(viewerUrl.split('#')[0]);
    }
  }, [viewerUrl]);

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
      const url = window.URL.createObjectURL(blob);
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

  const handlePreview = async (doc) => {
    setViewerDoc(doc);
    setViewerLoading(true);
    setViewerError('');
    if (viewerUrl) {
      window.URL.revokeObjectURL(viewerUrl.split('#')[0]);
      setViewerUrl('');
    }

    try {
      const blob = await api.get(`/documents/${doc.id}/view`, { responseType: 'blob' });
      if (!blob || blob.size === 0) {
        throw new Error("Le fichier PDF est vide ou illisible.");
      }
      const objectUrl = window.URL.createObjectURL(blob);
      setViewerUrl(objectUrl);
    } catch (err) {
      console.error(err);
      setViewerError(err.message || "Impossible d'ouvrir le lecteur PDF.");
    } finally {
      setViewerLoading(false);
    }
  };

  const closeViewer = () => {
    if (viewerUrl) {
      window.URL.revokeObjectURL(viewerUrl.split('#')[0]);
    }
    setViewerDoc(null);
    setViewerUrl('');
    setViewerError('');
    setViewerLoading(false);
  };

  const openDrawer = async (doc) => {
    setDrawerDoc(doc);
    setDrawerLoading(true);
    try {
      const [meta, history] = await Promise.all([
        api.get(`/documents/${doc.id}/viewer`),
        api.get(`/documents/${doc.id}/access-history`),
      ]);
      setSettingsState(meta);
      setAccessHistory(history);
    } catch (err) {
      console.error(err);
      setAccessHistory([]);
      setSettingsState({ allowed_roles: ['hr', 'admin'], rag_enabled: false, rag_status: 'error', rag_error: err.message || "Impossible de charger le détail du document.", rag_last_synced_at: null, can_preview: false });
    } finally {
      setDrawerLoading(false);
    }
  };

  const closeDrawer = () => {
    setDrawerDoc(null);
    setAccessHistory([]);
    setDrawerLoading(false);
  };

  const toggleRole = (role) => {
    setSettingsState((current) => {
      const hasRole = current.allowed_roles.includes(role);
      const nextRoles = hasRole
        ? current.allowed_roles.filter((item) => item !== role)
        : [...current.allowed_roles, role];
      return { ...current, allowed_roles: nextRoles };
    });
  };

  const saveSettings = async () => {
    if (!drawerDoc) return;
    setSettingsSaving(true);
    try {
      const nextState = await api.put(`/documents/${drawerDoc.id}/settings`, {
        allowed_roles: settingsState.allowed_roles,
        rag_enabled: settingsState.rag_enabled,
      });
      setSettingsState(nextState);
      const history = await api.get(`/documents/${drawerDoc.id}/access-history`);
      setAccessHistory(history);
      setDocs((currentDocs) => currentDocs.map((doc) => doc.id === drawerDoc.id ? { ...doc, ...nextState } : doc));
    } catch (err) {
      console.error(err);
      setSettingsState((current) => ({ ...current, rag_error: err.message || "Impossible d'enregistrer les paramètres." }));
    } finally {
      setSettingsSaving(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const extension = `.${file.name.split('.').pop()?.toLowerCase() || ''}`;
    if (!ALLOWED_DOCUMENT_EXTENSIONS.includes(extension)) {
      setUploadError('Format non autorisé. Utilisez uniquement PDF, Word, ODT, OTT, RTF ou Pages.');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setUploading(true);
    setUploadError('');
    setUploadSuccess('');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', selectedType);

    try {
      await api.post('/documents/upload', formData);
      await fetchDocs();
      setUploadSuccess(`Le document "${file.name}" a été importé avec succès.`);
      setShowUploadModal(false);
    } catch (err) {
      console.error(err);
      setUploadError(err.message || "Erreur lors de l'upload");
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

      {uploadSuccess && (
        <div className="rounded-2xl border border-brand-secondary/15 bg-brand-secondary/10 px-4 py-3 text-sm font-medium text-brand-secondary">
          {uploadSuccess}
        </div>
      )}

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
                      <button
                        onClick={() => handlePreview(doc)}
                        disabled={!doc.name.toLowerCase().endsWith('.pdf')}
                        title={doc.name.toLowerCase().endsWith('.pdf') ? "Lire dans le lecteur interne" : "Prévisualisation disponible uniquement pour les PDF"}
                        className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary transition-colors disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        <Eye size={14} />
                      </button>
                      <button onClick={() => handleDownload(doc)} className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary transition-colors"><Download size={14} /></button>
                      <button onClick={() => openDrawer(doc)} className="grid h-7 w-7 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary transition-colors"><Plus size={14} /></button>
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
      {showUploadModal && overlayRoot && createPortal((
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-brand-dark/55 p-4"
          onClick={() => !uploading && setShowUploadModal(false)}
        >
          <div
            className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl animate-fade-in-up"
            onClick={(event) => event.stopPropagation()}
          >
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
                <label className="block text-sm font-medium text-brand-dark mb-1">Fichier autorisé</label>
                <input 
                  type="file" 
                  ref={fileInputRef}
                  onChange={handleUpload}
                  accept={DOCUMENT_ACCEPT}
                  className="block w-full text-sm text-brand-secondary file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-brand-secondary/10 file:text-brand-secondary hover:file:bg-brand-secondary/20 cursor-pointer"
                />
                <p className="mt-2 text-xs text-brand-secondary/60">Formats acceptés : PDF, DOC, DOCX, ODT, OTT, RTF et Pages.</p>
              </div>

              {uploadError && <p className="text-sm font-medium text-brand-warning">{uploadError}</p>}
              {uploading && <p className="text-sm font-medium text-brand-secondary animate-pulse">Upload en cours...</p>}
            </div>
          </div>
        </div>
      ), overlayRoot)}

      {viewerDoc && overlayRoot && createPortal((
        <div
          className="fixed inset-0 z-[70] flex items-center justify-center bg-brand-dark/70 p-4"
          onClick={closeViewer}
        >
          <div
            className="flex h-[90vh] w-full max-w-6xl flex-col overflow-hidden rounded-3xl bg-white shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-brand-secondary/10 px-6 py-4">
              <div>
                <h3 className="text-lg font-bold text-brand-dark">{viewerDoc.name}</h3>
                <p className="text-sm text-brand-secondary/70">Lecteur PDF interne — téléchargement désactivé ici.</p>
              </div>
              <button onClick={closeViewer} className="text-brand-secondary hover:text-brand-dark">
                <X size={20} />
              </button>
            </div>
            <div className="flex-1 bg-brand-light/50">
              {viewerLoading ? (
                <div className="flex h-full items-center justify-center gap-3 text-brand-secondary">
                  <LoaderCircle size={18} className="animate-spin" />
                  Chargement du document...
                </div>
              ) : viewerError ? (
                <div className="flex h-full items-center justify-center px-6 text-center text-brand-warning">{viewerError}</div>
              ) : (
                <object data={viewerUrl} type="application/pdf" className="h-full w-full">
                  <div className="flex h-full items-center justify-center px-6 text-center text-brand-warning">
                    Impossible d'afficher le PDF dans le lecteur interne.
                  </div>
                </object>
              )}
            </div>
          </div>
        </div>
      ), overlayRoot)}

      {drawerDoc && overlayRoot && createPortal((
        <div
          className="fixed inset-0 z-[60] flex justify-end bg-brand-dark/45"
          onClick={closeDrawer}
        >
          <div
            className="h-full w-full max-w-xl overflow-y-auto border-l border-brand-secondary/10 bg-white shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between border-b border-brand-secondary/10 px-6 py-5">
              <div>
                <h3 className="text-lg font-bold text-brand-dark">{drawerDoc.name}</h3>
                <p className="mt-1 text-sm text-brand-secondary/70">Historique des accès, permissions par rôle et exposition RAG.</p>
              </div>
              <button onClick={closeDrawer} className="text-brand-secondary hover:text-brand-dark">
                <X size={20} />
              </button>
            </div>

            {drawerLoading ? (
              <div className="flex items-center gap-3 px-6 py-10 text-brand-secondary">
                <LoaderCircle size={18} className="animate-spin" />
                Chargement des détails du document...
              </div>
            ) : (
              <div className="space-y-6 px-6 py-6">
                <section className="rounded-2xl border border-brand-secondary/10 bg-brand-light/30 p-4">
                  <div className="mb-4 flex items-center gap-2">
                    <ShieldCheck size={16} className="text-brand-secondary" />
                    <h4 className="text-sm font-bold text-brand-dark">Autorisations d’accès par rôle</h4>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {ROLE_OPTIONS.map((role) => {
                      const active = settingsState.allowed_roles?.includes(role.key);
                      return (
                        <button
                          key={role.key}
                          type="button"
                          onClick={() => toggleRole(role.key)}
                          className={cn(
                            "flex items-center justify-between rounded-xl border px-3 py-2 text-sm transition-colors",
                            active
                              ? "border-brand-secondary bg-brand-secondary/10 text-brand-dark"
                              : "border-brand-secondary/15 bg-white text-brand-secondary/70"
                          )}
                        >
                          <span>{role.label}</span>
                          <span className={cn("h-2.5 w-2.5 rounded-full", active ? "bg-brand-secondary" : "bg-brand-secondary/20")} />
                        </button>
                      );
                    })}
                  </div>
                </section>

                <section className="rounded-2xl border border-brand-secondary/10 bg-white p-4 shadow-sm">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <h4 className="text-sm font-bold text-brand-dark">Ingestion Qdrant / RAG</h4>
                      <p className="mt-1 text-sm text-brand-secondary/70">Rend le contenu du document accessible au RAG selon les rôles autorisés.</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setSettingsState((current) => ({ ...current, rag_enabled: !current.rag_enabled }))}
                      className={cn(
                        "relative h-7 w-12 rounded-full transition-colors",
                        settingsState.rag_enabled ? "bg-brand-secondary" : "bg-brand-secondary/20"
                      )}
                    >
                      <span className={cn(
                        "absolute top-1 h-5 w-5 rounded-full bg-white transition-all",
                        settingsState.rag_enabled ? "left-6" : "left-1"
                      )} />
                    </button>
                  </div>
                  <div className="mt-3 space-y-1 text-sm text-brand-secondary/75">
                    <p>Statut : <span className="font-semibold text-brand-dark">{settingsState.rag_status || 'disabled'}</span></p>
                    {settingsState.rag_last_synced_at && <p>Dernière synchro : {new Date(settingsState.rag_last_synced_at).toLocaleString()}</p>}
                    {settingsState.rag_error && <p className="text-brand-warning">{settingsState.rag_error}</p>}
                  </div>
                </section>

                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={saveSettings}
                    disabled={settingsSaving || !settingsState.allowed_roles?.length}
                    className="rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {settingsSaving ? 'Enregistrement...' : 'Enregistrer les paramètres'}
                  </button>
                </div>

                <section className="rounded-2xl border border-brand-secondary/10 bg-white p-4 shadow-sm">
                  <div className="mb-4 flex items-center gap-2">
                    <History size={16} className="text-brand-secondary" />
                    <h4 className="text-sm font-bold text-brand-dark">Historique des accès</h4>
                  </div>
                  <div className="space-y-3">
                    {accessHistory.length === 0 ? (
                      <p className="text-sm text-brand-secondary/60">Aucun événement enregistré pour ce document.</p>
                    ) : (
                      accessHistory.map((event) => (
                        <div key={event.id} className="rounded-xl border border-brand-secondary/10 bg-brand-light/20 p-3">
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <p className="font-semibold text-brand-dark">{ACCESS_ACTION_LABELS[event.action] || event.action}</p>
                              <p className="text-sm text-brand-secondary/70">{event.user_email}</p>
                            </div>
                            <p className="text-xs text-brand-secondary/60">{new Date(event.created_at).toLocaleString()}</p>
                          </div>
                          <p className="mt-2 text-xs text-brand-secondary/60">Rôles: {(event.roles || []).join(', ') || '—'}</p>
                        </div>
                      ))
                    )}
                  </div>
                </section>
              </div>
            )}
          </div>
        </div>
      ), overlayRoot)}
    </div>
  );
}
