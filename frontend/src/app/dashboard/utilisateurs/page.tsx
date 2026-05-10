'use client';
import { useState, useEffect } from 'react';
import { usersAPI, getErrorMessage } from '@/lib/api';
import { FiUsers, FiPlus, FiSearch, FiEdit2, FiTrash2, FiX, FiLock, FiMail, FiPhone, FiCheckCircle, FiXCircle } from 'react-icons/fi';

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [passwordUser, setPasswordUser] = useState<any>(null);
  const [newPassword, setNewPassword] = useState('');
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', password: '', company_name: '' });

  const load = () => {
    usersAPI.list({ search: search || undefined }).then(r => { setUsers(r.data); setLoading(false); }).catch(() => setLoading(false));
  };
  useEffect(() => { load(); }, [search]);

  const update = (key: string, val: string) => setForm(f => ({ ...f, [key]: val }));
  const resetForm = () => setForm({ first_name: '', last_name: '', email: '', phone: '', password: '', company_name: '' });

  const openCreate = () => { resetForm(); setEditing(null); setShowModal(true); };
  const openEdit = (u: any) => {
    setForm({
      first_name: u.first_name, last_name: u.last_name,
      email: u.email, phone: u.phone || '',
      password: '', company_name: u.company_name || '',
    });
    setEditing(u); setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) {
        const { password, ...updateData } = form;
        await usersAPI.update(editing.id, updateData);
      } else {
        await usersAPI.create(form);
      }
      setShowModal(false); load();
    } catch (err: any) {
      alert(getErrorMessage(err));
    }
  };

  const handleDelete = async (u: any) => {
    if (!confirm(`Supprimer l'utilisateur ${u.first_name} ${u.last_name} et toutes ses données ?`)) return;
    try {
      await usersAPI.delete(u.id);
      load();
    } catch (err: any) {
      alert(getErrorMessage(err));
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordUser) return;
    try {
      await usersAPI.resetPassword(passwordUser.id, newPassword);
      setShowPasswordModal(false);
      setNewPassword('');
      alert('Mot de passe réinitialisé avec succès');
    } catch (err: any) {
      alert(getErrorMessage(err));
    }
  };

  return (
    <>
      <div className="page-header">
        <div>
          <h2 className="page-title">Utilisateurs</h2>
          <p className="page-subtitle">Gérer les comptes utilisateurs et leurs espaces</p>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <FiSearch style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
            <input className="form-input" placeholder="Rechercher..." value={search} onChange={e => setSearch(e.target.value)} style={{ paddingLeft: 36, width: 220 }} />
          </div>
          <button className="btn btn-primary" onClick={openCreate}><FiPlus /> Nouvel utilisateur</button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead><tr>
              <th>Nom</th><th>Email</th><th>Téléphone</th><th>Entreprise</th><th>Factures</th><th>Clients</th><th>Statut</th><th></th>
            </tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={8}><div className="loading-spinner" /></td></tr> :
               users.length === 0 ? (
                <tr><td colSpan={8}><div className="empty-state"><FiUsers style={{ fontSize: 48 }} /><h3>Aucun utilisateur</h3><p>Créez votre premier utilisateur</p></div></td></tr>
              ) : users.map(u => (
                <tr key={u.id}>
                  <td style={{ fontWeight: 600 }}>{u.first_name} {u.last_name}</td>
                  <td><span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><FiMail style={{ fontSize: 13, color: 'var(--text-secondary)' }} /> {u.email}</span></td>
                  <td>{u.phone ? <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><FiPhone style={{ fontSize: 13, color: 'var(--text-secondary)' }} /> {u.phone}</span> : '—'}</td>
                  <td style={{ fontSize: 13 }}>{u.company_name || '—'}</td>
                  <td style={{ textAlign: 'center' }}><span className="badge badge-info">{u.total_invoices}</span></td>
                  <td style={{ textAlign: 'center' }}><span className="badge badge-default">{u.total_clients}</span></td>
                  <td>
                    {u.is_active ? (
                      <span className="badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}><FiCheckCircle style={{ fontSize: 12 }} /> Actif</span>
                    ) : (
                      <span className="badge badge-danger" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}><FiXCircle style={{ fontSize: 12 }} /> Inactif</span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button className="btn btn-icon" title="Modifier" onClick={() => openEdit(u)}><FiEdit2 /></button>
                      <button className="btn btn-icon" title="Mot de passe" onClick={() => { setPasswordUser(u); setNewPassword(''); setShowPasswordModal(true); }}><FiLock /></button>
                      <button className="btn btn-icon" title="Supprimer" onClick={() => handleDelete(u)} style={{ color: 'var(--danger)' }}><FiTrash2 /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal création / édition */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header"><h3 className="modal-title">{editing ? 'Modifier utilisateur' : 'Nouvel utilisateur'}</h3><button className="btn btn-icon" onClick={() => setShowModal(false)}><FiX /></button></div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group"><label>Prénom *</label><input className="form-input" value={form.first_name} onChange={e => update('first_name', e.target.value)} required /></div>
                  <div className="form-group"><label>Nom *</label><input className="form-input" value={form.last_name} onChange={e => update('last_name', e.target.value)} required /></div>
                </div>
                <div className="form-row">
                  <div className="form-group"><label>Email *</label><input className="form-input" type="email" value={form.email} onChange={e => update('email', e.target.value)} required /></div>
                  <div className="form-group"><label>Téléphone</label><input className="form-input" value={form.phone} onChange={e => update('phone', e.target.value)} /></div>
                </div>
                <div className="form-group"><label>Nom de l&apos;entreprise</label><input className="form-input" value={form.company_name} onChange={e => update('company_name', e.target.value)} placeholder="Sera créée automatiquement" /></div>
                {!editing && (
                  <div className="form-group"><label>Mot de passe *</label><input className="form-input" type="password" value={form.password} onChange={e => update('password', e.target.value)} required={!editing} minLength={4} /></div>
                )}
                {editing && (
                  <div style={{ padding: '12px 16px', background: 'var(--bg-secondary)', borderRadius: 8, fontSize: 13, color: 'var(--text-secondary)', marginTop: 8 }}>
                    💡 Pour changer le mot de passe, utilisez le bouton <FiLock style={{ verticalAlign: 'middle' }} /> dans la liste.
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>{editing ? 'Modifier' : 'Créer'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal mot de passe */}
      {showPasswordModal && passwordUser && (
        <div className="modal-overlay" onClick={() => setShowPasswordModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 400 }}>
            <div className="modal-header"><h3 className="modal-title">Réinitialiser le mot de passe</h3><button className="btn btn-icon" onClick={() => setShowPasswordModal(false)}><FiX /></button></div>
            <form onSubmit={handleResetPassword}>
              <div className="modal-body">
                <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 16 }}>
                  Nouveau mot de passe pour <strong>{passwordUser.first_name} {passwordUser.last_name}</strong>
                </p>
                <div className="form-group"><label>Nouveau mot de passe *</label><input className="form-input" type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} required minLength={4} /></div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowPasswordModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>Réinitialiser</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
