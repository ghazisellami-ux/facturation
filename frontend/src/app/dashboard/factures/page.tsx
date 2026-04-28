'use client';
import { useState, useEffect } from 'react';
import { invoicesAPI, clientsAPI, productsAPI, getErrorMessage } from '@/lib/api';
import toast from 'react-hot-toast';
import { FiPlus, FiSearch, FiEdit2, FiTrash2, FiX, FiFileText, FiEye, FiDownload, FiCode } from 'react-icons/fi';
import Cookies from 'js-cookie';
import Link from 'next/link';

const statusMap: Record<string, { label: string; className: string }> = {
  brouillon: { label: 'Brouillon', className: 'badge-default' },
  envoyee: { label: 'Envoyée', className: 'badge-info' },
  payee: { label: 'Payée', className: 'badge-success' },
  partiellement_payee: { label: 'Partielle', className: 'badge-warning' },
  en_retard: { label: 'En retard', className: 'badge-danger' },
  annulee: { label: 'Annulée', className: 'badge-default' },
};

interface InvoiceItem { product_id?: string; description: string; quantity: number; unit: string; unit_price: number; discount_percent: number; tva_rate: number; fodec_rate: number; }

export default function FacturesPage() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ client_id: '', date: '', due_date: '', notes: '', timbre_fiscal: 1.0, items: [{ product_id: '', description: '', quantity: 1, unit: 'unité', unit_price: 0, discount_percent: 0, tva_rate: 19, fodec_rate: 0 }] as InvoiceItem[] });
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); setForm(f => ({ ...f, date: new Date().toISOString().split('T')[0] })); }, []);

  const load = () => {
    Promise.all([
      invoicesAPI.list({ invoice_type: 'facture', search: search || undefined }),
      clientsAPI.list(), productsAPI.list()
    ]).then(([inv, cli, pro]) => { setInvoices(inv.data); setClients(cli.data); setProducts(pro.data); setLoading(false); }).catch(() => setLoading(false));
  };
  useEffect(() => { load(); }, [search]);

  const fmt = (n: number) => new Intl.NumberFormat('fr-TN', { minimumFractionDigits: 3, maximumFractionDigits: 3 }).format(n);

  const addItem = () => setForm(p => ({ ...p, items: [...p.items, { product_id: '', description: '', quantity: 1, unit: 'unité', unit_price: 0, discount_percent: 0, tva_rate: 19, fodec_rate: 0 }] }));
  const removeItem = (i: number) => setForm(p => ({ ...p, items: p.items.filter((_, idx) => idx !== i) }));
  const updateItem = (i: number, f: string, v: any) => setForm(p => ({ ...p, items: p.items.map((item, idx) => idx === i ? { ...item, [f]: v } : item) }));

  const selectProduct = (i: number, productId: string) => {
    const product = products.find(p => p.id === productId);
    if (product) {
      setForm(p => ({ ...p, items: p.items.map((item, idx) => idx === i ? { ...item, product_id: productId, description: product.name, unit_price: product.unit_price, unit: product.unit, tva_rate: product.tva_rate, fodec_rate: product.fodec_rate } : item) }));
    }
  };

  // Calculate totals
  const calcItemTotal = (item: InvoiceItem) => {
    const sub = item.quantity * item.unit_price;
    const disc = sub * (item.discount_percent / 100);
    const afterDisc = sub - disc;
    const fodec = afterDisc * (item.fodec_rate / 100);
    const tva = (afterDisc + fodec) * (item.tva_rate / 100);
    return { subtotal: afterDisc, fodec, tva, total: afterDisc + fodec + tva };
  };

  const totals = form.items.reduce((acc, item) => {
    const t = calcItemTotal(item);
    return { subtotal: acc.subtotal + t.subtotal, tva: acc.tva + t.tva, fodec: acc.fodec + t.fodec };
  }, { subtotal: 0, tva: 0, fodec: 0 });
  const grandTotal = totals.subtotal + totals.tva + totals.fodec + form.timbre_fiscal;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.items.length === 0 || !form.items[0].description) { toast.error('Ajoutez au moins un article'); return; }
    try {
      // Clean up empty strings to null for optional UUID fields
      const payload = {
        ...form,
        invoice_type: 'facture',
        client_id: form.client_id || null,
        due_date: form.due_date || null,
        items: form.items.map(item => ({
          ...item,
          product_id: item.product_id || null,
        })),
      };
      await invoicesAPI.create(payload);
      toast.success('Facture créée !');
      setShowModal(false); load();
    } catch (err: any) { toast.error(getErrorMessage(err, 'Erreur lors de la création')); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer cette facture ?')) return;
    try { await invoicesAPI.delete(id); toast.success('Facture supprimée'); load(); } catch { toast.error('Erreur'); }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try { await invoicesAPI.update(id, { status }); toast.success('Statut mis à jour'); load(); } catch { toast.error('Erreur'); }
  };

  const handleDownload = (id: string, format: 'pdf' | 'xml') => {
    const token = Cookies.get('access_token');
    if (!token) { toast.error('Veuillez vous reconnecter'); return; }
    window.open(`http://localhost:8001/api/invoices/${id}/${format}?token=${token}`, '_blank');
  };

  return (
    <>
      <div className="toolbar">
        <div className="toolbar-left"><div className="search-input"><FiSearch /><input placeholder="Rechercher une facture..." value={search} onChange={e => setSearch(e.target.value)} /></div></div>
        <div className="toolbar-right">
          <button className="btn btn-primary btn-sm" onClick={() => { setForm({ client_id: '', date: new Date().toISOString().split('T')[0], due_date: '', notes: '', timbre_fiscal: 1.0, items: [{ product_id: '', description: '', quantity: 1, unit: 'unité', unit_price: 0, discount_percent: 0, tva_rate: 19, fodec_rate: 0 }] }); setShowModal(true); }} style={{ width: 'auto' }}><FiPlus /> Nouvelle facture</button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead><tr><th>Réf.</th><th>Date</th><th>Client</th><th>Total TTC</th><th>Payé</th><th>Reste</th><th>Statut</th><th></th></tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={8}><div className="loading-spinner" /></td></tr> :
               invoices.length === 0 ? (
                <tr><td colSpan={8}><div className="empty-state"><FiFileText style={{ fontSize: 48 }} /><h3>Aucune facture</h3><p>Créez votre première facture</p></div></td></tr>
              ) : invoices.map(inv => (
                <tr key={inv.id}>
                  <td style={{ fontWeight: 700, color: 'var(--primary)' }}>{inv.reference}</td>
                  <td>{new Date(inv.date).toLocaleDateString('fr-FR')}</td>
                  <td>{inv.client_name || '—'}</td>
                  <td className="text-amount text-bold">{fmt(inv.total)} <span className="currency">TND</span></td>
                  <td className="text-amount" style={{ color: 'var(--success)' }}>{fmt(inv.amount_paid)}</td>
                  <td className="text-amount" style={{ color: inv.balance_due > 0 ? 'var(--danger)' : 'var(--success)' }}>{fmt(inv.balance_due)}</td>
                  <td>
                    <select className="form-input" value={inv.status} onChange={e => handleStatusChange(inv.id, e.target.value)} style={{ padding: '4px 8px', fontSize: 12, width: 'auto', minWidth: 110 }}>
                      <option value="brouillon">Brouillon</option><option value="envoyee">Envoyée</option><option value="payee">Payée</option><option value="partiellement_payee">Partielle</option><option value="en_retard">En retard</option><option value="annulee">Annulée</option>
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
            <div className="modal-header"><h3 className="modal-title">Nouvelle facture</h3><button className="btn btn-icon" onClick={() => setShowModal(false)}><FiX /></button></div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group"><label>Client</label>
                    <select className="form-input" value={form.client_id} onChange={e => setForm(p => ({ ...p, client_id: e.target.value }))}>
                      <option value="">— Sélectionner —</option>
                      {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group"><label>Date</label><input className="form-input" type="date" value={form.date} onChange={e => setForm(p => ({ ...p, date: e.target.value }))} /></div>
                  <div className="form-group"><label>Échéance</label><input className="form-input" type="date" value={form.due_date} onChange={e => setForm(p => ({ ...p, due_date: e.target.value }))} /></div>
                </div>

                <h4 style={{ margin: '20px 0 12px', fontSize: 14, fontWeight: 700 }}>Articles</h4>
                <div className="table-container">
                  <table className="invoice-items-table">
                    <thead><tr><th>Produit</th><th>Description</th><th>Qté</th><th>Prix HT</th><th>TVA%</th><th>Total</th><th></th></tr></thead>
                    <tbody>
                      {form.items.map((item, i) => (
                        <tr key={i}>
                          <td><select className="form-input" value={item.product_id} onChange={e => selectProduct(i, e.target.value)} style={{ minWidth: 120, padding: '6px 8px', fontSize: 13 }}>
                            <option value="">— Libre —</option>{products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                          </select></td>
                          <td><input className="form-input" value={item.description} onChange={e => updateItem(i, 'description', e.target.value)} style={{ padding: '6px 8px', fontSize: 13 }} required /></td>
                          <td><input className="form-input" type="number" min="0.001" step="0.001" value={item.quantity} onChange={e => updateItem(i, 'quantity', parseFloat(e.target.value) || 0)} style={{ width: 70, padding: '6px 8px', fontSize: 13 }} /></td>
                          <td><input className="form-input" type="number" step="0.001" value={item.unit_price} onChange={e => updateItem(i, 'unit_price', parseFloat(e.target.value) || 0)} style={{ width: 100, padding: '6px 8px', fontSize: 13 }} /></td>
                          <td><select className="form-input" value={item.tva_rate} onChange={e => updateItem(i, 'tva_rate', parseFloat(e.target.value))} style={{ width: 70, padding: '6px 8px', fontSize: 13 }}>
                            <option value={19}>19%</option><option value={13}>13%</option><option value={7}>7%</option><option value={0}>0%</option>
                          </select></td>
                          <td className="text-amount text-bold" style={{ minWidth: 100 }}>{fmt(calcItemTotal(item).total)}</td>
                          <td>{form.items.length > 1 && <button type="button" className="btn btn-icon" onClick={() => removeItem(i)} style={{ color: 'var(--danger)' }}><FiTrash2 /></button>}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <button type="button" className="btn btn-secondary btn-sm" onClick={addItem} style={{ marginTop: 12 }}><FiPlus /> Ajouter un article</button>

                <div className="invoice-totals" style={{ marginTop: 24 }}>
                  <table className="invoice-totals-table">
                    <tbody>
                      <tr><td>Total HT</td><td>{fmt(totals.subtotal)} TND</td></tr>
                      {totals.fodec > 0 && <tr><td>FODEC</td><td>{fmt(totals.fodec)} TND</td></tr>}
                      <tr><td>TVA</td><td>{fmt(totals.tva)} TND</td></tr>
                      <tr><td>Timbre fiscal</td><td>
                        <input className="form-input" type="number" step="0.001" value={form.timbre_fiscal} onChange={e => setForm(p => ({ ...p, timbre_fiscal: parseFloat(e.target.value) || 0 }))} style={{ width: 80, padding: '4px 8px', fontSize: 13, textAlign: 'right' }} />
                      </td></tr>
                      <tr className="total-row"><td>Net à payer</td><td>{fmt(grandTotal)} TND</td></tr>
                    </tbody>
                  </table>
                </div>

                <div className="form-group" style={{ marginTop: 20 }}><label>Notes</label><textarea className="form-input" rows={2} value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} style={{ resize: 'vertical' }} /></div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>Créer la facture</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
