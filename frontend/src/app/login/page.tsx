'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Connexion réussie !');
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-left">
        <div className="auth-logo">SIC <span>Facture</span></div>
        <h1 className="auth-tagline">Gérez votre entreprise en un seul endroit !</h1>
        <p className="auth-subtitle">
          Prenez le contrôle de votre facturation et de vos flux financiers avec une simplicité sans précédent.
          Factures, devis, clients, stock — tout est centralisé.
        </p>
        <div className="auth-stats">
          <div className="auth-stat">
            <div className="auth-stat-value">100%</div>
            <div className="auth-stat-label">Gratuit</div>
          </div>
          <div className="auth-stat">
            <div className="auth-stat-value">∞</div>
            <div className="auth-stat-label">Factures</div>
          </div>
          <div className="auth-stat">
            <div className="auth-stat-value">TND</div>
            <div className="auth-stat-label">Devise locale</div>
          </div>
        </div>
      </div>
      <div className="auth-right">
        <div className="auth-form-container">
          <h2 className="auth-form-title">Se connecter</h2>
          <p className="auth-form-subtitle">
            Nouveau ici ? <Link href="/register">Créer un compte</Link>
          </p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email</label>
              <input type="email" className="form-input" placeholder="votre@email.com"
                value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Mot de passe</label>
              <input type="password" className="form-input" placeholder="Votre mot de passe"
                value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <div className="form-footer">
              <label className="form-checkbox">
                <input type="checkbox" /> Se souvenir de moi
              </label>
              <a href="#" className="form-link">Mot de passe oublié ?</a>
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Connexion...' : 'Accéder à mon espace'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
