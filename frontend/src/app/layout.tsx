import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "@/lib/auth";

export const metadata: Metadata = {
  title: "SIC Facture - Facturation & Gestion Commerciale",
  description: "Logiciel de facturation et gestion commerciale pour TPE/PME. Gérez vos factures, devis, clients et stocks.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>
        <AuthProvider>
          {children}
          <Toaster position="top-right" toastOptions={{
            style: { fontFamily: 'Inter, sans-serif', fontSize: '14px', borderRadius: '10px' },
            success: { duration: 3000 },
            error: { duration: 4000 },
          }} />
        </AuthProvider>
      </body>
    </html>
  );
}
