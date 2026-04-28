'use client';
import { useAuth } from '@/lib/auth';
import { FiUser, FiBriefcase, FiMail, FiPhone } from 'react-icons/fi';

export default function ParametresPage() {
  const { user, company } = useAuth();

  return (
    <>
      <div className="grid-2">
        <div className="card">
          <div className="card-header"><h3 className="card-title"><FiUser style={{ marginRight: 8 }} /> Mon profil</h3></div>
          <div className="card-body">
            <div className="form-group"><label>Prénom</label><input className="form-input" value={user?.first_name || ''} readOnly /></div>
            <div className="form-group"><label>Nom</label><input className="form-input" value={user?.last_name || ''} readOnly /></div>
            <div className="form-group"><label>Email</label><input className="form-input" value={user?.email || ''} readOnly /></div>
            <div className="form-group"><label>Téléphone</label><input className="form-input" value={user?.phone || ''} readOnly /></div>
          </div>
        </div>
        <div className="card">
          <div className="card-header"><h3 className="card-title"><FiBriefcase style={{ marginRight: 8 }} /> Mon entreprise</h3></div>
          <div className="card-body">
            <div className="form-group"><label>Nom de l&apos;entreprise</label><input className="form-input" value={company?.name || ''} readOnly /></div>
            <div className="form-group"><label>Devise</label><input className="form-input" value={company?.currency || 'TND'} readOnly /></div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 16 }}>La modification des paramètres sera disponible prochainement.</p>
          </div>
        </div>
      </div>
    </>
  );
}
