import { useState, useRef, useEffect } from 'react';
import { Upload, FileText, CheckCircle, XCircle, AlertTriangle, Info, Download, RefreshCw, FolderArchive, History } from 'lucide-react';
import { cn } from '../../lib/utils';
import keycloak from '../../config/keycloak';
import { api, API_BASE_URL } from '../../lib/api';

const IMPORT_TYPES = {
  departments: { id: 'departments', label: 'Départements' },
  jobs: { id: 'jobs', label: 'Postes (Jobs)' },
  employees: { id: 'employees', label: 'Employés' },
  contracts: { id: 'contracts', label: 'Contrats' },
  leaves: { id: 'leaves', label: 'Congés (Leaves)' },
  projects: { id: 'projects', label: 'Projets' },
  tasks: { id: 'tasks', label: 'Tâches' },
  attendances: { id: 'attendances', label: 'Présences (Attendances)' },
  skills: { id: 'skills', label: 'Compétences' },
  'employee-skills': { id: 'employee-skills', label: 'Compétences Employés' },
  'training-courses': { id: 'training-courses', label: 'Formations' },
  'training-enrollments': { id: 'training-enrollments', label: 'Inscriptions Formations' },
  'project-assignments': { id: 'project-assignments', label: 'Affectations Projets' },
  'engagement-snapshots': { id: 'engagement-snapshots', label: 'Engagement' },
  'performance-reviews': { id: 'performance-reviews', label: 'Revues de Performance' },
  'performance-objectives': { id: 'performance-objectives', label: 'Objectifs Performance' },
  'benefit-plans': { id: 'benefit-plans', label: 'Avantages Sociaux' },
  'employee-benefits': { id: 'employee-benefits', label: 'Avantages Employés' },
  'career-paths': { id: 'career-paths', label: 'Parcours Carrière' },
  'mobility-requests': { id: 'mobility-requests', label: 'Mobilité' },
  'promotion-history': { id: 'promotion-history', label: 'Promotions' },
};

