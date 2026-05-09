'use client';
import { useState, useEffect } from 'react';
import { dashboardAPI } from '@/lib/api';
import { FiFileText, FiDollarSign, FiUsers, FiPackage, FiAlertCircle, FiCheckCircle, FiPercent } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface Stats {
  total_invoices: number; total_revenue: number; unpaid_amount: number; paid_amount: number;
  total_clients: number; total_products: number; invoices_this_month: number; revenue_this_month: number;
  tva_a_payer: number; retenue_a_payer: number;
  recent_invoices: any[]; monthly_revenue: any[];
}

const statusMap: Record<string, { label: string; className: string }> = {
  brouillon: { label: 'Brouillon', className: 'badge-default' },
  envoyee: { label: 'Envoyée', className: 'badge-info' },
  payee: { label: 'Payée', className: 'badge-success' },
  partiellement_payee: { label: 'Partielle', className: 'badge-warning' },
  en_retard: { label: 'En retard', className: 'badge-danger' },
  annulee: { label: 'Annulée', className: 'badge-default' },
};

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.getStats().then(res => { setStats(res.data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loading"><div className="loading-spinner" /></div>;
  if (!stats) return <div>Erreur de chargement</div>;

  const fmt = (n: number) => new Intl.NumberFormat('fr-TN', { minimumFractionDigits: 3, maximumFractionDigits: 3 }).format(n);

  return (
    <>
      <div className="kpi-grid">
        <div className="kpi-card blue">
          <div className="kpi-icon blue"><FiFileText /></div>
          <div className="kpi-info">
            <div className="kpi-label">Total Factures</div>
            <div className="kpi-value">{stats.total_invoices}</div>
            <div className="kpi-change" style={{ color: 'var(--primary)' }}>{stats.invoices_this_month} ce mois</div>
          </div>
        </div>
        <div className="kpi-card green">
          <div className="kpi-icon green"><FiDollarSign /></div>
          <div className="kpi-info">
            <div className="kpi-label">Chiffre d&apos;affaires</div>
            <div className="kpi-value text-amount">{fmt(stats.total_revenue)}</div>
            <div className="kpi-change" style={{ color: 'var(--success)' }}>{fmt(stats.revenue_this_month)} ce mois</div>
          </div>
        </div>
        <div className="kpi-card orange">
          <div className="kpi-icon orange"><FiAlertCircle /></div>
          <div className="kpi-info">
            <div className="kpi-label">Impayé</div>
            <div className="kpi-value text-amount">{fmt(stats.unpaid_amount)}</div>
          </div>
        </div>
        <div className="kpi-card red">
          <div className="kpi-icon red"><FiUsers /></div>
          <div className="kpi-info">
            <div className="kpi-label">Clients</div>
            <div className="kpi-value">{stats.total_clients}</div>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <div className="card" style={{ flex: 1, padding: '20px 24px', display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: stats.tva_a_payer >= 0 ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, color: stats.tva_a_payer >= 0 ? '#ef4444' : '#22c55e' }}>
            <FiPercent />
          </div>
          <div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 2 }}>TVA à payer</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: stats.tva_a_payer >= 0 ? '#ef4444' : '#22c55e' }}>{fmt(stats.tva_a_payer)} <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--text-secondary)' }}>TND</span></div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>TVA vente − TVA achat</div>
          </div>
        </div>
        <div className="card" style={{ flex: 1, padding: '20px 24px', display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: stats.retenue_a_payer >= 0 ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, color: stats.retenue_a_payer >= 0 ? '#ef4444' : '#22c55e' }}>
            <FiDollarSign />
          </div>
          <div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 2 }}>Retenue à payer</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: stats.retenue_a_payer >= 0 ? '#ef4444' : '#22c55e' }}>{fmt(stats.retenue_a_payer)} <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--text-secondary)' }}>TND</span></div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>Retenue reçue − Retenue émise</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header"><h3 className="card-title">Chiffre d&apos;affaires mensuel</h3></div>
          <div className="chart-container" style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.monthly_revenue}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#6B7280' }} />
                <YAxis tick={{ fontSize: 12, fill: '#6B7280' }} />
                <Tooltip formatter={(value) => [`${fmt(Number(value))} TND`, 'CA']}
                  contentStyle={{ borderRadius: '10px', border: '1px solid #E5E7EB', fontSize: '13px' }} />
                <Bar dataKey="revenue" fill="url(#blueGradient)" radius={[6, 6, 0, 0]} />
                <defs>
                  <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2196F3" />
                    <stop offset="100%" stopColor="#64B5F6" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header"><h3 className="card-title">Dernières factures</h3></div>
          <div className="table-container">
            <table>
              <thead><tr><th>Réf.</th><th>Client</th><th>Total</th><th>Statut</th></tr></thead>
              <tbody>
                {stats.recent_invoices.length === 0 ? (
                  <tr><td colSpan={4} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>Aucune facture</td></tr>
                ) : stats.recent_invoices.map((inv: any) => (
                  <tr key={inv.id}>
                    <td style={{ fontWeight: 600 }}>{inv.reference}</td>
                    <td>{inv.client_name || '—'}</td>
                    <td className="text-amount">{fmt(inv.total)} <span className="currency">TND</span></td>
                    <td><span className={`badge ${statusMap[inv.status]?.className || 'badge-default'}`}>
                      {statusMap[inv.status]?.label || inv.status}
                    </span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
