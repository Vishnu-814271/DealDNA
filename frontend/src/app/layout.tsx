import './globals.css';
import type { Metadata } from 'next';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';

export const metadata: Metadata = {
  title: 'DealDNA AI — The Revenue Memory Engine',
  description: 'AI-powered persistent revenue memory and deal intelligence engine.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <Header />
          <div className="content-shell">
            <Sidebar />
            <main className="page-content">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
