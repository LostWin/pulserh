import { useState, useEffect } from 'react';
import { 
  Cpu, RefreshCw, Save, History, CheckCircle, Shield, AlertTriangle, 
  Trash2, Edit3, Plus, Play, ToggleLeft, ToggleRight, X, Settings, 
  HelpCircle, Key, FileText, Check, AlertOctagon, Sliders, Info, Brain
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';
import MLModuleCard from '../../components/MLModuleCard';

export default function ConfigIA() {
  const [activeTab, setActiveTab] = useState('conversational'); // 'conversational' | 'guardrails' | 'predictive'
  
  // LLM Config state
  const [llmConfig, setLlmConfig] = useState({
    provider: 'openrouter',
    model_name: 'mistralai/mistral-7b-instruct',
    temperature: 0.7,
    max_tokens: 2048,
    system_prompt: '',
    guardrails_enabled: true
  });
  
  // Guardrails list state
  const [guardrails, setGuardrails] = useState([]);
  const [editingGuardrail, setEditingGuardrail] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [guardrailForm, setGuardrailForm] = useState({
    name: '',
    pattern: '',
    action: 'block',
    description: '',
    is_active: true,
    priority: 0
  });

  // Guardrail testing state
  const [testText, setTestText] = useState('');
  const [testPattern, setTestPattern] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);

  // Predictive models state
  const [mlModules, setMlModules] = useState([]);
  const [mlLoading, setMlLoading] = useState(false);
  const [history, setHistory] = useState([]);

  // UI state
  const [loading, setLoading] = useState(false);
  const [savingLlm, setSavingLlm] = useState(false);
  const [savedLlm, setSavedLlm] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch configs and guardrails on load
  useEffect(() => {
    fetchConfigAndGuardrails();
  }, []);

  const fetchConfigAndGuardrails = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const [configData, guardrailsData, overviewData] = await Promise.all([
        api.get('/admin/ai/config'),
        api.get('/admin/guardrails'),
        api.get('/admin/ai/overview'),
      ]);
      if (configData) setLlmConfig(configData);
      if (guardrailsData) setGuardrails(guardrailsData);
      if (overviewData) {
        setHistory(overviewData.history || []);
      }
    } catch (err) {
      console.error("Error fetching AI config", err);
      setErrorMsg("Impossible de charger la configuration depuis le serveur.");
    } finally {
      setLoading(false);
    }
  };

  const fetchMlModules = async () => {
    setMlLoading(true);
    try {
      const data = await api.get('/admin/ml/modules');
      if (data) setMlModules(data);
    } catch (err) {
      console.error('Error fetching ML modules', err);
    } finally {
      setMlLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'predictive') fetchMlModules();
  }, [activeTab]);

  // Save LLM Config
  const handleSaveLlmConfig = async () => {
    setSavingLlm(true);
    setErrorMsg('');
    try {
      const updated = await api.put('/admin/ai/config', llmConfig);
      setLlmConfig(updated);
      setSavedLlm(true);
      setTimeout(() => setSavedLlm(false), 2000);
    } catch (err) {
      console.error("Error saving LLM config", err);
      setErrorMsg("Erreur lors de l'enregistrement de la configuration LLM.");
    } finally {
      setSavingLlm(false);
    }
  };

  // Toggle Guardrail state active/inactive
  const handleToggleGuardrail = async (g) => {
    try {
      const updated = await api.put(`/admin/guardrails/${g.id}`, {
        is_active: !g.is_active
      });
      setGuardrails(prev => prev.map(item => item.id === g.id ? updated : item));
    } catch (err) {
      console.error("Error toggling guardrail", err);
      setErrorMsg("Erreur lors de la modification du statut du guardrail.");
    }
  };

  // Save (Create/Update) Guardrail
  const handleSaveGuardrail = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      if (editingGuardrail) {
        // Update
        const updated = await api.put(`/admin/guardrails/${editingGuardrail.id}`, guardrailForm);
        setGuardrails(prev => prev.map(item => item.id === editingGuardrail.id ? updated : item));
      } else {
        // Create
        const created = await api.post('/admin/guardrails', guardrailForm);
        setGuardrails(prev => [created, ...prev]);
      }
      closeGuardrailForm();
    } catch (err) {
      console.error("Error saving guardrail", err);
      setErrorMsg("Erreur lors de l'enregistrement du guardrail.");
    }
  };

  // Delete Guardrail
  const handleDeleteGuardrail = async (id) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce guardrail ?")) return;
    setErrorMsg('');
    try {
      await api.delete(`/admin/guardrails/${id}`);
      setGuardrails(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      console.error("Error deleting guardrail", err);
      setErrorMsg("Erreur lors de la suppression du guardrail.");
    }
  };

  const startEditGuardrail = (g) => {
    setEditingGuardrail(g);
    setGuardrailForm({
      name: g.name,
      pattern: g.pattern,
      action: g.action,
      description: g.description || '',
      is_active: g.is_active,
      priority: g.priority
    });
    setShowForm(true);
  };

  const openCreateGuardrail = () => {
    setEditingGuardrail(null);
    setGuardrailForm({
      name: '',
      pattern: '',
      action: 'block',
      description: '',
      is_active: true,
      priority: 0
    });
    setShowForm(true);
  };

  const closeGuardrailForm = () => {
    setShowForm(false);
    setEditingGuardrail(null);
  };

  // Run live guardrail test
  const handleTestGuardrails = async () => {
    if (!testText.trim()) return;
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.post('/admin/guardrails/test', {
        text: testText,
        pattern: testPattern || null
      });
      setTestResult(res);
    } catch (err) {
      console.error("Error testing guardrails", err);
      setErrorMsg("Erreur lors du test des guardrails.");
    } finally {
      setTesting(false);
    }
  };

  const handleModuleSave = (updatedModule) => {
    setMlModules(prev => prev.map(m => m.module_id === updatedModule.module_id ? updatedModule : m));
  };

  return (
    <div className="animate-fade-in-up space-y-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-brand-secondary/10 pb-5">
        <div>
          <h1 className="text-3xl font-extrabold text-brand-dark tracking-tight">Configuration IA</h1>
          <p className="mt-2 text-sm text-brand-secondary/70">
            Paramétrez l'assistant conversationnel (LLM, RAG, Guardrails) et ajustez les modèles prédictifs RH.
          </p>
        </div>
        
        {/* Connection status indicator */}
        <div className="flex items-center gap-2 self-start md:self-center">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
            Service IA Connecté
          </span>
        </div>
      </div>

      {/* Error message alert banner */}
      {errorMsg && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-800 flex items-start gap-3 animate-shake">
          <AlertOctagon className="text-red-500 shrink-0 mt-0.5" size={16} />
          <div className="flex-1">
            <p className="font-semibold">Une erreur est survenue</p>
            <p className="text-red-700/90 mt-1">{errorMsg}</p>
          </div>
          <button onClick={() => setErrorMsg('')} className="text-red-500 hover:text-red-800">
            <X size={16} />
          </button>
        </div>
      )}

      {/* Main Tabs Navigation */}
      <div className="flex border-b border-brand-secondary/15">
        <button
          onClick={() => setActiveTab('conversational')}
          className={cn(
            "flex items-center gap-2 px-6 py-3 border-b-2 font-medium text-sm transition-all focus:outline-none",
            activeTab === 'conversational' 
              ? "border-brand-secondary text-brand-secondary bg-brand-light/20 font-bold"
              : "border-transparent text-brand-secondary/60 hover:text-brand-secondary hover:bg-brand-light/10"
          )}
        >
          <Cpu size={16} />
          Assistant & LLM
        </button>
        <button
          onClick={() => setActiveTab('guardrails')}
          className={cn(
            "flex items-center gap-2 px-6 py-3 border-b-2 font-medium text-sm transition-all focus:outline-none",
            activeTab === 'guardrails'
              ? "border-brand-secondary text-brand-secondary bg-brand-light/20 font-bold"
              : "border-transparent text-brand-secondary/60 hover:text-brand-secondary hover:bg-brand-light/10"
          )}
        >
          <Shield size={16} />
          Guardrails & Sécurité
          {guardrails.filter(g => g.is_active).length > 0 && (
            <span className="ml-1 px-1.5 py-0.5 text-xxs font-extrabold bg-brand-secondary text-white rounded-full">
              {guardrails.filter(g => g.is_active).length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('predictive')}
          className={cn(
            "flex items-center gap-2 px-6 py-3 border-b-2 font-medium text-sm transition-all focus:outline-none",
            activeTab === 'predictive'
              ? "border-brand-secondary text-brand-secondary bg-brand-light/20 font-bold"
              : "border-transparent text-brand-secondary/60 hover:text-brand-secondary hover:bg-brand-light/10"
          )}
        >
          <Sliders size={16} />
          Modèles Prédictifs
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-brand-secondary/50">
          <RefreshCw className="animate-spin text-brand-secondary mb-4" size={40} />
          <p className="text-sm font-medium">Chargement de la configuration...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* TAB 1: CONVERSATIONAL & LLM */}
          {activeTab === 'conversational' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Form Settings */}
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-white rounded-2xl border border-brand-secondary/10 shadow-sm p-6 space-y-6">
                  <div className="flex items-center gap-2 border-b border-brand-secondary/10 pb-4">
                    <Settings className="text-brand-secondary" size={18} />
                    <h2 className="text-lg font-bold text-brand-dark">Paramètres du Modèle de Langage</h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* LLM Provider */}
                    <div className="space-y-2">
                      <label className="block text-xs font-bold uppercase tracking-wider text-brand-secondary/70">
                        Fournisseur (Provider)
                      </label>
                      <select
                        value={llmConfig.provider}
                        onChange={(e) => setLlmConfig({...llmConfig, provider: e.target.value})}
                        className="w-full bg-brand-light/50 border border-brand-secondary/15 rounded-xl px-4 py-3 text-sm text-brand-dark focus:outline-none focus:ring-2 focus:ring-brand-secondary"
                      >
                        <option value="openrouter">OpenRouter (Distant / Cloud)</option>
                        <option value="ollama">Ollama (Local / On-Premise)</option>
                      </select>
                    </div>

                    {/* Model Name */}
                    <div className="space-y-2">
                      <label className="block text-xs font-bold uppercase tracking-wider text-brand-secondary/70">
                        Modèle de l'IA (Model Name)
                      </label>
                      <input
                        type="text"
                        value={llmConfig.model_name}
                        onChange={(e) => setLlmConfig({...llmConfig, model_name: e.target.value})}
                        placeholder="Ex: mistralai/mistral-7b-instruct"
                        className="w-full bg-brand-light/50 border border-brand-secondary/15 rounded-xl px-4 py-3 text-sm text-brand-dark focus:outline-none focus:ring-2 focus:ring-brand-secondary font-mono"
                      />
                    </div>

                    {/* Temperature */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <label className="block text-xs font-bold uppercase tracking-wider text-brand-secondary/70">
                          Température ({llmConfig.temperature})
                        </label>
                        <span className="text-xs text-brand-secondary/50">
                          {llmConfig.temperature < 0.4 ? 'Précis/Factuel' : llmConfig.temperature > 0.8 ? 'Créatif' : 'Équilibré'}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="1.2"
                        step="0.1"
                        value={llmConfig.temperature}
                        onChange={(e) => setLlmConfig({...llmConfig, temperature: parseFloat(e.target.value)})}
                        className="w-full accent-brand-secondary cursor-pointer h-2 bg-brand-light rounded-lg appearance-none"
                      />
                      <div className="flex justify-between text-xxs text-brand-secondary/40 px-1">
                        <span>0.0 (Strict)</span>
                        <span>1.2 (Créatif)</span>
                      </div>
                    </div>

                    {/* Max Tokens */}
                    <div className="space-y-2">
                      <label className="block text-xs font-bold uppercase tracking-wider text-brand-secondary/70">
                        Tokens Maximum
                      </label>
                      <input
                        type="number"
                        min="128"
                        max="8192"
                        step="128"
                        value={llmConfig.max_tokens}
                        onChange={(e) => setLlmConfig({...llmConfig, max_tokens: parseInt(e.target.value) || 2048})}
                        className="w-full bg-brand-light/50 border border-brand-secondary/15 rounded-xl px-4 py-3 text-sm text-brand-dark focus:outline-none focus:ring-2 focus:ring-brand-secondary font-mono"
                      />
                    </div>
                  </div>

                  {/* Guardrails Enabled Toggle */}
                  <div className="flex items-center justify-between bg-brand-light/35 p-4 rounded-xl border border-brand-secondary/5">
                    <div>
                      <p className="text-sm font-bold text-brand-dark">Activer les Guardrails</p>
                      <p className="text-xs text-brand-secondary/60 mt-0.5">
                        Applique le filtrage de sécurité et de confidentialité sur les questions/réponses.
                      </p>
                    </div>
                    <button
                      onClick={() => setLlmConfig({...llmConfig, guardrails_enabled: !llmConfig.guardrails_enabled})}
                      className="text-brand-secondary focus:outline-none"
                    >
                      {llmConfig.guardrails_enabled ? <ToggleRight size={38} className="text-brand-secondary" /> : <ToggleLeft size={38} className="text-brand-secondary/30" />}
                    </button>
                  </div>

                  {/* System Prompt */}
                  <div className="space-y-2">
                    <label className="block text-xs font-bold uppercase tracking-wider text-brand-secondary/70">
                      System Prompt (Instruction principale de l'IA)
                    </label>
                    <textarea
                      rows={6}
                      value={llmConfig.system_prompt}
                      onChange={(e) => setLlmConfig({...llmConfig, system_prompt: e.target.value})}
                      placeholder="Définissez les instructions globales de comportement de l'assistant..."
                      className="w-full bg-brand-light/50 border border-brand-secondary/15 rounded-xl p-4 text-sm text-brand-dark focus:outline-none focus:ring-2 focus:ring-brand-secondary font-sans leading-relaxed"
                    />
                  </div>

                  {/* Save button */}
                  <div className="flex justify-end pt-2">
                    <button
                      onClick={handleSaveLlmConfig}
                      disabled={savingLlm}
                      className="flex items-center gap-2 bg-brand-secondary text-white hover:bg-brand-dark transition-all rounded-xl px-6 py-3 font-semibold shadow-sm focus:outline-none disabled:opacity-60"
                    >
                      {savingLlm ? (
                        <>
                          <RefreshCw className="animate-spin" size={16} />
                          Enregistrement...
                        </>
                      ) : savedLlm ? (
                        <>
                          <CheckCircle size={16} />
                          Config Sauvegardée !
                        </>
                      ) : (
                        <>
                          <Save size={16} />
                          Sauvegarder la Config LLM
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Right Column: Info & Details */}
              <div className="space-y-6">
                <div className="bg-white rounded-2xl border border-brand-secondary/10 shadow-sm p-6 space-y-6">
                  <h3 className="text-md font-bold text-brand-dark flex items-center gap-2 border-b border-brand-secondary/5 pb-3">
                    <Info size={16} className="text-brand-secondary" /> Info Architecture
                  </h3>

                  <div className="space-y-4 text-sm text-brand-secondary/80">
                    <div className="p-3 bg-brand-light/40 rounded-xl space-y-1">
                      <p className="font-bold text-brand-dark text-xs flex items-center gap-1.5 uppercase">
                        <Key size={12} /> API Key / Provider
                      </p>
                      <p className="text-xs">
                        {llmConfig.provider === 'openrouter' 
                          ? 'Utilise le jeton configuré dans LLM_API_KEY sur le serveur pour appeler les modèles distants.'
                          : 'Se connecte directement à l\'instance Ollama locale configurée sur OLLAMA_BASE_URL.'}
                      </p>
                    </div>

                    <div className="p-3 bg-brand-light/40 rounded-xl space-y-1">
                      <p className="font-bold text-brand-dark text-xs flex items-center gap-1.5 uppercase">
                        <FileText size={12} /> RAG (Vecteurs)
                      </p>
                      <p className="text-xs">
                        Toutes les questions des collaborateurs passent par un moteur RAG qui interroge la base vectorielle <strong>Qdrant</strong> pour y adjoindre des documents internes pertinents en contexte.
                      </p>
                    </div>

                    <div className="p-3 bg-brand-light/40 rounded-xl space-y-1">
                      <p className="font-bold text-brand-dark text-xs flex items-center gap-1.5 uppercase">
                        <Shield size={12} /> Tool Calling
                      </p>
                      <p className="text-xs">
                        L'IA dispose d'outils lui permettant de générer automatiquement des attestations de travail, de récupérer le solde de congés ou d'accéder aux contrats en base, sous réserve des permissions de l'utilisateur connecté.
                      </p>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* TAB 2: GUARDRAILS CRUD & TEST */}
          {activeTab === 'guardrails' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left & Center Columns: List of Guardrails */}
              <div className="lg:col-span-2 space-y-6">
                {/* Header card with Action button */}
                <div className="bg-white rounded-2xl border border-brand-secondary/10 shadow-sm p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-brand-secondary/5 pb-4 mb-4">
                    <div className="flex items-center gap-2">
                      <Shield className="text-brand-secondary" size={20} />
                      <div>
                        <h2 className="text-lg font-bold text-brand-dark">Règles de Guardrails actives</h2>
                        <p className="text-xs text-brand-secondary/60">
                          Règles de sécurité pour intercepter ou masquer la donnée sensible (regex ou mots-clés).
                        </p>
                      </div>
                    </div>
                    {!showForm && (
                      <div className="flex gap-2">
                        <button
                          onClick={async () => {
                            if (!window.confirm("Initialiser les 21 guardrails par defaut (securite, legal, RH, ethique, conformite) ?")) return;
                            try {
                              const res = await api.post('/admin/guardrails/init-defaults', {});
                              alert(res.created + " guardrails crees, " + res.skipped + " deja presents.");
                              await fetchConfigAndGuardrails();
                            } catch(e) { alert("Erreur lors de l initialisation"); }
                          }}
                          className="flex items-center gap-2 border border-brand-secondary/30 text-brand-secondary hover:bg-brand-light font-medium text-sm rounded-xl px-4 py-2.5 transition-all focus:outline-none self-start sm:self-auto"
                        >
                          <Shield size={16} />
                          Init. par defaut
                        </button>
                        <button
                          onClick={openCreateGuardrail}
                          className="flex items-center gap-2 bg-brand-secondary text-white hover:bg-brand-dark font-medium text-sm rounded-xl px-4 py-2.5 shadow-sm transition-all focus:outline-none self-start sm:self-auto"
                        >
                          <Plus size={16} />
                          Ajouter une regle
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Form Card (Inline Creation / Modification) */}
                  {showForm && (
                    <div className="bg-brand-light/35 border border-brand-secondary/10 rounded-xl p-5 mb-6 space-y-4 animate-fade-in-up">
                      <div className="flex justify-between items-center border-b border-brand-secondary/5 pb-2">
                        <h3 className="text-sm font-bold text-brand-dark flex items-center gap-1.5">
                          {editingGuardrail ? <Edit3 size={14} /> : <Plus size={14} />}
                          {editingGuardrail ? 'Modifier le Guardrail' : 'Créer un nouveau Guardrail'}
                        </h3>
                        <button onClick={closeGuardrailForm} className="text-brand-secondary/50 hover:text-brand-secondary">
                          <X size={16} />
                        </button>
                      </div>

                      <form onSubmit={handleSaveGuardrail} className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div className="space-y-1">
                            <label className="text-xs font-semibold text-brand-secondary/80">Nom de la règle</label>
                            <input
                              type="text"
                              required
                              value={guardrailForm.name}
                              onChange={(e) => setGuardrailForm({...guardrailForm, name: e.target.value})}
                              placeholder="Ex: Filtrage des Salaires"
                              className="w-full bg-white border border-brand-secondary/15 rounded-lg px-3 py-2 text-sm text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary"
                            />
                          </div>

                          <div className="space-y-1">
                            <label className="text-xs font-semibold text-brand-secondary/80">Action de Filtrage</label>
                            <select
                              value={guardrailForm.action}
                              onChange={(e) => setGuardrailForm({...guardrailForm, action: e.target.value})}
                              className="w-full bg-white border border-brand-secondary/15 rounded-lg px-3 py-2 text-sm text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary"
                            >
                              <option value="block">Block (Bloquer le message et renvoyer une erreur)</option>
                              <option value="warn">Warn (Avertir / Logger dans Wazuh sans bloquer)</option>
                              <option value="redact">Redact (Masquer / Remplacer par [CONFIDENTIEL])</option>
                            </select>
                          </div>
                        </div>

                        <div className="space-y-1">
                          <label className="text-xs font-semibold text-brand-secondary/80">Pattern (Regex ou Mot-clé)</label>
                          <input
                            type="text"
                            required
                            value={guardrailForm.pattern}
                            onChange={(e) => setGuardrailForm({...guardrailForm, pattern: e.target.value})}
                            placeholder="Ex: (?i)(salaire|fiche de paie|remun|taux horaire)"
                            className="w-full bg-white border border-brand-secondary/15 rounded-lg px-3 py-2 text-sm text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary font-mono"
                          />
                        </div>

                        <div className="space-y-1">
                          <label className="text-xs font-semibold text-brand-secondary/80">Description</label>
                          <input
                            type="text"
                            value={guardrailForm.description}
                            onChange={(e) => setGuardrailForm({...guardrailForm, description: e.target.value})}
                            placeholder="Décrivez l'objectif de cette règle de sécurité..."
                            className="w-full bg-white border border-brand-secondary/15 rounded-lg px-3 py-2 text-sm text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary"
                          />
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                          <div className="space-y-1">
                            <label className="text-xs font-semibold text-brand-secondary/80">Priorité (Ordre d'exécution)</label>
                            <input
                              type="number"
                              value={guardrailForm.priority}
                              onChange={(e) => setGuardrailForm({...guardrailForm, priority: parseInt(e.target.value) || 0})}
                              className="w-full bg-white border border-brand-secondary/15 rounded-lg px-3 py-2 text-sm text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary"
                            />
                          </div>

                          <div className="flex items-center gap-3 pt-4">
                            <button
                              type="button"
                              onClick={() => setGuardrailForm({...guardrailForm, is_active: !guardrailForm.is_active})}
                              className="focus:outline-none"
                            >
                              {guardrailForm.is_active ? <ToggleRight size={30} className="text-brand-secondary" /> : <ToggleLeft size={30} className="text-brand-secondary/30" />}
                            </button>
                            <span className="text-xs font-medium text-brand-dark">Actif dès l'enregistrement</span>
                          </div>
                        </div>

                        <div className="flex justify-end gap-2 pt-2 border-t border-brand-secondary/5">
                          <button
                            type="button"
                            onClick={closeGuardrailForm}
                            className="rounded-lg border border-brand-secondary/20 px-4 py-2 text-xs font-semibold text-brand-secondary hover:bg-brand-light"
                          >
                            Annuler
                          </button>
                          <button
                            type="submit"
                            className="rounded-lg bg-brand-secondary px-4 py-2 text-xs font-semibold text-white hover:bg-brand-dark shadow-sm"
                          >
                            Enregistrer la règle
                          </button>
                        </div>
                      </form>
                    </div>
                  )}

                  {/* Guardrails List Table */}
                  {guardrails.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-brand-secondary/40 border border-dashed border-brand-secondary/15 rounded-2xl">
                      <Shield size={36} className="mb-2 text-brand-secondary/30" />
                      <p className="text-sm font-semibold">Aucun guardrail configuré en base.</p>
                      <p className="text-xs text-brand-secondary/50 mt-1">Créez votre premier guardrail pour sécuriser les données.</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto rounded-xl border border-brand-secondary/10">
                      <table className="w-full text-sm">
                        <thead className="bg-brand-light/60">
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-brand-secondary/50">Statut</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-brand-secondary/50">Règle</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-brand-secondary/50">Pattern</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-brand-secondary/50">Categorie</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-brand-secondary/50">Action</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-brand-secondary/50">Déclenchements</th>
                            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-brand-secondary/50">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-brand-secondary/5 bg-white">
                          {guardrails.map((g) => (
                            <tr key={g.id} className="hover:bg-brand-light/20 transition-colors">
                              <td className="px-4 py-3.5">
                                <button
                                  onClick={() => handleToggleGuardrail(g)}
                                  className="focus:outline-none"
                                >
                                  {g.is_active 
                                    ? <ToggleRight size={28} className="text-brand-secondary" />
                                    : <ToggleLeft size={28} className="text-brand-secondary/30" />
                                  }
                                </button>
                              </td>
                              <td className="px-4 py-3.5">
                                <p className="font-semibold text-brand-dark text-xs">{g.name}</p>
                                {g.description && <p className="text-xxs text-brand-secondary/50 mt-0.5 max-w-xs truncate">{g.description}</p>}
                              </td>
                              <td className="px-4 py-3.5 font-mono text-xxs bg-brand-light/20 text-brand-secondary/80 max-w-xxs truncate">
                                {g.pattern}
                              </td>
                              <td className="px-4 py-3.5">
                                <span className="text-xxs font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                                  {g.category || 'security'}
                                </span>
                              </td>
                              <td className="px-4 py-3.5">
                                <span className={cn(
                                  "text-xxs font-bold px-2 py-0.5 rounded-full border",
                                  g.action === 'block' && "bg-red-50 text-red-700 border-red-200",
                                  g.action === 'warn' && "bg-amber-50 text-amber-700 border-amber-200",
                                  g.action === 'redact' && "bg-blue-50 text-blue-700 border-blue-200"
                                )}>
                                  {g.action.toUpperCase()}
                                </span>
                              </td>
                              <td className="px-4 py-3.5 text-center font-bold text-brand-secondary/70">
                                {g.triggered_count}
                              </td>
                              <td className="px-4 py-3.5 text-right space-x-1">
                                <button
                                  onClick={() => startEditGuardrail(g)}
                                  className="inline-flex p-1.5 text-brand-secondary hover:text-brand-dark hover:bg-brand-light rounded-lg transition-all"
                                  title="Modifier"
                                >
                                  <Edit3 size={14} />
                                </button>
                                <button
                                  onClick={() => handleDeleteGuardrail(g.id)}
                                  className="inline-flex p-1.5 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all"
                                  title="Supprimer"
                                >
                                  <Trash2 size={14} />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column: Live Testing Playground */}
              <div className="space-y-6">
                <div className="bg-white rounded-2xl border border-brand-secondary/10 shadow-sm p-6 space-y-6">
                  <div className="flex items-center gap-2 border-b border-brand-secondary/5 pb-3">
                    <Play className="text-brand-secondary" size={18} />
                    <h3 className="text-md font-bold text-brand-dark">Bac à sable (Playground)</h3>
                  </div>
                  <p className="text-xs text-brand-secondary/70">
                    Testez instantanément si un message utilisateur déclenche vos règles de sécurité configurées.
                  </p>

                  <div className="space-y-4">
                    {/* Test text */}
                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-brand-secondary/80">Texte à tester</label>
                      <textarea
                        rows={3}
                        value={testText}
                        onChange={(e) => setTestText(e.target.value)}
                        placeholder="Tapez un message à évaluer, ex: 'Quel est mon salaire ?'"
                        className="w-full bg-brand-light/50 border border-brand-secondary/15 rounded-xl p-3 text-xs text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary"
                      />
                    </div>

                    {/* Specific pattern override (optional) */}
                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-brand-secondary/80 flex items-center gap-1">
                        Pattern spécifique <span className="text-xxs font-normal text-brand-secondary/50">(optionnel)</span>
                      </label>
                      <input
                        type="text"
                        value={testPattern}
                        onChange={(e) => setTestPattern(e.target.value)}
                        placeholder="Ex: (?i)salaire"
                        className="w-full bg-brand-light/50 border border-brand-secondary/15 rounded-xl px-3 py-2 text-xs text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary font-mono"
                      />
                    </div>

                    {/* Test Trigger Button */}
                    <button
                      onClick={handleTestGuardrails}
                      disabled={testing || !testText.trim()}
                      className="w-full flex items-center justify-center gap-2 bg-brand-secondary text-white hover:bg-brand-dark font-semibold text-xs py-2.5 px-4 rounded-xl transition-all shadow-sm focus:outline-none disabled:opacity-50"
                    >
                      {testing ? <RefreshCw className="animate-spin" size={12} /> : <Play size={12} />}
                      Exécuter l'analyse
                    </button>
                  </div>

                  {/* Test Results Output */}
                  {testResult && (
                    <div className="mt-4 p-4 rounded-xl border border-brand-secondary/10 bg-brand-light/20 space-y-3 animate-fade-in-up">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-brand-dark">Verdict :</span>
                        {testResult.passed !== undefined ? (
                          <span className={cn(
                            "text-xxs font-bold px-2 py-0.5 rounded-full",
                            testResult.passed ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-red-50 text-red-700 border border-red-200"
                          )}>
                            {testResult.passed ? 'PASSED (Conforme)' : `BLOCKED (Action: ${testResult.action})`}
                          </span>
                        ) : (
                          <span className={cn(
                            "text-xxs font-bold px-2 py-0.5 rounded-full",
                            testResult.matched ? "bg-red-50 text-red-700 border border-red-200" : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          )}>
                            {testResult.matched ? 'MATCHED (Trouvé)' : 'NO MATCH'}
                          </span>
                        )}
                      </div>

                      {/* Display matched text details if any */}
                      {testResult.matched_text && (
                        <div className="text-xxs space-y-1">
                          <p className="font-semibold text-brand-secondary/70">Occurrences trouvées :</p>
                          <p className="font-mono bg-white p-2 rounded border border-brand-secondary/5 text-red-700">
                            {testResult.matched_text}
                          </p>
                        </div>
                      )}

                      {/* Display triggered rules list if evaluating against database */}
                      {testResult.triggered_rules && testResult.triggered_rules.length > 0 && (
                        <div className="text-xxs space-y-1">
                          <p className="font-semibold text-brand-secondary/70">Règles déclenchées :</p>
                          <div className="space-y-1">
                            {testResult.triggered_rules.map((rule, idx) => (
                              <div key={idx} className="bg-white p-1.5 rounded border border-brand-secondary/5 flex justify-between">
                                <span className="font-bold text-brand-dark">{rule.name}</span>
                                <span className="text-red-600 font-semibold">{rule.action}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Redacted output test block */}
                      {testResult.message && !testResult.passed && (
                        <div className="text-xxs space-y-1">
                          <p className="font-semibold text-brand-secondary/70">Message d'erreur bloquant :</p>
                          <p className="bg-white p-2 rounded border border-brand-secondary/5 text-brand-dark italic">
                            "{testResult.message}"
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: PREDICTIVE MODELS — Mode Heuristique/ML par module */}
          {activeTab === 'predictive' && (
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-bold text-lg text-brand-dark flex items-center gap-2">
                    <Brain size={20} className="text-brand-secondary" />
                    Moteurs Analytiques RH
                  </h2>
                  <p className="text-xs text-brand-secondary/60 mt-1">
                    Configurez chaque module indépendamment — basculez entre le mode heuristique (règles métier) et le mode ML (modèles entraînés).
                  </p>
                </div>
                <button
                  onClick={fetchMlModules}
                  disabled={mlLoading}
                  className="flex items-center gap-2 text-xs font-semibold text-brand-secondary border border-brand-secondary/20 hover:bg-brand-light px-3 py-2 rounded-xl transition-all"
                >
                  <RefreshCw size={13} className={mlLoading ? 'animate-spin' : ''} />
                  Actualiser
                </button>
              </div>

              {/* Info banner */}
              <div className="flex items-start gap-3 bg-indigo-50 border border-indigo-200 rounded-xl p-4 text-xs text-indigo-800">
                <Info size={15} className="shrink-0 mt-0.5" />
                <p>En <strong>mode Heuristique</strong>, les scores sont calculés en temps réel via des formules configurables. En <strong>mode ML</strong>, un modèle entraîné est utilisé (avec fallback heuristique si le modèle n'est pas disponible). <strong>Le mode strict</strong> force la validation humaine avant toute action.</p>
              </div>

              {/* Module cards */}
              {mlLoading ? (
                <div className="flex flex-col items-center justify-center py-16 text-brand-secondary/40">
                  <RefreshCw className="animate-spin mb-3" size={32} />
                  <p className="text-sm">Chargement des modules...</p>
                </div>
              ) : mlModules.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-brand-secondary/40 border border-dashed border-brand-secondary/15 rounded-2xl">
                  <Brain size={40} className="mb-3" />
                  <p className="text-sm font-semibold">Aucun module trouvé</p>
                  <p className="text-xs mt-1">Exécutez le script de seed pour initialiser les modules.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {mlModules.map(m => (
                    <MLModuleCard
                      key={m.module_id}
                      module={m}
                      onSave={handleModuleSave}
                      onTrain={(moduleId) => console.log('Training started for', moduleId)}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
