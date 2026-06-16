import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { FileText, Code, Layers, Plus, Trash2, Edit2, CheckCircle, XCircle, Image as ImageIcon, Briefcase, Users, LayoutDashboard } from 'lucide-react';
import { api } from '../../lib/api';
import { cn } from '../../lib/utils';

const BASE_VARIABLES_GROUPS = {
  "Employé": [
    "employee.first_name", "employee.last_name", "employee.email", 
    "employee.phone", "employee.address", "employee.hire_date"
  ],
  "Contrat": [
    "contract.type", "contract.start_date", "contract.end_date", 
    "contract.salary", "contract.status"
  ],
  "Poste": [
    "job.title", "job.department"
  ],
  "Manager": [
    "manager.first_name", "manager.last_name", "manager.email"
  ]
};

const AVAILABLE_ROLES = [
  { value: 'collaborator', label: 'Collaborateur' },
  { value: 'manager', label: 'Manager' },
  { value: 'hr', label: 'Ressources Humaines' },
  { value: 'direction', label: 'Direction' },
];

export default function MoteurDocumentaire() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('types');
  const [types, setTypes] = useState([]);
  const [baseTemplates, setBaseTemplates] = useState([]);
  const [documentTemplates, setDocumentTemplates] = useState([]);
  const [assets, setAssets] = useState([]);

  // Forms
  const [editingTypeId, setEditingTypeId] = useState(null);
  const [newType, setNewType] = useState({ name: '', code: '', responsible_role: '', allowed_roles: [], required_variables: [] });
  const [newBase, setNewBase] = useState({ name: '', html_content: '{% block content %}{% endblock %}' });
  const [newDocTpl, setNewDocTpl] = useState({ name: '', document_type_id: '', base_template_id: '', html_content: '<h1>Titre</h1>\n<p>Contenu...</p>', is_active: false });
  const [newAsset, setNewAsset] = useState({ key: '', type: 'text', value: '', file: null });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      if (activeTab === 'types') {
        const [resTypes, resAssets] = await Promise.all([
          api.get('/templates/types'),
          api.get('/templates/assets')
        ]);
        setTypes(resTypes || []);
        setAssets(resAssets || []);
      } else if (activeTab === 'base') {
        const res = await api.get('/templates/base');
        setBaseTemplates(res || []);
      } else if (activeTab === 'templates') {
        const [resActive, resTypes, resBase] = await Promise.all([
          api.get('/templates/active'),
          api.get('/templates/types'),
          api.get('/templates/base')
        ]);
        setDocumentTemplates(resActive || []);
        setTypes(resTypes || []);
        setBaseTemplates(resBase || []);
      } else if (activeTab === 'assets') {
        const res = await api.get('/templates/assets');
        setAssets(res || []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateType = async (e) => {
    e.preventDefault();
    try {
      if (editingTypeId) {
        await api.put(`/templates/types/${editingTypeId}`, newType);
        setEditingTypeId(null);
      } else {
        await api.post('/templates/types', newType);
      }
      setNewType({ name: '', code: '', responsible_role: '', allowed_roles: [], required_variables: [] });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const handleEditTypeClick = (t) => {
    setEditingTypeId(t.id);
    setNewType({
      name: t.name,
      code: t.code,
      responsible_role: t.responsible_role || '',
      allowed_roles: t.allowed_roles || [],
      required_variables: t.required_variables || []
    });
  };

  const handleCancelEditType = () => {
    setEditingTypeId(null);
    setNewType({ name: '', code: '', responsible_role: '', allowed_roles: [], required_variables: [] });
  };

  const handleDeleteType = async (id) => {
    try { await api.delete(`/templates/types/${id}`); fetchData(); } catch (err) { console.error(err); }
  };

  const handleCreateBase = async (e) => {
    e.preventDefault();
    try {
      await api.post('/templates/base', newBase);
      setNewBase({ name: '', html_content: '{% block content %}{% endblock %}' });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const handleDeleteBase = async (id) => {
    try { await api.delete(`/templates/base/${id}`); fetchData(); } catch (err) { console.error(err); }
  };

  const handleCreateDocTpl = async (e) => {
    e.preventDefault();
    try {
      await api.post('/templates/active', newDocTpl);
      setNewDocTpl({ name: '', document_type_id: '', base_template_id: '', html_content: '', is_active: false });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const handleDeleteDocTpl = async (id) => {
    try { await api.delete(`/templates/active/${id}`); fetchData(); } catch (err) { console.error(err); }
  };

  const handleCreateAsset = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('key', newAsset.key);
      formData.append('asset_type', newAsset.type);
      if (newAsset.type === 'text') {
        formData.append('value', newAsset.value);
      } else if (newAsset.type === 'image_base64' && newAsset.file) {
        formData.append('file', newAsset.file);
      }
      
      await api.post('/templates/assets', formData);
      setNewAsset({ key: '', type: 'text', value: '', file: null });
      fetchData();
    } catch (err) { console.error(err); }
  };

  const handleDeleteAsset = async (id) => {
    try { await api.delete(`/templates/assets/${id}`); fetchData(); } catch (err) { console.error(err); }
  };

  const handleRoleToggle = (roleValue) => {
    setNewType(prev => {
      const roles = prev.allowed_roles.includes(roleValue)
        ? prev.allowed_roles.filter(r => r !== roleValue)
        : [...prev.allowed_roles, roleValue];
      return { ...prev, allowed_roles: roles };
    });
  };

  const handleVarToggle = (varName) => {
    setNewType(prev => {
      const vars = prev.required_variables.includes(varName)
        ? prev.required_variables.filter(v => v !== varName)
        : [...prev.required_variables, varName];
      return { ...prev, required_variables: vars };
    });
  };

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Moteur Documentaire</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">
            Gérez les types de documents, les variables, les actifs globaux et les templates Jinja.
          </p>
        </div>
      </div>

      <div className="border-b border-brand-secondary/15">
        <nav className="-mb-px flex space-x-8">
          <button onClick={() => setActiveTab('types')} className={cn(
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors',
            activeTab === 'types' ? 'border-brand-secondary text-brand-secondary' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark hover:border-brand-secondary/30'
          )}>
            <FileText className="w-5 h-5 mr-2" /> Types & Variables
          </button>
          <button onClick={() => setActiveTab('base')} className={cn(
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors',
            activeTab === 'base' ? 'border-brand-secondary text-brand-secondary' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark hover:border-brand-secondary/30'
          )}>
            <Layers className="w-5 h-5 mr-2" /> Base Templates
          </button>
          <button onClick={() => setActiveTab('templates')} className={cn(
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors',
            activeTab === 'templates' ? 'border-brand-secondary text-brand-secondary' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark hover:border-brand-secondary/30'
          )}>
            <Code className="w-5 h-5 mr-2" /> Templates Actifs
          </button>
          <button onClick={() => setActiveTab('assets')} className={cn(
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors',
            activeTab === 'assets' ? 'border-brand-secondary text-brand-secondary' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark hover:border-brand-secondary/30'
          )}>
            <ImageIcon className="w-5 h-5 mr-2" /> Assets Globaux
          </button>
        </nav>
      </div>

      {activeTab === 'types' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 bg-white rounded-xl shadow-sm border border-brand-secondary/15 p-6">
            <h3 className="text-lg font-bold text-brand-dark mb-4">{editingTypeId ? 'Modifier le Type' : 'Créer un Type'}</h3>
            <form onSubmit={handleCreateType} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Nom</label>
                <input required type="text" className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newType.name} onChange={e => setNewType({...newType, name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Code (unique)</label>
                <input required type="text" className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newType.code} onChange={e => setNewType({...newType, code: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Rôles Autorisés (Génération)</label>
                <div className="space-y-2 border border-brand-secondary/20 rounded-lg p-3 bg-brand-light">
                  {AVAILABLE_ROLES.map(role => (
                    <div key={role.value} className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="rounded text-brand-secondary focus:ring-brand-secondary w-4 h-4"
                        checked={newType.allowed_roles.includes(role.value)}
                        onChange={() => handleRoleToggle(role.value)}
                      />
                      <span className="ml-2 text-sm text-brand-dark">{role.label}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Rôle Responsable (Valideur)</label>
                <select className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newType.responsible_role} onChange={e => setNewType({...newType, responsible_role: e.target.value})}>
                  <option value="">Aucun (Auto-validation)</option>
                  <option value="hr">Ressources Humaines</option>
                  <option value="manager">Manager</option>
                  <option value="direction">Direction</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Variables Requises</label>
                <div className="h-48 overflow-y-auto border border-brand-secondary/20 bg-brand-light rounded-lg p-3 space-y-4">
                  {Object.entries({
                    ...BASE_VARIABLES_GROUPS,
                    "Entreprise (Assets)": assets.length > 0 ? assets.map(a => `assets['${a.key}']`) : ["Aucun asset configuré"]
                  }).map(([groupName, vars]) => (
                    <div key={groupName}>
                      <p className="text-xs font-bold text-brand-secondary/60 uppercase tracking-wider mb-2">{groupName}</p>
                      <div className="space-y-1.5 pl-1">
                        {vars.map(v => (
                          <div key={v} className="flex items-center">
                            <input type="checkbox" className="rounded text-brand-secondary focus:ring-brand-secondary w-3.5 h-3.5" 
                              checked={newType.required_variables.includes(v)}
                              onChange={() => handleVarToggle(v)}
                              disabled={v === "Aucun asset configuré"}
                            />
                            <span className="ml-2 text-xs font-medium text-brand-dark">{v}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                {editingTypeId && (
                  <button type="button" onClick={handleCancelEditType} className="w-1/3 flex justify-center items-center px-4 py-2 border border-brand-secondary/30 text-brand-secondary rounded-lg hover:bg-brand-light transition-colors font-medium text-sm">
                    Annuler
                  </button>
                )}
                <button type="submit" className={`flex justify-center items-center px-4 py-2 bg-brand-secondary text-white rounded-lg hover:bg-brand-secondary/90 transition-colors font-medium text-sm ${editingTypeId ? 'w-2/3' : 'w-full'}`}>
                  {editingTypeId ? 'Enregistrer' : <><Plus className="w-4 h-4 mr-2" /> Créer le Type</>}
                </button>
              </div>
            </form>
          </div>
          <div className="md:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-brand-secondary/15 overflow-hidden">
              <table className="min-w-full divide-y divide-brand-secondary/10">
                <thead className="bg-brand-light/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Nom / Code</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Accès / Responsable</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Variables</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-brand-secondary/10">
                  {types.map(t => (
                    <tr key={t.id} className="hover:bg-brand-light/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="text-sm font-bold text-brand-dark">{t.name}</div>
                        <div className="text-xs text-brand-secondary/60 mt-0.5">{t.code}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-xs text-brand-dark mb-1">
                          <span className="font-semibold text-brand-secondary/70">Génération:</span> {t.allowed_roles?.join(', ') || 'Tous'}
                        </div>
                        <div className="text-xs text-brand-dark">
                          <span className="font-semibold text-brand-secondary/70">Validation:</span> {t.responsible_role || 'Automatique'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1 max-w-[200px]">
                          {(t.required_variables || []).slice(0, 3).map(rv => (
                            <span key={rv} className="px-1.5 py-0.5 bg-brand-light border border-brand-secondary/20 rounded text-[10px] text-brand-dark">
                              {rv}
                            </span>
                          ))}
                          {(t.required_variables || []).length > 3 && (
                            <span className="px-1.5 py-0.5 bg-brand-light border border-brand-secondary/20 rounded text-[10px] text-brand-dark">
                              +{(t.required_variables || []).length - 3}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => handleEditTypeClick(t)} className="text-brand-secondary/60 hover:text-brand-secondary transition-colors mr-3" title="Modifier">
                          <Edit2 className="w-4 h-4"/>
                        </button>
                        <button onClick={() => handleDeleteType(t.id)} className="text-brand-secondary/40 hover:text-red-500 transition-colors" title="Supprimer">
                          <Trash2 className="w-4 h-4"/>
                        </button>
                      </td>
                    </tr>
                  ))}
                  {types.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-sm text-brand-secondary/60">
                        Aucun type de document configuré.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'base' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-brand-secondary/15 p-6">
            <h3 className="text-lg font-bold text-brand-dark mb-4">Nouveau Base Template</h3>
            <form onSubmit={handleCreateBase} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Nom</label>
                <input required type="text" className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newBase.name} onChange={e => setNewBase({...newBase, name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Code HTML (Jinja)</label>
                <textarea required rows={10} className="w-full font-mono text-sm rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newBase.html_content} onChange={e => setNewBase({...newBase, html_content: e.target.value})} />
              </div>
              <button type="submit" className="w-full flex justify-center items-center px-4 py-2 bg-brand-secondary text-white rounded-lg hover:bg-brand-secondary/90 transition-colors font-medium">
                <Plus className="w-4 h-4 mr-2" /> Enregistrer le base template
              </button>
            </form>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-brand-secondary/15 overflow-hidden">
            <table className="min-w-full divide-y divide-brand-secondary/10">
              <thead className="bg-brand-light/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Nom</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-secondary/10">
                {baseTemplates.map(t => (
                  <tr key={t.id} className="hover:bg-brand-light/30 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-brand-dark">{t.name}</td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => handleDeleteBase(t.id)} className="text-brand-secondary/40 hover:text-red-500 transition-colors">
                        <Trash2 className="w-4 h-4"/>
                      </button>
                    </td>
                  </tr>
                ))}
                {baseTemplates.length === 0 && (
                  <tr>
                    <td colSpan={2} className="px-6 py-8 text-center text-sm text-brand-secondary/60">
                      Aucun base template configuré.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 bg-white rounded-xl shadow-sm border border-brand-secondary/15 p-6">
            <h3 className="text-lg font-bold text-brand-dark mb-4">Créer un Template Actif</h3>
            <form onSubmit={handleCreateDocTpl} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Nom</label>
                <input required type="text" className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newDocTpl.name} onChange={e => setNewDocTpl({...newDocTpl, name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Type de Document</label>
                <select required className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newDocTpl.document_type_id} onChange={e => setNewDocTpl({...newDocTpl, document_type_id: e.target.value})}>
                  <option value="">Sélectionner...</option>
                  {types.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Base Template (Héritage)</label>
                <select required className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newDocTpl.base_template_id} onChange={e => setNewDocTpl({...newDocTpl, base_template_id: e.target.value})}>
                  <option value="">Sélectionner...</option>
                  {baseTemplates.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">HTML Content ({'{% block content %}'})</label>
                <textarea required rows={6} className="w-full font-mono text-sm rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newDocTpl.html_content} onChange={e => setNewDocTpl({...newDocTpl, html_content: e.target.value})} />
              </div>
              <div className="flex items-center">
                <input type="checkbox" className="rounded text-brand-secondary focus:ring-brand-secondary w-4 h-4" checked={newDocTpl.is_active} onChange={e => setNewDocTpl({...newDocTpl, is_active: e.target.checked})} />
                <span className="ml-2 text-sm text-brand-dark font-medium">Activer (désactivera les autres pour ce type)</span>
              </div>
              <button type="submit" className="w-full flex justify-center items-center px-4 py-2 bg-brand-secondary text-white rounded-lg hover:bg-brand-secondary/90 transition-colors font-medium">
                <Plus className="w-4 h-4 mr-2" /> Créer le Template
              </button>
            </form>
          </div>
          <div className="md:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-brand-secondary/15 overflow-hidden">
              <table className="min-w-full divide-y divide-brand-secondary/10">
                <thead className="bg-brand-light/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Template</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Héritage / Type</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Statut</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-brand-secondary/10">
                  {documentTemplates.map(t => (
                    <tr key={t.id} className="hover:bg-brand-light/30 transition-colors">
                      <td className="px-6 py-4 text-sm font-bold text-brand-dark">{t.name}</td>
                      <td className="px-6 py-4 text-xs text-brand-dark">
                        <div className="mb-0.5"><span className="font-semibold text-brand-secondary/70">Type:</span> {t.document_type_name}</div>
                        <div><span className="font-semibold text-brand-secondary/70">Base:</span> {t.base_template_name}</div>
                      </td>
                      <td className="px-6 py-4">
                        {t.is_active ? 
                          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-green-100 text-green-700 border border-green-200"><CheckCircle className="w-3 h-3 mr-1"/> Actif</span> :
                          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-gray-100 text-gray-700 border border-gray-200"><XCircle className="w-3 h-3 mr-1"/> Inactif</span>
                        }
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => handleDeleteDocTpl(t.id)} className="text-brand-secondary/40 hover:text-red-500 transition-colors">
                          <Trash2 className="w-4 h-4"/>
                        </button>
                      </td>
                    </tr>
                  ))}
                  {documentTemplates.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-sm text-brand-secondary/60">
                        Aucun template actif.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'assets' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 bg-white rounded-xl shadow-sm border border-brand-secondary/15 p-6">
            <h3 className="text-lg font-bold text-brand-dark mb-4">Nouvel Asset</h3>
            <form onSubmit={handleCreateAsset} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Clé d'Asset (ex: company.logo)</label>
                <input required type="text" placeholder="company.name" className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newAsset.key} onChange={e => setNewAsset({...newAsset, key: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-semibold text-brand-dark mb-1">Type</label>
                <select className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newAsset.type} onChange={e => setNewAsset({...newAsset, type: e.target.value})}>
                  <option value="text">Texte / URL simple</option>
                  <option value="image_base64">Image (Upload fichier)</option>
                </select>
              </div>
              
              {newAsset.type === 'text' ? (
                <div>
                  <label className="block text-sm font-semibold text-brand-dark mb-1">Valeur</label>
                  <input required type="text" placeholder="Pulse RH" className="w-full rounded-lg border-brand-secondary/20 bg-brand-light text-brand-dark px-3 py-2 text-sm focus:border-brand-secondary focus:ring-1 focus:ring-brand-secondary outline-none" value={newAsset.value} onChange={e => setNewAsset({...newAsset, value: e.target.value})} />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-semibold text-brand-dark mb-1">Fichier (Image)</label>
                  <input required type="file" accept="image/*" className="w-full text-sm text-brand-secondary/70 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-brand-light file:text-brand-dark hover:file:bg-brand-secondary/20" onChange={e => setNewAsset({...newAsset, file: e.target.files[0]})} />
                  <p className="text-[10px] text-brand-secondary/60 mt-1">L'image sera convertie et injectée de manière optimale dans les PDF générés.</p>
                </div>
              )}
              
              <button type="submit" className="w-full flex justify-center items-center px-4 py-2 bg-brand-secondary text-white rounded-lg hover:bg-brand-secondary/90 transition-colors font-medium">
                <Plus className="w-4 h-4 mr-2" /> Créer / Remplacer
              </button>
            </form>
          </div>
          <div className="md:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-brand-secondary/15 overflow-hidden">
              <table className="min-w-full divide-y divide-brand-secondary/10">
                <thead className="bg-brand-light/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Clé</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Valeur / Aperçu</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-brand-secondary/70 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-brand-secondary/10">
                  {assets.map(a => (
                    <tr key={a.id} className="hover:bg-brand-light/30 transition-colors">
                      <td className="px-6 py-4 text-sm font-bold text-brand-dark">{a.key}</td>
                      <td className="px-6 py-4 text-xs">
                        <span className="px-2 py-1 bg-brand-light rounded border border-brand-secondary/20 font-medium text-brand-dark">
                          {a.asset_type === 'image_base64' ? 'Image Uploadée' : 'Texte'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {a.asset_type === 'image_base64' ? (
                          <div className="h-10 w-24 bg-brand-light border border-brand-secondary/20 rounded flex items-center justify-center p-1 overflow-hidden">
                            <img src={a.value} alt={a.key} className="max-h-full max-w-full object-contain" />
                          </div>
                        ) : (
                          <span className="text-sm text-brand-dark truncate max-w-[200px] block">{a.value}</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => handleDeleteAsset(a.id)} className="text-brand-secondary/40 hover:text-red-500 transition-colors">
                          <Trash2 className="w-4 h-4"/>
                        </button>
                      </td>
                    </tr>
                  ))}
                  {assets.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-sm text-brand-secondary/60">
                        Aucun asset global configuré.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
