'use client';
import { useState, useEffect } from 'react';
import { invoicesAPI, suppliersAPI, getErrorMessage } from '@/lib/api';
import toast from 'react-hot-toast';
import { FiPlus, FiSearch, FiTrash2, FiX, FiShoppingCart, FiDownload, FiCode } from 'react-icons/fi';
import Cookies from 'js-cookie';

export default function AchatsPage() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    supplier_id: '', date: '', due_date: '', notes: '',
    montant_ht: 0, tva_rate: 19, fodec: false, fodec_rate: 1, timbre_fiscal: 1.0,
  });
  useEffect(() => { setForm(f => ({ ...f, date: new Date().toISOString().split('T')[0] })); }, []);

  const load = () => {
    invoicesAPI.list({ invoice_type: 'facture_achat', search: search || undefined }).then(r => { setInvoices(r.data); setLoading(false); }).catch(() => setLoading(false));
  };
  useEffect(() => { load(); }, [search]);
  useEffect(() => { suppliersAPI.list().then(r => setSuppliers(r.data)).catch(() => {}); }, []);

  const fmt = (n: number) => new Intl.NumberFormat('fr-TN', { minimumFractionDigits: 3 }).format(n);

  // Calcul automatique
  const fodecAmount = form.fodec ? form.montant_ht * (form.fodec_rate / 100) : 0;
  const tvaBase = form.montant_ht + fodecAmount;
  const tvaAmount = tvaBase * (form.tva_rate / 100);
  const netAPayer = form.montant_ht + fodecAmount + tvaAmount + form.timbre_fiscal;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.montant_ht <= 0) { toast.error('Veuillez saisir un montant HT'); return; }
    try {
      const payload = {
        invoice_type: 'facture_achat',
        client_id: null,
        supplier_id: form.supplier_id || null,
        date: form.date,
        due_date: form.due_date || null,
        notes: form.notes || null,
        timbre_fiscal: form.timbre_fiscal,
        items: [{
          description: 'Montant total HT',
          quantity: 1,
          unit: 'forfait',
          unit_price: form.montant_ht,
          discount_percent: 0,
          tva_rate: form.tva_rate,
          fodec_rate: form.fodec ? form.fodec_rate : 0,
          product_id: null,
        }],
      };
      await invoicesAPI.create(payload);
      toast.success("Facture d'achat créée !");
      setShowModal(false); load();
    } catch (err: any) { toast.error(getErrorMessage(err, 'Erreur lors de la création')); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Supprimer cette facture d'achat ?")) return;
    try { await invoicesAPI.delete(id); toast.success("Facture d'achat supprimée"); load(); } catch { toast.error('Erreur'); }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try { await invoicesAPI.update(id, { status }); toast.success('Statut mis à jour'); load(); } catch { toast.error('Erreur'); }
  };

  const handleDownload = (id: string, format: 'pdf' | 'xml') => {
    const token = Cookies.get('access_token');
    if (!token) { toast.error('Veuillez vous reconnecter'); return; }
    const url = `/api/download/${id}/${format}?token=${token}`;
    if (format === 'pdf') {
      window.open(url, '_blank');
    } else {
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      iframe.src = url;
      document.body.appendChild(iframe);
      setTimeout(() => document.body.removeChild(iframe), 30000);
    }
  };

  const openCreate = () => {
    setForm({
      supplier_id: '', date: new Date().toISOString().split('T')[0], due_date: '', notes: '',
      montant_ht: 0, tva_rate: 19, fodec: false, fodec_rate: 1, timbre_fiscal: 1.0,
    });
    setShowModal(true);
  };

  return (
    <>
      <div className="toolbar">
        <div className="toolbar-left"><div className="search-input"><FiSearch /><input placeholder="Rechercher une facture d'achat..." value={search} onChange={e => setSearch(e.target.value)} /></div></div>
        <div className="toolbar-right">
          <button className="btn btn-primary btn-sm" onClick={openCreate} style={{ width: 'auto' }}><FiPlus /> Nouvelle facture d&apos;achat</button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead><tr><th>Réf.</th><th>Date</th><th>Fournisseur</th><th>Total TTC</th><th>Payé</th><th>Reste</th><th>Statut</th><th></th></tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={8}><div className="loading-spinner" /></td></tr> :
               invoices.length === 0 ? (
                <tr><td colSpan={8}><div className="empty-state"><FiShoppingCart style={{ fontSize: 48 }} /><h3>Aucune facture d&apos;achat</h3><p>Créez votre première facture d&apos;achat</p></div></td></tr>
              ) : invoices.map(inv => (
                <tr key={inv.id}>
                  <td style={{ fontWeight: 700, color: '#e67e22' }}>{inv.reference}</td>
                  <td>{new Date(inv.date).toLocaleDateString('fr-FR')}</td>
                  <td>{inv.client_name || '—'}</td>
                  <td className="text-amount text-bold">{fmt(inv.total)} <span className="currency">TND</span></td>
                  <td className="text-amount" style={{ color: 'var(--success)' }}>{fmt(inv.amount_paid)}</td>
                  <td className="text-amount" style={{ color: inv.balance_due > 0 ? 'var(--danger)' : 'var(--success)' }}>{fmt(inv.balance_due)}</td>
                  <td>
                    <select className="form-input" value={inv.status} onChange={e => handleStatusChange(inv.id, e.target.value)} style={{ padding: '4px 8px', fontSize: 12, width: 'auto', minWidth: 110 }}>
                      <option value="brouillon">Brouillon</option><option value="envoyee">Reçue</option><option value="payee">Payée</option><option value="partiellement_payee">Partielle</option><option value="en_retard">En retard</option><option value="annulee">Annulée</option>
                    </select>
                  </td>
                  <td>
                    <button className="btn btn-icon" onClick={() => handleDownload(inv.id, 'pdf')} title="Télécharger PDF" style={{ color: 'var(--primary)' }}><FiDownload /></button>
                    <button className="btn btn-icon" onClick={() => handleDownload(inv.id, 'xml')} title="Télécharger XML" style={{ color: '#f59e0b' }}><FiCode /></button>
                    <button className="btn btn-icon" onClick={() => handleDelete(inv.id)} style={{ color: 'var(--danger)' }}><FiTrash2 /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 550 }}>
            <div className="modal-header"><h3 className="modal-title">Nouvelle facture d&apos;achat</h3><button className="btn btn-icon" onClick={() => setShowModal(false)}><FiX /></button></div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Fournisseur</label>
                  <select className="form-input" value={form.supplier_id} onChange={e => setForm({ ...form, supplier_id: e.target.value })}>
                    <option value="">— Sélectionner un fournisseur —</option>
                    {suppliers.map((s: any) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div className="form-row">
                  <div className="form-group"><label>Date</label><input className="form-input" type="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} /></div>
                  <div className="form-group"><label>Échéance</label><input className="form-input" type="date" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })} /></div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', borderRadius: 12, padding: 20, marginTop: 16 }}>
                  <div className="form-group">
                    <label style={{ fontWeight: 700, fontSize: 15 }}>Montant Total HT (TND) *</label>
                    <input className="form-input" type="number" step="0.001" min="0" value={form.montant_ht || ''} onChange={e => setForm({ ...form, montant_ht: parseFloat(e.target.value) || 0 })} placeholder="0.000" style={{ fontSize: 18, fontWeight: 700, textAlign: 'right' }} required />
                  </div>

                  <div className="form-row" style={{ marginTop: 12 }}>
                    <div className="form-group">
                      <label>Taux TVA</label>
                      <select className="form-input" value={form.tva_rate} onChange={e => setForm({ ...form, tva_rate: parseFloat(e.target.value) })}>
                        <option value={19}>19%</option>
                        <option value={13}>13%</option>
                        <option value={7}>7%</option>
                        <option value={0}>0% (Exonéré)</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Timbre fiscal (TND)</label>
                      <input className="form-input" type="number" step="0.1" value={form.timbre_fiscal} onChange={e => setForm({ ...form, timbre_fiscal: parseFloat(e.target.value) || 0 })} style={{ textAlign: 'right' }} />
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 12 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 14 }}>
                      <input type="checkbox" checked={form.fodec} onChange={e => setForm({ ...form, fodec: e.target.checked })} style={{ width: 18, height: 18 }} />
                      Appliquer FODEC
                    </label>
                    {form.fodec && (
                      <select className="form-input" value={form.fodec_rate} onChange={e => setForm({ ...form, fodec_rate: parseFloat(e.target.value) })} style={{ width: 80 }}>
                        <option value={1}>1%</option>
                        <option value={0.5}>0.5%</option>
                      </select>
                    )}
                  </div>
                </div>

                {/* Récapitulatif */}
                <div style={{ marginTop: 16, borderTop: '2px solid var(--border)', paddingTop: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: 14 }}><span>Montant HT</span><strong>{fmt(form.montant_ht)} TND</strong></div>
                  {form.fodec && <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: 14 }}><span>FODEC ({form.fodec_rate}%)</span><strong>{fmt(fodecAmount)} TND</strong></div>}
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: 14 }}><span>TVA ({form.tva_rate}%)</span><strong>{fmt(tvaAmount)} TND</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: 14 }}><span>Timbre fiscal</span><strong>{fmt(form.timbre_fiscal)} TND</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderTop: '2px solid var(--primary)', marginTop: 8 }}>
                    <span style={{ color: 'var(--primary)', fontWeight: 700, fontSize: 16 }}>Net à payer</span>
                    <span style={{ color: 'var(--primary)', fontWeight: 700, fontSize: 18 }}>{fmt(netAPayer)} TND</span>
                  </div>
                </div>

                <div className="form-group" style={{ marginTop: 12 }}><label>Notes</label><textarea className="form-input" rows={2} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} style={{ resize: 'vertical' }} /></div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>Créer la facture d&apos;achat</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
