'use client';
import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { authAPI, getErrorMessage } from '@/lib/api';
import toast from 'react-hot-toast';
import { FiUser, FiBriefcase, FiSave } from 'react-icons/fi';

export default function ParametresPage() {
  const { user, company } = useAuth();
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: '', tax_id: '', address: '', city: '', postal_code: '',
    country: 'Tunisie', phone: '', email: '', website: '',
    invoice_prefix: 'FAC', devis_prefix: 'DEV',
  });

  useEffect(() => {
    if (company) {
      setForm({
        name: company.name || '',
        tax_id: (company as any).tax_id || '',
        address: (company as any).address || '',
        city: (company as any).city || '',
        postal_code: (company as any).postal_code || '',
        country: (company as any).country || 'Tunisie',
        phone: (company as any).phone || '',
        email: (company as any).email || '',
        website: (company as any).website || '',
        invoice_prefix: (company as any).invoice_prefix || 'FAC',
        devis_prefix: (company as any).devis_prefix || 'DEV',
      });
    }
  }, [company]);

  const update = (field: string, value: string) => setForm(p => ({ ...p, [field]: value }));

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await authAPI.updateCompany(form);
      toast.success('Paramètres enregistrés !');
    } catch (err: any) {
      toast.error(getErrorMessage(err, 'Erreur lors de la sauvegarde'));
    } finally { setSaving(false); }
  };

  return (
    <form onSubmit={handleSave}>
      <div className="grid-2">
        {/* Profil utilisateur */}
        <div className="card">
          <div className="card-header"><h3 className="card-title"><FiUser style={{ marginRight: 8 }} /> Mon profil</h3></div>
          <div className="card-body">
            <div className="form-row">
              <div className="form-group"><label>Prénom</label><input className="form-input" value={user?.first_name || ''} readOnly /></div>
              <div className="form-group"><label>Nom</label><input className="form-input" value={user?.last_name || ''} readOnly /></div>
            </div>
            <div className="form-group"><label>Email</label><input className="form-input" value={user?.email || ''} readOnly /></div>
            <div className="form-group"><label>Téléphone</label><input className="form-input" value={user?.phone || ''} readOnly /></div>
          </div>
        </div>

        {/* Infos entreprise */}
        <div className="card">
          <div className="card-header"><h3 className="card-title"><FiBriefcase style={{ marginRight: 8 }} /> Mon entreprise</h3></div>
          <div className="card-body">
            <div className="form-group"><label>Nom / Raison sociale *</label><input className="form-input" value={form.name} onChange={e => update('name', e.target.value)} required /></div>
            <div className="form-group"><label>Matricule Fiscal (MF)</label><input className="form-input" value={form.tax_id} onChange={e => update('tax_id', e.target.value)} placeholder="0000000/X/A/M/000" /></div>
            <div className="form-group"><label>Adresse</label><input className="form-input" value={form.address} onChange={e => update('address', e.target.value)} /></div>
            <div className="form-row">
              <div className="form-group"><label>Ville</label><input className="form-input" value={form.city} onChange={e => update('city', e.target.value)} /></div>
              <div className="form-group"><label>Code postal</label><input className="form-input" value={form.postal_code} onChange={e => update('postal_code', e.target.value)} /></div>
            </div>
            <div className="form-row">
              <div className="form-group"><label>Téléphone</label><input className="form-input" value={form.phone} onChange={e => update('phone', e.target.value)} /></div>
              <div className="form-group"><label>Email</label><input className="form-input" type="email" value={form.email} onChange={e => update('email', e.target.value)} /></div>
            </div>
            <div className="form-group"><label>Site web</label><input className="form-input" value={form.website} onChange={e => update('website', e.target.value)} placeholder="https://..." /></div>
          </div>
        </div>
      </div>

      {/* Préfixes */}
      <div className="card" style={{ marginTop: 20 }}>
        <div className="card-header"><h3 className="card-title">Numérotation des documents</h3></div>
        <div className="card-body">
          <div className="form-row">
            <div className="form-group"><label>Préfixe factures</label><input className="form-input" value={form.invoice_prefix} onChange={e => update('invoice_prefix', e.target.value)} /></div>
            <div className="form-group"><label>Préfixe devis</label><input className="form-input" value={form.devis_prefix} onChange={e => update('devis_prefix', e.target.value)} /></div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 20, textAlign: 'right' }}>
        <button type="submit" className="btn btn-primary" disabled={saving} style={{ width: 'auto' }}>
          <FiSave style={{ marginRight: 6 }} /> {saving ? 'Enregistrement...' : 'Enregistrer les paramètres'}
        </button>
      </div>
    </form>
  );
}
