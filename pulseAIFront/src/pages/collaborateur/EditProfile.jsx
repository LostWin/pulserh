import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';

export default function EditProfile() {
  const { user } = useAuth();
  const [form, setForm] = useState({
    email: user?.email || '',
    poste: 'Développeur Front-end',
    localisation: 'Paris, France',
  });
  const [saved, setSaved] = useState(false);

  const handleChange = (key) => (event) => {
    setForm((prev) => ({ ...prev, [key]: event.target.value }));
    setSaved(false);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setSaved(true);
  };

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
              Poste
              <input
                value={form.poste}
                onChange={handleChange('poste')}
                className="rounded-xl border border-brand-secondary/20 bg-brand-light px-4 py-3 text-sm text-brand-dark outline-none transition focus:border-brand-secondary focus:bg-white"
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

          <button type="submit" className="rounded-2xl bg-orange-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-orange-700">
            Enregistrer
          </button>

          {saved && (
            <p className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">Vos modifications ont bien été enregistrées en mode démo.</p>
          )}
        </form>
      </Card>
    </div>
  );
}
