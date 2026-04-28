'use client';
import { useState, useEffect } from 'react';
import { invoicesAPI, suppliersAPI, productsAPI, getErrorMessage } from '@/lib/api';
import toast from 'react-hot-toast';
import { FiPlus, FiSearch, FiTrash2, FiX, FiShoppingCart, FiDownload, FiCode } from 'react-icons/fi';
import Cookies from 'js-cookie';

const statusMap: Record<string, { label: string; className: string }> = {
  brouillon: { label: 'Brouillon', className: 'badge-default' },
  envoyee: { label: 'Reçue', className: 'badge-info' },
  payee: { label: 'Payée', className: 'badge-success' },
  partiellement_payee: { label: 'Partielle', className: 'badge-warning' },
  en_retard: { label: 'En retard', className: 'badge-danger' },
};

export default function AchatsPage() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<any>({
    supplier_id: '', date: new Date().toISOString().split('T')[0], due_date: '', notes: '', timbre_fiscal: 1.0,
    items: [{ product_id: '', description: '', quantity: 1, unit: 'unité', unit_price: 0, discount_percent: 0, tva_rate: 19, fodec_rate: 0 }],
  });

  const load = () => {
    invoicesAPI.list({ invoice_type: 'facture_achat', search: search || undefined }).then(r => { setInvoices(r.data); setLoading(false); }).catch(() => setLoading(false));
  };
  useEffect(() => { load(); }, [search]);
  useEffect(() => {
    suppliersAPI.list().then(r => setSuppliers(r.data)).catch(() => {});
    productsAPI.list().then(r => setProducts(r.data)).catch(() => {});
  }, []);

  const fmt = (n: number) => new Intl.NumberFormat('fr-TN', { minimumFractionDigits: 3 }).format(n);

  const calcItemTotal = (item: any) => {
    const st = item.quantity * item.unit_price;
    const disc = st * (item.discount_percent / 100);
    const stAfter = st - disc;
    const fodec = stAfter * (item.fodec_rate / 100);
    const tva = (stAfter + fodec) * (item.tva_rate / 100);
    return stAfter + fodec + tva;
  };

  const totalHT = form.items.reduce((s: number, i: any) => s + (i.quantity * i.unit_price * (1 - i.discount_percent / 100)), 0);
  const totalTVA = form.items.reduce((s: number, i: any) => {
    const st = i.quantity * i.unit_price * (1 - i.discount_percent / 100);
    const fodec = st * (i.fodec_rate / 100);
    return s + (st + fodec) * (i.tva_rate / 100);
  }, 0);
  const netAPayer = totalHT + totalTVA + (form.timbre_fiscal || 0);

  const updateItem = (idx: number, field: string, value: any) => {
    const newItems = [...form.items];
    newItems[idx] = { ...newItems[idx], [field]: value };
    if (field === 'product_id' && value) {
      const prod = products.find((p: any) => p.id === value);
      if (prod) { newItems[idx].description = prod.name; newItems[idx].unit_price = prod.purchase_price || prod.unit_price; newItems[idx].tva_rate = prod.tva_rate; newItems[idx].fodec_rate = prod.fodec_rate; }
    }
    setForm({ ...form, items: newItems });
  };
  const addItem = () => setForm({ ...form, items: [...form.items, { product_id: '', description: '', quantity: 1, unit: 'unité', unit_price: 0, discount_percent: 0, tva_rate: 19, fodec_rate: 0 }] });
  const removeItem = (idx: number) => { if (form.items.length > 1) setForm({ ...form, items: form.items.filter((_: any, i: number) => i !== idx) }); };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.items.length === 0 || !form.items[0].description) { toast.error('Ajoutez au moins un article'); return; }
    try {
      const payload = {
        ...form,
        invoice_type: 'facture_achat',
        client_id: null,
        supplier_id: form.supplier_id || null,
        due_date: form.due_date || null,
        items: form.items.map((item: any) => ({ ...item, product_id: item.product_id || null })),
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
    const url = format === 'pdf' ? invoicesAPI.downloadPdf(id) : invoicesAPI.downloadXml(id);
    window.open(`${url}?token=${token}`, '_blank');
  };

  const openCreate = () => {
    setForm({
      supplier_id: '', date: new Date().toISOString().split('T')[0], due_date: '', notes: '', timbre_fiscal: 1.0,
      items: [{ product_id: '', description: '', quantity: 1, unit: 'unité', unit_price: 0, discount_percent: 0, tva_rate: 19, fodec_rate: 0 }],
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
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 900 }}>
            <div className="modal-header"><h3 className="modal-title">Nouvelle facture d&apos;achat</h3><button className="btn btn-icon" onClick={() => setShowModal(false)}><FiX /></button></div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group">
                    <label>Fournisseur</label>
                    <select className="form-input" value={form.supplier_id} onChange={e => setForm({ ...form, supplier_id: e.target.value })}>
                      <option value="">— Aucun —</option>
                      {suppliers.map((s: any) => <option key={s.id} value={s.id}>{s.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group"><label>Date</label><input className="form-input" type="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} /></div>
                  <div className="form-group"><label>Échéance</label><input className="form-input" type="date" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })} /></div>
                </div>

                <h4 style={{ marginTop: 16, marginBottom: 8 }}>Articles</h4>
                <div className="table-container" style={{ maxHeight: 250, overflowY: 'auto' }}>
                  <table style={{ fontSize: 13 }}>
                    <thead><tr><th>PRODUIT</th><th>DESCRIPTION</th><th>QTÉ</th><th>PRIX HT</th><th>TVA%</th><th>TOTAL</th><th></th></tr></thead>
                    <tbody>
                      {form.items.map((item: any, idx: number) => (
                        <tr key={idx}>
                          <td><select className="form-input" value={item.product_id} onChange={e => updateItem(idx, 'product_id', e.target.value)} style={{ fontSize: 12, padding: '4px' }}><option value="">— Libre —</option>{products.map((p: any) => <option key={p.id} value={p.id}>{p.name}</option>)}</select></td>
                          <td><input className="form-input" value={item.description} onChange={e => updateItem(idx, 'description', e.target.value)} style={{ fontSize: 12 }} /></td>
                          <td><input className="form-input" type="number" min="1" value={item.quantity} onChange={e => updateItem(idx, 'quantity', parseFloat(e.target.value) || 1)} style={{ width: 60, fontSize: 12 }} /></td>
                          <td><input className="form-input" type="number" step="0.001" value={item.unit_price} onChange={e => updateItem(idx, 'unit_price', parseFloat(e.target.value) || 0)} style={{ width: 90, fontSize: 12 }} /></td>
                          <td><select className="form-input" value={item.tva_rate} onChange={e => updateItem(idx, 'tva_rate', parseFloat(e.target.value))} style={{ width: 70, fontSize: 12 }}><option value={19}>19%</option><option value={13}>13%</option><option value={7}>7%</option><option value={0}>0%</option></select></td>
                          <td style={{ fontWeight: 600, whiteSpace: 'nowrap' }}>{fmt(calcItemTotal(item))}</td>
                          <td><button type="button" className="btn btn-icon" onClick={() => removeItem(idx)} style={{ color: 'var(--danger)', fontSize: 12 }}><FiTrash2 /></button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <button type="button" className="btn btn-secondary btn-sm" onClick={addItem} style={{ marginTop: 8, width: 'auto' }}><FiPlus /> Ajouter un article</button>

                <div style={{ marginTop: 16, borderTop: '1px solid var(--border)', paddingTop: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span>Total HT</span><strong>{fmt(totalHT)} TND</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span>TVA</span><strong>{fmt(totalTVA)} TND</strong></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', alignItems: 'center' }}><span>Timbre fiscal</span><input className="form-input" type="number" step="0.1" value={form.timbre_fiscal} onChange={e => setForm({ ...form, timbre_fiscal: parseFloat(e.target.value) || 0 })} style={{ width: 80, textAlign: 'right' }} /></div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderTop: '2px solid var(--primary)', marginTop: 8 }}><span style={{ color: 'var(--primary)', fontWeight: 700, fontSize: 16 }}>Net à payer</span><span style={{ color: 'var(--primary)', fontWeight: 700, fontSize: 16 }}>{fmt(netAPayer)} TND</span></div>
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
