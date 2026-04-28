'use client';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';
import { authAPI } from '@/lib/api';

interface User { id: string; email: string; first_name: string; last_name: string; phone?: string; }
interface Company { id: string; name: string; tax_id?: string; currency: string; }
interface AuthContextType { user: User | null; company: Company | null; isLoading: boolean; login: (email: string, password: string) => Promise<void>; register: (data: any) => Promise<void>; logout: () => void; }

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => { checkAuth(); }, []);

  const checkAuth = async () => {
    try {
      const token = Cookies.get('access_token');
      if (!token) { setIsLoading(false); return; }
      const [userRes, companyRes] = await Promise.all([authAPI.getMe(), authAPI.getCompany()]);
      setUser(userRes.data); setCompany(companyRes.data);
    } catch { Cookies.remove('access_token'); Cookies.remove('refresh_token'); }
    finally { setIsLoading(false); }
  };

  const login = async (email: string, password: string) => {
    const res = await authAPI.login(email, password);
    Cookies.set('access_token', res.data.access_token, { expires: 1 });
    Cookies.set('refresh_token', res.data.refresh_token, { expires: 30 });
    await checkAuth();
  };

  const register = async (data: any) => {
    const res = await authAPI.register(data);
    Cookies.set('access_token', res.data.access_token, { expires: 1 });
    Cookies.set('refresh_token', res.data.refresh_token, { expires: 30 });
    await checkAuth();
  };

  const logout = () => {
    Cookies.remove('access_token'); Cookies.remove('refresh_token');
    setUser(null); setCompany(null); window.location.href = '/login';
  };

  return (<AuthContext.Provider value={{ user, company, isLoading, login, register, logout }}>{children}</AuthContext.Provider>);
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
