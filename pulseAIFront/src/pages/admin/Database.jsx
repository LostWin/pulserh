import { useState } from 'react';
import { Download, Upload, Trash2, Database as DatabaseIcon, AlertTriangle } from 'lucide-react';
import { api } from '../../lib/api';
import { cn } from '../../lib/utils';

export default function Database() {
  const [loadingAction, setLoadingAction] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  const [clearConfirmation, setClearConfirmation] = useState('');
  
  const handleClearDatabase = async () => {
    if (clearConfirmation !== 'SUPPRIMER') {
      setError('Veuillez taper SUPPRIMER pour confirmer le vidage de la base de données.');
      return;
    }
    setLoadingAction('clear');
    setError(null);
    setSuccess(null);
    try {
      const res = await api.post('/admin/database/clear');
      setSuccess(res.message || 'Base de données vidée avec succès.');
      setClearConfirmation('');
    } catch (err) {
      setError(err.message || 'Erreur lors du vidage de la base de données.');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleBackup = async () => {
    setLoadingAction('backup');
    setError(null);
    setSuccess(null);
    try {
      const response = await api.get('/admin/database/backup', { responseType: 'blob' });
      // Create a blob from the response
      const blob = new Blob([response], { type: 'application/sql' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pulse_db_backup_${new Date().toISOString().replace(/[:.]/g, '-')}.sql`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      setSuccess('Sauvegarde générée et téléchargée avec succès.');
    } catch (err) {
      setError(err.message || 'Erreur lors de la création de la sauvegarde.');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleRestore = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.name.endsWith('.sql')) {
      setError('Veuillez sélectionner un fichier .sql valide.');
      return;
    }

    setLoadingAction('restore');
    setError(null);
    setSuccess(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // Use standard fetch since api wrapper might not support FormData out of the box depending on implementation
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://api.pulse.local'}/admin/database/restore`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Erreur lors de la restauration');
      
      setSuccess(data.message || 'Restauration effectuée avec succès.');
    } catch (err) {
      setError(err.message || 'Erreur lors de la restauration.');
    } finally {
      setLoadingAction(null);
      e.target.value = ''; // Reset input
    }
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Base de Données</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Gestion avancée de la base de données : Sauvegarde, Restauration et Remise à zéro.</p>
        </div>
        <DatabaseIcon size={32} className="text-brand-secondary/20" />
      </div>

      {error && <div className="rounded-xl bg-red-50 p-4 text-sm text-red-700 font-medium border border-red-200">{error}</div>}
      {success && <div className="rounded-xl bg-green-50 p-4 text-sm text-green-700 font-medium border border-green-200">{success}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backup Card */}
        <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-6 flex flex-col">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-brand-primary/10 text-brand-primary rounded-lg">
              <Download size={24} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-brand-dark">Sauvegarde Complète</h2>
              <p className="text-xs text-brand-secondary/70">Génère un fichier .sql contenant le schéma et les données</p>
            </div>
          </div>
          <p className="text-sm text-brand-dark/80 mb-6 flex-1">
            Téléchargez une copie complète de la base de données PulseRH. Cette sauvegarde peut être utilisée pour restaurer le système ou migrer vers un nouvel environnement.
          </p>
          <button
            onClick={handleBackup}
            disabled={loadingAction !== null}
            className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-brand-primary hover:bg-brand-primary-dark text-white rounded-xl font-medium transition-colors disabled:opacity-50"
          >
            {loadingAction === 'backup' ? 'Création en cours...' : 'Télécharger la sauvegarde'}
          </button>
        </div>

        {/* Restore Card */}
        <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-6 flex flex-col">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-brand-secondary/10 text-brand-secondary rounded-lg">
              <Upload size={24} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-brand-dark">Restauration</h2>
              <p className="text-xs text-brand-secondary/70">Restaure la base à partir d'un fichier .sql</p>
            </div>
          </div>
          <p className="text-sm text-brand-dark/80 mb-6 flex-1">
            Importez un fichier de sauvegarde existant pour remplacer les données actuelles. Attention : cela écrasera les données présentes.
          </p>
          <div className="relative overflow-hidden w-full">
            <input
              type="file"
              accept=".sql"
              onChange={handleRestore}
              disabled={loadingAction !== null}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
            />
            <button
              disabled={loadingAction !== null}
              className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-brand-light hover:bg-brand-secondary/10 text-brand-dark border border-brand-secondary/20 rounded-xl font-medium transition-colors disabled:opacity-50 pointer-events-none"
            >
              {loadingAction === 'restore' ? 'Restauration en cours...' : 'Uploader un fichier .sql'}
            </button>
          </div>
        </div>

        {/* Clear Data Card */}
        <div className="rounded-2xl bg-white border border-red-200 shadow-sm p-6 md:col-span-2">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-red-100 text-red-600 rounded-lg">
              <Trash2 size={24} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-brand-dark">Remise à Zéro (Données RH)</h2>
              <p className="text-xs text-red-600/80 font-medium">Action irréversible</p>
            </div>
          </div>
          
          <div className="flex items-start gap-3 bg-red-50 p-4 rounded-xl border border-red-100 mb-6">
            <AlertTriangle size={20} className="text-red-500 shrink-0 mt-0.5" />
            <div className="text-sm text-red-800">
              <p className="font-bold mb-1">Attention, cette action est définitive.</p>
              <p>Elle supprimera de manière irréversible tous les employés, contrats, congés, présences, projets, évaluations et alertes. <b>Vos configurations IA et vos utilisateurs Keycloak ne seront pas affectés.</b></p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <input
              type="text"
              placeholder="Tapez SUPPRIMER pour confirmer"
              value={clearConfirmation}
              onChange={(e) => setClearConfirmation(e.target.value)}
              disabled={loadingAction !== null}
              className="flex-1 rounded-xl border border-brand-secondary/20 bg-white px-4 py-2.5 text-sm outline-none focus:border-red-300"
            />
            <button
              onClick={handleClearDatabase}
              disabled={clearConfirmation !== 'SUPPRIMER' || loadingAction !== null}
              className="flex items-center justify-center gap-2 py-2.5 px-6 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:bg-red-400"
            >
              {loadingAction === 'clear' ? 'Suppression...' : 'Vider la base'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