export default function ImportDonnees() {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [detectedType, setDetectedType] = useState(null);
  const [importing, setImporting] = useState(false);
  const [downloadingSamples, setDownloadingSamples] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const inputRef = useRef();
  const formatHistoryDate = (createdAt) => {
    if (!createdAt) return 'Date indisponible';
    const parsedDate = new Date(createdAt);
    if (Number.isNaN(parsedDate.getTime())) return 'Date indisponible';
    return `${parsedDate.toLocaleDateString()} ${parsedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  };

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const data = await api.get('/imports/history');
      setHistory(data);
    } catch (err) {
      console.error("Erreur lors de la récupération de l'historique :", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const detectFileType = (csvHeader) => {
    const header = csvHeader.toLowerCase();
    if (header.includes('first_name') && header.includes('last_name')) return 'employees';
    if (header.includes('target_job_id') && header.includes('readiness_level')) return 'career-paths';
    if (header.includes('target_department_id') && header.includes('request_type')) return 'mobility-requests';
    if (header.includes('previous_job_title') && header.includes('new_job_title')) return 'promotion-history';
    if (header.includes('benefit_plan_id') && header.includes('tier_label')) return 'employee-benefits';
    if (header.includes('provider') && header.includes('coverage_summary')) return 'benefit-plans';
    if (header.includes('progress_pct') && header.includes('due_date') && header.includes('title')) return 'performance-objectives';
    if (header.includes('review_period') && header.includes('overall_score')) return 'performance-reviews';
    if (header.includes('score') && header.includes('pulse_label')) return 'engagement-snapshots';
    if (header.includes('project_id') && header.includes('role_on_project')) return 'project-assignments';
    if (header.includes('training_id') && header.includes('completed_at')) return 'training-enrollments';
    if (header.includes('duration_hours') && header.includes('format')) return 'training-courses';
    if (header.includes('skill_id') && header.includes('proficiency_level')) return 'employee-skills';
    if (header.includes('category') && header.includes('level_scale')) return 'skills';
    if (header.includes('title') && header.includes('level')) return 'jobs';
    if (header.includes('check_in')) return 'attendances';
    if (header.includes('salary')) return 'contracts';
    if (header.includes('leave_type') && header.includes('start_date') && header.includes('end_date')) return 'leaves';
    if (header.includes('deadline')) return 'projects';
    if (header.includes('project_id') && header.includes('title')) return 'tasks';
    if (header.includes('name') && header.includes('manager_id')) return 'departments';
    return null; // Unknown type
  };

  const processFile = (f) => {
    if (!f) return;
    setFile(f);
    setReport(null);
    setError(null);
    setDetectedType(null);

    // Read the first line of the file to detect columns
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const firstLine = text.split('\n')[0];
      const type = detectFileType(firstLine);
      
      if (type) {
        setDetectedType(type);
      } else {
        setError("Impossible de déterminer automatiquement le type de données. Vérifiez les en-têtes du fichier CSV.");
        setFile(null);
      }
    };
    reader.onerror = () => setError("Erreur de lecture du fichier.");
    // Read only the first 500 bytes to be fast
    reader.readAsText(f.slice(0, 500));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    processFile(e.dataTransfer.files[0]);
  };

  const handleFile = (e) => {
    processFile(e.target.files[0]);
  };

  const startImport = async () => {
    if (!file || !detectedType || importing) return;
    setImporting(true);
    setReport(null);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Utilisation du wrapper API centralisé
      const data = await api.post(`/imports/${detectedType}`, formData);
      setReport(data);
      
      // Recharger l'historique depuis la BDD
      await fetchHistory();
    } catch (err) {
      setError(err.message);
      // Recharger l'historique pour inclure l'erreur si elle a été sauvegardée
      await fetchHistory();
    } finally {
      setImporting(false);
    }
  };

  const reset = () => { 
    setFile(null); 
    setDetectedType(null);
    setReport(null); 
    setError(null); 
    if (inputRef.current) inputRef.current.value = '';
  };

  const downloadSamples = async () => {
    if (downloadingSamples) return;
    setDownloadingSamples(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/imports/samples`, {
        headers: keycloak.token ? { Authorization: `Bearer ${keycloak.token}` } : {},
      });

      if (!response.ok) {
        throw new Error(`Téléchargement impossible (HTTP ${response.status})`);
      }

      const blob = await response.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = 'pulseai-import-samples.zip';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(objectUrl);
    } catch (err) {
      setError(err.message || "Impossible de télécharger le kit d'exemples.");
    } finally {
      setDownloadingSamples(false);
    }
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Import de données</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Le système détecte automatiquement le type d'entité grâce aux colonnes du CSV.</p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={downloadSamples}
            disabled={downloadingSamples}
            className="inline-flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-70"
          >
            {downloadingSamples ? <RefreshCw size={16} className="animate-spin" /> : <Download size={16} />}
            {downloadingSamples ? 'Téléchargement...' : 'Télécharger les fichiers samples'}
          </button>
          <button
            type="button"
            onClick={fetchHistory}
            disabled={historyLoading}
            className="inline-flex items-center gap-2 rounded-xl border border-brand-secondary/20 px-4 py-2.5 text-sm font-semibold text-brand-secondary transition-colors hover:bg-brand-light disabled:cursor-not-allowed disabled:opacity-70"
          >
            <RefreshCw size={16} className={cn(historyLoading && "animate-spin")} />
            Actualiser l'historique
          </button>
        </div>
      </div>

      <div className="rounded-2xl border border-brand-secondary/10 bg-white p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-brand-secondary/10">
            <FolderArchive size={24} className="text-brand-secondary" />
          </div>
          <div className="space-y-3">
            <div>
              <h2 className="text-lg font-bold text-brand-dark">Kit d'exemples d'import</h2>
              <p className="mt-1 text-sm text-brand-secondary/70">
                Le bouton de téléchargement fournit un dossier compressé avec des CSV modèles et un mémo détaillé pour préparer correctement vos imports.
              </p>
            </div>
            <div className="grid gap-3 text-sm text-brand-secondary/80 md:grid-cols-2">
              <div className="rounded-xl bg-brand-light/30 p-4">
                <p className="font-semibold text-brand-dark">Le mémo explique</p>
                <p className="mt-1">les colonnes attendues, les types par colonne, les champs obligatoires, les dépendances entre fichiers et l'ordre d'import recommandé.</p>
              </div>
              <div className="rounded-xl bg-brand-light/30 p-4">
                <p className="font-semibold text-brand-dark">Le dossier contient</p>
                <p className="mt-1">des exemples `departments`, `jobs`, `employees`, `contracts`, `leaves`, `projects`, `tasks` et `attendances`, déjà ordonnés pour guider vos utilisateurs.</p>
              </div>
            </div>
          </div>
        </div>
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
        <input ref={inputRef} type="file" accept=".csv" className="hidden" onChange={handleFile} />
        {file ? (
          <>
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-secondary/10">
              <FileText size={28} className="text-brand-secondary" />
            </div>
            <div className="text-center">
              <p className="font-semibold text-brand-dark">{file.name}</p>
              <p className="text-sm text-brand-secondary/60">{(file.size / 1024).toFixed(1)} Ko</p>
            </div>
            
            {importing && (
              <div className="flex items-center gap-2 text-sm text-brand-secondary font-medium">
                <div className="h-4 w-4 rounded-full border-2 border-brand-secondary border-t-transparent animate-spin" />
                Importation en cours...
              </div>
            )}

            {!importing && detectedType && !report && !error && (
              <div className="mt-4 flex flex-col items-center max-w-md w-full gap-4">
                <div className="w-full rounded-xl bg-brand-secondary/5 border border-brand-secondary/20 p-4">
                  <h3 className="font-semibold text-brand-dark flex items-center gap-2">
                    <CheckCircle size={18} className="text-brand-secondary" />
                    Type détecté : {IMPORT_TYPES[detectedType].label}
                  </h3>
                  <div className="mt-3 flex gap-2 items-start text-xs text-brand-secondary/80 bg-white p-3 rounded-lg border border-brand-secondary/10">
                    <Info size={16} className="text-brand-secondary shrink-0 mt-0.5" />
                    <p>
                      <strong>Stratégie de mise à jour (Upsert) :</strong><br/>
                      Si un ID du fichier n'existe pas, la ligne sera créée. S'il existe déjà, la ligne correspondante sera entièrement mise à jour avec les nouvelles données du fichier.
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 mt-2 w-full justify-center">
                  <button onClick={startImport} className="rounded-xl bg-brand-secondary px-8 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-brand-dark transition-colors">
                    Confirmer l'import
                  </button>
                  <button onClick={reset} className="rounded-xl border border-brand-secondary/20 px-6 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">
                    Annuler
                  </button>
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 flex w-full max-w-md items-start gap-3 rounded-xl bg-brand-warning/10 p-4 text-left">
                <XCircle size={20} className="text-brand-warning shrink-0" />
                <div>
                  <h4 className="text-sm font-bold text-brand-warning">Échec de l'import</h4>
                  <p className="mt-1 text-xs text-brand-warning/80">{error}</p>
                  <button onClick={reset} className="mt-3 rounded-lg border border-brand-warning/30 px-4 py-1.5 text-xs font-semibold text-brand-warning hover:bg-brand-warning/20">Réessayer</button>
                </div>
              </div>
            )}
          </>
        ) : (
          <>
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-brand-secondary/10">
              <Upload size={28} className="text-brand-secondary" />
            </div>
            <div className="text-center">
              <p className="font-semibold text-brand-dark">Glissez votre fichier CSV ici</p>
              <p className="text-sm text-brand-secondary/60">Le système détectera automatiquement le type de données.</p>
            </div>
          </>
        )}
      </div>

      {/* Rapport d'import */}
      {report && (
        <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden animate-fade-in-up">
          <div className="flex items-center justify-between px-5 py-4 border-b border-brand-secondary/10 bg-brand-light/20">
            <h2 className="font-semibold text-brand-dark flex items-center gap-2">
              <CheckCircle size={18} className="text-brand-secondary" />
              Rapport de traitement ({IMPORT_TYPES[detectedType]?.label})
            </h2>
            <button onClick={reset} className="text-xs font-semibold text-brand-secondary hover:underline">Nouvel import</button>
          </div>
          
          <div className="p-5 grid grid-cols-3 gap-4">
            <div className="rounded-xl bg-brand-light/30 p-4 text-center">
              <p className="text-sm font-semibold text-brand-secondary/70">Lignes lues</p>
              <p className="text-3xl font-bold text-brand-dark mt-1">{report.processed}</p>
            </div>
            <div className="rounded-xl bg-brand-secondary/10 p-4 text-center">
              <p className="text-sm font-semibold text-brand-secondary/70">Créés / Mis à jour</p>
              <p className="text-3xl font-bold text-brand-secondary mt-1">{report.created + report.updated}</p>
            </div>
            <div className={cn("rounded-xl p-4 text-center", report.errors.length > 0 ? "bg-brand-warning/10" : "bg-brand-light/30")}>
              <p className={cn("text-sm font-semibold", report.errors.length > 0 ? "text-brand-warning/70" : "text-brand-secondary/70")}>Erreurs</p>
              <p className={cn("text-3xl font-bold mt-1", report.errors.length > 0 ? "text-brand-warning" : "text-brand-dark")}>{report.errors.length}</p>
            </div>
          </div>

          {report.errors.length > 0 && (
            <div className="border-t border-brand-secondary/10">
              <div className="px-5 py-3 bg-brand-warning/5 border-b border-brand-warning/10 flex items-center gap-2">
                <AlertTriangle size={16} className="text-brand-warning" />
                <h3 className="text-sm font-bold text-brand-warning">Détails des erreurs de validation</h3>
              </div>
              <ul className="max-h-64 overflow-y-auto divide-y divide-brand-secondary/5 p-2">
                {report.errors.map((err, idx) => (
                  <li key={idx} className="px-4 py-2 text-sm flex gap-3 items-start">
                    <span className="font-mono text-xs bg-brand-warning/10 text-brand-warning px-2 py-0.5 rounded">Ligne {err.line}</span>
                    <span className="text-brand-dark/80">{err.error}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="rounded-2xl border border-brand-secondary/10 bg-white p-6 shadow-sm">
        <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-brand-secondary/10">
              <History size={18} className="text-brand-secondary" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-brand-dark">Historique des imports</h2>
              <p className="text-sm text-brand-secondary/70">Tous les imports enregistrés sont listés ici, avec accès rapide au dernier rapport.</p>
            </div>
          </div>
          <div className="rounded-full bg-brand-light px-3 py-1 text-xs font-semibold text-brand-secondary">
            {history.length} import{history.length > 1 ? 's' : ''} enregistré{history.length > 1 ? 's' : ''}
          </div>
        </div>
        <div className="space-y-3">
          {historyLoading ? (
            <div className="flex items-center gap-2 rounded-xl bg-brand-light/30 p-4 text-sm text-brand-secondary/80">
              <RefreshCw size={16} className="animate-spin" />
              Chargement de l'historique...
            </div>
          ) : history.length === 0 ? (
            <p className="text-sm text-brand-secondary/60">Aucun import enregistré pour le moment.</p>
          ) : (
            history.map((item) => (
              <div 
                key={item.id} 
                onClick={() => {
                  if (item.full_report) {
                    setDetectedType(item.entity_type);
                    setReport(item.full_report);
                    setError(null);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  } else if (item.status === 'error') {
                    setError("Cet import a échoué. Aucun rapport détaillé disponible.");
                    setReport(null);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }
                }}
                className={cn(
                  "flex items-center justify-between rounded-xl border border-brand-secondary/10 bg-brand-light/20 p-4 transition-colors",
                  (item.full_report || item.status === 'error') ? "cursor-pointer hover:bg-brand-light/40" : ""
                )}
              >
                <div className="flex items-center gap-4">
                  <div className={cn(
                    "grid h-10 w-10 place-items-center rounded-lg",
                    item.status === 'success' && "bg-green-100 text-green-600",
                    item.status === 'error' && "bg-red-100 text-red-600",
                    item.status === 'warning' && "bg-orange-100 text-orange-600"
                  )}>
                    {item.status === 'success' ? <CheckCircle size={20} /> : item.status === 'warning' ? <AlertTriangle size={20} /> : <XCircle size={20} />}
                  </div>
                  <div>
                    <p className="font-semibold text-brand-dark">{item.filename}</p>
                    <p className="text-xs font-medium text-brand-secondary/60">
                      {item.entity_type ? IMPORT_TYPES[item.entity_type]?.label : 'Inconnu'} • {item.processed_lines} lignes lues ({item.error_count} erreurs) • Importé par {item.author_name || 'Inconnu'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-brand-dark">
                    {item.status === 'success' ? 'Réussi' : item.status === 'warning' ? 'Partiel' : 'Échoué'}
                  </p>
                  <p className="text-xs font-medium text-brand-secondary/60">
                    {formatHistoryDate(item.created_at)}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
