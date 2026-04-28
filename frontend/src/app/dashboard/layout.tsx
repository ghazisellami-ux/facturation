'use client';
import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { FiGrid, FiFileText, FiUsers, FiPackage, FiShoppingCart, FiSettings, FiLogOut, FiFile } from 'react-icons/fi';

const navItems = [
  { section: 'Principal', items: [
    { href: '/dashboard', icon: FiGrid, label: 'Tableau de bord' },
  ]},
  { section: 'Ventes', items: [
    { href: '/dashboard/factures', icon: FiFileText, label: 'Factures' },
    { href: '/dashboard/devis', icon: FiFile, label: 'Devis' },
  ]},
  { section: 'Gestion', items: [
    { href: '/dashboard/clients', icon: FiUsers, label: 'Clients' },
    { href: '/dashboard/produits', icon: FiPackage, label: 'Produits' },
  ]},
  { section: 'Paramètres', items: [
    { href: '/dashboard/parametres', icon: FiSettings, label: 'Paramètres' },
  ]},
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, company, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !user) router.replace('/login');
  }, [user, isLoading, router]);

  if (isLoading || !user) return <div className="page-loading"><div className="loading-spinner" /></div>;

  const getInitials = () => `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-brand">SIC <span>Facture</span></div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((section) => (
            <div className="sidebar-section" key={section.section}>
              <div className="sidebar-section-title">{section.section}</div>
              {section.items.map((item) => (
                <Link key={item.href} href={item.href}
                  className={`sidebar-link ${pathname === item.href ? 'active' : ''}`}>
                  <item.icon /> {item.label}
                </Link>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button onClick={logout} className="sidebar-link" style={{ width: '100%', border: 'none', cursor: 'pointer', background: 'transparent', fontFamily: 'inherit' }}>
            <FiLogOut /> Déconnexion
          </button>
        </div>
      </aside>
      <main className="main-content">
        <header className="top-header">
          <h1 className="header-title">{company?.name || 'SIC Facture'}</h1>
          <div className="header-actions">
            <div className="header-avatar" title={`${user.first_name} ${user.last_name}`}>
              {getInitials()}
            </div>
          </div>
        </header>
        <div className="page-content">{children}</div>
      </main>
    </div>
  );
}
