import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import { api } from '../../lib/api';
import { Loader2 } from 'lucide-react';

export default function EditProfile() {
  const { user } = useAuth();
  const [form, setForm] = useState({
    email: user?.email || '',
    poste: 'Développeur Front-end',
    localisation: 'Paris, France',
  });
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get('/employees/me');
        if (data) {
          setForm({
            email: data.email,
            poste: data.contract_type || 'Collaborateur',
            localisation: 'Paris Hub',
          });
        }
      } catch (err) {
        console.error("Erreur de chargement du profil", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user]);

  const handleChange = (key) => (event) => {
    setForm((prev) => ({ ...prev, [key]: event.target.value }));
    setSaved(false);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      // Soumettre une demande de modification au RH
      await api.post('/employees/me/change-request', {
        field: 'email',
        new_value: form.email
      });
      setSaved(true);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-brand-secondary/50">
        <Loader2 className="animate-spin mr-2" size={20} />
        Chargement...
      </div>
    );
  }

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Modifier mon profil" subtitle="Mettez à jour vos informations personnelles" />

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm font-medium text-brand-secondary">
              Email
              <input
                type="email"
                value={form.email}
                onChange={handleChange('email')}
                className="rounded-xl border border-brand-secondary/20 bg-brand-light px-4 py-3 text-sm text-brand-dark outline-none transition focus:border-brand-secondary focus:bg-white"
              />
            </label>
            <label className="flex flex-col gap-2 text-sm font-medium text-brand-secondary">
              Poste (lecture seule)
              <input
                disabled
                value={form.poste}
                className="rounded-xl border border-brand-secondary/20 bg-brand-light/55 px-4 py-3 text-sm text-brand-secondary/70 outline-none cursor-not-allowed"
              />
            </label>
          </div>

          <label className="flex flex-col gap-2 text-sm font-medium text-brand-secondary">
            Localisation
            <input
              value={form.localisation}
              onChange={handleChange('localisation')}
              className="rounded-xl border border-brand-secondary/20 bg-brand-light px-4 py-3 text-sm text-brand-dark outline-none transition focus:border-brand-secondary focus:bg-white"
            />
          </label>

          <button type="submit" className="rounded-2xl bg-brand-secondary px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-dark shadow-sm">
            Enregistrer
          </button>

          {saved && (
            <p className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700 font-semibold">Demande de modification soumise à l'équipe RH avec succès.</p>
          )}
        </form>
      </Card>
    </div>
  );
}
