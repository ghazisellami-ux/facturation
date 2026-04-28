'use client';
import { useState, useEffect } from 'react';
import { suppliersAPI, getErrorMessage } from '@/lib/api';
import toast from 'react-hot-toast';
import { FiPlus, FiSearch, FiEdit2, FiTrash2, FiX, FiTruck } from 'react-icons/fi';

export default function FournisseursPage() {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [form, setForm] = useState({ name: '', tax_id: '', email: '', phone: '', address: '', city: '', country: 'Tunisie', contact_name: '', notes: '' });

  const load = () => { suppliersAPI.list({ search: search || undefined }).then(r => { setSuppliers(r.data); setLoading(false); }).catch(() => setLoading(false)); };
  useEffect(() => { load(); }, [search]);

  const resetForm = () => setForm({ name: '', tax_id: '', email: '', phone: '', address: '', city: '', country: 'Tunisie', contact_name: '', notes: '' });
  const openCreate = () => { resetForm(); setEditing(null); setShowModal(true); };
  const openEdit = (s: any) => { setForm({ name: s.name, tax_id: s.tax_id || '', email: s.email || '', phone: s.phone || '', address: s.address || '', city: s.city || '', country: s.country, contact_name: s.contact_name || '', notes: s.notes || '' }); setEditing(s); setShowModal(true); };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) { await suppliersAPI.update(editing.id, form); toast.success('Fournisseur modifié'); }
      else { await suppliersAPI.create(form); toast.success('Fournisseur créé'); }
      setShowModal(false); load();
    } catch (err: any) { toast.error(getErrorMessage(err)); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer ce fournisseur ?')) return;
    try { await suppliersAPI.delete(id); toast.success('Fournisseur supprimé'); load(); }
    catch { toast.error('Erreur'); }
  };

  const update = (f: string, v: string) => setForm(p => ({ ...p, [f]: v }));

  return (
    <>
      <div className="toolbar">
        <div className="toolbar-left">
          <div className="search-input"><FiSearch /><input placeholder="Rechercher un fournisseur..." value={search} onChange={e => setSearch(e.target.value)} /></div>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-primary btn-sm" onClick={openCreate} style={{ width: 'auto' }}><FiPlus /> Nouveau fournisseur</button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead><tr><th>Nom</th><th>MF</th><th>Email</th><th>Téléphone</th><th>Ville</th><th>Solde</th><th></th></tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={7}><div className="loading-spinner" /></td></tr> :
               suppliers.length === 0 ? (
                <tr><td colSpan={7}><div className="empty-state"><FiTruck style={{ fontSize: 48 }} /><h3>Aucun fournisseur</h3><p>Ajoutez votre premier fournisseur</p></div></td></tr>
              ) : suppliers.map(s => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 600 }}>{s.name}</td>
                  <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s.tax_id || '—'}</td>
                  <td>{s.email || '—'}</td>
                  <td>{s.phone || '—'}</td>
                  <td>{s.city || '—'}</td>
                  <td className="text-amount">{new Intl.NumberFormat('fr-TN', { minimumFractionDigits: 3 }).format(s.balance)} <span className="currency">TND</span></td>
                  <td>
                    <button className="btn btn-icon" onClick={() => openEdit(s)}><FiEdit2 /></button>
                    <button className="btn btn-icon" onClick={() => handleDelete(s.id)} style={{ color: 'var(--danger)' }}><FiTrash2 /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header"><h3 className="modal-title">{editing ? 'Modifier fournisseur' : 'Nouveau fournisseur'}</h3><button className="btn btn-icon" onClick={() => setShowModal(false)}><FiX /></button></div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group"><label>Nom / Raison sociale *</label><input className="form-input" value={form.name} onChange={e => update('name', e.target.value)} required /></div>
                <div className="form-row">
                  <div className="form-group"><label>Matricule Fiscal</label><input className="form-input" value={form.tax_id} onChange={e => update('tax_id', e.target.value)} /></div>
                  <div className="form-group"><label>Personne de contact</label><input className="form-input" value={form.contact_name} onChange={e => update('contact_name', e.target.value)} /></div>
                </div>
                <div className="form-row">
                  <div className="form-group"><label>Email</label><input className="form-input" type="email" value={form.email} onChange={e => update('email', e.target.value)} /></div>
                  <div className="form-group"><label>Téléphone</label><input className="form-input" value={form.phone} onChange={e => update('phone', e.target.value)} /></div>
                </div>
                <div className="form-group"><label>Adresse</label><input className="form-input" value={form.address} onChange={e => update('address', e.target.value)} /></div>
                <div className="form-row">
                  <div className="form-group"><label>Ville</label><input className="form-input" value={form.city} onChange={e => update('city', e.target.value)} /></div>
                  <div className="form-group"><label>Pays</label><input className="form-input" value={form.country} onChange={e => update('country', e.target.value)} /></div>
                </div>
                <div className="form-group"><label>Notes</label><textarea className="form-input" rows={3} value={form.notes} onChange={e => update('notes', e.target.value)} style={{ resize: 'vertical' }} /></div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>{editing ? 'Modifier' : 'Créer'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
