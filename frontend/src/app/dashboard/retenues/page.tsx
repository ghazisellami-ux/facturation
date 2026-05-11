'use client';
import { useState, useEffect } from 'react';
import { withholdingsAPI, clientsAPI, suppliersAPI, getErrorMessage } from '@/lib/api';
import toast from 'react-hot-toast';
import { FiPlus, FiSearch, FiTrash2, FiFileText, FiX, FiPercent, FiFilter, FiDownload, FiCode } from 'react-icons/fi';
import Cookies from 'js-cookie';

const MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];

export default function RetenuesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<'emise' | 'recue'>('emise');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedClient, setSelectedClient] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [exportYear, setExportYear] = useState(new Date().getFullYear());
  const [exportMonth, setExportMonth] = useState(0);
  const [form, setForm] = useState({
    type: 'emise' as 'emise' | 'recue',
    rate: 1,
    base_amount: 0,
    date: new Date().toISOString().split('T')[0],
    reference: '',
    client_id: '',
    supplier_id: '',
    beneficiary_name: '',
    beneficiary_tax_id: '',
    notes: '',
  });

  const load = () => {
    setLoading(true);
    const params: any = { type: activeTab, search: search || undefined, year: selectedYear };
    if (selectedClient) params.client_id = selectedClient;
    Promise.all([
      withholdingsAPI.list(params),
      clientsAPI.list(),
      suppliersAPI.list(),
    ]).then(([wh, cli, sup]) => {
      setItems(wh.data.data);
      setClients(cli.data);
      setSuppliers(sup.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  };
  useEffect(() => { load(); }, [activeTab, search, selectedYear, selectedClient]);

  const fmt = (n: number) => new Intl.NumberFormat('fr-TN', { minimumFractionDigits: 3, maximumFractionDigits: 3 }).format(n);

  const getWhDownloadUrl = (id: string, format: 'pdf' | 'xml') => {
    const token = Cookies.get('access_token');
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    return token ? `${apiUrl}/api/withholdings/${id}/${format}?token=${token}` : '';
  };

  const taxAmount = form.base_amount * form.rate / 100;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await withholdingsAPI.create({
        ...form,
        type: activeTab,
        client_id: form.client_id || null,
        supplier_id: form.supplier_id || null,
      });
      toast.success('Retenue créée !');
      setShowModal(false);
      load();
    } catch (err: any) { toast.error(getErrorMessage(err, 'Erreur')); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer cette retenue ?')) return;
    try { await withholdingsAPI.delete(id); toast.success('Retenue supprimée'); load(); } catch { toast.error('Erreur'); }
  };

  const openModal = () => {
    setForm({
      type: activeTab,
      rate: 1,
      base_amount: 0,
      date: new Date().toISOString().split('T')[0],
      reference: '',
      client_id: '',
      supplier_id: '',
      beneficiary_name: '',
      beneficiary_tax_id: '',
      notes: '',
    });
    setShowModal(true);
  };

  const totalBase = items.reduce((s, i) => s + (i.base_amount || 0), 0);
  const totalTax = items.reduce((s, i) => s + (i.tax_amount || 0), 0);

  return (
    <>
      <div className="toolbar">
        <div className="toolbar-left">
          <div className="search-input"><FiSearch /><input placeholder="Rechercher..." value={search} onChange={e => setSearch(e.target.value)} /></div>
        </div>
        <div className="toolbar-right" style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowExport(true)} style={{ width: 'auto' }}><FiDownload /> Exporter</button>
          <button className="btn btn-primary btn-sm" onClick={openModal} style={{ width: 'auto' }}><FiPlus /> Nouvelle retenue</button>
        </div>
      </div>

      {/* Onglets */}
      <div style={{ display: 'flex', gap: 0, marginBottom: 20 }}>
        <button
          onClick={() => setActiveTab('emise')}
          style={{
            flex: 1, padding: '12px 24px', fontSize: 14, fontWeight: 600, cursor: 'pointer', border: 'none',
            background: activeTab === 'emise' ? 'var(--primary)' : 'var(--bg-card)',
            color: activeTab === 'emise' ? '#fff' : 'var(--text-secondary)',
            borderRadius: '10px 0 0 10px', transition: 'all .2s',
          }}
        >
          Retenues Émises
          <span style={{ display: 'block', fontSize: 11, fontWeight: 400, opacity: 0.8, marginTop: 2 }}>
            Retenues que vous effectuez sur vos paiements
          </span>
        </button>
        <button
          onClick={() => setActiveTab('recue')}
          style={{
            flex: 1, padding: '12px 24px', fontSize: 14, fontWeight: 600, cursor: 'pointer', border: 'none',
            background: activeTab === 'recue' ? 'var(--primary)' : 'var(--bg-card)',
            color: activeTab === 'recue' ? '#fff' : 'var(--text-secondary)',
            borderRadius: '0 10px 10px 0', transition: 'all .2s',
          }}
        >
          Retenues Reçues
          <span style={{ display: 'block', fontSize: 11, fontWeight: 400, opacity: 0.8, marginTop: 2 }}>
            Retenues effectuées par vos clients sur vous
          </span>
        </button>
      </div>

      <div className="card" style={{ padding: '12px 16px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
        <FiFilter style={{ color: 'var(--text-secondary)' }} />
        <select className="form-input" value={selectedYear} onChange={e => setSelectedYear(Number(e.target.value))} style={{ padding: '5px 10px', fontSize: 13, width: 'auto', minWidth: 90 }}>
          {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map(y => <option key={y} value={y}>{y}</option>)}
        </select>
        <select className="form-input" value={selectedClient} onChange={e => setSelectedClient(e.target.value)} style={{ padding: '5px 10px', fontSize: 13, width: 'auto', minWidth: 160 }}>
          <option value="">Tous les clients</option>
          {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        {(selectedYear !== new Date().getFullYear() || selectedClient) && <button className="btn btn-sm btn-secondary" onClick={() => { setSelectedYear(new Date().getFullYear()); setSelectedClient(''); }} style={{ fontSize: 11, padding: '4px 12px' }}>Réinitialiser</button>}
      </div>

      {/* Totaux */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
        <div className="card" style={{ flex: 1, padding: '16px 20px' }}>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>Total base HT</div>
          <div style={{ fontSize: 20, fontWeight: 700 }}>{fmt(totalBase)} <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>TND</span></div>
        </div>
        <div className="card" style={{ flex: 1, padding: '16px 20px' }}>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>Total retenu</div>
          <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--primary)' }}>{fmt(totalTax)} <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>TND</span></div>
        </div>
        <div className="card" style={{ flex: 1, padding: '16px 20px' }}>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>Nombre</div>
          <div style={{ fontSize: 20, fontWeight: 700 }}>{items.length}</div>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Référence</th>
                <th>{activeTab === 'emise' ? 'Fournisseur' : 'Client'}</th>
                <th>MF</th>
                <th>Taux</th>
                <th>Base HT</th>
                <th>Montant retenu</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {loading ? <tr><td colSpan={8}><div className="loading-spinner" /></td></tr> :
               items.length === 0 ? (
                <tr><td colSpan={8}><div className="empty-state"><FiPercent style={{ fontSize: 48 }} /><h3>Aucune retenue {activeTab === 'emise' ? 'émise' : 'reçue'}</h3><p>Ajoutez votre première retenue à la source</p></div></td></tr>
              ) : items.map(w => (
                <tr key={w.id}>
                  <td>{new Date(w.date).toLocaleDateString('fr-FR')}</td>
                  <td style={{ fontWeight: 600 }}>{w.reference || '—'}</td>
                  <td>{w.beneficiary_name || '—'}</td>
                  <td style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{w.beneficiary_tax_id || '—'}</td>
                  <td><span className="badge badge-info">{w.rate}%</span></td>
                  <td className="text-amount">{fmt(w.base_amount)}</td>
                  <td className="text-amount text-bold" style={{ color: 'var(--primary)' }}>{fmt(w.tax_amount)} <span className="currency">TND</span></td>
                  <td>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <a href={getWhDownloadUrl(w.id, 'pdf')} className="btn btn-icon" title="Télécharger PDF" style={{ color: 'var(--primary)' }}><FiDownload /></a>
                      <a href={getWhDownloadUrl(w.id, 'xml')} className="btn btn-icon" title="Télécharger XML" style={{ color: 'var(--success)' }}><FiCode /></a>
                      <button className="btn btn-icon" onClick={() => handleDelete(w.id)} style={{ color: 'var(--danger)' }}><FiTrash2 /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <div className="modal-header">
              <h3 className="modal-title">Nouvelle retenue {activeTab === 'emise' ? 'émise' : 'reçue'}</h3>
              <button className="btn btn-icon" onClick={() => setShowModal(false)}><FiX /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {/* Taux */}
                <div className="form-group">
                  <label>Taux de retenue</label>
                  <div style={{ display: 'flex', gap: 12 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px', borderRadius: 8, border: form.rate === 1 ? '2px solid var(--primary)' : '2px solid var(--border)', cursor: 'pointer', background: form.rate === 1 ? 'var(--primary-light)' : 'transparent', flex: 1, justifyContent: 'center', fontWeight: 600, fontSize: 16 }}>
                      <input type="radio" name="rate" value={1} checked={form.rate === 1} onChange={() => setForm(p => ({ ...p, rate: 1 }))} style={{ display: 'none' }} />
                      1%
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px', borderRadius: 8, border: form.rate === 1.5 ? '2px solid var(--primary)' : '2px solid var(--border)', cursor: 'pointer', background: form.rate === 1.5 ? 'var(--primary-light)' : 'transparent', flex: 1, justifyContent: 'center', fontWeight: 600, fontSize: 16 }}>
                      <input type="radio" name="rate" value={1.5} checked={form.rate === 1.5} onChange={() => setForm(p => ({ ...p, rate: 1.5 }))} style={{ display: 'none' }} />
                      1,5%
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px', borderRadius: 8, border: form.rate === 3 ? '2px solid var(--primary)' : '2px solid var(--border)', cursor: 'pointer', background: form.rate === 3 ? 'var(--primary-light)' : 'transparent', flex: 1, justifyContent: 'center', fontWeight: 600, fontSize: 16 }}>
                      <input type="radio" name="rate" value={3} checked={form.rate === 3} onChange={() => setForm(p => ({ ...p, rate: 3 }))} style={{ display: 'none' }} />
                      3%
                    </label>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Montant base HT</label>
                    <input className="form-input" type="number" step="0.001" value={form.base_amount} onChange={e => setForm(p => ({ ...p, base_amount: parseFloat(e.target.value) || 0 }))} required />
                  </div>
                  <div className="form-group">
                    <label>Montant retenu</label>
                    <input className="form-input" type="text" value={fmt(taxAmount) + ' TND'} readOnly style={{ background: 'var(--bg-main)', fontWeight: 700, color: 'var(--primary)' }} />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Date</label>
                    <input className="form-input" type="date" value={form.date} onChange={e => setForm(p => ({ ...p, date: e.target.value }))} required />
                  </div>
                  <div className="form-group">
                    <label>N° certificat / Référence</label>
                    <input className="form-input" value={form.reference} onChange={e => setForm(p => ({ ...p, reference: e.target.value }))} placeholder="RS-2026-001" />
                  </div>
                </div>

                {/* Bénéficiaire */}
                {activeTab === 'emise' ? (
                  <div className="form-group">
                    <label>Fournisseur</label>
                    <select className="form-input" value={form.supplier_id} onChange={e => setForm(p => ({ ...p, supplier_id: e.target.value }))}>
                      <option value="">— Sélectionner ou saisir manuellement —</option>
                      {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                    </select>
                  </div>
                ) : (
                  <div className="form-group">
                    <label>Client</label>
                    <select className="form-input" value={form.client_id} onChange={e => setForm(p => ({ ...p, client_id: e.target.value }))}>
                      <option value="">— Sélectionner ou saisir manuellement —</option>
                      {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                )}

                {!form.client_id && !form.supplier_id && (
                  <div className="form-row">
                    <div className="form-group">
                      <label>Nom du bénéficiaire</label>
                      <input className="form-input" value={form.beneficiary_name} onChange={e => setForm(p => ({ ...p, beneficiary_name: e.target.value }))} />
                    </div>
                    <div className="form-group">
                      <label>Matricule fiscal</label>
                      <input className="form-input" value={form.beneficiary_tax_id} onChange={e => setForm(p => ({ ...p, beneficiary_tax_id: e.target.value }))} />
                    </div>
                  </div>
                )}

                <div className="form-group">
                  <label>Notes</label>
                  <textarea className="form-input" rows={2} value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} style={{ resize: 'vertical' }} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>Créer la retenue</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showExport && (
        <div className="modal-overlay" onClick={() => setShowExport(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 420 }}>
            <div className="modal-header"><h3 className="modal-title">Exporter les retenues</h3><button className="btn btn-icon" onClick={() => setShowExport(false)}><FiX /></button></div>
            <div className="modal-body">
              <div className="form-group"><label>Année</label>
                <select className="form-input" value={exportYear} onChange={e => setExportYear(Number(e.target.value))}>
                  {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </div>
              <div className="form-group"><label>Mois</label>
                <select className="form-input" value={exportMonth} onChange={e => setExportMonth(Number(e.target.value))}>
                  <option value={0}>Toute l&apos;année</option>
                  {MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
                </select>
              </div>
            </div>
            <div className="modal-footer" style={{ display: 'flex', gap: 8 }}>
              <a href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/export/retenues?year=${exportYear}${exportMonth ? '&month=' + exportMonth : ''}&format=xlsx&token=${Cookies.get('access_token')}`} className="btn btn-primary" style={{ width: 'auto', textDecoration: 'none' }} onClick={() => setShowExport(false)}><FiDownload /> Excel</a>
              <a href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/export/retenues?year=${exportYear}${exportMonth ? '&month=' + exportMonth : ''}&format=csv&token=${Cookies.get('access_token')}`} className="btn btn-secondary" style={{ width: 'auto', textDecoration: 'none' }} onClick={() => setShowExport(false)}><FiDownload /> CSV</a>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
