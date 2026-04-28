'use client';
import { useState, useEffect } from 'react';
import { invoicesAPI, clientsAPI, productsAPI } from '@/lib/api';
import toast from 'react-hot-toast';
import { FiPlus, FiSearch, FiTrash2, FiFileText, FiArrowRight } from 'react-icons/fi';

const statusMap: Record<string, { label: string; className: string }> = {
  brouillon: { label: 'Brouillon', className: 'badge-default' },
  envoyee: { label: 'Envoyé', className: 'badge-info' },
  accepte: { label: 'Accepté', className: 'badge-success' },
  refuse: { label: 'Refusé', className: 'badge-danger' },
};

export default function DevisPage() {
  const [devis, setDevis] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const load = () => { invoicesAPI.list({ invoice_type: 'devis', search: search || undefined }).then(r => { setDevis(r.data); setLoading(false); }).catch(() => setLoading(false)); };
  useEffect(() => { load(); }, [search]);

  const fmt = (n: number) => new Intl.NumberFormat('fr-TN', { minimumFractionDigits: 3 }).format(n);

  const handleConvert = async (id: string) => {
    if (!confirm('Convertir ce devis en facture ?')) return;
    try { await invoicesAPI.convert(id); toast.success('Devis converti en facture !'); load(); } catch { toast.error('Erreur'); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer ce devis ?')) return;
    try { await invoicesAPI.delete(id); toast.success('Devis supprimé'); load(); } catch { toast.error('Erreur'); }
  };

  return (
    <>
      <div className="toolbar">
        <div className="toolbar-left"><div className="search-input"><FiSearch /><input placeholder="Rechercher un devis..." value={search} onChange={e => setSearch(e.target.value)} /></div></div>
        <div className="toolbar-right"><span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Créez un devis depuis la page Factures</span></div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead><tr><th>Réf.</th><th>Date</th><th>Client</th><th>Total TTC</th><th>Statut</th><th>Actions</th></tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={6}><div className="loading-spinner" /></td></tr> :
               devis.length === 0 ? (
                <tr><td colSpan={6}><div className="empty-state"><FiFileText style={{ fontSize: 48 }} /><h3>Aucun devis</h3><p>Les devis apparaîtront ici</p></div></td></tr>
              ) : devis.map(d => (
                <tr key={d.id}>
                  <td style={{ fontWeight: 700, color: 'var(--primary)' }}>{d.reference}</td>
                  <td>{new Date(d.date).toLocaleDateString('fr-FR')}</td>
                  <td>{d.client_name || '—'}</td>
                  <td className="text-amount text-bold">{fmt(d.total)} <span className="currency">TND</span></td>
                  <td><span className={`badge ${statusMap[d.status]?.className || 'badge-default'}`}>{statusMap[d.status]?.label || d.status}</span></td>
                  <td>
                    {d.status !== 'accepte' && <button className="btn btn-sm btn-success" onClick={() => handleConvert(d.id)} style={{ fontSize: 12, padding: '4px 12px' }}><FiArrowRight /> Convertir</button>}
                    <button className="btn btn-icon" onClick={() => handleDelete(d.id)} style={{ color: 'var(--danger)' }}><FiTrash2 /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
