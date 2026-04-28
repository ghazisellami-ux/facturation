'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import toast from 'react-hot-toast';

export default function RegisterPage() {
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', password: '', phone: '' });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password.length < 6) { toast.error('Le mot de passe doit contenir au moins 6 caractères'); return; }
    setLoading(true);
    try {
      await register(form);
      toast.success('Compte créé avec succès !');
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Erreur lors de l\'inscription');
    } finally { setLoading(false); }
  };

  const update = (field: string, value: string) => setForm(prev => ({ ...prev, [field]: value }));

  return (
    <div className="auth-page">
      <div className="auth-left">
        <div className="auth-logo">SIC <span>Facture</span></div>
        <h1 className="auth-tagline">Gérez votre entreprise en un seul endroit !</h1>
        <p className="auth-subtitle">
          Créez votre compte gratuitement et commencez à facturer en quelques minutes.
          TVA, FODEC, Timbre fiscal — tout est pris en charge automatiquement.
        </p>
        <div className="auth-stats">
          <div className="auth-stat"><div className="auth-stat-value">100%</div><div className="auth-stat-label">Gratuit</div></div>
          <div className="auth-stat"><div className="auth-stat-value">∞</div><div className="auth-stat-label">Factures</div></div>
          <div className="auth-stat"><div className="auth-stat-value">TND</div><div className="auth-stat-label">Devise locale</div></div>
        </div>
      </div>
      <div className="auth-right">
        <div className="auth-form-container">
          <h2 className="auth-form-title">Créer un compte</h2>
          <p className="auth-form-subtitle">Déjà inscrit ? <Link href="/login">Se connecter</Link></p>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Prénom</label>
                <input type="text" className="form-input" placeholder="Prénom" value={form.first_name} onChange={(e) => update('first_name', e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Nom</label>
                <input type="text" className="form-input" placeholder="Nom" value={form.last_name} onChange={(e) => update('last_name', e.target.value)} required />
              </div>
            </div>
            <div className="form-group">
              <label>Téléphone</label>
              <input type="tel" className="form-input" placeholder="+216 XX XXX XXX" value={form.phone} onChange={(e) => update('phone', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" className="form-input" placeholder="votre@email.com" value={form.email} onChange={(e) => update('email', e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Mot de passe</label>
              <input type="password" className="form-input" placeholder="Min. 6 caractères" value={form.password} onChange={(e) => update('password', e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Création...' : 'Créer mon compte'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
