'use client';
import { useState, useEffect } from 'react';
import { productsAPI } from '@/lib/api';
import toast from 'react-hot-toast';
import { FiPlus, FiSearch, FiEdit2, FiTrash2, FiX, FiPackage } from 'react-icons/fi';

export default function ProduitsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [form, setForm] = useState({ reference: '', name: '', description: '', category: '', unit: 'unité', unit_price: 0, purchase_price: 0, tva_rate: 19.0, fodec_rate: 0, stock_quantity: 0, min_stock: 0, is_service: false });

  const load = () => { productsAPI.list({ search: search || undefined }).then(r => { setProducts(r.data); setLoading(false); }).catch(() => setLoading(false)); };
  useEffect(() => { load(); }, [search]);

  const resetForm = () => setForm({ reference: '', name: '', description: '', category: '', unit: 'unité', unit_price: 0, purchase_price: 0, tva_rate: 19.0, fodec_rate: 0, stock_quantity: 0, min_stock: 0, is_service: false });
  const openCreate = () => { resetForm(); setEditing(null); setShowModal(true); };
  const openEdit = (p: any) => { setForm({ reference: p.reference || '', name: p.name, description: p.description || '', category: p.category || '', unit: p.unit, unit_price: p.unit_price, purchase_price: p.purchase_price, tva_rate: p.tva_rate, fodec_rate: p.fodec_rate, stock_quantity: p.stock_quantity, min_stock: p.min_stock, is_service: p.is_service }); setEditing(p); setShowModal(true); };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) { await productsAPI.update(editing.id, form); toast.success('Produit modifié'); }
      else { await productsAPI.create(form); toast.success('Produit créé'); }
      setShowModal(false); load();
    } catch (err: any) { toast.error(err.response?.data?.detail || 'Erreur'); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer ce produit ?')) return;
    try { await productsAPI.delete(id); toast.success('Produit supprimé'); load(); } catch { toast.error('Erreur'); }
  };

  const update = (f: string, v: any) => setForm(p => ({ ...p, [f]: v }));
  const fmt = (n: number) => new Intl.NumberFormat('fr-TN', { minimumFractionDigits: 3 }).format(n);

  return (
    <>
      <div className="toolbar">
        <div className="toolbar-left"><div className="search-input"><FiSearch /><input placeholder="Rechercher un produit..." value={search} onChange={e => setSearch(e.target.value)} /></div></div>
        <div className="toolbar-right"><button className="btn btn-primary btn-sm" onClick={openCreate} style={{ width: 'auto' }}><FiPlus /> Nouveau produit</button></div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead><tr><th>Réf.</th><th>Nom</th><th>Catégorie</th><th>Prix HT</th><th>TVA</th><th>Stock</th><th></th></tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={7}><div className="loading-spinner" /></td></tr> :
               products.length === 0 ? (
                <tr><td colSpan={7}><div className="empty-state"><FiPackage style={{ fontSize: 48 }} /><h3>Aucun produit</h3><p>Ajoutez votre premier produit ou service</p></div></td></tr>
              ) : products.map(p => (
                <tr key={p.id}>
                  <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{p.reference || '—'}</td>
                  <td style={{ fontWeight: 600 }}>{p.name}</td>
                  <td>{p.category || '—'}</td>
                  <td className="text-amount">{fmt(p.unit_price)} <span className="currency">TND</span></td>
                  <td>{p.tva_rate}%</td>
                  <td>
                    {p.is_service ? <span className="badge badge-info">Service</span> :
                     <span className={`badge ${p.stock_quantity <= p.min_stock ? 'badge-danger' : 'badge-success'}`}>{p.stock_quantity}</span>}
                  </td>
                  <td>
                    <button className="btn btn-icon" onClick={() => openEdit(p)}><FiEdit2 /></button>
                    <button className="btn btn-icon" onClick={() => handleDelete(p.id)} style={{ color: 'var(--danger)' }}><FiTrash2 /></button>
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
            <div className="modal-header"><h3 className="modal-title">{editing ? 'Modifier produit' : 'Nouveau produit'}</h3><button className="btn btn-icon" onClick={() => setShowModal(false)}><FiX /></button></div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group"><label>Référence</label><input className="form-input" value={form.reference} onChange={e => update('reference', e.target.value)} /></div>
                  <div className="form-group"><label>Nom *</label><input className="form-input" value={form.name} onChange={e => update('name', e.target.value)} required /></div>
                </div>
                <div className="form-group"><label>Description</label><textarea className="form-input" rows={2} value={form.description} onChange={e => update('description', e.target.value)} style={{ resize: 'vertical' }} /></div>
                <div className="form-row">
                  <div className="form-group"><label>Catégorie</label><input className="form-input" value={form.category} onChange={e => update('category', e.target.value)} /></div>
                  <div className="form-group"><label>Unité</label>
                    <select className="form-input" value={form.unit} onChange={e => update('unit', e.target.value)}>
                      <option value="unité">Unité</option><option value="kg">Kg</option><option value="m">Mètre</option><option value="l">Litre</option><option value="h">Heure</option><option value="jour">Jour</option>
                    </select>
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group"><label>Prix de vente HT *</label><input className="form-input" type="number" step="0.001" value={form.unit_price} onChange={e => update('unit_price', parseFloat(e.target.value) || 0)} required /></div>
                  <div className="form-group"><label>Prix d&apos;achat HT</label><input className="form-input" type="number" step="0.001" value={form.purchase_price} onChange={e => update('purchase_price', parseFloat(e.target.value) || 0)} /></div>
                </div>
                <div className="form-row">
                  <div className="form-group"><label>TVA (%)</label>
                    <select className="form-input" value={form.tva_rate} onChange={e => update('tva_rate', parseFloat(e.target.value))}>
                      <option value={19}>19%</option><option value={13}>13%</option><option value={7}>7%</option><option value={0}>0%</option>
                    </select>
                  </div>
                  <div className="form-group"><label>FODEC (%)</label><input className="form-input" type="number" step="0.01" value={form.fodec_rate} onChange={e => update('fodec_rate', parseFloat(e.target.value) || 0)} /></div>
                </div>
                <div className="form-group" style={{ marginTop: 8 }}>
                  <label className="form-checkbox"><input type="checkbox" checked={form.is_service} onChange={e => update('is_service', e.target.checked)} /> C&apos;est un service (pas de gestion de stock)</label>
                </div>
                {!form.is_service && (
                  <div className="form-row">
                    <div className="form-group"><label>Stock initial</label><input className="form-input" type="number" value={form.stock_quantity} onChange={e => update('stock_quantity', parseInt(e.target.value) || 0)} /></div>
                    <div className="form-group"><label>Stock minimum</label><input className="form-input" type="number" value={form.min_stock} onChange={e => update('min_stock', parseInt(e.target.value) || 0)} /></div>
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
    </>
  );
}
