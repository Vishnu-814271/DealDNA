"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { fetchJson } from '@/lib/api/client';
import { Deal, MemoryItem } from '@/types';

const navItems = [
  { href: '/', label: 'Overview' },
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/deals', label: 'Deals' },
  { href: '/memory', label: 'Memory' },
  { href: '/assistant', label: 'AI Assistant' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [dealCount, setDealCount] = useState<number | null>(null);
  const [memoryCount, setMemoryCount] = useState<number | null>(null);
  const [openDealCount, setOpenDealCount] = useState<number>(0);

  useEffect(() => {
    Promise.all([
      fetchJson<Deal[]>('/deals'),
      fetchJson<MemoryItem[]>('/memory'),
    ])
      .then(([deals, memories]) => {
        setDealCount(deals.length);
        setMemoryCount(memories.length);
        setOpenDealCount(deals.filter((d) => d.stage !== 'WON' && d.stage !== 'LOST').length);
      })
      .catch(() => {});
  }, []);

  return (
    <aside className="sidebar">
      <div className="nav-group">
        <div className="nav-label">Workspace</div>
        <nav className="nav-list">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href));
            return (
              <Link key={item.href} href={item.href} className={`nav-item ${isActive ? 'active' : ''}`}>
                <span className="nav-dot" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="sidebar-card">
        <div className="nav-label" style={{ marginBottom: '0.75rem' }}>Signal</div>
        <div className="metric-row">
          <span>Active Deals</span>
          <span className="status info">{openDealCount ?? '—'}</span>
        </div>
        <div className="metric-row" style={{ marginTop: '0.5rem' }}>
          <span>Total Deals</span>
          <span className="status success">{dealCount ?? '—'}</span>
        </div>
        <div className="metric-row" style={{ marginTop: '0.5rem' }}>
          <span>Memories</span>
          <span className="status warning">{memoryCount ?? '—'}</span>
        </div>
      </div>
    </aside>
  );
}
